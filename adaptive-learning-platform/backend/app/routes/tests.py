from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from bson import ObjectId
from datetime import datetime
import random

from app.core.database import get_database
from app.core.security import get_current_user_id
from app.models.test_session import (
    TestSessionCreate,
    TestSessionResponse,
    TestStatus,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
    MarkQuestionRequest,
    TestResult,
    TestScore,
    QuestionAnswer,
    AnswerStatus
)
from app.models.question import QuestionResponse, QuestionWithAnswer
from app.services.question_stats_service import QuestionStatsService

router = APIRouter()


@router.post("/start", response_model=TestSessionResponse, status_code=status.HTTP_201_CREATED)
async def start_test(
    test_config: TestSessionCreate,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Start a new test session"""

    # Verify document exists and belongs to user
    document = await db.documents.find_one({
        "_id": ObjectId(test_config.document_id),
        "user_id": ObjectId(user_id)
    })

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # Get available questions
    query = {"document_id": ObjectId(test_config.document_id)}

    if test_config.config.topics:
        query["topic"] = {"$in": test_config.config.topics}

    if test_config.config.difficulty_levels:
        query["difficulty"] = {"$in": test_config.config.difficulty_levels}

    # CRITICAL: Filter by question type (MCQ vs Short Answer)
    if test_config.config.question_types:
        # Convert enum to string if needed
        question_types = [qt if isinstance(qt, str) else qt.value for qt in test_config.config.question_types]
        query["question_type"] = {"$in": question_types}

    cursor = db.questions.find(query)
    available_questions = await cursor.to_list(length=1000)

    if len(available_questions) < test_config.config.total_questions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Not enough questions available. Found {len(available_questions)}, need {test_config.config.total_questions}"
        )

    # Randomly select questions
    selected_questions = random.sample(available_questions, test_config.config.total_questions)
    question_ids = [str(q["_id"]) for q in selected_questions]

    # Initialize answers
    answers = [
        QuestionAnswer(
            question_id=q_id,
            status=AnswerStatus.NOT_ATTEMPTED
        ).dict()
        for q_id in question_ids
    ]

    # Create test session
    session = {
        "user_id": ObjectId(user_id),
        "document_id": ObjectId(test_config.document_id),
        "config": test_config.config.dict(),
        "questions": question_ids,
        "answers": answers,
        "current_question_index": 0,
        "status": TestStatus.IN_PROGRESS,
        "started_at": datetime.utcnow(),
        "completed_at": None
    }

    result = await db.test_sessions.insert_one(session)

    return TestSessionResponse(
        _id=str(result.inserted_id),
        document_id=test_config.document_id,
        config=test_config.config,
        current_question_index=0,
        total_questions=test_config.config.total_questions,
        status=TestStatus.IN_PROGRESS,
        started_at=session["started_at"]
    )


@router.get("/{session_id}", response_model=TestSessionResponse)
async def get_test_session(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Get test session details"""

    session = await db.test_sessions.find_one({
        "_id": ObjectId(session_id),
        "user_id": ObjectId(user_id)
    })

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test session not found"
        )

    from app.models.test_session import TestConfig

    return TestSessionResponse(
        _id=str(session["_id"]),
        document_id=str(session["document_id"]),
        config=TestConfig(**session["config"]),
        current_question_index=session["current_question_index"],
        total_questions=len(session["questions"]),
        status=session["status"],
        started_at=session["started_at"],
        completed_at=session.get("completed_at")
    )


@router.get("/{session_id}/current-question", response_model=QuestionResponse)
async def get_current_question(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Get the current question for the test"""

    session = await db.test_sessions.find_one({
        "_id": ObjectId(session_id),
        "user_id": ObjectId(user_id)
    })

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test session not found"
        )

    if session["status"] != TestStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Test is not in progress"
        )

    current_index = session["current_question_index"]
    if current_index >= len(session["questions"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No more questions available"
        )

    question_id = session["questions"][current_index]
    question = await db.questions.find_one({"_id": ObjectId(question_id)})

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )

    return QuestionResponse(
        _id=str(question["_id"]),
        question_text=question["question_text"],
        question_type=question["question_type"],
        difficulty=question["difficulty"],
        topic=question["topic"],
        section_title=question.get("section_title"),
        options=[
            {"text": opt["text"]}
            for opt in question.get("options", [])
        ] if question.get("options") else None
    )


@router.post("/{session_id}/submit-answer", response_model=SubmitAnswerResponse)
async def submit_answer(
    session_id: str,
    answer_data: SubmitAnswerRequest,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Submit answer for current question"""

    session = await db.test_sessions.find_one({
        "_id": ObjectId(session_id),
        "user_id": ObjectId(user_id)
    })

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test session not found"
        )

    if session["status"] != TestStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Test is not in progress"
        )

    current_index = session["current_question_index"]

    # Get question and check answer
    question = await db.questions.find_one({"_id": ObjectId(answer_data.question_id)})

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )

    is_correct = answer_data.user_answer.strip().lower() == question["correct_answer"].strip().lower()

    # Update empirical difficulty statistics
    await QuestionStatsService.update_question_stats(
        question_id=answer_data.question_id,
        correct=is_correct,
        time_taken=answer_data.time_taken,
        db=db
    )

    # Update answer in session
    answer_update = {
        "question_id": answer_data.question_id,
        "user_answer": answer_data.user_answer,
        "is_correct": is_correct,
        "time_taken": answer_data.time_taken,
        "status": AnswerStatus.CORRECT if is_correct else AnswerStatus.WRONG,
        "answered_at": datetime.utcnow(),
        # Initialize new behavioral fields
        "changed_answer": False,  # TODO: Track in frontend
        "hesitation_count": 0  # TODO: Track in frontend
    }

    session["answers"][current_index] = answer_update

    # Move to next question
    next_index = current_index + 1
    is_complete = next_index >= len(session["questions"])

    update_data = {
        "answers": session["answers"],
        "current_question_index": next_index
    }

    if is_complete:
        update_data["status"] = TestStatus.COMPLETED
        update_data["completed_at"] = datetime.utcnow()

    await db.test_sessions.update_one(
        {"_id": ObjectId(session_id)},
        {"$set": update_data}
    )

    return SubmitAnswerResponse(
        is_correct=is_correct,
        correct_answer=question["correct_answer"],
        explanation=question["explanation"],
        next_question_index=next_index,
        is_test_complete=is_complete
    )


@router.post("/{session_id}/mark-question", status_code=status.HTTP_200_OK)
async def mark_question(
    session_id: str,
    mark_data: MarkQuestionRequest,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Mark a question as tricky or for review"""

    session = await db.test_sessions.find_one({
        "_id": ObjectId(session_id),
        "user_id": ObjectId(user_id)
    })

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test session not found"
        )

    # Find answer and update marks
    for answer in session["answers"]:
        if answer["question_id"] == mark_data.question_id:
            answer["marked_tricky"] = mark_data.marked_tricky
            answer["marked_review"] = mark_data.marked_review
            break

    await db.test_sessions.update_one(
        {"_id": ObjectId(session_id)},
        {"$set": {"answers": session["answers"]}}
    )

    return {"status": "success"}


@router.post("/{session_id}/finish-early", status_code=status.HTTP_200_OK)
async def finish_test_early(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Finish test early and mark remaining questions as skipped"""

    session = await db.test_sessions.find_one({
        "_id": ObjectId(session_id),
        "user_id": ObjectId(user_id)
    })

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test session not found"
        )

    if session["status"] == TestStatus.COMPLETED:
        return {"status": "already_completed"}

    # Mark all remaining questions as skipped
    current_index = session["current_question_index"]
    answers = session["answers"]

    for i in range(current_index, len(answers)):
        if answers[i]["status"] == AnswerStatus.NOT_ATTEMPTED:
            answers[i]["status"] = AnswerStatus.SKIPPED
            answers[i]["answered_at"] = datetime.utcnow()

    # Mark test as completed
    await db.test_sessions.update_one(
        {"_id": ObjectId(session_id)},
        {"$set": {
            "status": TestStatus.COMPLETED,
            "completed_at": datetime.utcnow(),
            "answers": answers
        }}
    )

    return {"status": "success"}


@router.get("/{session_id}/results", response_model=TestResult)
async def get_test_results(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Get test results and analytics"""

    session = await db.test_sessions.find_one({
        "_id": ObjectId(session_id),
        "user_id": ObjectId(user_id)
    })

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test session not found"
        )

    if session["status"] != TestStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Test not yet completed"
        )

    # Calculate score
    answers = [QuestionAnswer(**a) for a in session["answers"]]

    correct = sum(1 for a in answers if a.status == AnswerStatus.CORRECT)
    wrong = sum(1 for a in answers if a.status == AnswerStatus.WRONG)
    skipped = sum(1 for a in answers if a.status == AnswerStatus.SKIPPED)
    not_attempted = sum(1 for a in answers if a.status == AnswerStatus.NOT_ATTEMPTED)
    total = len(answers)

    percentage = (correct / total * 100) if total > 0 else 0
    time_spent = sum(a.time_taken for a in answers)

    marked_tricky = [a.question_id for a in answers if a.marked_tricky]
    marked_review = [a.question_id for a in answers if a.marked_review]
    wrong_questions = [a.question_id for a in answers if a.status == AnswerStatus.WRONG]

    score = TestScore(
        total_questions=total,
        correct=correct,
        wrong=wrong,
        skipped=skipped,
        not_attempted=not_attempted,
        percentage=round(percentage, 2),
        time_spent=time_spent,
        marked_tricky_count=len(marked_tricky),
        marked_review_count=len(marked_review)
    )

    return TestResult(
        session_id=session_id,
        score=score,
        answers=answers,
        tricky_questions=marked_tricky,
        wrong_questions=wrong_questions,
        completed_at=session["completed_at"]
    )


@router.get("/{session_id}/review-questions", response_model=List[QuestionWithAnswer])
async def get_review_questions(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Get marked and wrong questions for review"""

    session = await db.test_sessions.find_one({
        "_id": ObjectId(session_id),
        "user_id": ObjectId(user_id)
    })

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test session not found"
        )

    # Get marked or wrong questions
    review_question_ids = []
    for answer in session["answers"]:
        if (answer.get("marked_tricky") or
            answer.get("marked_review") or
            answer.get("status") == AnswerStatus.WRONG):
            review_question_ids.append(answer["question_id"])

    # Fetch full questions
    questions = []
    for q_id in review_question_ids:
        question = await db.questions.find_one({"_id": ObjectId(q_id)})
        if question:
            from app.models.question import MCQOption

            questions.append(QuestionWithAnswer(
                _id=str(question["_id"]),
                question_text=question["question_text"],
                question_type=question["question_type"],
                difficulty=question["difficulty"],
                topic=question["topic"],
                section_title=question.get("section_title"),
                options=[MCQOption(**opt) for opt in question.get("options", [])],
                correct_answer=question["correct_answer"],
                explanation=question["explanation"]
            ))

    return questions
