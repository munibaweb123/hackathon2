"""Sort functionality for the Todo application."""

from datetime import datetime
from typing import Optional

from ..models import Priority, Task


# Priority ordering (high = 0, medium = 1, low = 2)
PRIORITY_ORDER = {
    Priority.HIGH: 0,
    Priority.MEDIUM: 1,
    Priority.LOW: 2,
}


def sort_by_due_date(tasks: list[Task], ascending: bool = True) -> list[Task]:
    """
    Sort tasks by due date.

    Args:
        tasks: List of tasks to sort.
        ascending: If True, earliest dates first. If False, latest dates first.

    Returns:
        Sorted list of tasks. Tasks without due dates are placed at the end.
    """
    def parse_date(date_str: Optional[str]) -> tuple[int, datetime]:
        """Return (has_date, date) tuple for sorting. None dates go last."""
        if date_str is None:
            # No date -> put at end (use max date)
            return (1, datetime.max)
        try:
            return (0, datetime.strptime(date_str, "%Y-%m-%d"))
        except ValueError:
            # Invalid date format -> put at end
            return (1, datetime.max)

    sorted_tasks = sorted(tasks, key=lambda t: parse_date(t.due_date))

    if not ascending:
        # Reverse but keep None dates at the end
        with_dates = [t for t in sorted_tasks if t.due_date is not None]
        without_dates = [t for t in sorted_tasks if t.due_date is None]
        sorted_tasks = list(reversed(with_dates)) + without_dates

    return sorted_tasks


def sort_by_priority(tasks: list[Task]) -> list[Task]:
    """
    Sort tasks by priority (high first, then medium, then low).

    Args:
        tasks: List of tasks to sort.

    Returns:
        Sorted list of tasks.
    """
    return sorted(tasks, key=lambda t: PRIORITY_ORDER[t.priority])


def sort_by_title(tasks: list[Task]) -> list[Task]:
    """
    Sort tasks alphabetically by title (case-insensitive).

    Args:
        tasks: List of tasks to sort.

    Returns:
        Sorted list of tasks.
    """
    return sorted(tasks, key=lambda t: t.title.lower())


def sort_by_created_at(tasks: list[Task], ascending: bool = True) -> list[Task]:
    """
    Sort tasks by creation date.

    Args:
        tasks: List of tasks to sort.
        ascending: If True, oldest first. If False, newest first.

    Returns:
        Sorted list of tasks.
    """
    def parse_datetime(dt_str: str) -> datetime:
        """Parse ISO 8601 datetime string."""
        try:
            # Handle both with and without microseconds
            if "." in dt_str:
                return datetime.fromisoformat(dt_str)
            return datetime.fromisoformat(dt_str)
        except ValueError:
            return datetime.min

    sorted_tasks = sorted(tasks, key=lambda t: parse_datetime(t.created_at))

    if not ascending:
        sorted_tasks = list(reversed(sorted_tasks))

    return sorted_tasks
