"""Pydantic schemas for Kafka event payloads."""

from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID
from pydantic import BaseModel, Field

from app.models.enums import Priority, TaskStatus


class TaskData(BaseModel):
    """Task data included in events."""
    title: str
    description: Optional[str] = None
    status: TaskStatus
    priority: Priority
    due_date: Optional[datetime] = None
    reminder_at: Optional[datetime] = None
    tags: List[str] = Field(default_factory=list)
    recurrence_id: Optional[UUID] = None
    parent_task_id: Optional[int] = None


class TaskEvent(BaseModel):
    """
    Event for task CRUD operations.
    Published to 'task-events' topic.
    Consumed by: Recurring Service, Audit Service
    """
    event_id: UUID
    event_type: str = Field(
        ...,
        description="Type of task operation",
        pattern="^(created|updated|completed|deleted)$"
    )
    task_id: int
    user_id: str
    task_data: Optional[TaskData] = Field(
        default=None,
        description="Full task object (included for created/updated/completed)"
    )
    timestamp: datetime
    correlation_id: Optional[UUID] = None

    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "123e4567-e89b-12d3-a456-426614174000",
                "event_type": "created",
                "task_id": 1,
                "user_id": "user-123",
                "task_data": {
                    "title": "Buy groceries",
                    "description": "Milk, eggs, bread",
                    "status": "pending",
                    "priority": "medium",
                    "due_date": "2024-12-15T18:00:00Z",
                    "tags": ["shopping", "weekly"]
                },
                "timestamp": "2024-12-10T10:00:00Z",
                "correlation_id": "789e4567-e89b-12d3-a456-426614174000"
            }
        }


class NotificationPreferences(BaseModel):
    """User notification channel preferences."""
    in_app: bool = True
    email: bool = True
    user_email: Optional[str] = None


class ReminderEvent(BaseModel):
    """
    Event for scheduled reminder triggers.
    Published to 'reminders' topic.
    Consumed by: Notification Service
    """
    event_id: UUID
    task_id: int
    user_id: str
    title: str
    description: Optional[str] = None
    due_at: datetime
    remind_at: datetime
    notification_preferences: NotificationPreferences
    timestamp: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "123e4567-e89b-12d3-a456-426614174000",
                "task_id": 1,
                "user_id": "user-123",
                "title": "Buy groceries",
                "description": "Don't forget the milk!",
                "due_at": "2024-12-15T18:00:00Z",
                "remind_at": "2024-12-15T17:00:00Z",
                "notification_preferences": {
                    "in_app": True,
                    "email": True,
                    "user_email": "user@example.com"
                },
                "timestamp": "2024-12-10T10:00:00Z"
            }
        }


class TaskUpdateEvent(BaseModel):
    """
    Event for real-time client synchronization.
    Published to 'task-updates' topic.
    Consumed by: WebSocket Service
    """
    event_id: UUID
    event_type: str = Field(default="sync", const=True)
    task_id: int
    user_id: str
    changes: Dict[str, Any] = Field(
        default_factory=dict,
        description="Changed fields and their new values"
    )
    full_task: Optional[TaskData] = Field(
        default=None,
        description="Optional full task for initial sync"
    )
    timestamp: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "123e4567-e89b-12d3-a456-426614174000",
                "event_type": "sync",
                "task_id": 1,
                "user_id": "user-123",
                "changes": {
                    "status": "completed",
                    "updated_at": "2024-12-10T11:00:00Z"
                },
                "full_task": None,
                "timestamp": "2024-12-10T11:00:00Z"
            }
        }


class CloudEvent(BaseModel):
    """
    CloudEvents specification wrapper for Dapr subscriptions.
    Used when receiving events from Dapr Pub/Sub.
    """
    id: str
    source: str
    specversion: str = "1.0"
    type: str
    datacontenttype: str = "application/json"
    data: Dict[str, Any]
    time: Optional[datetime] = None
    traceparent: Optional[str] = None
