from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from bson import ObjectId
from enum import Enum


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")


class TestStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class AnswerStatus(str, Enum):
    CORRECT = "correct"
    WRONG = "wrong"
    SKIPPED = "skipped"
    NOT_ATTEMPTED = "not_attempted"


class QuestionAnswer(BaseModel):
    """Raw behavioral signals - NO interpretations"""
    question_id: str
    user_answer: Optional[str] = None
    is_correct: Optional[bool] = None
    time_taken: int = 0  # seconds - RAW SIGNAL
    status: AnswerStatus = AnswerStatus.NOT_ATTEMPTED
    marked_tricky: bool = False  # RAW SIGNAL - user explicitly marked
    marked_review: bool = False  # RAW SIGNAL
    answered_at: Optional[datetime] = None
    # Additional raw signals
    changed_answer: bool = False  # Did user change their answer?
    hesitation_count: int = 0  # How many times they changed before submitting
    time_to_first_answer: Optional[int] = None  # Time until first option selected


class TestConfig(BaseModel):
    total_questions: int
    time_per_question: int = 90
    topics: Optional[List[str]] = None
    difficulty_levels: Optional[List[str]] = None
    question_types: Optional[List[str]] = None  # NEW: MCQ, short_answer, or both


class TestSessionCreate(BaseModel):
    document_id: str
    config: TestConfig


class TestSessionInDB(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    document_id: PyObjectId
    config: TestConfig
    questions: List[str]  # List of question IDs
    answers: List[QuestionAnswer] = []
    current_question_index: int = 0
    status: TestStatus = TestStatus.IN_PROGRESS
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class TestSessionResponse(BaseModel):
    id: str = Field(alias="_id")
    document_id: str
    config: TestConfig
    current_question_index: int
    total_questions: int
    status: TestStatus
    started_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        populate_by_name = True


class SubmitAnswerRequest(BaseModel):
    question_id: str
    user_answer: str
    time_taken: int


class SubmitAnswerResponse(BaseModel):
    is_correct: bool
    correct_answer: str
    explanation: str
    next_question_index: int
    is_test_complete: bool


class MarkQuestionRequest(BaseModel):
    question_id: str
    marked_tricky: bool = False
    marked_review: bool = False


class TestScore(BaseModel):
    total_questions: int
    correct: int
    wrong: int
    skipped: int
    not_attempted: int
    percentage: float
    time_spent: int  # total seconds
    marked_tricky_count: int
    marked_review_count: int


class TestResult(BaseModel):
    session_id: str
    score: TestScore
    answers: List[QuestionAnswer]
    tricky_questions: List[str]  # question IDs
    wrong_questions: List[str]  # question IDs
    completed_at: datetime
