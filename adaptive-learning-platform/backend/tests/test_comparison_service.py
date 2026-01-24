"""
Tests for comparison and ranking service.
"""
import pytest
from app.services.comparison_service import ComparisonService


@pytest.mark.asyncio
@pytest.mark.integration
async def test_percentile_ranking(test_db, test_user, test_document):
    """Test percentile ranking calculation."""
    # Create sessions for multiple users
    document_id = str(test_document["_id"])
    user_id = str(test_user["_id"])

    # User1: 80% average
    for score in [75, 80, 85]:
        await test_db.test_sessions.insert_one({
            "user_id": user_id,
            "document_id": document_id,
            "score": score,
            "status": "completed"
        })

    # Other users with various scores
    for i, score in enumerate([60, 65, 70, 90, 95]):
        await test_db.test_sessions.insert_one({
            "user_id": f"other_user_{i}",
            "document_id": document_id,
            "score": score,
            "status": "completed"
        })

    # Get ranking
    ranking = await ComparisonService.calculate_percentile_ranking(
        db=test_db,
        user_id=user_id,
        document_id=document_id
    )

    assert "percentile" in ranking
    assert ranking["percentile"] >= 0 and ranking["percentile"] <= 100
    assert "rank" in ranking


@pytest.mark.asyncio
@pytest.mark.integration
async def test_peer_comparison(test_db, test_user, test_document):
    """Test peer comparison."""
    document_id = str(test_document["_id"])
    user_id = str(test_user["_id"])

    # User session
    await test_db.test_sessions.insert_one({
        "user_id": user_id,
        "document_id": document_id,
        "score": 85,
        "total_time": 1200,
        "status": "completed"
    })

    # Peer sessions
    for i in range(5):
        await test_db.test_sessions.insert_one({
            "user_id": f"peer_{i}",
            "document_id": document_id,
            "score": 70 + i * 3,
            "total_time": 1500 - i * 50,
            "status": "completed"
        })

    comparison = await ComparisonService.get_peer_comparison(
        db=test_db,
        user_id=user_id,
        document_id=document_id
    )

    assert "your_stats" in comparison
    assert "peer_stats" in comparison
    assert "comparison" in comparison
