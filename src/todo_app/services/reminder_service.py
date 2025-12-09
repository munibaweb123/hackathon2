"""Reminder service for managing task reminders and notifications."""

from datetime import datetime, timedelta
from typing import Optional

from ..models import Reminder, ReminderOffset, Task


def add_reminder(
    task: Task,
    offset: ReminderOffset,
    custom_minutes: Optional[int] = None,
) -> Optional[Reminder]:
    """
    Add a reminder to a task.

    Args:
        task: The task to add the reminder to.
        offset: When to trigger relative to due time.
        custom_minutes: For CUSTOM offset, minutes before due time.

    Returns:
        The created Reminder, or None if task has no due date.
    """
    if not task.due_date:
        return None

    # Calculate trigger time
    trigger_time = calculate_trigger_time(task, offset, custom_minutes)
    if trigger_time is None:
        return None

    reminder = Reminder(
        id=Reminder.generate_id(),
        task_id=task.id,
        offset=offset,
        trigger_time=trigger_time,
        custom_minutes=custom_minutes,
        shown=False,
    )

    task.reminders.append(reminder)
    return reminder


def calculate_trigger_time(
    task: Task,
    offset: ReminderOffset,
    custom_minutes: Optional[int] = None,
) -> Optional[str]:
    """
    Calculate when a reminder should trigger.

    Args:
        task: The task with due date/time.
        offset: Reminder offset type.
        custom_minutes: For CUSTOM offset.

    Returns:
        ISO datetime string for trigger time, or None if invalid.
    """
    if not task.due_date:
        return None

    # Parse due datetime
    due_time = task.due_time or "23:59:00"
    due_datetime_str = f"{task.due_date}T{due_time}"
    due_datetime = datetime.fromisoformat(due_datetime_str)

    # Get minutes before
    minutes_before = offset.get_minutes(custom_minutes)

    # Calculate trigger time
    trigger_datetime = due_datetime - timedelta(minutes=minutes_before)

    return trigger_datetime.isoformat()


def check_due_reminders(store) -> list[tuple[Reminder, Task]]:
    """
    Check for reminders that are due and haven't been shown.

    Args:
        store: The JsonStore to check tasks from.

    Returns:
        List of (reminder, task) tuples for reminders that need to be shown.
    """
    now = datetime.now()
    due_reminders = []

    for task in store.get_all_tasks():
        for reminder in task.reminders:
            if reminder.shown:
                continue

            # Parse trigger time
            try:
                trigger_time = datetime.fromisoformat(reminder.trigger_time)
            except (ValueError, TypeError):
                continue

            # Check if reminder is due (trigger time has passed)
            if trigger_time <= now:
                due_reminders.append((reminder, task))

    return due_reminders


def mark_as_shown(reminder: Reminder, task: Task, store) -> bool:
    """
    Mark a reminder as shown.

    Args:
        reminder: The reminder to mark.
        task: The task containing the reminder.
        store: The JsonStore to persist changes.

    Returns:
        True if successfully marked, False otherwise.
    """
    reminder.shown = True
    return store.update_task(task)


def recalculate_reminders(task: Task) -> None:
    """
    Recalculate trigger times for all reminders when due date/time changes.

    Updates reminder trigger times in-place.

    Args:
        task: The task with updated due date/time.
    """
    if not task.due_date:
        # No due date - clear reminders
        task.reminders.clear()
        return

    for reminder in task.reminders:
        if reminder.shown:
            # Don't recalculate already shown reminders
            continue

        new_trigger = calculate_trigger_time(
            task,
            reminder.offset,
            reminder.custom_minutes,
        )
        if new_trigger:
            reminder.trigger_time = new_trigger


def remove_reminder(task: Task, reminder_id: str) -> bool:
    """
    Remove a specific reminder from a task.

    Args:
        task: The task to remove the reminder from.
        reminder_id: The ID of the reminder to remove.

    Returns:
        True if removed, False if not found.
    """
    for i, reminder in enumerate(task.reminders):
        if reminder.id == reminder_id:
            task.reminders.pop(i)
            return True
    return False


def get_upcoming_reminders(store, hours: int = 24) -> list[tuple[Reminder, Task]]:
    """
    Get reminders that will trigger within the next N hours.

    Args:
        store: The JsonStore to check tasks from.
        hours: Number of hours to look ahead.

    Returns:
        List of (reminder, task) tuples sorted by trigger time.
    """
    now = datetime.now()
    cutoff = now + timedelta(hours=hours)
    upcoming = []

    for task in store.get_all_tasks():
        for reminder in task.reminders:
            if reminder.shown:
                continue

            try:
                trigger_time = datetime.fromisoformat(reminder.trigger_time)
            except (ValueError, TypeError):
                continue

            if now <= trigger_time <= cutoff:
                upcoming.append((reminder, task))

    # Sort by trigger time
    upcoming.sort(key=lambda x: x[0].trigger_time)
    return upcoming


def create_reminders_for_new_instance(
    old_task: Task,
    new_task: Task,
) -> None:
    """
    Create reminders for a new recurring task instance based on the old task.

    Args:
        old_task: The completed task with original reminders.
        new_task: The new task instance to add reminders to.
    """
    if not new_task.due_date:
        return

    for old_reminder in old_task.reminders:
        add_reminder(
            new_task,
            old_reminder.offset,
            old_reminder.custom_minutes,
        )
