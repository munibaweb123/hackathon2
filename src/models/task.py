"""Task model for the Todo Console Application."""

from dataclasses import dataclass, field


@dataclass
class Task:
    """Represents a single todo item.

    Attributes:
        title: Short description of the task (required, non-empty).
        description: Detailed information about the task (optional).
        completed: Completion state (False = incomplete, True = complete).
        id: Unique numeric identifier (auto-generated).
    """

    title: str
    description: str = ""
    completed: bool = False
    id: int = field(default=0)

    def __post_init__(self) -> None:
        """Validate title is non-empty after initialization."""
        if not self.title or not self.title.strip():
            raise ValueError("Task title cannot be empty")

    def mark_complete(self) -> None:
        """Mark task as completed."""
        self.completed = True

    def mark_incomplete(self) -> None:
        """Mark task as incomplete."""
        self.completed = False

    def toggle_status(self) -> None:
        """Toggle between complete and incomplete."""
        self.completed = not self.completed
