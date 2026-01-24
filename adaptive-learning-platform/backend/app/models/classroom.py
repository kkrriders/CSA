"""
Classroom and teacher dashboard models.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


class Classroom(BaseModel):
    """Classroom model for teacher management."""
    teacher_id: str
    name: str
    description: Optional[str] = None
    students: List[str] = []  # List of user IDs
    created_at: datetime = Field(default_factory=datetime.utcnow)
    active: bool = True


class Assignment(BaseModel):
    """Assignment model."""
    classroom_id: str
    teacher_id: str
    document_id: str
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    assigned_students: List[str] = []
    min_questions: int = 10
    difficulty_levels: List[str] = ["Easy", "Medium", "Hard"]
    created_at: datetime = Field(default_factory=datetime.utcnow)


class StudentAlert(BaseModel):
    """Alert for struggling students."""
    student_id: str
    classroom_id: str
    alert_type: str  # "low_score", "no_progress", "declining"
    severity: str  # "low", "medium", "high"
    message: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
