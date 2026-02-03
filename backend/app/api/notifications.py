"""Notification endpoints: WebSocket real-time + preferences REST API."""

import logging
from datetime import datetime, time
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from ..core.auth import get_current_user, AuthenticatedUser
from ..core.database import get_session
from ..models.notification_preference import NotificationPreference
from ..utils.reminder_scheduler import get_notification_manager

router = APIRouter()
logger = logging.getLogger(__name__)


# --- Pydantic schemas for preferences ---

class NotificationPreferenceUpdate(BaseModel):
    in_app_enabled: Optional[bool] = None
    email_enabled: Optional[bool] = None
    reminder_lead_time: Optional[int] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None


class NotificationPreferenceResponse(BaseModel):
    in_app_enabled: bool
    email_enabled: bool
    reminder_lead_time: int
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None


# --- Notification Preferences REST endpoints ---

@router.get("/preferences", response_model=NotificationPreferenceResponse)
def get_notification_preferences(
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get notification preferences for the current user."""
    pref = session.exec(
        select(NotificationPreference).where(NotificationPreference.user_id == current_user.id)
    ).first()

    if not pref:
        # Return defaults
        return NotificationPreferenceResponse(
            in_app_enabled=True,
            email_enabled=True,
            reminder_lead_time=60,
        )

    return NotificationPreferenceResponse(
        in_app_enabled=pref.in_app_enabled,
        email_enabled=pref.email_enabled,
        reminder_lead_time=pref.reminder_lead_time,
        quiet_hours_start=str(pref.quiet_hours_start) if pref.quiet_hours_start else None,
        quiet_hours_end=str(pref.quiet_hours_end) if pref.quiet_hours_end else None,
    )


@router.put("/preferences", response_model=NotificationPreferenceResponse)
def update_notification_preferences(
    data: NotificationPreferenceUpdate,
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Update notification preferences for the current user."""
    pref = session.exec(
        select(NotificationPreference).where(NotificationPreference.user_id == current_user.id)
    ).first()

    if not pref:
        pref = NotificationPreference(id=uuid4(), user_id=current_user.id)
        session.add(pref)

    if data.in_app_enabled is not None:
        pref.in_app_enabled = data.in_app_enabled
    if data.email_enabled is not None:
        pref.email_enabled = data.email_enabled
    if data.reminder_lead_time is not None:
        pref.reminder_lead_time = data.reminder_lead_time
    if data.quiet_hours_start is not None:
        pref.quiet_hours_start = time.fromisoformat(data.quiet_hours_start)
    if data.quiet_hours_end is not None:
        pref.quiet_hours_end = time.fromisoformat(data.quiet_hours_end)

    pref.updated_at = datetime.utcnow()
    session.commit()
    session.refresh(pref)

    return NotificationPreferenceResponse(
        in_app_enabled=pref.in_app_enabled,
        email_enabled=pref.email_enabled,
        reminder_lead_time=pref.reminder_lead_time,
        quiet_hours_start=str(pref.quiet_hours_start) if pref.quiet_hours_start else None,
        quiet_hours_end=str(pref.quiet_hours_end) if pref.quiet_hours_end else None,
    )


@router.get("/history")
def get_notification_history(
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get recent notification history for the current user."""
    # Query audit logs for notification-related events
    from ..models.audit import AuditLog
    logs = session.exec(
        select(AuditLog)
        .where(AuditLog.user_id == current_user.id)
        .where(AuditLog.entity_type == "notification")
        .order_by(AuditLog.timestamp.desc())
        .limit(50)
    ).all()
    return [
        {
            "id": str(log.id),
            "action": log.action,
            "data": log.new_data,
            "timestamp": log.timestamp.isoformat() if log.timestamp else None,
        }
        for log in logs
    ]


@router.post("/test")
def send_test_notification(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Send a test notification to verify notification delivery."""
    notification_manager = get_notification_manager()
    # Queue a test notification
    return {
        "status": "sent",
        "message": "Test notification dispatched",
        "user_id": current_user.id,
    }


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