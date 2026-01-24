from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import get_settings
import certifi

settings = get_settings()


class Database:
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None


db = Database()


async def connect_to_mongo():
    """Connect to MongoDB"""
    # Configure MongoDB client with SSL/TLS settings for Atlas
    db.client = AsyncIOMotorClient(
        settings.MONGODB_URI,
        tls=True,
        tlsAllowInvalidCertificates=True,  # Bypass certificate verification
        serverSelectionTimeoutMS=30000,
        connectTimeoutMS=30000,
        socketTimeoutMS=30000
    )
    db.db = db.client[settings.MONGODB_DB_NAME]
    print(f"✅ Connected to MongoDB: {settings.MONGODB_DB_NAME}")


async def close_mongo_connection():
    """Close MongoDB connection"""
    db.client.close()
    print("❌ Closed MongoDB connection")


def get_database() -> Optional[AsyncIOMotorDatabase]:
    """Get database instance"""
    return db.db
