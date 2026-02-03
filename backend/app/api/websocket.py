"""
WebSocket API endpoints for real-time task synchronization.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, HTTPException, status, Depends
from typing import List, Dict, Optional
import json
import logging
from ..auth import decode_jwt_token, get_current_user
from ..models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["websocket"])

# Store connected WebSocket clients
connected_clients: Dict[str, List[WebSocket]] = {}


class ConnectionManager:
    """Manages WebSocket connections for the main API."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_websockets: Dict[str, List[WebSocket]] = {}  # user_id -> [websocket connections]

    async def connect(self, websocket: WebSocket, user_id: str):
        """Connect a new WebSocket and register it with the user."""
        await websocket.accept()
        self.active_connections.append(websocket)

        if user_id not in self.user_websockets:
            self.user_websockets[user_id] = []
        self.user_websockets[user_id].append(websocket)

        logger.info(f"WebSocket connected for user {user_id}. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket, user_id: str):
        """Disconnect a WebSocket and unregister it from the user."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

        if user_id in self.user_websockets:
            if websocket in self.user_websockets[user_id]:
                self.user_websockets[user_id].remove(websocket)

            # Clean up user entry if no more connections
            if not self.user_websockets[user_id]:
                del self.user_websockets[user_id]

        logger.info(f"WebSocket disconnected for user {user_id}. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific WebSocket."""
        await websocket.send_text(message)

    async def broadcast_to_user(self, message: str, user_id: str):
        """Broadcast a message to all WebSocket connections for a specific user."""
        if user_id in self.user_websockets:
            websockets = self.user_websockets[user_id].copy()  # Copy to avoid modification during iteration
            for websocket in websockets:
                try:
                    await websocket.send_text(message)
                except WebSocketDisconnect:
                    # Remove disconnected websockets
                    await self.disconnect(websocket, user_id)
                except Exception as e:
                    logger.error(f"Error sending message to user {user_id}: {e}")
                    try:
                        await self.disconnect(websocket, user_id)
                    except:
                        pass  # Already handled


manager = ConnectionManager()


@router.websocket("/tasks/{user_id}")
async def websocket_task_sync(websocket: WebSocket, user_id: str, token: str = Query(..., alias="token")):
    """
    WebSocket endpoint for real-time task synchronization.
    Only allows connections from the authenticated user.
    Token is passed as a query parameter.
    """
    # Authenticate the user using the token from query parameter
    try:
        payload = decode_jwt_token(token)
        token_user_id = payload.get("sub")
        if not token_user_id:
            await websocket.close(code=1008, reason="Invalid token: missing user ID")
            return
    except Exception as e:
        logger.error(f"Failed to decode JWT token: {e}")
        await websocket.close(code=1008, reason="Invalid token")
        return

    # Verify that the user_id in the path matches the authenticated user
    if token_user_id != user_id:
        await websocket.close(code=1008, reason="Unauthorized")
        return

    await manager.connect(websocket, user_id)

    try:
        while True:
            # Listen for messages from client (for future use, like acknowledgments)
            data = await websocket.receive_text()
            logger.info(f"Received message from user {user_id}: {data}")

            # Optionally handle client messages here
            # For now, we mainly push data to clients from task updates
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)


@router.get("/status")
async def websocket_status(current_user: User = Depends(get_current_user)):
    """Get WebSocket connection status for the authenticated user."""
    user_connections = len(manager.user_websockets.get(current_user.id, []))
    total_connections = len(manager.active_connections)

    return {
        "user_connections": user_connections,
        "total_connections": total_connections,
        "user_id": current_user.id
    }