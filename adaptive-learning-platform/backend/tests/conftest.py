"""
Pytest fixtures and configuration for backend tests.
"""
import asyncio
import os
from typing import AsyncGenerator, Generator
import pytest
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.testclient import TestClient
from httpx import AsyncClient

# Set test environment
os.environ["TESTING"] = "true"
os.environ["MONGODB_URI"] = os.getenv("MONGODB_TEST_URI", "mongodb://localhost:27017/test_adaptive_learning")
os.environ["SECRET_KEY"] = "test-secret-key-do-not-use-in-production"

from app.main import app
from app.core.database import get_database


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def test_db() -> AsyncGenerator:
    """
    Create a test database connection.
    Cleans up after each test.
    """
    client = AsyncIOMotorClient(os.getenv("MONGODB_URI"))
    db_name = "test_adaptive_learning"
    db = client[db_name]

    # Clean database before test
    await client.drop_database(db_name)

    yield db

    # Clean database after test
    await client.drop_database(db_name)
    client.close()


@pytest.fixture(scope="function")
def client() -> Generator:
    """
    Create a test client for synchronous tests.
    """
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="function")
async def async_client() -> AsyncGenerator:
    """
    Create an async test client for async tests.
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def test_user(test_db) -> dict:
    """
    Create a test user in the database.
    """
    from app.models.user import UserInDB
    from app.core.security import get_password_hash

    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": get_password_hash("testpassword123"),
        "full_name": "Test User"
    }

    result = await test_db.users.insert_one(user_data)
    user_data["_id"] = result.inserted_id

    return user_data


@pytest.fixture
async def auth_headers(test_user) -> dict:
    """
    Create authentication headers for a test user.
    """
    from app.core.security import create_access_token

    access_token = create_access_token(data={"sub": test_user["username"]})
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
async def test_document(test_db, test_user) -> dict:
    """
    Create a test document in the database.
    """
    document_data = {
        "title": "Test Document",
        "user_id": str(test_user["_id"]),
        "content": "This is test content for learning.",
        "file_type": "markdown",
        "sections": [
            {
                "title": "Introduction",
                "content": "Introduction to testing",
                "topics": ["Testing", "Python"]
            },
            {
                "title": "Advanced Concepts",
                "content": "Advanced testing concepts",
                "topics": ["Mocking", "Fixtures"]
            }
        ],
        "metadata": {
            "total_sections": 2,
            "total_topics": 4
        }
    }

    result = await test_db.documents.insert_one(document_data)
    document_data["_id"] = result.inserted_id

    return document_data


@pytest.fixture
async def test_questions(test_db, test_document) -> list:
    """
    Create test questions in the database.
    """
    from datetime import datetime

    questions = [
        {
            "document_id": str(test_document["_id"]),
            "topic": "Testing",
            "difficulty": "Easy",
            "question_type": "MCQ",
            "question_text": "What is a unit test?",
            "options": [
                "A test of a single unit",
                "A test of the entire system",
                "A performance test",
                "A security test"
            ],
            "correct_answer": "A test of a single unit",
            "explanation": "Unit tests focus on individual components.",
            "source_section": "Introduction",
            "created_at": datetime.utcnow()
        },
        {
            "document_id": str(test_document["_id"]),
            "topic": "Mocking",
            "difficulty": "Medium",
            "question_type": "MCQ",
            "question_text": "Why use mocks in testing?",
            "options": [
                "To isolate the code under test",
                "To make tests slower",
                "To avoid testing",
                "To complicate the code"
            ],
            "correct_answer": "To isolate the code under test",
            "explanation": "Mocks help isolate dependencies.",
            "source_section": "Advanced Concepts",
            "created_at": datetime.utcnow()
        },
        {
            "document_id": str(test_document["_id"]),
            "topic": "Fixtures",
            "difficulty": "Hard",
            "question_type": "Short Answer",
            "question_text": "What are pytest fixtures?",
            "correct_answer": "Reusable test setup and teardown code",
            "explanation": "Fixtures provide a fixed baseline for tests.",
            "source_section": "Advanced Concepts",
            "created_at": datetime.utcnow()
        }
    ]

    result = await test_db.questions.insert_many(questions)
    for i, q in enumerate(questions):
        q["_id"] = result.inserted_ids[i]

    return questions


@pytest.fixture
async def test_session(test_db, test_user, test_document, test_questions) -> dict:
    """
    Create a test session with answers.
    """
    from datetime import datetime

    session_data = {
        "user_id": str(test_user["_id"]),
        "document_id": str(test_document["_id"]),
        "questions": [
            {
                "question_id": str(test_questions[0]["_id"]),
                "topic": test_questions[0]["topic"],
                "difficulty": test_questions[0]["difficulty"],
                "answered": True,
                "correct": True,
                "user_answer": test_questions[0]["correct_answer"],
                "time_spent": 25,
                "changed_answer": False,
                "hesitation_count": 0,
                "marked_tricky": False
            },
            {
                "question_id": str(test_questions[1]["_id"]),
                "topic": test_questions[1]["topic"],
                "difficulty": test_questions[1]["difficulty"],
                "answered": True,
                "correct": False,
                "user_answer": "To make tests slower",
                "time_spent": 60,
                "changed_answer": True,
                "hesitation_count": 2,
                "marked_tricky": True
            },
            {
                "question_id": str(test_questions[2]["_id"]),
                "topic": test_questions[2]["topic"],
                "difficulty": test_questions[2]["difficulty"],
                "answered": False,
                "correct": False,
                "user_answer": None,
                "time_spent": 15,
                "changed_answer": False,
                "hesitation_count": 0,
                "marked_tricky": False
            }
        ],
        "started_at": datetime.utcnow(),
        "completed_at": datetime.utcnow(),
        "total_time": 100,
        "score": 33.33
    }

    result = await test_db.test_sessions.insert_one(session_data)
    session_data["_id"] = result.inserted_id

    return session_data


@pytest.fixture
def mock_llm_response():
    """
    Mock LLM response for question generation.
    """
    return {
        "questions": [
            {
                "question_type": "MCQ",
                "difficulty": "Medium",
                "question_text": "What is test-driven development?",
                "options": [
                    "Writing tests before code",
                    "Writing tests after code",
                    "Never writing tests",
                    "Only manual testing"
                ],
                "correct_answer": "Writing tests before code",
                "explanation": "TDD involves writing tests first.",
                "topic": "Testing Methodologies"
            }
        ]
    }
