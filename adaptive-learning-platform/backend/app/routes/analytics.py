from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from bson import ObjectId

from app.core.database import get_database
from app.core.security import get_current_user_id
from app.models.analytics import (
    WeaknessMapResponse,
    WeaknessAnalysis,
    AIExplanation,
    ExplainAnswerRequest,
    AdaptiveTargeting,
    BehavioralSignals,
    CognitiveScores,
    LearningVelocity,
    ForgettingCurveData,
    ExamReadinessScore,
    BehaviorFingerprint
)
from app.models.test_session import QuestionAnswer, TestStatus
from app.services.analytics_service import AnalyticsService
from app.services.analytics_service_v2 import AnalyticsServiceV2
from app.services.question_stats_service import QuestionStatsService
from app.services.advanced_analytics_service import AdvancedAnalyticsService
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
    request: ExplainAnswerRequest,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Get AI-generated explanation for a wrong answer"""

    session = await db.test_sessions.find_one({
        "_id": ObjectId(request.session_id),
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
        if answer["question_id"] == request.question_id:
            user_answer_data = answer
            break

    if not user_answer_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Answer not found"
        )

    # Get question
    question = await db.questions.find_one({"_id": ObjectId(request.question_id)})
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )

    # Handle missing or None user_answer
    user_answer = user_answer_data.get("user_answer") or "SKIPPED"

    # Build behavioral context - NO HALLUCINATION
    behavioral_context = {
        "time_spent": user_answer_data.get("time_taken", 0),
        "skipped": user_answer_data.get("status") == "skipped",
        "hesitation_count": user_answer_data.get("hesitation_count", 0),
        "marked_tricky": user_answer_data.get("marked_tricky", False)
    }

    # Generate explanation using LLM WITH behavioral grounding
    llm_service = LLMService()

    try:
        explanation = await llm_service.explain_wrong_answer(
            question=question["question_text"],
            user_answer=user_answer,
            correct_answer=question["correct_answer"],
            context=question["source_context"],
            behavioral_context=behavioral_context
        )

        # Extract source grounding
        source_paragraph = explanation.get("source_paragraph", question["source_context"][:200] + "...")
        section_ref = explanation.get("section_reference", question.get("section_title", "Source material"))

        return AIExplanation(
            question_id=request.question_id,
            user_answer=user_answer,
            correct_answer=question["correct_answer"],
            source_paragraph=source_paragraph,
            section_reference=section_ref,
            why_wrong=explanation["why_wrong"],
            concept_explanation=explanation["concept_explanation"],
            common_mistake=explanation["common_mistake"],
            behavioral_insight=explanation.get("behavioral_insight", "N/A")
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


# ============================================================
# WORLD-CLASS FEATURES
# ============================================================

@router.get("/user/learning-velocity")
async def get_learning_velocity(
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """
    Get learning velocity across all topics
    
    Returns: "You learn CNNs 3× faster than Transformers"
    """
    velocities = await AdvancedAnalyticsService.compare_learning_velocities(
        user_id, db
    )
    
    return {
        "velocities": [v.dict() for v in velocities]
    }


@router.get("/user/topic/{topic}/learning-velocity", response_model=LearningVelocity)
async def get_topic_learning_velocity(
    topic: str,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Get learning velocity for specific topic"""
    return await AdvancedAnalyticsService.calculate_learning_velocity(
        user_id, topic, db
    )


@router.get("/user/topic/{topic}/forgetting-curve", response_model=ForgettingCurveData)
async def get_forgetting_curve(
    topic: str,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """
    Detect if mastery has decayed over time
    
    Returns: Ebbinghaus forgetting curve analysis
    """
    return await AdvancedAnalyticsService.detect_forgetting_curve(
        user_id, topic, db
    )


@router.get("/document/{document_id}/exam-readiness", response_model=ExamReadinessScore)
async def get_exam_readiness(
    document_id: str,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """
    Holistic exam readiness score
    
    Returns: "You are 72% ready for this exam"
    """
    return await AdvancedAnalyticsService.calculate_exam_readiness(
        user_id, document_id, db
    )


@router.get("/session/{session_id}/behavior-fingerprint", response_model=BehaviorFingerprint)
async def get_behavior_fingerprint(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """
    Deep personality profiling from session
    
    Traits: risk-taker, perfectionist, skimmer, grinder
    """
    
    # Get session
    session = await db.test_sessions.find_one({
        "_id": ObjectId(session_id),
        "user_id": ObjectId(user_id)
    })
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test session not found"
        )
    
    # Get questions and build signals
    question_ids = [ObjectId(q_id) for q_id in session["questions"]]
    cursor = db.questions.find({"_id": {"$in": question_ids}})
    questions_data = await cursor.to_list(length=1000)
    question_lookup = {str(q["_id"]): q for q in questions_data}
    
    # Extract behavioral signals
    signals = []
    for answer in session["answers"]:
        question = question_lookup.get(answer["question_id"])
        if question:
            # Get empirical difficulty
            empirical_diff = await QuestionStatsService.get_empirical_difficulty(
                answer["question_id"], db
            )
            
            signal = BehavioralSignals(
                question_id=answer["question_id"],
                time_spent=answer.get("time_taken", 0),
                answered=answer.get("status") != "skipped",
                correct=answer.get("status") == "correct",
                changed_answer=answer.get("changed_answer", False),
                hesitation_count=answer.get("hesitation_count", 0),
                marked_tricky=answer.get("marked_tricky", False),
                empirical_difficulty=empirical_diff,
                topic=question.get("topic", "Unknown"),
                llm_difficulty=question.get("difficulty", "medium")
            )
            signals.append(signal)
    
    # Generate fingerprint
    fingerprint = await AdvancedAnalyticsService.generate_behavior_fingerprint(
        user_id, signals, db
    )
    
    return fingerprint


@router.get("/user/behavior-fingerprint-aggregate", response_model=BehaviorFingerprint)
async def get_aggregate_behavior_fingerprint(
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """
    Aggregate behavior fingerprint across ALL user sessions
    
    Most accurate personality profiling
    """
    
    # Get all completed sessions
    sessions = await db.test_sessions.find({
        "user_id": ObjectId(user_id),
        "status": "completed"
    }).to_list(length=100)
    
    if not sessions:
        return AdvancedAnalyticsService._default_fingerprint(user_id)
    
    # Collect all signals across all sessions
    all_signals = []
    
    for session in sessions:
        question_ids = [ObjectId(q_id) for q_id in session["questions"]]
        cursor = db.questions.find({"_id": {"$in": question_ids}})
        questions_data = await cursor.to_list(length=1000)
        question_lookup = {str(q["_id"]): q for q in questions_data}
        
        for answer in session["answers"]:
            question = question_lookup.get(answer["question_id"])
            if question:
                empirical_diff = await QuestionStatsService.get_empirical_difficulty(
                    answer["question_id"], db
                )
                
                signal = BehavioralSignals(
                    question_id=answer["question_id"],
                    time_spent=answer.get("time_taken", 0),
                    answered=answer.get("status") != "skipped",
                    correct=answer.get("status") == "correct",
                    changed_answer=answer.get("changed_answer", False),
                    hesitation_count=answer.get("hesitation_count", 0),
                    marked_tricky=answer.get("marked_tricky", False),
                    empirical_difficulty=empirical_diff,
                    topic=question.get("topic", "Unknown"),
                    llm_difficulty=question.get("difficulty", "medium")
                )
                all_signals.append(signal)
    
    # Generate aggregate fingerprint
    fingerprint = await AdvancedAnalyticsService.generate_behavior_fingerprint(
        user_id, all_signals, db
    )
    
    return fingerprint
