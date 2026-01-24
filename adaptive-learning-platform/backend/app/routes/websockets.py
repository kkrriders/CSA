"""
WebSocket routes for real-time features.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.websockets import manager
from app.core.database import get_database

router = APIRouter()


@router.websocket("/exam/{session_id}")
async def exam_monitor(websocket: WebSocket, session_id: str):
    """WebSocket for live exam monitoring."""
    await manager.connect(websocket, "exam", session_id)

    try:
        while True:
            # Receive updates from client
            data = await websocket.receive_json()

            # Broadcast to all monitors (teachers/coaches)
            await manager.broadcast(
                {
                    "session_id": session_id,
                    "type": "progress_update",
                    "data": data
                },
                "exam",
                session_id
            )
    except WebSocketDisconnect:
        manager.disconnect(websocket, "exam", session_id)


@router.websocket("/leaderboard/{document_id}")
async def live_leaderboard(websocket: WebSocket, document_id: str):
    """WebSocket for live leaderboard updates."""
    await manager.connect(websocket, "leaderboard", document_id)

    try:
        while True:
            data = await websocket.receive_json()

            # Broadcast score update
            await manager.broadcast(
                {
                    "document_id": document_id,
                    "type": "score_update",
                    "data": data
                },
                "leaderboard",
                document_id
            )
    except WebSocketDisconnect:
        manager.disconnect(websocket, "leaderboard", document_id)


@router.websocket("/study-room/{room_id}")
async def study_room(websocket: WebSocket, room_id: str):
    """WebSocket for collaborative study rooms."""
    await manager.connect(websocket, "study_room", room_id)

    try:
        while True:
            data = await websocket.receive_json()

            # Broadcast to all participants
            await manager.broadcast(
                {
                    "room_id": room_id,
                    "type": data.get("type", "message"),
                    "data": data
                },
                "study_room",
                room_id
            )
    except WebSocketDisconnect:
        manager.disconnect(websocket, "study_room", room_id)
