"""
Performance comparison and ranking routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.database import get_database
from app.core.security import get_current_user_id
from app.services.comparison_service import ComparisonService

router = APIRouter()


@router.get("/percentile-ranking/{document_id}")
async def get_percentile_ranking(
    document_id: str,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Get user's percentile ranking for a document."""
    return await ComparisonService.calculate_percentile_ranking(
        db=db,
        user_id=user_id,
        document_id=document_id
    )


@router.get("/peer-comparison/{document_id}")
async def get_peer_comparison(
    document_id: str,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Get anonymized peer comparison."""
    return await ComparisonService.get_peer_comparison(
        db=db,
        user_id=user_id,
        document_id=document_id
    )


@router.get("/historical")
async def get_historical_comparison(
    document_id: str = None,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Compare current vs historical performance."""
    return await ComparisonService.get_historical_comparison(
        db=db,
        user_id=user_id,
        document_id=document_id
    )


@router.get("/cohort-stats/{document_id}")
async def get_cohort_stats(
    document_id: str,
    db=Depends(get_database)
):
    """Get aggregate cohort statistics for a document."""
    return await ComparisonService.get_cohort_stats(
        db=db,
        document_id=document_id
    )
