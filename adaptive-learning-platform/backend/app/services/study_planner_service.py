"""
Study plan generation service.
"""
from datetime import datetime, timedelta
from typing import List, Dict
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.study_plan import StudyPlan, StudySessionPlan, SessionType, CreateStudyPlanRequest
from app.services.analytics_service_v2 import AnalyticsServiceV2
from app.services.advanced_analytics_service import AdvancedAnalyticsService


class StudyPlannerService:
    """Service for generating personalized study plans."""

    @staticmethod
    async def generate_plan(
        db: AsyncIOMotorDatabase,
        user_id: str,
        request: CreateStudyPlanRequest
    ) -> StudyPlan:
        """Generate a personalized study plan."""
        # Get document
        document = await db.documents.find_one({"_id": ObjectId(request.document_id)})
        if not document:
            raise ValueError("Document not found")

        # Get all topics from the document
        topics = []
        for section in document.get("sections", []):
            topics.extend(section.get("topics", []))
        topics = list(set(topics))  # Unique topics

        # Get user's current mastery for each topic
        user_sessions = await db.test_sessions.find({
            "user_id": user_id,
            "document_id": request.document_id,
            "status": "completed"
        }).to_list(length=1000)

        # Calculate topic priorities (low mastery = high priority)
        topic_priorities = {}
        analytics = AnalyticsServiceV2()

        for topic in topics:
            topic_answers = []
            for session in user_sessions:
                for answer in session.get("answers", []):
                    if answer.get("topic") == topic:
                        topic_answers.append(answer)

            if topic_answers:
                mastery = analytics._calculate_topic_mastery(topic, topic_answers)
                topic_priorities[topic] = 1 - mastery  # Inverse for priority
            else:
                topic_priorities[topic] = 1.0  # Never practiced = highest priority

        # Sort topics by priority
        sorted_topics = sorted(topic_priorities.items(), key=lambda x: x[1], reverse=True)

        # Calculate sessions needed
        total_topics = len(topics)
        sessions_per_topic = 3  # Practice, review, test
        total_sessions = total_topics * sessions_per_topic

        # Calculate timeline
        days_available = (request.target_date - datetime.utcnow()).days if request.target_date else 30
        sessions_per_week = request.sessions_per_week
        weeks_needed = total_sessions / sessions_per_week
        estimated_hours = (total_sessions * request.session_duration_minutes) / 60

        # Generate sessions
        sessions = []
        current_date = datetime.utcnow() + timedelta(days=1)  # Start tomorrow
        session_number = 1

        for topic, priority in sorted_topics:
            # Practice session
            sessions.append(StudySessionPlan(
                session_number=session_number,
                session_type=SessionType.PRACTICE,
                topic=topic,
                difficulty="Easy" if priority > 0.7 else "Medium",
                duration_minutes=request.session_duration_minutes,
                num_questions=15,
                scheduled_date=current_date
            ))
            session_number += 1
            current_date += timedelta(days=7 / sessions_per_week)

            # Review session (spaced)
            sessions.append(StudySessionPlan(
                session_number=session_number,
                session_type=SessionType.REVIEW,
                topic=topic,
                difficulty="Medium",
                duration_minutes=request.session_duration_minutes - 10,
                num_questions=10,
                scheduled_date=current_date
            ))
            session_number += 1
            current_date += timedelta(days=7 / sessions_per_week)

            # Test session
            sessions.append(StudySessionPlan(
                session_number=session_number,
                session_type=SessionType.TEST,
                topic=topic,
                difficulty="Mixed",
                duration_minutes=request.session_duration_minutes,
                num_questions=20,
                scheduled_date=current_date
            ))
            session_number += 1
            current_date += timedelta(days=7 / sessions_per_week)

        # Create plan
        plan = StudyPlan(
            user_id=user_id,
            document_id=request.document_id,
            title=request.title,
            description=f"Personalized study plan for {document.get('title', 'document')}",
            goal_type=request.goal_type,
            target_date=request.target_date,
            sessions=sessions,
            total_sessions=len(sessions),
            sessions_per_week=sessions_per_week,
            estimated_hours=estimated_hours,
            active=True
        )

        return plan

    @staticmethod
    async def get_next_session(
        db: AsyncIOMotorDatabase,
        plan_id: str
    ) -> Dict:
        """Get the next recommended session from a study plan."""
        plan_data = await db.study_plans.find_one({"_id": ObjectId(plan_id)})
        if not plan_data:
            return {"message": "Study plan not found"}

        # Find first incomplete session
        for session_data in plan_data.get("sessions", []):
            if not session_data.get("completed", False):
                return {
                    "next_session": session_data,
                    "message": "Ready to start your next session!"
                }

        return {
            "message": "All sessions completed!",
            "next_session": None
        }

    @staticmethod
    async def complete_session(
        db: AsyncIOMotorDatabase,
        plan_id: str,
        session_number: int
    ):
        """Mark a study session as completed."""
        # Update the specific session
        await db.study_plans.update_one(
            {
                "_id": ObjectId(plan_id),
                "sessions.session_number": session_number
            },
            {
                "$set": {
                    "sessions.$.completed": True,
                    "sessions.$.completed_at": datetime.utcnow()
                },
                "$inc": {"completed_sessions": 1},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )

    @staticmethod
    async def get_progress(
        db: AsyncIOMotorDatabase,
        plan_id: str
    ) -> Dict:
        """Get study plan progress."""
        plan_data = await db.study_plans.find_one({"_id": ObjectId(plan_id)})
        if not plan_data:
            return {"message": "Study plan not found"}

        completed = plan_data.get("completed_sessions", 0)
        total = plan_data.get("total_sessions", 1)
        progress = (completed / total) * 100

        # Check if on schedule
        planned_by_now = 0
        for session in plan_data.get("sessions", []):
            if session["scheduled_date"] <= datetime.utcnow():
                planned_by_now += 1

        on_schedule = completed >= planned_by_now

        # Estimate completion
        sessions_remaining = total - completed
        sessions_per_week = plan_data.get("sessions_per_week", 3)
        weeks_remaining = sessions_remaining / sessions_per_week
        estimated_completion = datetime.utcnow() + timedelta(weeks=weeks_remaining)

        return {
            "plan_id": plan_id,
            "total_sessions": total,
            "completed_sessions": completed,
            "progress_percentage": round(progress, 1),
            "on_schedule": on_schedule,
            "planned_by_now": planned_by_now,
            "days_remaining": (plan_data.get("target_date") - datetime.utcnow()).days if plan_data.get("target_date") else None,
            "estimated_completion_date": estimated_completion
        }
