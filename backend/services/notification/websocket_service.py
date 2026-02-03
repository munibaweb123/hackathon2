"""
WebSocket service for real-time task synchronization.
Handles incoming task-update events from Dapr and broadcasts to connected WebSocket clients.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import uvicorn

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="WebSocket Service for Real-time Sync")

# Store connected WebSocket clients
connected_clients: Dict[str, List[WebSocket]] = {}


class TaskUpdateEvent(BaseModel):
    """Schema for task update events from Dapr pub/sub."""
    event_id: str
    event_type: str
    task_id: int
    user_id: str
    changes: Dict
    full_task: Optional[Dict] = None
    timestamp: str


class ConnectionManager:
    """Manages WebSocket connections and broadcasting."""

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


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time task synchronization."""
    await manager.connect(websocket, user_id)

    try:
        while True:
            # Listen for messages from client (though in this case, we mainly push data)
            data = await websocket.receive_text()
            logger.info(f"Received message from user {user_id}: {data}")
            # Optionally handle client messages here
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)


@app.post("/dapr/subscribe")
async def dapr_subscribe():
    """
    Dapr subscription endpoint to register which topics this service wants to listen to.
    This tells Dapr that this service wants to receive messages from the task-updates topic.
    """
    subscriptions = [
        {
            "pubsubname": "kafka-pubsub",  # This should match the Dapr pubsub component name
            "topic": "task-updates",
            "route": "/events/task-updates"
        }
    ]
    return subscriptions


@app.post("/events/task-updates")
async def handle_task_updates(event: dict):
    """
    Handle incoming task update events from Dapr pub/sub.
    This endpoint receives events from the 'task-updates' topic and broadcasts them to connected clients.
    """
    try:
        # Parse the incoming event
        task_event = TaskUpdateEvent(**event)

        logger.info(f"Received task update event for user {task_event.user_id}, task {task_event.task_id}")

        # Prepare message to broadcast
        message_data = {
            "event_type": task_event.event_type,
            "task_id": task_event.task_id,
            "user_id": task_event.user_id,
            "changes": task_event.changes,
            "full_task": task_event.full_task,
            "timestamp": task_event.timestamp
        }

        message_json = json.dumps(message_data)

        # Broadcast to all connected WebSocket clients for this user
        await manager.broadcast_to_user(message_json, task_event.user_id)

        logger.info(f"Broadcasted task update to user {task_event.user_id}")

        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error handling task update event: {e}")
        return {"status": "error", "message": str(e)}


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "websocket service running", "connections": len(manager.active_connections)}


if __name__ == "__main__":
    # This service typically runs behind Dapr, so it's usually called with:
    # dapr run --app-id websocket-service --app-port 8001 --dapr-http-port 3501 -- python websocket_service.py
    uvicorn.run(app, host="0.0.0.0", port=8001)