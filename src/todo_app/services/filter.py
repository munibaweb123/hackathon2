"""Filter functionality for the Todo application."""

from datetime import datetime
from typing import Optional

from ..models import Priority, Status, Task


def filter_by_status(tasks: list[Task], status: Status) -> list[Task]:
    """
    Filter tasks by completion status.

    Args:
        tasks: List of tasks to filter.
        status: Status to filter by.

    Returns:
        List of tasks with the specified status.
    """
    return [task for task in tasks if task.status == status]


def filter_by_priority(tasks: list[Task], priority: Priority) -> list[Task]:
    """
    Filter tasks by priority.

    Args:
        tasks: List of tasks to filter.
        priority: Priority to filter by.

    Returns:
        List of tasks with the specified priority.
    """
    return [task for task in tasks if task.priority == priority]


def filter_by_category(tasks: list[Task], category: str) -> list[Task]:
    """
    Filter tasks by category.

    Args:
        tasks: List of tasks to filter.
        category: Category to filter by (case-insensitive).

    Returns:
        List of tasks containing the specified category.
    """
    category = category.lower()
    return [
        task for task in tasks
        if any(cat.lower() == category for cat in task.categories)
    ]


def filter_by_date_range(
    tasks: list[Task],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> list[Task]:
    """
    Filter tasks by due date range.

    Args:
        tasks: List of tasks to filter.
        start_date: Start of date range (inclusive) in YYYY-MM-DD format.
        end_date: End of date range (inclusive) in YYYY-MM-DD format.

    Returns:
        List of tasks with due dates in the specified range.
        Tasks without due dates are excluded.
    """
    def parse_date(date_str: str) -> datetime:
        return datetime.strptime(date_str, "%Y-%m-%d")

    results = []

    for task in tasks:
        if not task.due_date:
            continue

        try:
            task_date = parse_date(task.due_date)

            if start_date:
                start = parse_date(start_date)
                if task_date < start:
                    continue

            if end_date:
                end = parse_date(end_date)
                if task_date > end:
                    continue

            results.append(task)
        except ValueError:
            # Invalid date format, skip this task
            continue

    return results


def combine_filters(
    tasks: list[Task],
    status: Optional[Status] = None,
    priority: Optional[Priority] = None,
    category: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> list[Task]:
    """
    Apply multiple filters to tasks.

    Args:
        tasks: List of tasks to filter.
        status: Filter by status (optional).
        priority: Filter by priority (optional).
        category: Filter by category (optional).
        start_date: Filter by start date (optional).
        end_date: Filter by end date (optional).

    Returns:
        List of tasks matching all specified filters.
    """
    results = tasks

    if status is not None:
        results = filter_by_status(results, status)

    if priority is not None:
        results = filter_by_priority(results, priority)

    if category is not None:
        results = filter_by_category(results, category)

    if start_date is not None or end_date is not None:
        results = filter_by_date_range(results, start_date, end_date)

    return results
