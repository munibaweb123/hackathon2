"""Task model and related enums for the Todo application."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class Priority(str, Enum):
    """Priority levels for tasks."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Status(str, Enum):
    """Completion status for tasks."""
    INCOMPLETE = "incomplete"
    COMPLETE = "complete"


@dataclass
class Task:
    """
    A todo item with title, description, due date, priority, categories, and status.

    Attributes:
        id: Unique sequential identifier (positive integer, never reused)
        title: Short description of the task (1-100 characters)
        priority: Importance level (HIGH, MEDIUM, LOW)
        status: Completion state (INCOMPLETE, COMPLETE)
        description: Detailed information about the task (0-500 characters)
        due_date: Target completion date in YYYY-MM-DD format
        categories: Organization tags (case-insensitive, stored as lowercase)
        created_at: ISO 8601 datetime when task was created
    """
    id: int
    title: str
    priority: Priority = Priority.MEDIUM
    status: Status = Status.INCOMPLETE
    description: str = ""
    due_date: Optional[str] = None
    categories: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def toggle_status(self) -> None:
        """Toggle the task status between INCOMPLETE and COMPLETE."""
        if self.status == Status.INCOMPLETE:
            self.status = Status.COMPLETE
        else:
            self.status = Status.INCOMPLETE

    def is_complete(self) -> bool:
        """Check if the task is complete."""
        return self.status == Status.COMPLETE

    def to_dict(self) -> dict:
        """Convert the task to a dictionary for JSON serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date,
            "priority": self.priority.value,
            "categories": self.categories,
            "status": self.status.value,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Create a Task from a dictionary."""
        return cls(
            id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            due_date=data.get("due_date"),
            priority=Priority(data.get("priority", "medium")),
            categories=data.get("categories", []),
            status=Status(data.get("status", "incomplete")),
            created_at=data.get("created_at", datetime.now().isoformat()),
        )
