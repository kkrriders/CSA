"""
Review scheduling models for spaced repetition.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class Review(BaseModel):
    """Individual review item."""
    question_id: str
    user_id: str
    document_id: str
    topic: str
    difficulty: str

    # Spaced repetition state (SM-2 algorithm)
    interval: int = 1  # Days until next review
    repetitions: int = 0  # Number of successful reviews
    ease_factor: float = 2.5  # Ease factor (quality of recall)

    # Schedule
    next_review_date: datetime
    last_reviewed_at: Optional[datetime] = None

    # Performance tracking
    total_reviews: int = 0
    successful_reviews: int = 0
    average_quality: float = 0.0

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ReviewResponse(BaseModel):
    """User response to a review question."""
    quality: int  # 0-5 rating (SM-2)
    time_spent: int  # seconds
    correct: bool


class ReviewSession(BaseModel):
    """A review session containing multiple reviews."""
    user_id: str
    document_id: Optional[str] = None
    review_ids: list[str]

    # Session state
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    # Results
    total_reviews: int = 0
    completed_reviews: int = 0
    average_quality: float = 0.0


class ReviewQueueItem(BaseModel):
    """Item in the review queue."""
    review_id: str
    question_id: str
    topic: str
    difficulty: str
    next_review_date: datetime
    days_overdue: int
    priority: float


class ReviewSchedule(BaseModel):
    """Review schedule for a topic or document."""
    user_id: str
    document_id: Optional[str] = None
    topic: Optional[str] = None

    # Schedule stats
    due_today: int = 0
    due_this_week: int = 0
    due_this_month: int = 0
    total_reviews: int = 0

    # Next review
    next_review_date: Optional[datetime] = None
    next_review_topic: Optional[str] = None
