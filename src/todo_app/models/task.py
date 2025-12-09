"""Task model and related enums for the Todo application."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .recurrence import RecurrencePattern
    from .reminder import Reminder


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
        due_time: Target completion time in HH:MM:SS format (NEW)
        categories: Organization tags (case-insensitive, stored as lowercase)
        created_at: ISO 8601 datetime when task was created
        recurrence: Recurrence pattern for recurring tasks (NEW)
        series_id: UUID linking recurring task instances (NEW)
        reminders: List of reminders for this task (NEW)
    """
    id: int
    title: str
    priority: Priority = Priority.MEDIUM
    status: Status = Status.INCOMPLETE
    description: str = ""
    due_date: Optional[str] = None
    due_time: Optional[str] = None  # NEW: HH:MM:SS format
    categories: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    recurrence: Optional["RecurrencePattern"] = None  # NEW
    series_id: Optional[str] = None  # NEW: UUID for recurring series
    reminders: list = field(default_factory=list)  # NEW: list of Reminder objects

    def toggle_status(self) -> None:
        """Toggle the task status between INCOMPLETE and COMPLETE."""
        if self.status == Status.INCOMPLETE:
            self.status = Status.COMPLETE
        else:
            self.status = Status.INCOMPLETE

    def is_complete(self) -> bool:
        """Check if the task is complete."""
        return self.status == Status.COMPLETE

    def is_recurring(self) -> bool:
        """Check if this is a recurring task."""
        return self.recurrence is not None

    def has_reminders(self) -> bool:
        """Check if this task has reminders."""
        return len(self.reminders) > 0

    def get_due_datetime_str(self) -> Optional[str]:
        """Get combined due date and time as ISO datetime string."""
        if not self.due_date:
            return None
        time = self.due_time or "23:59:00"
        return f"{self.due_date}T{time}"

    def to_dict(self) -> dict:
        """Convert the task to a dictionary for JSON serialization."""
        from .recurrence import RecurrencePattern
        from .reminder import Reminder

        result = {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date,
            "due_time": self.due_time,
            "priority": self.priority.value,
            "categories": self.categories,
            "status": self.status.value,
            "created_at": self.created_at,
            "series_id": self.series_id,
        }

        # Serialize recurrence if present
        if self.recurrence is not None:
            result["recurrence"] = self.recurrence.to_dict()
        else:
            result["recurrence"] = None

        # Serialize reminders
        result["reminders"] = [
            r.to_dict() if hasattr(r, 'to_dict') else r
            for r in self.reminders
        ]

        return result

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Create a Task from a dictionary."""
        from .recurrence import RecurrencePattern
        from .reminder import Reminder

        # Parse recurrence if present
        recurrence = None
        if data.get("recurrence"):
            recurrence = RecurrencePattern.from_dict(data["recurrence"])

        # Parse reminders if present
        reminders = []
        for r in data.get("reminders", []):
            if isinstance(r, dict):
                reminders.append(Reminder.from_dict(r))
            else:
                reminders.append(r)

        return cls(
            id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            due_date=data.get("due_date"),
            due_time=data.get("due_time"),
            priority=Priority(data.get("priority", "medium")),
            categories=data.get("categories", []),
            status=Status(data.get("status", "incomplete")),
            created_at=data.get("created_at", datetime.now().isoformat()),
            recurrence=recurrence,
            series_id=data.get("series_id"),
            reminders=reminders,
        )
