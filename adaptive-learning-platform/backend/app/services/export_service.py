

from datetime import datetime
from typing import Dict
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
import json


class ExportService:
    """Service for exporting user data."""

    @staticmethod
    async def export_all_user_data(
        db: AsyncIOMotorDatabase,
        user_id: str
    ) -> Dict:
        """Export all data for a user (GDPR compliance)."""
        user_id_obj = ObjectId(user_id)

        # Get user profile
        user = await db.users.find_one({"_id": user_id_obj})
        if user:
            user["_id"] = str(user["_id"])
            user.pop("hashed_password", None)  # Don't export password hash

        # Get documents
        documents = await db.documents.find({"user_id": user_id}).to_list(length=1000)
        for doc in documents:
            doc["_id"] = str(doc["_id"])

        # Get test sessions
        sessions = await db.test_sessions.find({"user_id": user_id}).to_list(length=10000)
        for session in sessions:
            session["_id"] = str(session["_id"])
            session["user_id"] = str(session.get("user_id"))

        # Get reviews
        reviews = await db.reviews.find({"user_id": user_id}).to_list(length=10000)
        for review in reviews:
            review["_id"] = str(review["_id"])

        # Get study plans
        plans = await db.study_plans.find({"user_id": user_id}).to_list(length=100)
        for plan in plans:
            plan["_id"] = str(plan["_id"])

        # Get notification preferences
        notif_prefs = await db.notification_preferences.find_one({"user_id": user_id})
        if notif_prefs:
            notif_prefs["_id"] = str(notif_prefs["_id"])

        # Get notification history
        notif_history = await db.notification_history.find({"user_id": user_id}).to_list(length=1000)
        for notif in notif_history:
            notif["_id"] = str(notif["_id"])

        # Compile export
        export_data = {
            "export_date": datetime.utcnow().isoformat(),
            "user_profile": user,
            "documents": documents,
            "test_sessions": sessions,
            "reviews": reviews,
            "study_plans": plans,
            "notification_preferences": notif_prefs,
            "notification_history": notif_history,
            "statistics": {
                "total_documents": len(documents),
                "total_sessions": len(sessions),
                "total_reviews": len(reviews),
                "total_plans": len(plans)
            }
        }

        return export_data

    @staticmethod
    async def delete_all_user_data(
        db: AsyncIOMotorDatabase,
        user_id: str
    ) -> int:
        """Delete all data for a user (GDPR right to be forgotten)."""
        user_id_obj = ObjectId(user_id)

        collections_to_delete = [
            ("documents", {"user_id": user_id}),
            ("test_sessions", {"user_id": user_id}),
            ("reviews", {"user_id": user_id}),
            ("study_plans", {"user_id": user_id}),
            ("notification_preferences", {"user_id": user_id}),
            ("notification_history", {"user_id": user_id}),
            ("two_factor_auth", {"user_id": user_id}),
            ("api_keys", {"user_id": user_id}),
            ("review_sessions", {"user_id": user_id}),
            ("users", {"_id": user_id_obj})
        ]

        total_deleted = 0

        for collection_name, query in collections_to_delete:
            result = await db[collection_name].delete_many(query)
            total_deleted += result.deleted_count

        return total_deleted

    @staticmethod
    async def log_export(
        db: AsyncIOMotorDatabase,
        user_id: str,
        export_type: str
    ):
        """Log a data export action."""
        await db.data_exports.insert_one({
            "user_id": user_id,
            "export_type": export_type,
            "exported_at": datetime.utcnow()
        })
