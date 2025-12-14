"""Recurrence utilities for handling recurring tasks."""

from datetime import datetime, timedelta
from typing import List, Optional
from app.schemas.task import RecurrencePattern


def calculate_next_occurrence(
    start_date: datetime,
    pattern: RecurrencePattern,
    interval: int = 1,
    current_date: Optional[datetime] = None
) -> datetime:
    """
    Calculate the next occurrence date based on recurrence pattern.

    Args:
        start_date: The original due date of the recurring task
        pattern: The recurrence pattern (daily, weekly, etc.)
        interval: How often to repeat (e.g., every 2 weeks)
        current_date: The reference date to calculate from (defaults to now)

    Returns:
        datetime: The next occurrence date
    """
    if current_date is None:
        current_date = datetime.utcnow()

    # If the start date is in the future, use it as the next occurrence
    if start_date > current_date:
        return start_date

    # Calculate based on pattern
    if pattern == RecurrencePattern.DAILY:
        return current_date + timedelta(days=interval)
    elif pattern == RecurrencePattern.WEEKLY:
        return current_date + timedelta(weeks=interval)
    elif pattern == RecurrencePattern.BIWEEKLY:
        return current_date + timedelta(weeks=interval * 2)
    elif pattern == RecurrencePattern.MONTHLY:
        # For monthly, we add months carefully (not just 30 days)
        # This is a simplified version - in production, you'd want to handle month boundaries properly
        target_month = current_date.month + interval
        target_year = current_date.year
        while target_month > 12:
            target_year += 1
            target_month -= 12

        # Handle day overflow (e.g., Jan 31 + 1 month -> Feb 28/29)
        day = min(current_date.day, _days_in_month(target_year, target_month))
        return current_date.replace(year=target_year, month=target_month, day=day)
    elif pattern == RecurrencePattern.YEARLY:
        return current_date.replace(year=current_date.year + interval)
    else:  # CUSTOM or unknown pattern
        # For custom patterns, default to daily
        return current_date + timedelta(days=interval)


def _days_in_month(year: int, month: int) -> int:
    """Helper function to get the number of days in a month."""
    if month == 2:  # February
        if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
            return 29  # Leap year
        else:
            return 28
    elif month in [4, 6, 9, 11]:  # April, June, September, November
        return 30
    else:  # All other months
        return 31


def generate_recurring_tasks(
    original_task_data: dict,
    start_date: datetime,
    end_date: Optional[datetime] = None,
    max_instances: int = 10
) -> List[dict]:
    """
    Generate recurring task instances based on the original task and recurrence pattern.

    Args:
        original_task_data: The original task data (without recurrence fields)
        start_date: When to start generating tasks
        end_date: When to stop generating tasks (optional)
        max_instances: Maximum number of instances to generate

    Returns:
        List[dict]: List of task instances with updated dates
    """
    if not original_task_data.get('is_recurring') or not original_task_data.get('recurrence_pattern'):
        return []

    pattern = RecurrencePattern(original_task_data['recurrence_pattern'])
    interval = original_task_data.get('recurrence_interval', 1)

    tasks = []
    current_date = start_date
    count = 0

    while count < max_instances and (end_date is None or current_date <= end_date):
        # Create a new task instance
        task_instance = original_task_data.copy()

        # Update the due date for this instance
        task_instance['due_date'] = current_date
        # Reset completion status for new instance
        task_instance['completed'] = False
        # Clear any existing ID to generate a new one
        if 'id' in task_instance:
            del task_instance['id']
        # Clear parent ID for the first instance (subsequent ones will be linked)
        if 'parent_task_id' in task_instance:
            del task_instance['parent_task_id']

        tasks.append(task_instance)

        # Calculate next occurrence
        current_date = calculate_next_occurrence(
            start_date=current_date,
            pattern=pattern,
            interval=interval
        )

        count += 1

    return tasks


def is_recurring_task_expired(task: dict, current_date: Optional[datetime] = None) -> bool:
    """
    Check if a recurring task has expired based on its end date.

    Args:
        task: The task dictionary
        current_date: The reference date to check against (defaults to now)

    Returns:
        bool: True if the task has expired, False otherwise
    """
    if current_date is None:
        current_date = datetime.utcnow()

    recurrence_end_date = task.get('recurrence_end_date')
    if recurrence_end_date and current_date > recurrence_end_date:
        return True

    return False