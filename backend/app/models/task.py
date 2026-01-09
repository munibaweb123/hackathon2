"""Task model for SQLModel/PostgreSQL."""

from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import Text

from .enums import Priority, TaskStatus

if TYPE_CHECKING:
    from .user import User
    from .reminder import Reminder
    from .task_tag import TaskTag
    from .recurrence import RecurrencePattern


class Task(SQLModel, table=True):
    """Task model for todo items with advanced features."""

    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(min_length=1, max_length=255, index=True)
    description: Optional[str] = Field(default=None, max_length=1000)
    user_id: str = Field(foreign_key="users.id", index=True, nullable=False)

    # Status and priority (Phase V)
    status: TaskStatus = Field(default=TaskStatus.PENDING, index=True)
    priority: Priority = Field(default=Priority.NONE, index=True)

    # Due date and reminders (Phase V - US1)
    due_date: Optional[datetime] = Field(default=None, index=True)
    reminder_at: Optional[datetime] = Field(default=None)

    # Recurrence support (Phase V - US2)
    recurrence_id: Optional[UUID] = Field(
        default=None,
        foreign_key="recurrence_patterns.id"
    )
    parent_task_id: Optional[int] = Field(
        default=None,
        foreign_key="tasks.id"
    )

    # Full-text search (Phase V - US4)
    # Note: search_vector is managed by PostgreSQL trigger, not set directly
    # search_vector column added via migration

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Recurring task flag (added via migration)
    is_recurring: bool = Field(default=False)

    # Legacy field for backward compatibility
    completed: bool = Field(default=False)

    # Relationships
    user: Optional["User"] = Relationship(back_populates="tasks")
    reminders: List["Reminder"] = Relationship(back_populates="task")
    task_tags: List["TaskTag"] = Relationship(back_populates="task")
    # Note: recurrence relationship is not defined here to avoid circular import issues
    # It's handled in the __init__.py file

    @property
    def is_overdue(self) -> bool:
        """Check if task is overdue."""
        if self.due_date and self.status != TaskStatus.COMPLETED:
            return datetime.utcnow() > self.due_date
        return False

    @property
    def has_recurrence(self) -> bool:
        """Check if task has a recurrence pattern."""
        return self.recurrence_id is not None

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "status": "pending",
                "priority": "medium",
                "due_date": "2024-12-15T18:00:00Z",
                "reminder_at": "2024-12-15T17:00:00Z",
                "user_id": "user-123",
                "recurrence_id": None,
                "parent_task_id": None,
                "created_at": "2024-12-10T10:00:00Z",
                "updated_at": "2024-12-10T10:00:00Z",
            }
        }
