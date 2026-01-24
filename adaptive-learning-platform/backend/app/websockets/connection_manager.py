"""
WebSocket connection manager.
"""
from typing import Dict, List
from fastapi import WebSocket


class ConnectionManager:
    """Manage WebSocket connections."""

    def __init__(self):
        # Store connections by type and ID
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, connection_type: str, connection_id: str):
        """Accept and store a WebSocket connection."""
        await websocket.accept()
        key = f"{connection_type}:{connection_id}"

        if key not in self.active_connections:
            self.active_connections[key] = []

        self.active_connections[key].append(websocket)

    def disconnect(self, websocket: WebSocket, connection_type: str, connection_id: str):
        """Remove a WebSocket connection."""
        key = f"{connection_type}:{connection_id}"

        if key in self.active_connections:
            if websocket in self.active_connections[key]:
                self.active_connections[key].remove(websocket)

            if len(self.active_connections[key]) == 0:
                del self.active_connections[key]

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific websocket."""
        await websocket.send_json(message)

    async def broadcast(self, message: dict, connection_type: str, connection_id: str):
        """Broadcast a message to all connections of a specific type/ID."""
        key = f"{connection_type}:{connection_id}"

        if key in self.active_connections:
            for connection in self.active_connections[key]:
                try:
                    await connection.send_json(message)
                except:
                    # Remove dead connections
                    self.disconnect(connection, connection_type, connection_id)


# Global connection manager
manager = ConnectionManager()
