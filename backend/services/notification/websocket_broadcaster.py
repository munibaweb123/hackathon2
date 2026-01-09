"""WebSocket broadcaster for in-app notifications.

Manages WebSocket connections and broadcasts notifications to connected clients.
"""

import os
import logging
import json
from typing import Dict, Any, Set, Optional
from datetime import datetime
import asyncio

try:
    from websockets.server import serve, WebSocketServerProtocol
    from websockets.exceptions import ConnectionClosed
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    WebSocketServerProtocol = Any

logger = logging.getLogger(__name__)

# Configuration
WEBSOCKET_HOST = os.getenv("WEBSOCKET_HOST", "0.0.0.0")
WEBSOCKET_PORT = int(os.getenv("WEBSOCKET_PORT", "8002"))


class WebSocketBroadcaster:
    """
    Manages WebSocket connections and broadcasts notifications.

    Each user can have multiple connections (multiple browser tabs/devices).
    Messages are broadcast to all connections for a given user.
    """

    def __init__(self):
        # Map user_id -> set of WebSocket connections
        self._connections: Dict[str, Set[WebSocketServerProtocol]] = {}
        self._lock = asyncio.Lock()
        self._server = None
        self._is_running = False

    def is_ready(self) -> bool:
        """Check if the broadcaster is ready to accept connections."""
        return WEBSOCKETS_AVAILABLE

    async def start_server(self):
        """Start the WebSocket server."""
        if not WEBSOCKETS_AVAILABLE:
            logger.warning("websockets library not available, skipping server start")
            return

        if self._is_running:
            return

        self._server = await serve(
            self._handle_connection,
            WEBSOCKET_HOST,
            WEBSOCKET_PORT,
        )
        self._is_running = True
        logger.info(f"WebSocket server started on {WEBSOCKET_HOST}:{WEBSOCKET_PORT}")

    async def stop_server(self):
        """Stop the WebSocket server."""
        if self._server:
            self._server.close()
            await self._server.wait_closed()
            self._is_running = False
            logger.info("WebSocket server stopped")

    async def _handle_connection(
        self,
        websocket: WebSocketServerProtocol,
        path: str
    ):
        """
        Handle a new WebSocket connection.

        Expected path format: /ws/{user_id}
        """
        # Extract user_id from path
        parts = path.strip("/").split("/")
        if len(parts) < 2 or parts[0] != "ws":
            await websocket.close(4001, "Invalid path format. Expected: /ws/{user_id}")
            return

        user_id = parts[1]

        # Register the connection
        await self._register_connection(user_id, websocket)

        try:
            # Send connection confirmation
            await websocket.send(json.dumps({
                "type": "connected",
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
            }))

            # Keep connection alive and handle incoming messages
            async for message in websocket:
                try:
                    data = json.loads(message)

                    # Handle ping/pong for keep-alive
                    if data.get("type") == "ping":
                        await websocket.send(json.dumps({
                            "type": "pong",
                            "timestamp": datetime.utcnow().isoformat(),
                        }))

                    # Handle subscription updates
                    elif data.get("type") == "subscribe":
                        # Client can subscribe to specific event types
                        # For now, we just acknowledge
                        await websocket.send(json.dumps({
                            "type": "subscribed",
                            "events": data.get("events", ["all"]),
                        }))

                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON from user {user_id}")

        except ConnectionClosed as e:
            logger.info(f"Connection closed for user {user_id}: {e.code}")
        except Exception as e:
            logger.exception(f"Error handling connection for user {user_id}: {e}")
        finally:
            # Unregister the connection
            await self._unregister_connection(user_id, websocket)

    async def _register_connection(
        self,
        user_id: str,
        websocket: WebSocketServerProtocol
    ):
        """Register a new WebSocket connection for a user."""
        async with self._lock:
            if user_id not in self._connections:
                self._connections[user_id] = set()
            self._connections[user_id].add(websocket)
            logger.info(
                f"Registered connection for user {user_id}. "
                f"Total connections: {len(self._connections[user_id])}"
            )

    async def _unregister_connection(
        self,
        user_id: str,
        websocket: WebSocketServerProtocol
    ):
        """Unregister a WebSocket connection for a user."""
        async with self._lock:
            if user_id in self._connections:
                self._connections[user_id].discard(websocket)
                if not self._connections[user_id]:
                    del self._connections[user_id]
                logger.info(f"Unregistered connection for user {user_id}")

    async def broadcast_to_user(
        self,
        user_id: str,
        message: Dict[str, Any]
    ) -> int:
        """
        Broadcast a message to all connections for a specific user.

        Args:
            user_id: The user to send the message to
            message: The message payload

        Returns:
            Number of connections the message was sent to
        """
        async with self._lock:
            connections = self._connections.get(user_id, set()).copy()

        if not connections:
            logger.debug(f"No active connections for user {user_id}")
            return 0

        # Prepare the message
        message_json = json.dumps({
            **message,
            "sent_at": datetime.utcnow().isoformat(),
        })

        # Send to all connections
        sent_count = 0
        failed_connections = []

        for websocket in connections:
            try:
                await websocket.send(message_json)
                sent_count += 1
            except ConnectionClosed:
                failed_connections.append(websocket)
            except Exception as e:
                logger.error(f"Error sending to user {user_id}: {e}")
                failed_connections.append(websocket)

        # Clean up failed connections
        if failed_connections:
            async with self._lock:
                for ws in failed_connections:
                    if user_id in self._connections:
                        self._connections[user_id].discard(ws)

        logger.info(f"Broadcast to {sent_count}/{len(connections)} connections for user {user_id}")
        return sent_count

    async def broadcast_to_all(self, message: Dict[str, Any]) -> int:
        """
        Broadcast a message to all connected users.

        Args:
            message: The message payload

        Returns:
            Total number of connections the message was sent to
        """
        total_sent = 0

        async with self._lock:
            user_ids = list(self._connections.keys())

        for user_id in user_ids:
            sent = await self.broadcast_to_user(user_id, message)
            total_sent += sent

        return total_sent

    def get_connected_users(self) -> int:
        """Get the number of unique connected users."""
        return len(self._connections)

    def get_total_connections(self) -> int:
        """Get the total number of active connections."""
        return sum(len(conns) for conns in self._connections.values())


# Singleton instance
_broadcaster: Optional[WebSocketBroadcaster] = None


def get_websocket_broadcaster() -> WebSocketBroadcaster:
    """Get the singleton WebSocket broadcaster instance."""
    global _broadcaster
    if _broadcaster is None:
        _broadcaster = WebSocketBroadcaster()
    return _broadcaster
