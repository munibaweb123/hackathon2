"""Task model for SQLModel/PostgreSQL."""

from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
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


class Task(SQLModel, table=True):
    """Task model for todo items."""

    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(min_length=1, max_length=255, index=True)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    priority: Priority = Field(default=Priority.MEDIUM)
    due_date: Optional[datetime] = None
    user_id: str = Field(foreign_key="users.id", index=True)

    # Recurring task fields
    is_recurring: bool = Field(default=False)
    recurrence_pattern: Optional[RecurrencePattern] = Field(default=None)
    recurrence_interval: Optional[int] = Field(default=1)  # How often to repeat (e.g., every 2 weeks)
    recurrence_end_date: Optional[datetime] = None  # When to stop recurring
    parent_task_id: Optional[int] = Field(default=None, foreign_key="tasks.id")  # For recurring instances

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to user
    user: Optional["User"] = Relationship(back_populates="tasks")

    # Relationship to reminders
    reminders: List["Reminder"] = Relationship(back_populates="task")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "completed": False,
                "priority": "medium",
                "due_date": "2024-12-15T18:00:00Z",
                "user_id": "user-123",
                "is_recurring": False,
                "recurrence_pattern": None,
                "recurrence_interval": None,
                "recurrence_end_date": None,
                "parent_task_id": None,
                "created_at": "2024-12-10T10:00:00Z",
                "updated_at": "2024-12-10T10:00:00Z",
            }
        }
