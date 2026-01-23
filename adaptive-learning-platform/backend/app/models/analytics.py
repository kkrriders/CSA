from pydantic import BaseModel, Field
from typing import List, Dict, Optional
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


class FailurePattern(str, Enum):
    FAST_WRONG = "fast_wrong"  # Guessed
    SLOW_WRONG = "slow_wrong"  # Confused
    REPEATED_TOPIC = "repeated_topic_failure"  # Doesn't understand concept
    TRICKY_WRONG = "tricky_wrong"  # High-priority weakness
    EASY_WRONG = "easy_wrong"  # Dangerous knowledge gap


class TopicMastery(BaseModel):
    topic: str
    total_attempts: int
    correct_attempts: int
    wrong_attempts: int
    mastery_percentage: float
    avg_time_taken: float
    difficulty_breakdown: Dict[str, Dict[str, int]] = {}  # {easy: {correct: x, wrong: y}, ...}


class WeaknessAnalysis(BaseModel):
    topic: str
    mastery_percentage: float
    failure_patterns: List[FailurePattern]
    question_ids: List[str]
    priority_score: float  # Higher = more urgent to review
    recommendation: str


class CognitiveProfile(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    document_id: PyObjectId
    topic_mastery: List[TopicMastery] = []
    weakness_areas: List[WeaknessAnalysis] = []
    overall_stats: Dict[str, any] = {}
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class PatternDetection(BaseModel):
    session_id: str
    patterns: List[Dict[str, any]]


class WeaknessMapResponse(BaseModel):
    user_id: str
    document_id: str
    weakness_areas: List[WeaknessAnalysis]
    high_priority_topics: List[str]
    recommended_focus: List[str]


class AIExplanation(BaseModel):
    question_id: str
    user_answer: str
    correct_answer: str
    why_wrong: str
    concept_explanation: str
    common_mistake: str


class AdaptiveTargeting(BaseModel):
    weak_topics: List[str]
    recommended_difficulty: List[str]
    focus_question_types: List[str]
    estimated_questions_needed: int


class ReviewOrder(BaseModel):
    question_id: str
    priority: int  # 1 = highest
    reason: str
    topic: str
