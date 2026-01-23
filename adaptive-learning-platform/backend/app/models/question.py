from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
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


class QuestionType(str, Enum):
    MCQ = "mcq"
    SHORT_ANSWER = "short_answer"
    CONCEPTUAL = "conceptual"


class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    TRICKY = "tricky"


class MCQOption(BaseModel):
    text: str
    is_correct: bool
    explanation: Optional[str] = None


class QuestionBase(BaseModel):
    question_text: str
    question_type: QuestionType
    difficulty: DifficultyLevel
    topic: str
    section_title: Optional[str] = None


class QuestionCreate(QuestionBase):
    document_id: str
    options: Optional[List[MCQOption]] = None
    correct_answer: str
    explanation: str
    source_context: str  # The text from document this question is based on


class QuestionInDB(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    document_id: PyObjectId
    user_id: PyObjectId
    question_text: str
    question_type: QuestionType
    difficulty: DifficultyLevel
    topic: str
    section_title: Optional[str] = None
    options: Optional[List[MCQOption]] = None
    correct_answer: str
    explanation: str
    source_context: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class QuestionResponse(BaseModel):
    id: str = Field(alias="_id")
    question_text: str
    question_type: QuestionType
    difficulty: DifficultyLevel
    topic: str
    section_title: Optional[str] = None
    options: Optional[List[Dict[str, str]]] = None  # Hide is_correct and explanation

    class Config:
        populate_by_name = True


class QuestionWithAnswer(QuestionResponse):
    correct_answer: str
    explanation: str
    options: Optional[List[MCQOption]] = None

    class Config:
        populate_by_name = True


class GenerateQuestionsRequest(BaseModel):
    document_id: str
    num_questions: int = Field(..., ge=5, le=100)
    difficulty_distribution: Optional[Dict[DifficultyLevel, int]] = None
    topics: Optional[List[str]] = None  # Specific topics to focus on
    question_types: List[QuestionType] = [QuestionType.MCQ, QuestionType.SHORT_ANSWER, QuestionType.CONCEPTUAL]


class GenerateQuestionsResponse(BaseModel):
    document_id: str
    total_generated: int
    questions: List[QuestionResponse]
