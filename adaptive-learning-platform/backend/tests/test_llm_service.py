"""
Tests for LLM service.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.llm
async def test_llm_provider_selection():
    """Test LLM provider selection based on config."""
    from app.services.llm_service import LLMService
    from app.core.config import settings

    service = LLMService()
    assert service.provider in ["ollama", "huggingface", "lmstudio", "openrouter"]


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.llm
async def test_generate_questions_structure(mock_llm_response):
    """Test question generation returns correct structure."""
    from app.services.llm_service import LLMService

    service = LLMService()

    # Mock the LLM call
    with patch.object(service, '_call_llm', new=AsyncMock(return_value=mock_llm_response)):
        questions = await service.generate_questions(
            content="Test content about TDD",
            topics=["Testing"],
            num_questions=1,
            difficulty="Medium"
        )

        assert len(questions) > 0
        question = questions[0]
        assert "question_type" in question
        assert "difficulty" in question
        assert "question_text" in question
        assert "correct_answer" in question
        assert "explanation" in question


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.llm
async def test_generate_mcq_has_options(mock_llm_response):
    """Test MCQ generation includes options."""
    from app.services.llm_service import LLMService

    service = LLMService()

    with patch.object(service, '_call_llm', new=AsyncMock(return_value=mock_llm_response)):
        questions = await service.generate_questions(
            content="Test content",
            topics=["Testing"],
            num_questions=1,
            difficulty="Easy"
        )

        mcq_questions = [q for q in questions if q["question_type"] == "MCQ"]
        if mcq_questions:
            assert "options" in mcq_questions[0]
            assert len(mcq_questions[0]["options"]) >= 2


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.llm
async def test_generate_explanation_with_citations():
    """Test explanation generation includes citations."""
    from app.services.llm_service import LLMService

    service = LLMService()

    mock_explanation = {
        "explanation": "The answer is correct because...",
        "source_citation": "From section 2, paragraph 3: 'Unit tests...'"
    }

    with patch.object(service, '_call_llm', new=AsyncMock(return_value=mock_explanation)):
        explanation = await service.generate_explanation(
            question="What is a unit test?",
            correct_answer="A test of a single unit",
            user_answer="A test of the entire system",
            source_content="Unit tests focus on individual components."
        )

        assert "explanation" in explanation
        assert "source_citation" in explanation or "citation" in explanation.lower()


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.llm
async def test_llm_error_handling():
    """Test LLM service handles errors gracefully."""
    from app.services.llm_service import LLMService

    service = LLMService()

    # Mock LLM failure
    with patch.object(service, '_call_llm', new=AsyncMock(side_effect=Exception("LLM API error"))):
        with pytest.raises(Exception):
            await service.generate_questions(
                content="Test",
                topics=["Test"],
                num_questions=1
            )


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.llm
async def test_question_validation():
    """Test generated questions are validated."""
    from app.services.llm_service import LLMService

    service = LLMService()

    # Mock invalid question (missing required fields)
    invalid_response = {
        "questions": [
            {
                "question_type": "MCQ",
                # Missing difficulty, question_text, etc.
            }
        ]
    }

    with patch.object(service, '_call_llm', new=AsyncMock(return_value=invalid_response)):
        questions = await service.generate_questions(
            content="Test",
            topics=["Test"],
            num_questions=1
        )

        # Should filter out invalid questions or raise error
        assert len(questions) == 0 or all("question_text" in q for q in questions)
