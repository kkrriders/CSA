"""
Tests for spaced repetition service.
"""
import pytest
from datetime import datetime, timedelta
from app.services.spaced_repetition_service import SpacedRepetitionService
from app.models.review import ReviewResponse


@pytest.mark.asyncio
@pytest.mark.unit
async def test_sm2_algorithm():
    """Test SM-2 algorithm calculations."""
    # Initial review - quality 4 (good)
    interval, reps, ease = SpacedRepetitionService.calculate_next_review(
        interval=1,
        repetitions=0,
        ease_factor=2.5,
        quality=4
    )

    assert reps == 1
    assert interval == 1  # First repetition is 1 day
    assert ease > 2.5  # Ease factor should increase

    # Second review - quality 5 (perfect)
    interval, reps, ease = SpacedRepetitionService.calculate_next_review(
        interval=interval,
        repetitions=reps,
        ease_factor=ease,
        quality=5
    )

    assert reps == 2
    assert interval == 6  # Second repetition is 6 days

    # Forgot (quality < 3) - reset
    interval, reps, ease = SpacedRepetitionService.calculate_next_review(
        interval=interval,
        repetitions=reps,
        ease_factor=ease,
        quality=2
    )

    assert reps == 0
    assert interval == 1  # Reset to 1 day


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_and_update_review(test_db, test_user, test_questions):
    """Test creating and updating a review."""
    # Create review
    review_id = await SpacedRepetitionService.create_review(
        db=test_db,
        user_id=str(test_user["_id"]),
        question_id=str(test_questions[0]["_id"]),
        document_id="doc123",
        topic="Testing",
        difficulty="Medium"
    )

    assert review_id is not None

    # Update review with good response
    response = ReviewResponse(quality=4, time_spent=30, correct=True)
    updated = await SpacedRepetitionService.update_review(
        db=test_db,
        review_id=review_id,
        response=response
    )

    assert updated.interval > 0
    assert updated.total_reviews == 1
    assert updated.successful_reviews == 1


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_due_reviews(test_db, test_user):
    """Test getting due reviews."""
    # Create some reviews
    past_date = datetime.utcnow() - timedelta(days=2)

    await test_db.reviews.insert_one({
        "user_id": str(test_user["_id"]),
        "question_id": "q1",
        "document_id": "doc1",
        "topic": "Topic1",
        "difficulty": "Medium",
        "interval": 1,
        "repetitions": 0,
        "ease_factor": 2.5,
        "next_review_date": past_date
    })

    # Get due reviews
    due = await SpacedRepetitionService.get_due_reviews(
        db=test_db,
        user_id=str(test_user["_id"])
    )

    assert len(due) > 0
    assert due[0].days_overdue >= 2
