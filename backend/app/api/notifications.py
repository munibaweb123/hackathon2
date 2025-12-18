"""WebSocket endpoints for real-time notifications."""

import logging
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlmodel import Session

from ..core.auth import get_current_user, AuthenticatedUser
from ..core.database import get_session
from ..utils.reminder_scheduler import get_notification_manager

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/ws/notifications/{user_id}")
async def websocket_notifications(
    websocket: WebSocket,
    user_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    WebSocket endpoint for real-time notifications.

    Args:
        websocket: The WebSocket connection
        user_id: The user ID to subscribe to notifications for
        current_user: The authenticated user (for validation)
        session: Database session
    """
    # Verify that the user_id matches the authenticated user
    if current_user.id != user_id:
        await websocket.close(code=1008, reason="Unauthorized")
        return

    # Accept the WebSocket connection
    await websocket.accept()

    # Get the notification manager and connect this WebSocket
    notification_manager = get_notification_manager()

    try:
        # Add this connection to the manager
        notification_manager.connect(websocket, user_id)

        # Keep the connection alive until it's closed
        while True:
            # We don't expect to receive messages from the client in this implementation
            # Just keep the connection alive to receive notifications
            data = await websocket.receive_text()
            # Optionally, you could handle client messages here if needed
            # For now, we'll just continue the loop

    except WebSocketDisconnect:
        # Remove the connection when the client disconnects
        notification_manager.disconnect(websocket, user_id)
        logger.info(f"WebSocket disconnected for user {user_id}")
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {str(e)}")
        notification_manager.disconnect(websocket, user_id)
        await websocket.close()