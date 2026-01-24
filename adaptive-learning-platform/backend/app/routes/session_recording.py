"""
Session recording routes for interaction tracking.
"""
from fastapi import APIRouter, Depends
from bson import ObjectId
from typing import List

from app.core.database import get_database
from app.core.security import get_current_user_id
from app.models.interaction import InteractionEvent

router = APIRouter()


@router.post("/{session_id}/events")
async def log_interaction_event(
    session_id: str,
    event: InteractionEvent,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Log an interaction event."""
    event.session_id = session_id
    event.user_id = user_id

    await db.interaction_events.insert_one(event.dict())

    return {"message": "Event logged"}


@router.get("/{session_id}/replay")
async def get_session_replay_data(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Get all interaction events for session replay."""
    # Verify session ownership
    session = await db.test_sessions.find_one({
        "_id": ObjectId(session_id),
        "user_id": user_id
    })

    if not session:
        return {"message": "Session not found"}

    # Get all events
    cursor = db.interaction_events.find({
        "session_id": session_id
    }).sort("timestamp", 1)

    events = await cursor.to_list(length=100000)

    return {
        "session_id": session_id,
        "events": events,
        "total_events": len(events)
    }


@router.get("/{session_id}/timeline")
async def get_answer_change_timeline(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Get timeline of answer changes."""
    cursor = db.interaction_events.find({
        "session_id": session_id,
        "event_type": "answer_change"
    }).sort("timestamp", 1)

    events = await cursor.to_list(length=10000)

    return {
        "session_id": session_id,
        "timeline": events,
        "total_changes": len(events)
    }
