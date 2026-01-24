"""
Notification models for email and in-app notifications.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum


class NotificationType(str, Enum):
    """Types of notifications."""
    REVIEW_REMINDER = "review_reminder"
    WEEKLY_REPORT = "weekly_report"
    MILESTONE = "milestone"
    STREAK_REMINDER = "streak_reminder"
    EXAM_READY = "exam_ready"
    INTERVENTION = "intervention"  # For teachers


class NotificationFrequency(str, Enum):
    """Notification frequency options."""
    IMMEDIATE = "immediate"
    DAILY = "daily"
    WEEKLY = "weekly"
    NEVER = "never"


class NotificationPreference(BaseModel):
    """User notification preferences."""
    user_id: str

    # Email preferences
    review_reminders: NotificationFrequency = NotificationFrequency.DAILY
    weekly_reports: NotificationFrequency = NotificationFrequency.WEEKLY
    milestones: NotificationFrequency = NotificationFrequency.IMMEDIATE
    streak_reminders: NotificationFrequency = NotificationFrequency.DAILY
    exam_ready_alerts: NotificationFrequency = NotificationFrequency.IMMEDIATE

    # In-app notification preferences
    in_app_notifications: bool = True

    # Quiet hours
    quiet_hours_start: Optional[int] = None  # Hour (0-23)
    quiet_hours_end: Optional[int] = None  # Hour (0-23)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class NotificationHistory(BaseModel):
    """History of sent notifications."""
    user_id: str
    notification_type: NotificationType
    subject: str
    sent_at: datetime = Field(default_factory=datetime.utcnow)
    delivered: bool = False
    opened: bool = False
    error_message: Optional[str] = None


class EmailTemplate(BaseModel):
    """Email template data."""
    template_name: str
    subject: str
    data: dict
