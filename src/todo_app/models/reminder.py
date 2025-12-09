"""Reminder models for task notifications."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import uuid


class ReminderOffset(str, Enum):
    """Pre-defined reminder timing options."""
    AT_TIME = "at_time"           # 0 minutes before
    MINUTES_15 = "minutes_15"     # 15 minutes before
    MINUTES_30 = "minutes_30"     # 30 minutes before
    HOUR_1 = "hour_1"             # 1 hour before
    HOURS_2 = "hours_2"           # 2 hours before
    DAY_1 = "day_1"               # 1 day before
    CUSTOM = "custom"             # Custom minutes

    def get_minutes(self, custom_minutes: Optional[int] = None) -> int:
        """Get the number of minutes before the due time."""
        mapping = {
            ReminderOffset.AT_TIME: 0,
            ReminderOffset.MINUTES_15: 15,
            ReminderOffset.MINUTES_30: 30,
            ReminderOffset.HOUR_1: 60,
            ReminderOffset.HOURS_2: 120,
            ReminderOffset.DAY_1: 1440,
        }
        if self == ReminderOffset.CUSTOM:
            if custom_minutes is None:
                raise ValueError("custom_minutes required for CUSTOM offset")
            return custom_minutes
        return mapping[self]

    def __str__(self) -> str:
        """Human-readable description."""
        descriptions = {
            ReminderOffset.AT_TIME: "At due time",
            ReminderOffset.MINUTES_15: "15 minutes before",
            ReminderOffset.MINUTES_30: "30 minutes before",
            ReminderOffset.HOUR_1: "1 hour before",
            ReminderOffset.HOURS_2: "2 hours before",
            ReminderOffset.DAY_1: "1 day before",
            ReminderOffset.CUSTOM: "Custom",
        }
        return descriptions[self]


@dataclass
class Reminder:
    """
    A reminder linked to a specific task.

    Attributes:
        id: Unique reminder identifier (UUID)
        task_id: ID of the associated task
        offset: When to trigger relative to due time
        custom_minutes: For CUSTOM offset, minutes before
        trigger_time: Calculated ISO datetime to trigger
        shown: Whether notification was displayed
    """
    id: str
    task_id: int
    offset: ReminderOffset
    trigger_time: str
    custom_minutes: Optional[int] = None
    shown: bool = False

    def __post_init__(self):
        """Validate the reminder."""
        if self.offset == ReminderOffset.CUSTOM and self.custom_minutes is None:
            raise ValueError("custom_minutes required for CUSTOM offset")

    @staticmethod
    def generate_id() -> str:
        """Generate a unique reminder ID."""
        return str(uuid.uuid4())

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "task_id": self.task_id,
            "offset": self.offset.value,
            "custom_minutes": self.custom_minutes,
            "trigger_time": self.trigger_time,
            "shown": self.shown,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Reminder":
        """Create a Reminder from a dictionary."""
        return cls(
            id=data["id"],
            task_id=data["task_id"],
            offset=ReminderOffset(data["offset"]),
            custom_minutes=data.get("custom_minutes"),
            trigger_time=data["trigger_time"],
            shown=data.get("shown", False),
        )

    def get_display_text(self) -> str:
        """Get display text for the reminder."""
        if self.offset == ReminderOffset.CUSTOM and self.custom_minutes:
            if self.custom_minutes >= 60:
                hours = self.custom_minutes // 60
                mins = self.custom_minutes % 60
                if mins:
                    return f"{hours}h {mins}m before"
                return f"{hours} hour{'s' if hours > 1 else ''} before"
            return f"{self.custom_minutes} minutes before"
        return str(self.offset)
