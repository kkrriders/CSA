"""
Review scheduling routes for spaced repetition.
"""
from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
from bson import ObjectId

from app.core.database import get_database
from app.core.security import get_current_user_id
from app.models.review import ReviewResponse, ReviewSession
from app.services.spaced_repetition_service import SpacedRepetitionService

router = APIRouter()


@router.get("/queue")
async def get_review_queue(
    document_id: str = None,
    limit: int = 20,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Get the user's review queue (due reviews)."""
    queue = await SpacedRepetitionService.get_due_reviews(
        db=db,
        user_id=user_id,
        document_id=document_id,
        limit=limit
    )

    return {
        "queue": queue,
        "total_due": len(queue)
    }


@router.post("/sessions")
async def create_review_session(
    document_id: str = None,
    max_reviews: int = 20,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Create a new review session from due reviews."""
    # Get due reviews
    queue = await SpacedRepetitionService.get_due_reviews(
        db=db,
        user_id=user_id,
        document_id=document_id,
        limit=max_reviews
    )

    if not queue:
        return {
            "message": "No reviews due at this time",
            "session": None
        }

    # Create session
    session = ReviewSession(
        user_id=user_id,
        document_id=document_id,
        review_ids=[item.review_id for item in queue],
        total_reviews=len(queue)
    )

    result = await db.review_sessions.insert_one(session.dict())

    return {
        "session_id": str(result.inserted_id),
        "total_reviews": len(queue),
        "reviews": queue
    }


@router.post("/sessions/{session_id}/reviews/{review_id}")
async def submit_review_response(
    session_id: str,
    review_id: str,
    response: ReviewResponse,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Submit a response to a review question."""
    # Verify session ownership
    session = await db.review_sessions.find_one({
        "_id": ObjectId(session_id),
        "user_id": user_id
    })

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review session not found"
        )

    # Update the review
    updated_review = await SpacedRepetitionService.update_review(
        db=db,
        review_id=review_id,
        response=response
    )

    # Update session progress
    await db.review_sessions.update_one(
        {"_id": ObjectId(session_id)},
        {
            "$inc": {"completed_reviews": 1},
            "$set": {
                "average_quality": (
                    session.get("average_quality", 0) * session.get("completed_reviews", 0) +
                    response.quality
                ) / (session.get("completed_reviews", 0) + 1)
            }
        }
    )

    return {
        "review_id": review_id,
        "next_review_date": updated_review.next_review_date,
        "interval_days": updated_review.interval,
        "message": "Review updated successfully"
    }


@router.post("/sessions/{session_id}/complete")
async def complete_review_session(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Mark a review session as complete."""
    session = await db.review_sessions.find_one({
        "_id": ObjectId(session_id),
        "user_id": user_id
    })

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review session not found"
        )

    await db.review_sessions.update_one(
        {"_id": ObjectId(session_id)},
        {"$set": {"completed_at": datetime.utcnow()}}
    )

    return {
        "session_id": session_id,
        "completed_reviews": session.get("completed_reviews", 0),
        "total_reviews": session.get("total_reviews", 0),
        "average_quality": session.get("average_quality", 0),
        "message": "Review session completed"
    }


@router.get("/schedule")
async def get_review_schedule(
    document_id: str = None,
    topic: str = None,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Get the user's review schedule."""
    schedule = await SpacedRepetitionService.get_review_schedule(
        db=db,
        user_id=user_id,
        document_id=document_id,
        topic=topic
    )

    return schedule


@router.put("/{review_id}/reschedule")
async def reschedule_review(
    review_id: str,
    new_date: datetime,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Manually reschedule a review."""
    # Verify review ownership
    review = await db.reviews.find_one({
        "_id": ObjectId(review_id),
        "user_id": user_id
    })

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )

    await SpacedRepetitionService.reschedule_review(
        db=db,
        review_id=review_id,
        new_date=new_date
    )

    return {
        "review_id": review_id,
        "new_date": new_date,
        "message": "Review rescheduled successfully"
    }


@router.post("/from-session/{session_id}")
async def create_reviews_from_session(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Create review items from questions answered incorrectly in a test session."""
    reviews_created = await SpacedRepetitionService.create_reviews_from_mistakes(
        db=db,
        user_id=user_id,
        session_id=session_id
    )

    return {
        "session_id": session_id,
        "reviews_created": reviews_created,
        "message": f"Created {reviews_created} review items from incorrect answers"
    }
