"""Task schemas for API requests/responses."""

from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel, Field, field_serializer
from enum import Enum


class Priority(str, Enum):
    """Task priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RecurrencePattern(str, Enum):
    """Task recurrence patterns."""

    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"  # Every two weeks
    MONTHLY = "monthly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class TaskCreate(BaseModel):
    """Schema for creating a new task."""

    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    priority: Priority = Priority.MEDIUM
    due_date: Optional[datetime] = None
    reminder_at: Optional[datetime] = Field(
        default=None,
        description="When to send reminder notification. Must be before due_date if both are set."
    )

    # Recurring task fields
    is_recurring: bool = Field(default=False)
    recurrence_pattern: Optional[RecurrencePattern] = Field(default=None)
    recurrence_interval: Optional[int] = Field(default=1)  # How often to repeat (e.g., every 2 weeks)
    recurrence_end_date: Optional[datetime] = None  # When to stop recurring

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "priority": "medium",
                "due_date": "2024-12-15T18:00:00Z",
                "reminder_at": "2024-12-15T17:00:00Z",
                "is_recurring": False,
                "recurrence_pattern": None,
                "recurrence_interval": 1,
                "recurrence_end_date": None,
            }
        }


class TaskUpdate(BaseModel):
    """Schema for updating an existing task."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    completed: Optional[bool] = None
    priority: Optional[Priority] = None
    due_date: Optional[datetime] = None
    reminder_at: Optional[datetime] = Field(
        default=None,
        description="When to send reminder notification. Must be before due_date if both are set."
    )

    # Recurring task fields
    is_recurring: Optional[bool] = None
    recurrence_pattern: Optional[RecurrencePattern] = None
    recurrence_interval: Optional[int] = None
    recurrence_end_date: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Buy groceries (updated)",
                "completed": True,
                "priority": "high",
                "due_date": "2024-12-15T18:00:00Z",
                "reminder_at": "2024-12-15T17:00:00Z",
                "is_recurring": True,
                "recurrence_pattern": "weekly",
                "recurrence_interval": 1,
            }
        }


# Import reminder schemas for nested response - import at the end to avoid circular import
from .recurrence import RecurrencePatternResponse
from .reminder import ReminderResponse
from .tag import TagResponse


class TaskResponse(BaseModel):
    """Schema for task response."""

    id: int
    title: str
    description: Optional[str] = None
    completed: bool
    priority: Priority
    due_date: Optional[datetime] = None
    reminder_at: Optional[datetime] = None
    user_id: str

    # Computed property for overdue status
    is_overdue: bool = False

    # Recurring task fields
    is_recurring: bool
    recurrence_pattern: Optional[RecurrencePattern] = None
    recurrence_interval: Optional[int] = None
    recurrence_end_date: Optional[datetime] = None
    parent_task_id: Optional[int] = None

    # Include recurrence pattern in the response
    recurrence_pattern: Optional[RecurrencePatternResponse] = None

    # Include tags in the response
    tags: Optional[List[TagResponse]] = []

    # Include reminders in the response
    reminders: Optional[List[ReminderResponse]] = []

    created_at: datetime
    updated_at: datetime

    @field_serializer('due_date', 'reminder_at', 'recurrence_end_date', 'created_at', 'updated_at')
    def serialize_datetime(self, v: Optional[datetime]) -> Optional[str]:
        """Serialize datetime to ISO format with timezone info."""
        if v is None:
            return None
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        return v.isoformat()

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """Schema for paginated task list response."""

    tasks: List[TaskResponse]
    total: int
    page: int = 1
    page_size: int = 50

    class Config:
        json_schema_extra = {
            "example": {
                "tasks": [],
                "total": 0,
                "page": 1,
                "page_size": 50,
            }
        }
