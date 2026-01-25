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
from app.services.question_selection_service import QuestionSelectionService

router = APIRouter()


@router.get("/in-progress", response_model=List[TestSessionResponse])
async def get_in_progress_tests(
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Get all in-progress tests for current user (only those worth resuming)"""

    cursor = db.test_sessions.find({
        "user_id": ObjectId(user_id),
        "status": TestStatus.IN_PROGRESS
    }).sort("started_at", -1)

    sessions = await cursor.to_list(length=100)

    from app.models.test_session import TestConfig

    # Only return sessions with at least 1 correct answer (worth resuming)
    worth_resuming = []
    for s in sessions:
        answers = s.get("answers", [])
        has_correct = any(a.get("is_correct") == True for a in answers)

        if has_correct:
            worth_resuming.append(
                TestSessionResponse(
                    _id=str(s["_id"]),
                    document_id=str(s["document_id"]),
                    config=TestConfig(**s["config"]),
                    current_question_index=s["current_question_index"],
                    total_questions=len(s.get("questions", [])),
                    status=s["status"],
                    started_at=s["started_at"],
                    completed_at=s.get("completed_at")
                )
            )

    return worth_resuming


@router.post("/start", response_model=TestSessionResponse, status_code=status.HTTP_201_CREATED)
async def start_test(
    test_config: TestSessionCreate,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Start a new test session OR resume existing in-progress test"""

    # CHECK FOR EXISTING IN-PROGRESS TEST FIRST
    existing_test = await db.test_sessions.find_one({
        "user_id": ObjectId(user_id),
        "document_id": ObjectId(test_config.document_id),
        "status": TestStatus.IN_PROGRESS
    })

    if existing_test:
        # Check if test is worth resuming (has at least 1 correct answer)
        answers = existing_test.get("answers", [])
        has_correct = any(a.get("is_correct") == True for a in answers)

        if has_correct:
            # Return existing test - user will resume where they left off
            from app.models.test_session import TestConfig
            return TestSessionResponse(
                _id=str(existing_test["_id"]),
                document_id=str(existing_test["document_id"]),
                config=TestConfig(**existing_test["config"]),
                current_question_index=existing_test["current_question_index"],
                total_questions=len(existing_test.get("questions", [])),
                status=existing_test["status"],
                started_at=existing_test["started_at"],
                completed_at=existing_test.get("completed_at")
            )
        else:
            # Test has no correct answers, delete it and create new one
            await db.test_sessions.delete_one({"_id": existing_test["_id"]})

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

    # SMART QUESTION SELECTION - Reuse existing questions first!
    # This reduces LLM costs and database load significantly

    # Prepare filters
    question_types = None
    if test_config.config.question_types:
        question_types = [qt if isinstance(qt, str) else qt.value for qt in test_config.config.question_types]

    # Get available questions using intelligent selection
    selected_questions, needs_generation = await QuestionSelectionService.get_available_questions(
        document_id=test_config.document_id,
        user_id=user_id,
        num_needed=test_config.config.total_questions,
        question_types=question_types,
        topics=test_config.config.topics,
        difficulty_levels=test_config.config.difficulty_levels,
        db=db
    )

    # AUTO-GENERATE if not enough questions available
    if needs_generation:
        num_missing = test_config.config.total_questions - len(selected_questions)

        # Trigger background question generation
        from app.routes.questions import generate_questions_background
        from app.models.question import QuestionType

        # Convert question types
        gen_question_types = [QuestionType.MCQ, QuestionType.SHORT_ANSWER] if not question_types else [
            QuestionType(qt) if isinstance(qt, str) else qt for qt in question_types
        ]

        # Generate questions in background
        import asyncio
        asyncio.create_task(generate_questions_background(
            document_id=test_config.document_id,
            user_id=user_id,
            num_questions=num_missing,
            difficulty_distribution=None,
            topics=test_config.config.topics or [],
            question_types=gen_question_types
        ))

        # Inform user to wait
        raise HTTPException(
            status_code=status.HTTP_202_ACCEPTED,
            detail=f"Generating {num_missing} questions. Please wait 30-60 seconds and try again."
        )

    # Mark these questions as used
    question_ids = [str(q["_id"]) for q in selected_questions]
    await QuestionSelectionService.mark_questions_used(question_ids, db)

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

    # Validate questions array exists and has items
    if not session.get("questions") or len(session["questions"]) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Test session has no questions. Please create a new test."
        )

    if current_index >= len(session["questions"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No more questions available. Test may be complete."
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

    # Update question performance tracking (for smart reuse)
    await QuestionSelectionService.update_question_performance(
        question_id=answer_data.question_id,
        is_correct=is_correct,
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
