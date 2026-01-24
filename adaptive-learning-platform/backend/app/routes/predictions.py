"""
ML prediction routes.
"""
from fastapi import APIRouter, Depends

from app.core.database import get_database
from app.core.security import get_current_user_id
try:
    from app.services.ml_prediction_service import MLPredictionService
except ImportError:
    # Fallback to version without sklearn
    from app.services.ml_prediction_service_fallback import MLPredictionService

router = APIRouter()


@router.get("/success/{topic}")
async def predict_success(
    topic: str,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Predict probability of success on a topic."""
    return await MLPredictionService.predict_success(
        db=db,
        user_id=user_id,
        topic=topic
    )


@router.get("/burnout-risk")
async def detect_burnout_risk(
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Detect burnout risk from behavioral patterns."""
    return await MLPredictionService.detect_burnout(
        db=db,
        user_id=user_id
    )


@router.get("/next-difficulty/{topic}")
async def recommend_difficulty(
    topic: str,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Recommend optimal difficulty for next session."""
    difficulty = await MLPredictionService.recommend_next_difficulty(
        db=db,
        user_id=user_id,
        topic=topic
    )

    return {
        "recommended_difficulty": difficulty,
        "topic": topic
    }
