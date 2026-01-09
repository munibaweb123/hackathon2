"""Dapr event publisher utility for publishing events to Kafka via Dapr sidecar."""

import os
import logging
from typing import Optional, Dict, Any
from uuid import uuid4
from datetime import datetime

import httpx

logger = logging.getLogger(__name__)

# Dapr configuration
DAPR_HTTP_PORT = int(os.getenv("DAPR_HTTP_PORT", "3500"))
DAPR_BASE_URL = f"http://localhost:{DAPR_HTTP_PORT}"
PUBSUB_NAME = os.getenv("PUBSUB_NAME", "kafka-pubsub")

# Topic names
TOPIC_TASK_EVENTS = "task-events"
TOPIC_REMINDERS = "reminders"
TOPIC_TASK_UPDATES = "task-updates"


class EventPublisher:
    """Publisher for Dapr Pub/Sub events."""

    def __init__(
        self,
        dapr_url: str = DAPR_BASE_URL,
        pubsub_name: str = PUBSUB_NAME
    ):
        self.dapr_url = dapr_url
        self.pubsub_name = pubsub_name
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def publish(
        self,
        topic: str,
        data: Dict[str, Any],
        correlation_id: Optional[str] = None
    ) -> bool:
        """
        Publish an event to a Dapr Pub/Sub topic.

        Args:
            topic: The topic name to publish to
            data: The event payload
            correlation_id: Optional correlation ID for tracing

        Returns:
            True if published successfully, False otherwise
        """
        try:
            client = await self._get_client()

            # Add metadata to event
            event_data = {
                **data,
                "correlation_id": correlation_id or str(uuid4()),
                "published_at": datetime.utcnow().isoformat(),
            }

            url = f"{self.dapr_url}/v1.0/publish/{self.pubsub_name}/{topic}"

            response = await client.post(
                url,
                json=event_data,
                headers={
                    "Content-Type": "application/json",
                    "traceparent": f"00-{correlation_id or uuid4()}-0000000000000000-01"
                }
            )

            if response.status_code in (200, 204):
                logger.info(
                    f"Published event to {topic}",
                    extra={
                        "topic": topic,
                        "correlation_id": event_data["correlation_id"]
                    }
                )
                return True
            else:
                logger.error(
                    f"Failed to publish event to {topic}: {response.status_code}",
                    extra={
                        "topic": topic,
                        "status_code": response.status_code,
                        "response": response.text
                    }
                )
                return False

        except httpx.RequestError as e:
            logger.error(
                f"HTTP error publishing to {topic}: {e}",
                extra={"topic": topic, "error": str(e)}
            )
            return False
        except Exception as e:
            logger.exception(f"Unexpected error publishing to {topic}: {e}")
            return False

    async def publish_task_event(
        self,
        event_type: str,
        task_id: int,
        user_id: str,
        task_data: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None
    ) -> bool:
        """
        Publish a task event (created, updated, completed, deleted).

        Args:
            event_type: One of 'created', 'updated', 'completed', 'deleted'
            task_id: The task ID
            user_id: The user ID who performed the action
            task_data: Optional full task data
            correlation_id: Optional correlation ID for tracing

        Returns:
            True if published successfully
        """
        event = {
            "event_id": str(uuid4()),
            "event_type": event_type,
            "task_id": task_id,
            "user_id": user_id,
            "task_data": task_data,
            "timestamp": datetime.utcnow().isoformat(),
        }
        return await self.publish(TOPIC_TASK_EVENTS, event, correlation_id)

    async def publish_reminder_event(
        self,
        task_id: int,
        user_id: str,
        title: str,
        due_at: datetime,
        remind_at: datetime,
        notification_preferences: Dict[str, Any],
        description: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> bool:
        """
        Publish a reminder event for notification delivery.

        Args:
            task_id: The task ID
            user_id: The user to notify
            title: Task title for the notification
            due_at: When the task is due
            remind_at: When to send the reminder
            notification_preferences: User's notification channel preferences
            description: Optional task description
            correlation_id: Optional correlation ID for tracing

        Returns:
            True if published successfully
        """
        event = {
            "event_id": str(uuid4()),
            "task_id": task_id,
            "user_id": user_id,
            "title": title,
            "description": description,
            "due_at": due_at.isoformat(),
            "remind_at": remind_at.isoformat(),
            "notification_preferences": notification_preferences,
            "timestamp": datetime.utcnow().isoformat(),
        }
        return await self.publish(TOPIC_REMINDERS, event, correlation_id)

    async def publish_task_update_event(
        self,
        task_id: int,
        user_id: str,
        changes: Dict[str, Any],
        full_task: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None
    ) -> bool:
        """
        Publish a task update event for real-time client sync.

        Args:
            task_id: The task ID that was updated
            user_id: The user who owns the task
            changes: Dictionary of changed fields and their new values
            full_task: Optional full task object for initial sync
            correlation_id: Optional correlation ID for tracing

        Returns:
            True if published successfully
        """
        event = {
            "event_id": str(uuid4()),
            "event_type": "sync",
            "task_id": task_id,
            "user_id": user_id,
            "changes": changes,
            "full_task": full_task,
            "timestamp": datetime.utcnow().isoformat(),
        }
        return await self.publish(TOPIC_TASK_UPDATES, event, correlation_id)


# Singleton instance
_publisher: Optional[EventPublisher] = None


def get_event_publisher() -> EventPublisher:
    """Get the singleton EventPublisher instance."""
    global _publisher
    if _publisher is None:
        _publisher = EventPublisher()
    return _publisher
