"""
Tests for analytics services (v2 and advanced).
"""
import pytest
from datetime import datetime, timedelta


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.analytics
async def test_behavioral_signals_extraction(test_session):
    """Test extraction of behavioral signals from session data."""
    from app.services.analytics_service_v2 import AnalyticsServiceV2

    service = AnalyticsServiceV2()
    signals = service._extract_behavioral_signals(test_session["questions"][0])

    assert signals["time_spent"] == 25
    assert signals["answered"] is True
    assert signals["correct"] is True
    assert signals["changed_answer"] is False
    assert signals["hesitation_count"] == 0
    assert signals["marked_tricky"] is False


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.analytics
async def test_cognitive_scores_calculation():
    """Test cognitive score calculations."""
    from app.services.analytics_service_v2 import AnalyticsServiceV2

    service = AnalyticsServiceV2()

    # Test guessing score (fast wrong on hard question)
    signals = {
        "time_spent": 10,
        "answered": True,
        "correct": False,
        "changed_answer": False,
        "hesitation_count": 0,
        "difficulty": "Hard"
    }
    scores = service._calculate_cognitive_scores(signals)
    assert scores["guessing"] > 0.5  # High guessing probability

    # Test confusion score (slow wrong with hesitation)
    signals = {
        "time_spent": 80,
        "answered": True,
        "correct": False,
        "changed_answer": True,
        "hesitation_count": 3,
        "difficulty": "Medium"
    }
    scores = service._calculate_cognitive_scores(signals)
    assert scores["confusion"] > 0.5  # High confusion

    # Test confidence score (fast correct)
    signals = {
        "time_spent": 20,
        "answered": True,
        "correct": True,
        "changed_answer": False,
        "hesitation_count": 0,
        "difficulty": "Medium"
    }
    scores = service._calculate_cognitive_scores(signals)
    assert scores["confidence"] > 0.5  # High confidence


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.analytics
async def test_topic_mastery_calculation():
    """Test topic mastery score calculation."""
    from app.services.analytics_service_v2 import AnalyticsServiceV2

    service = AnalyticsServiceV2()

    # Mock question answers for a topic
    topic_answers = [
        {"correct": True, "difficulty": "Easy", "time_spent": 20},
        {"correct": True, "difficulty": "Medium", "time_spent": 30},
        {"correct": False, "difficulty": "Hard", "time_spent": 60},
    ]

    mastery = service._calculate_topic_mastery("Testing", topic_answers)

    assert 0 <= mastery <= 1
    assert mastery > 0  # Should have some mastery with 2/3 correct


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.analytics
async def test_weakness_priority_calculation():
    """Test weakness priority scoring."""
    from app.services.analytics_service_v2 import AnalyticsServiceV2

    service = AnalyticsServiceV2()

    # High priority weakness: low mastery, high exposure, low confidence
    weakness = {
        "topic": "Difficult Topic",
        "mastery": 0.2,
        "exposure": 10,
        "avg_confidence": 0.3
    }

    priority = service._calculate_weakness_priority(weakness)
    assert priority > 0.5  # Should be high priority


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.analytics
async def test_forgetting_curve_calculation():
    """Test forgetting curve half-life calculation."""
    from app.services.advanced_analytics_service import AdvancedAnalyticsService

    service = AdvancedAnalyticsService()

    # Mock session data with mastery decline
    sessions = [
        {"timestamp": datetime.utcnow() - timedelta(days=10), "mastery": 0.9},
        {"timestamp": datetime.utcnow() - timedelta(days=5), "mastery": 0.7},
        {"timestamp": datetime.utcnow(), "mastery": 0.5}
    ]

    half_life = service._calculate_half_life(sessions)
    assert half_life > 0  # Should have positive half-life
    assert half_life < 30  # Reasonable half-life for learning


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.analytics
async def test_learning_velocity_calculation():
    """Test learning velocity calculation."""
    from app.services.advanced_analytics_service import AdvancedAnalyticsService

    service = AdvancedAnalyticsService()

    # Mock improving mastery over time
    sessions = [
        {"session_number": 1, "mastery": 0.3},
        {"session_number": 2, "mastery": 0.5},
        {"session_number": 3, "mastery": 0.7},
        {"session_number": 4, "mastery": 0.85}
    ]

    velocity = service._calculate_velocity(sessions)
    assert velocity > 0  # Positive velocity for improvement
    assert velocity < 1  # Reasonable velocity range


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.analytics
async def test_exam_readiness_score():
    """Test exam readiness score calculation."""
    from app.services.advanced_analytics_service import AdvancedAnalyticsService

    service = AdvancedAnalyticsService()

    # Mock metrics for readiness
    metrics = {
        "avg_mastery": 0.85,
        "consistency": 0.9,
        "confidence": 0.8,
        "coverage": 0.95
    }

    readiness = service._calculate_exam_readiness(metrics)

    assert 0 <= readiness <= 100
    assert readiness > 70  # Should be "Almost Ready" or better


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.analytics
async def test_behavior_fingerprint_traits():
    """Test behavior fingerprint trait calculations."""
    from app.services.advanced_analytics_service import AdvancedAnalyticsService

    service = AdvancedAnalyticsService()

    # Mock behavioral data for a risk-taker
    behaviors = {
        "avg_time_on_hard": 20,  # Fast on hard questions
        "hard_question_attempts": 15,
        "skip_rate": 0.1,  # Low skip rate
        "guess_rate": 0.3  # High guess rate
    }

    traits = service._calculate_behavior_traits(behaviors)

    assert "risk_taking" in traits
    assert "perfectionism" in traits
    assert "skimming" in traits
    assert "grinding" in traits

    # Risk taker should have high risk_taking score
    assert traits["risk_taking"] > 0.5
