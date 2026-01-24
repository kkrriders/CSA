"""
Study plan models.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class SessionType(str, Enum):
    """Types of study sessions."""
    PRACTICE = "practice"
    REVIEW = "review"
    TEST = "test"
    BREAK = "break"


class StudySessionPlan(BaseModel):
    """Individual study session in a plan."""
    session_number: int
    session_type: SessionType
    topic: str
    difficulty: Optional[str] = None
    duration_minutes: int
    num_questions: int
    scheduled_date: datetime
    completed: bool = False
    completed_at: Optional[datetime] = None


class StudyPlan(BaseModel):
    """Complete study plan."""
    user_id: str
    document_id: str
    title: str
    description: str

    # Goal
    goal_type: str  # "mastery", "exam_prep", "review"
    target_date: Optional[datetime] = None
    target_mastery: float = 0.85

    # Sessions
    sessions: List[StudySessionPlan] = []
    total_sessions: int = 0
    completed_sessions: int = 0

    # Timing
    sessions_per_week: int = 3
    estimated_hours: float = 0.0

    # Status
    active: bool = True
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CreateStudyPlanRequest(BaseModel):
    """Request to create a study plan."""
    document_id: str
    title: str
    goal_type: str = "mastery"
    target_date: Optional[datetime] = None
    sessions_per_week: int = 3
    session_duration_minutes: int = 30


class StudyPlanProgress(BaseModel):
    """Study plan progress summary."""
    plan_id: str
    total_sessions: int
    completed_sessions: int
    progress_percentage: float
    on_schedule: bool
    days_remaining: int
    estimated_completion_date: datetime
