"""Recurrence service for managing recurring tasks."""

import uuid
from datetime import datetime, timedelta
from typing import Optional

from dateutil.relativedelta import relativedelta

from ..models import RecurrenceFrequency, RecurrencePattern, Task, Status


def generate_series_id() -> str:
    """
    Generate a unique series ID for linking recurring task instances.

    Returns:
        A UUID string to identify a recurring task series.
    """
    return str(uuid.uuid4())


def calculate_next_date(
    current_date: str,
    pattern: RecurrencePattern,
) -> Optional[str]:
    """
    Calculate the next occurrence date based on the recurrence pattern.

    Args:
        current_date: The current due date in YYYY-MM-DD format.
        pattern: The recurrence pattern defining how the task repeats.

    Returns:
        The next due date in YYYY-MM-DD format, or None if recurrence has ended.
    """
    current = datetime.strptime(current_date, "%Y-%m-%d")

    if pattern.frequency == RecurrenceFrequency.DAILY:
        next_date = current + timedelta(days=pattern.interval)

    elif pattern.frequency == RecurrenceFrequency.WEEKLY:
        if pattern.day_of_week:
            # Find the next occurrence on one of the specified days
            next_date = _find_next_weekday(current, pattern.day_of_week, pattern.interval)
        else:
            # Simple weekly interval
            next_date = current + timedelta(weeks=pattern.interval)

    elif pattern.frequency == RecurrenceFrequency.MONTHLY:
        next_date = current + relativedelta(months=pattern.interval)
        if pattern.day_of_month:
            # Adjust to the specified day, handling month-end edge cases
            next_date = _adjust_to_day_of_month(next_date, pattern.day_of_month)

    elif pattern.frequency == RecurrenceFrequency.CUSTOM:
        # Custom uses interval as days
        next_date = current + timedelta(days=pattern.interval)

    else:
        return None

    # Check if we've passed the end date
    if pattern.end_date:
        end = datetime.strptime(pattern.end_date, "%Y-%m-%d")
        if next_date > end:
            return None

    return next_date.strftime("%Y-%m-%d")


def _find_next_weekday(
    current: datetime,
    days_of_week: list[int],
    interval: int,
) -> datetime:
    """
    Find the next occurrence on one of the specified weekdays.

    Args:
        current: The current date.
        days_of_week: List of weekday indices (0=Mon, 6=Sun).
        interval: Week interval (1 = every week, 2 = every 2 weeks).

    Returns:
        The next occurrence date.
    """
    # Get current weekday (0=Mon, 6=Sun)
    current_weekday = current.weekday()

    # Sort the days
    sorted_days = sorted(days_of_week)

    # First, look for the next day in the current week (after today)
    for day in sorted_days:
        if day > current_weekday:
            return current + timedelta(days=(day - current_weekday))

    # If no day found in current week, move to next interval week
    # and get the first specified day
    days_until_next_monday = 7 - current_weekday
    next_interval_start = current + timedelta(days=days_until_next_monday + (interval - 1) * 7)

    # Get the first specified day in that week
    first_day = sorted_days[0]
    return next_interval_start + timedelta(days=first_day)


def _adjust_to_day_of_month(date: datetime, day_of_month: int) -> datetime:
    """
    Adjust a date to a specific day of month, handling month-end edge cases.

    Args:
        date: The date to adjust.
        day_of_month: The target day (1-31).

    Returns:
        The adjusted date, clamped to the last day of the month if needed.
    """
    import calendar

    # Get the last day of the month
    _, last_day = calendar.monthrange(date.year, date.month)

    # Clamp to the last day if the target day doesn't exist
    actual_day = min(day_of_month, last_day)

    return date.replace(day=actual_day)


def create_next_instance(
    completed_task: Task,
    store,
) -> Optional[Task]:
    """
    Create the next instance of a recurring task when the current one is completed.

    Args:
        completed_task: The task that was just completed.
        store: The JsonStore for persisting the new task.

    Returns:
        The newly created task instance, or None if recurrence has ended.
    """
    if not completed_task.recurrence:
        return None

    if not completed_task.due_date:
        return None

    # Calculate the next due date
    next_due_date = calculate_next_date(
        completed_task.due_date,
        completed_task.recurrence,
    )

    if next_due_date is None:
        return None

    # Create a new task instance
    new_task = Task(
        id=0,  # Will be assigned by store
        title=completed_task.title,
        description=completed_task.description,
        due_date=next_due_date,
        due_time=completed_task.due_time,
        priority=completed_task.priority,
        categories=list(completed_task.categories),  # Copy the list
        status=Status.INCOMPLETE,
        recurrence=completed_task.recurrence,
        series_id=completed_task.series_id,
        reminders=[],  # Reminders will be recalculated based on new due date
    )

    return store.add_task(new_task)


def get_series_tasks(series_id: str, store) -> list[Task]:
    """
    Get all tasks belonging to a recurring series.

    Args:
        series_id: The series UUID to search for.
        store: The JsonStore to search in.

    Returns:
        List of tasks with the matching series_id, sorted by due_date.
    """
    all_tasks = store.get_all_tasks()
    series_tasks = [t for t in all_tasks if t.series_id == series_id]

    # Sort by due_date (None values last)
    return sorted(
        series_tasks,
        key=lambda t: t.due_date or "9999-99-99",
    )


def update_series(
    series_id: str,
    store,
    title: Optional[str] = None,
    description: Optional[str] = None,
    priority=None,
    categories: Optional[list[str]] = None,
    update_past: bool = False,
) -> int:
    """
    Update all future (or all) instances of a recurring series.

    Args:
        series_id: The series UUID to update.
        store: The JsonStore containing the tasks.
        title: New title (if provided).
        description: New description (if provided).
        priority: New priority (if provided).
        categories: New categories (if provided).
        update_past: If True, also update past/completed instances.

    Returns:
        Number of tasks updated.
    """
    tasks = get_series_tasks(series_id, store)
    today = datetime.now().strftime("%Y-%m-%d")
    updated_count = 0

    for task in tasks:
        # Skip past tasks unless update_past is True
        if not update_past:
            if task.due_date and task.due_date < today:
                continue
            if task.status == Status.COMPLETE:
                continue

        # Apply updates
        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if priority is not None:
            task.priority = priority
        if categories is not None:
            task.categories = list(categories)

        store.update_task(task)
        updated_count += 1

    return updated_count


def delete_series(
    series_id: str,
    store,
    delete_past: bool = False,
) -> int:
    """
    Delete all future (or all) instances of a recurring series.

    Args:
        series_id: The series UUID to delete.
        store: The JsonStore containing the tasks.
        delete_past: If True, also delete past/completed instances.

    Returns:
        Number of tasks deleted.
    """
    tasks = get_series_tasks(series_id, store)
    today = datetime.now().strftime("%Y-%m-%d")
    deleted_count = 0

    for task in tasks:
        # Skip past tasks unless delete_past is True
        if not delete_past:
            if task.due_date and task.due_date < today:
                continue
            if task.status == Status.COMPLETE:
                continue

        store.delete_task(task.id)
        deleted_count += 1

    return deleted_count


def stop_recurrence(task: Task, store) -> bool:
    """
    Stop recurrence for a task (remove recurrence pattern but keep the task).

    Args:
        task: The task to stop recurrence for.
        store: The JsonStore to update.

    Returns:
        True if updated, False if task had no recurrence.
    """
    if not task.recurrence:
        return False

    task.recurrence = None
    task.series_id = None
    return store.update_task(task)
