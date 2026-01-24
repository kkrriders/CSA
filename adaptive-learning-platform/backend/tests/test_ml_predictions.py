"""
Tests for ML prediction service.
"""
import pytest
from datetime import datetime, timedelta
from app.services.ml_prediction_service import MLPredictionService


@pytest.mark.asyncio
@pytest.mark.integration
async def test_predict_success(test_db, test_user):
    """Test success prediction."""
    user_id = str(test_user["_id"])

    # Create sessions with varying scores
    for score in [60, 70, 80, 85, 90]:
        await test_db.test_sessions.insert_one({
            "user_id": user_id,
            "status": "completed",
            "answers": [
                {"topic": "Python", "correct": True if score > 70 else False}
                for _ in range(10)
            ]
        })

    prediction = await MLPredictionService.predict_success(
        db=test_db,
        user_id=user_id,
        topic="Python"
    )

    assert "probability" in prediction
    assert "confidence" in prediction
    assert 0 <= prediction["probability"] <= 1


@pytest.mark.asyncio
@pytest.mark.integration
async def test_detect_burnout(test_db, test_user):
    """Test burnout detection."""
    user_id = str(test_user["_id"])

    # Create declining performance pattern
    now = datetime.utcnow()
    for i, score in enumerate([90, 85, 75, 65, 55]):
        await test_db.test_sessions.insert_one({
            "user_id": user_id,
            "completed_at": now - timedelta(days=i),
            "score": score,
            "total_time": 3600,
            "answers": [],
            "status": "completed"
        })

    burnout = await MLPredictionService.detect_burnout(
        db=test_db,
        user_id=user_id
    )

    assert "risk" in burnout
    assert "indicators" in burnout
    assert burnout["risk"] in ["low", "medium", "high", "unknown"]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_recommend_difficulty(test_db, test_user):
    """Test difficulty recommendation."""
    user_id = str(test_user["_id"])

    # Create session with high easy performance
    await test_db.test_sessions.insert_one({
        "user_id": user_id,
        "status": "completed",
        "answers": [
            {"topic": "Python", "difficulty": "Easy", "correct": True}
            for _ in range(10)
        ]
    })

    difficulty = await MLPredictionService.recommend_next_difficulty(
        db=test_db,
        user_id=user_id,
        topic="Python"
    )

    assert difficulty in ["Easy", "Medium", "Hard", "Tricky"]
