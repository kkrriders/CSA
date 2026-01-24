"""
Session recording and interaction event models.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class InteractionEvent(BaseModel):
    """Individual interaction event."""
    session_id: str
    user_id: str
    event_type: str  # "mouse_move", "click", "keypress", "focus", "blur", "answer_change"
    question_id: Optional[str] = None

    # Event data
    x: Optional[int] = None  # Mouse position
    y: Optional[int] = None
    element: Optional[str] = None  # DOM element
    value: Optional[str] = None  # For input events

    timestamp: datetime = Field(default_factory=datetime.utcnow)
    time_since_start: int = 0  # Milliseconds since session start
