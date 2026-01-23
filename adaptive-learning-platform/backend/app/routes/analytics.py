from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from bson import ObjectId

from app.core.database import get_database
from app.core.security import get_current_user_id
from app.models.analytics import (
    WeaknessMapResponse,
    WeaknessAnalysis,
    AIExplanation,
    AdaptiveTargeting
)
from app.models.test_session import QuestionAnswer, TestStatus
from app.services.analytics_service import AnalyticsService
from app.services.llm_service import LLMService

router = APIRouter()


@router.get("/session/{session_id}/patterns")
async def get_session_patterns(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Detect cognitive patterns from a test session"""

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

    answers = [QuestionAnswer(**a) for a in session["answers"]]
    patterns = AnalyticsService.detect_answer_patterns(answers)

    return {
        "session_id": session_id,
        "patterns": patterns,
        "summary": {
            "fast_wrong_count": len(patterns["fast_wrong"]),
            "slow_wrong_count": len(patterns["slow_wrong"]),
            "tricky_wrong_count": len(patterns["tricky_wrong"])
        }
    }


@router.get("/session/{session_id}/topic-mastery")
async def get_topic_mastery(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Get topic-wise mastery analysis"""

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

    # Get all questions for this session
    question_ids = [ObjectId(q_id) for q_id in session["questions"]]
    cursor = db.questions.find({"_id": {"$in": question_ids}})
    questions_data = await cursor.to_list(length=1000)

    # Convert to format needed
    questions_data = [{**q, "_id": str(q["_id"])} for q in questions_data]

    answers = [QuestionAnswer(**a) for a in session["answers"]]
    topic_mastery = AnalyticsService.calculate_topic_mastery(answers, questions_data)

    return {
        "session_id": session_id,
        "topic_mastery": [tm.dict() for tm in topic_mastery]
    }


@router.get("/session/{session_id}/weakness-map", response_model=WeaknessMapResponse)
async def get_weakness_map(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Generate cognitive weakness map"""

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

    # Get questions
    question_ids = [ObjectId(q_id) for q_id in session["questions"]]
    cursor = db.questions.find({"_id": {"$in": question_ids}})
    questions_data = await cursor.to_list(length=1000)
    questions_data = [{**q, "_id": str(q["_id"])} for q in questions_data]

    # Analyze
    answers = [QuestionAnswer(**a) for a in session["answers"]]
    patterns = AnalyticsService.detect_answer_patterns(answers)
    topic_mastery = AnalyticsService.calculate_topic_mastery(answers, questions_data)
    weakness_areas = AnalyticsService.identify_weakness_areas(
        topic_mastery,
        patterns,
        questions_data
    )

    # Get high priority topics
    high_priority = [w.topic for w in weakness_areas if w.priority_score > 50]
    recommended = [w.topic for w in weakness_areas[:3]]  # Top 3

    return WeaknessMapResponse(
        user_id=user_id,
        document_id=str(session["document_id"]),
        weakness_areas=weakness_areas,
        high_priority_topics=high_priority,
        recommended_focus=recommended
    )


@router.get("/session/{session_id}/adaptive-targeting", response_model=AdaptiveTargeting)
async def get_adaptive_targeting(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Get adaptive targeting for next test"""

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

    # Get questions and analyze
    question_ids = [ObjectId(q_id) for q_id in session["questions"]]
    cursor = db.questions.find({"_id": {"$in": question_ids}})
    questions_data = await cursor.to_list(length=1000)
    questions_data = [{**q, "_id": str(q["_id"])} for q in questions_data]

    answers = [QuestionAnswer(**a) for a in session["answers"]]
    patterns = AnalyticsService.detect_answer_patterns(answers)
    topic_mastery = AnalyticsService.calculate_topic_mastery(answers, questions_data)
    weakness_areas = AnalyticsService.identify_weakness_areas(
        topic_mastery,
        patterns,
        questions_data
    )

    adaptive_targeting = AnalyticsService.generate_adaptive_targeting(weakness_areas)

    return adaptive_targeting


@router.get("/session/{session_id}/review-order")
async def get_smart_review_order(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Get smart ordering for question review"""

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

    # Get review questions (marked or wrong)
    review_question_ids = []
    for answer in session["answers"]:
        if (answer.get("marked_tricky") or
            answer.get("marked_review") or
            answer.get("status") == "wrong"):
            review_question_ids.append(answer["question_id"])

    if not review_question_ids:
        return {"review_order": [], "message": "No questions to review"}

    # Get questions and analyze
    question_ids = [ObjectId(q_id) for q_id in session["questions"]]
    cursor = db.questions.find({"_id": {"$in": question_ids}})
    questions_data = await cursor.to_list(length=1000)
    questions_data = [{**q, "_id": str(q["_id"])} for q in questions_data]

    answers = [QuestionAnswer(**a) for a in session["answers"]]
    patterns = AnalyticsService.detect_answer_patterns(answers)
    topic_mastery = AnalyticsService.calculate_topic_mastery(answers, questions_data)
    weakness_areas = AnalyticsService.identify_weakness_areas(
        topic_mastery,
        patterns,
        questions_data
    )

    review_order = AnalyticsService.smart_review_ordering(
        weakness_areas,
        review_question_ids
    )

    return {"review_order": review_order}


@router.post("/explain-wrong-answer", response_model=AIExplanation)
async def explain_wrong_answer(
    session_id: str,
    question_id: str,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Get AI-generated explanation for a wrong answer"""

    session = await db.test_sessions.find_one({
        "_id": ObjectId(session_id),
        "user_id": ObjectId(user_id)
    })

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test session not found"
        )

    # Find the answer
    user_answer_data = None
    for answer in session["answers"]:
        if answer["question_id"] == question_id:
            user_answer_data = answer
            break

    if not user_answer_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Answer not found"
        )

    # Get question
    question = await db.questions.find_one({"_id": ObjectId(question_id)})
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )

    # Generate explanation using LLM
    llm_service = LLMService()

    try:
        explanation = await llm_service.explain_wrong_answer(
            question=question["question_text"],
            user_answer=user_answer_data["user_answer"],
            correct_answer=question["correct_answer"],
            context=question["source_context"]
        )

        return AIExplanation(
            question_id=question_id,
            user_answer=user_answer_data["user_answer"],
            correct_answer=question["correct_answer"],
            why_wrong=explanation["why_wrong"],
            concept_explanation=explanation["concept_explanation"],
            common_mistake=explanation["common_mistake"]
        )
    finally:
        await llm_service.close()


@router.get("/document/{document_id}/overall-performance")
async def get_overall_performance(
    document_id: str,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Get overall performance across all tests for a document"""

    # Get all completed sessions for this document
    cursor = db.test_sessions.find({
        "document_id": ObjectId(document_id),
        "user_id": ObjectId(user_id),
        "status": TestStatus.COMPLETED
    })

    sessions = await cursor.to_list(length=100)

    if not sessions:
        return {
            "message": "No completed tests found",
            "total_tests": 0
        }

    # Aggregate stats
    total_tests = len(sessions)
    total_questions = 0
    total_correct = 0
    total_time = 0

    for session in sessions:
        answers = session["answers"]
        total_questions += len(answers)
        total_correct += sum(1 for a in answers if a.get("status") == "correct")
        total_time += sum(a.get("time_taken", 0) for a in answers)

    avg_accuracy = (total_correct / total_questions * 100) if total_questions > 0 else 0
    avg_time_per_question = (total_time / total_questions) if total_questions > 0 else 0

    return {
        "document_id": document_id,
        "total_tests": total_tests,
        "total_questions_attempted": total_questions,
        "total_correct": total_correct,
        "average_accuracy": round(avg_accuracy, 2),
        "average_time_per_question": round(avg_time_per_question, 2)
    }
