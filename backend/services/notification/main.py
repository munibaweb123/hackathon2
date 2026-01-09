"""Notification microservice main entry point.

This service handles:
- Receiving reminder events from Dapr Pub/Sub
- Sending in-app notifications via WebSocket
- Sending email notifications via Resend/SendGrid

Dapr subscription handler for 'reminders' topic.
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel, Field
from uuid import UUID

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app for Dapr subscriptions
app = FastAPI(
    title="Notification Service",
    description="Handles reminder notifications via WebSocket and email",
    version="1.0.0",
)

# Environment configuration
PUBSUB_NAME = os.getenv("PUBSUB_NAME", "kafka-pubsub")
TOPIC_REMINDERS = "reminders"


class NotificationPreferences(BaseModel):
    """User notification channel preferences."""
    in_app: bool = True
    email: bool = True
    user_email: Optional[str] = None


class ReminderEvent(BaseModel):
    """Schema for incoming reminder events from Dapr Pub/Sub."""
    event_id: UUID
    task_id: int
    user_id: str
    title: str
    description: Optional[str] = None
    due_at: datetime
    remind_at: datetime
    notification_preferences: NotificationPreferences
    timestamp: datetime
    correlation_id: Optional[UUID] = None
    published_at: Optional[str] = None


class CloudEvent(BaseModel):
    """CloudEvents specification wrapper for Dapr subscriptions."""
    id: str
    source: str
    specversion: str = "1.0"
    type: str
    datacontenttype: str = "application/json"
    data: Dict[str, Any]
    time: Optional[datetime] = None
    traceparent: Optional[str] = None


# Import notification senders (created in parallel tasks)
from .websocket_broadcaster import WebSocketBroadcaster
from .email_sender import EmailSender

# Initialize senders
websocket_broadcaster = WebSocketBroadcaster()
email_sender = EmailSender()


@app.get("/dapr/subscribe")
async def subscribe():
    """
    Dapr subscription endpoint.

    Returns the list of topics this service subscribes to.
    """
    return [
        {
            "pubsubname": PUBSUB_NAME,
            "topic": TOPIC_REMINDERS,
            "route": "/reminders",
        }
    ]


@app.post("/reminders")
async def handle_reminder_event(request: Request):
    """
    Handle incoming reminder events from Dapr Pub/Sub.

    This endpoint receives CloudEvents from Kafka/Redpanda and
    dispatches notifications to the appropriate channels.
    """
    try:
        # Parse the incoming CloudEvent
        body = await request.json()
        logger.info(f"Received reminder event: {body.get('id', 'unknown')}")

        # Extract the event data
        if "data" in body:
            # CloudEvents format
            event_data = body["data"]
        else:
            # Raw event format
            event_data = body

        # Parse the reminder event
        reminder = ReminderEvent(**event_data)

        # Check if the reminder time has passed
        now = datetime.utcnow()
        if reminder.remind_at > now:
            # Reminder is for the future - log and acknowledge
            logger.info(
                f"Reminder for task {reminder.task_id} scheduled for "
                f"{reminder.remind_at}, current time is {now}"
            )
            # In production, this would be handled by a scheduler
            # For now, we process immediately when the event arrives

        # Process notification based on user preferences
        prefs = reminder.notification_preferences
        notification_sent = False

        # Send in-app notification via WebSocket
        if prefs.in_app:
            try:
                await websocket_broadcaster.broadcast_to_user(
                    user_id=reminder.user_id,
                    message={
                        "type": "reminder",
                        "task_id": reminder.task_id,
                        "title": reminder.title,
                        "description": reminder.description,
                        "due_at": reminder.due_at.isoformat(),
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )
                notification_sent = True
                logger.info(f"Sent in-app notification for task {reminder.task_id}")
            except Exception as e:
                logger.error(f"Failed to send in-app notification: {e}")

        # Send email notification
        if prefs.email and prefs.user_email:
            try:
                await email_sender.send_reminder_email(
                    to_email=prefs.user_email,
                    task_title=reminder.title,
                    task_description=reminder.description,
                    due_at=reminder.due_at,
                )
                notification_sent = True
                logger.info(f"Sent email notification for task {reminder.task_id}")
            except Exception as e:
                logger.error(f"Failed to send email notification: {e}")

        if not notification_sent:
            logger.warning(
                f"No notifications sent for task {reminder.task_id} - "
                f"in_app={prefs.in_app}, email={prefs.email}"
            )

        # Return success to acknowledge the message
        return {"status": "SUCCESS"}

    except Exception as e:
        logger.exception(f"Error processing reminder event: {e}")
        # Return success anyway to avoid message redelivery for bad messages
        # In production, you might want to dead-letter these
        return {"status": "DROP"}


@app.get("/health")
async def health_check():
    """Health check endpoint for Kubernetes probes."""
    return {
        "status": "healthy",
        "service": "notification",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint for Kubernetes probes."""
    return {
        "status": "ready",
        "websocket_broadcaster": websocket_broadcaster.is_ready(),
        "email_sender": email_sender.is_ready(),
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8001"))
    uvicorn.run(app, host="0.0.0.0", port=port)
