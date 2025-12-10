"""Task schemas for API requests/responses."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
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
                "is_recurring": True,
                "recurrence_pattern": "weekly",
                "recurrence_interval": 1,
            }
        }


# Import reminder schemas for nested response - import at the end to avoid circular import
from .reminder import ReminderResponse


class TaskResponse(BaseModel):
    """Schema for task response."""

    id: str
    title: str
    description: Optional[str] = None
    completed: bool
    priority: Priority
    due_date: Optional[datetime] = None
    user_id: str

    # Recurring task fields
    is_recurring: bool
    recurrence_pattern: Optional[RecurrencePattern] = None
    recurrence_interval: Optional[int] = None
    recurrence_end_date: Optional[datetime] = None
    parent_task_id: Optional[str] = None

    # Include reminders in the response
    reminders: Optional[List[ReminderResponse]] = []

    created_at: datetime
    updated_at: datetime

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
