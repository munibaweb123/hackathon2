"""Recurrence pattern models for recurring tasks."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class RecurrenceFrequency(str, Enum):
    """How often a task repeats."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


@dataclass
class RecurrencePattern:
    """
    Defines the complete recurrence rule for a task.

    Attributes:
        frequency: How often the task repeats (daily, weekly, monthly, custom)
        interval: Every N periods (e.g., every 2 weeks). Default is 1.
        day_of_week: For WEEKLY: list of days (0=Mon, 1=Tue, ..., 6=Sun)
        day_of_month: For MONTHLY: day of month (1-31, adjusted for short months)
        end_date: ISO date when recurrence stops (optional)
    """
    frequency: RecurrenceFrequency
    interval: int = 1
    day_of_week: list[int] = field(default_factory=list)
    day_of_month: Optional[int] = None
    end_date: Optional[str] = None

    def __post_init__(self):
        """Validate the recurrence pattern."""
        if self.interval < 1:
            raise ValueError("interval must be >= 1")
        for day in self.day_of_week:
            if not 0 <= day <= 6:
                raise ValueError(f"day_of_week values must be 0-6, got {day}")
        if self.day_of_month is not None and not 1 <= self.day_of_month <= 31:
            raise ValueError(f"day_of_month must be 1-31, got {self.day_of_month}")

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "frequency": self.frequency.value,
            "interval": self.interval,
            "day_of_week": self.day_of_week,
            "day_of_month": self.day_of_month,
            "end_date": self.end_date,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RecurrencePattern":
        """Create a RecurrencePattern from a dictionary."""
        return cls(
            frequency=RecurrenceFrequency(data["frequency"]),
            interval=data.get("interval", 1),
            day_of_week=data.get("day_of_week", []),
            day_of_month=data.get("day_of_month"),
            end_date=data.get("end_date"),
        )

    def __str__(self) -> str:
        """Human-readable description of the recurrence pattern."""
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

        if self.frequency == RecurrenceFrequency.DAILY:
            if self.interval == 1:
                return "Repeats: Daily"
            return f"Repeats: Every {self.interval} days"

        elif self.frequency == RecurrenceFrequency.WEEKLY:
            if self.day_of_week:
                day_names = ", ".join(days[d] for d in sorted(self.day_of_week))
                if self.interval == 1:
                    return f"Repeats: Weekly on {day_names}"
                return f"Repeats: Every {self.interval} weeks on {day_names}"
            if self.interval == 1:
                return "Repeats: Weekly"
            return f"Repeats: Every {self.interval} weeks"

        elif self.frequency == RecurrenceFrequency.MONTHLY:
            if self.day_of_month:
                suffix = self._get_ordinal_suffix(self.day_of_month)
                if self.interval == 1:
                    return f"Repeats: Monthly on the {self.day_of_month}{suffix}"
                return f"Repeats: Every {self.interval} months on the {self.day_of_month}{suffix}"
            if self.interval == 1:
                return "Repeats: Monthly"
            return f"Repeats: Every {self.interval} months"

        else:  # CUSTOM
            return f"Repeats: Every {self.interval} days"

    @staticmethod
    def _get_ordinal_suffix(n: int) -> str:
        """Get ordinal suffix for a number (1st, 2nd, 3rd, etc.)."""
        if 11 <= n <= 13:
            return "th"
        return {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
