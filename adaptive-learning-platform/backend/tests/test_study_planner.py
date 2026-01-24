"""
Tests for study plan service.
"""
import pytest
from datetime import datetime, timedelta
from app.services.study_planner_service import StudyPlannerService
from app.models.study_plan import CreateStudyPlanRequest


@pytest.mark.asyncio
@pytest.mark.integration
async def test_generate_study_plan(test_db, test_user, test_document):
    """Test study plan generation."""
    request = CreateStudyPlanRequest(
        document_id=str(test_document["_id"]),
        title="Test Study Plan",
        target_date=datetime.utcnow() + timedelta(days=30),
        sessions_per_week=3,
        session_duration_minutes=30
    )

    plan = await StudyPlannerService.generate_plan(
        db=test_db,
        user_id=str(test_user["_id"]),
        request=request
    )

    assert plan.title == "Test Study Plan"
    assert len(plan.sessions) > 0
    assert plan.total_sessions == len(plan.sessions)
    assert plan.sessions_per_week == 3


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_next_session(test_db, test_user):
    """Test getting next session from a plan."""
    # Create a plan with sessions
    plan_data = {
        "user_id": str(test_user["_id"]),
        "document_id": "doc1",
        "title": "Test Plan",
        "sessions": [
            {"session_number": 1, "completed": False, "topic": "Topic1"},
            {"session_number": 2, "completed": False, "topic": "Topic2"}
        ],
        "total_sessions": 2
    }

    result = await test_db.study_plans.insert_one(plan_data)
    plan_id = str(result.inserted_id)

    # Get next session
    next_session = await StudyPlannerService.get_next_session(
        db=test_db,
        plan_id=plan_id
    )

    assert "next_session" in next_session
    assert next_session["next_session"]["session_number"] == 1
