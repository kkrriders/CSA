"""
Background service for scheduling and sending notifications.
"""
from datetime import datetime, timedelta
from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.notification import NotificationFrequency, NotificationHistory, NotificationType
from app.services.email_service import EmailService
from app.services.spaced_repetition_service import SpacedRepetitionService


class NotificationScheduler:
    """Background scheduler for automated notifications."""

    def __init__(self):
        self.email_service = EmailService()

    async def send_daily_review_reminders(self, db: AsyncIOMotorDatabase):
        """Send daily review reminders to users with due reviews."""
        # Get all users with daily review reminder preference
        cursor = db.notification_preferences.find({
            "review_reminders": NotificationFrequency.DAILY
        })

        preferences = await cursor.to_list(length=10000)

        for pref in preferences:
            user_id = pref["user_id"]

            # Get due reviews
            due_reviews = await SpacedRepetitionService.get_due_reviews(
                db=db,
                user_id=user_id,
                limit=100
            )

            if len(due_reviews) > 0:
                # Get user info
                user = await db.users.find_one({"_id": user_id})
                if not user:
                    continue

                # Get unique topics
                topics = list(set([review.topic for review in due_reviews]))

                # Send email
                sent = await self.email_service.send_review_reminder(
                    recipient=user["email"],
                    user_name=user.get("full_name", user["username"]),
                    due_reviews=len(due_reviews),
                    topics=topics[:5]  # Top 5 topics
                )

                # Log notification
                if sent:
                    await db.notification_history.insert_one(
                        NotificationHistory(
                            user_id=user_id,
                            notification_type=NotificationType.REVIEW_REMINDER,
                            subject=f"You have {len(due_reviews)} reviews due today!",
                            delivered=True
                        ).dict()
                    )

    async def send_weekly_reports(self, db: AsyncIOMotorDatabase):
        """Send weekly progress reports."""
        # Get all users with weekly report preference
        cursor = db.notification_preferences.find({
            "weekly_reports": NotificationFrequency.WEEKLY
        })

        preferences = await cursor.to_list(length=10000)

        for pref in preferences:
            user_id = pref["user_id"]

            # Get user sessions from the past week
            week_ago = datetime.utcnow() - timedelta(days=7)
            sessions = await db.test_sessions.find({
                "user_id": user_id,
                "completed_at": {"$gte": week_ago}
            }).to_list(length=1000)

            if len(sessions) > 0:
                # Calculate weekly stats
                total_questions = sum(len(s.get("answers", [])) for s in sessions)
                total_correct = sum(
                    sum(1 for a in s.get("answers", []) if a.get("correct", False))
                    for s in sessions
                )
                avg_score = (total_correct / total_questions * 100) if total_questions > 0 else 0

                # Get user info
                user = await db.users.find_one({"_id": user_id})
                if not user:
                    continue

                # Prepare report data
                report_data = {
                    "sessions_completed": len(sessions),
                    "total_questions": total_questions,
                    "total_correct": total_correct,
                    "average_score": round(avg_score, 1),
                    "week_start": week_ago.strftime("%B %d"),
                    "week_end": datetime.utcnow().strftime("%B %d, %Y")
                }

                # Send email
                sent = await self.email_service.send_weekly_report(
                    recipient=user["email"],
                    user_name=user.get("full_name", user["username"]),
                    report_data=report_data
                )

                # Log notification
                if sent:
                    await db.notification_history.insert_one(
                        NotificationHistory(
                            user_id=user_id,
                            notification_type=NotificationType.WEEKLY_REPORT,
                            subject="Your Weekly Learning Progress Report",
                            delivered=True
                        ).dict()
                    )

    async def check_milestones(self, db: AsyncIOMotorDatabase, user_id: str, session_id: str):
        """Check and notify for milestones after a session."""
        # Get user preference
        pref = await db.notification_preferences.find_one({"user_id": user_id})
        if not pref or pref.get("milestones") == NotificationFrequency.NEVER:
            return

        # Get user and session
        user = await db.users.find_one({"_id": user_id})
        session = await db.test_sessions.find_one({"_id": session_id})

        if not user or not session:
            return

        # Check various milestones
        milestone = None
        achievement = None

        # Perfect score
        if session.get("score", 0) == 100:
            milestone = "Perfect Score!"
            achievement = "You got 100% on this test!"

        # Get user's total sessions
        total_sessions = await db.test_sessions.count_documents({"user_id": user_id})

        # Session count milestones
        if total_sessions in [10, 50, 100, 500]:
            milestone = f"{total_sessions} Tests Completed!"
            achievement = f"You've completed {total_sessions} tests. Keep learning!"

        # Send milestone email if detected
        if milestone:
            sent = await self.email_service.send_milestone_email(
                recipient=user["email"],
                user_name=user.get("full_name", user["username"]),
                milestone=milestone,
                achievement=achievement
            )

            if sent:
                await db.notification_history.insert_one(
                    NotificationHistory(
                        user_id=user_id,
                        notification_type=NotificationType.MILESTONE,
                        subject=f"Congratulations! {milestone}",
                        delivered=True
                    ).dict()
                )
