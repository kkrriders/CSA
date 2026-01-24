"""
Study plan routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId

from app.core.database import get_database
from app.core.security import get_current_user_id
from app.models.study_plan import CreateStudyPlanRequest
from app.services.study_planner_service import StudyPlannerService

router = APIRouter()


@router.post("/generate")
async def generate_study_plan(
    request: CreateStudyPlanRequest,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Generate a personalized study plan."""
    plan = await StudyPlannerService.generate_plan(
        db=db,
        user_id=user_id,
        request=request
    )

    # Save plan
    result = await db.study_plans.insert_one(plan.dict())

    return {
        "plan_id": str(result.inserted_id),
        "message": "Study plan created successfully",
        "plan": plan
    }


@router.get("/{plan_id}")
async def get_study_plan(
    plan_id: str,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Get a study plan."""
    plan = await db.study_plans.find_one({
        "_id": ObjectId(plan_id),
        "user_id": user_id
    })

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study plan not found"
        )

    return plan


@router.get("/{plan_id}/next-session")
async def get_next_session(
    plan_id: str,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Get the next recommended session."""
    # Verify ownership
    plan = await db.study_plans.find_one({
        "_id": ObjectId(plan_id),
        "user_id": user_id
    })

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study plan not found"
        )

    return await StudyPlannerService.get_next_session(db=db, plan_id=plan_id)


@router.post("/{plan_id}/complete-session/{session_number}")
async def complete_session(
    plan_id: str,
    session_number: int,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Mark a session as completed."""
    # Verify ownership
    plan = await db.study_plans.find_one({
        "_id": ObjectId(plan_id),
        "user_id": user_id
    })

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study plan not found"
        )

    await StudyPlannerService.complete_session(
        db=db,
        plan_id=plan_id,
        session_number=session_number
    )

    return {"message": "Session marked as completed"}


@router.get("/{plan_id}/progress")
async def get_plan_progress(
    plan_id: str,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Get study plan progress."""
    # Verify ownership
    plan = await db.study_plans.find_one({
        "_id": ObjectId(plan_id),
        "user_id": user_id
    })

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study plan not found"
        )

    return await StudyPlannerService.get_progress(db=db, plan_id=plan_id)


@router.get("/")
async def list_study_plans(
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """List all study plans for the user."""
    cursor = db.study_plans.find({"user_id": user_id}).sort("created_at", -1)
    plans = await cursor.to_list(length=100)

    return {"plans": plans, "total": len(plans)}
