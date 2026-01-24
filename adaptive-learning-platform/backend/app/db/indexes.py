"""
Database index definitions for MongoDB.
"""
from motor.motor_asyncio import AsyncIOMotorDatabase


async def create_indexes(db: AsyncIOMotorDatabase):
    """Create all database indexes for optimal query performance."""

    # Users collection
    await db.users.create_index("username", unique=True)
    await db.users.create_index("email", unique=True)

    # Documents collection
    await db.documents.create_index("user_id")
    await db.documents.create_index([("user_id", 1), ("created_at", -1)])

    # Questions collection
    await db.questions.create_index("document_id")
    await db.questions.create_index([("document_id", 1), ("topic", 1)])
    await db.questions.create_index([("document_id", 1), ("difficulty", 1)])
    await db.questions.create_index([("topic", 1), ("difficulty", 1)])

    # Test sessions collection
    await db.test_sessions.create_index([("user_id", 1), ("created_at", -1)])
    await db.test_sessions.create_index([("user_id", 1), ("document_id", 1)])
    await db.test_sessions.create_index([("document_id", 1), ("status", 1)])
    await db.test_sessions.create_index([("user_id", 1), ("status", 1)])
    await db.test_sessions.create_index([("user_id", 1), ("completed_at", -1)])

    # Reviews collection
    await db.reviews.create_index([("user_id", 1), ("next_review_date", 1)])
    await db.reviews.create_index([("user_id", 1), ("document_id", 1)])
    await db.reviews.create_index([("user_id", 1), ("topic", 1)])
    await db.reviews.create_index("question_id")

    # Question statistics collection
    await db.question_statistics.create_index("question_id", unique=True)
    await db.question_statistics.create_index([("question_id", 1), ("total_attempts", -1)])

    # Study plans collection
    await db.study_plans.create_index([("user_id", 1), ("active", 1)])
    await db.study_plans.create_index([("user_id", 1), ("document_id", 1)])

    # Notification history
    await db.notification_history.create_index([("user_id", 1), ("sent_at", -1)])

    # API keys
    await db.api_keys.create_index("key_hash")
    await db.api_keys.create_index([("user_id", 1), ("revoked", 1)])

    print("✓ Database indexes created successfully")
