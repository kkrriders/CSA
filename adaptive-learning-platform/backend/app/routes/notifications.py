"""
Notification preference and history routes.
"""
from fastapi import APIRouter, HTTPException, status, Depends
from bson import ObjectId

from app.core.database import get_database
from app.core.security import get_current_user_id
from app.models.notification import NotificationPreference, NotificationFrequency
from app.services.email_service import EmailService

router = APIRouter()


@router.get("/preferences")
async def get_notification_preferences(
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Get user's notification preferences."""
    prefs = await db.notification_preferences.find_one({"user_id": user_id})

    if not prefs:
        # Return defaults
        return NotificationPreference(user_id=user_id).dict()

    return prefs


@router.put("/preferences")
async def update_notification_preferences(
    preferences: NotificationPreference,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Update user's notification preferences."""
    preferences.user_id = user_id

    await db.notification_preferences.update_one(
        {"user_id": user_id},
        {"$set": preferences.dict()},
        upsert=True
    )

    return {
        "message": "Notification preferences updated successfully",
        "preferences": preferences
    }


@router.post("/test")
async def send_test_email(
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Send a test email to verify email configuration."""
    user = await db.users.find_one({"_id": ObjectId(user_id)})

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    email_service = EmailService()
    sent = await email_service.send_email(
        recipients=[user["email"]],
        subject="Test Email from Adaptive Learning Platform",
        body="<h1>Test Email</h1><p>If you received this, your email notifications are working!</p>",
        html=True
    )

    if sent:
        return {"message": "Test email sent successfully", "email": user["email"]}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send test email"
        )


@router.get("/history")
async def get_notification_history(
    limit: int = 50,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Get user's notification history."""
    cursor = db.notification_history.find(
        {"user_id": user_id}
    ).sort("sent_at", -1).limit(limit)

    history = await cursor.to_list(length=limit)

    return {
        "history": history,
        "total": len(history)
    }
