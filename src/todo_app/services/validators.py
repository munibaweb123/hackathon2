"""Input validation functions for the Todo application."""

import re
from datetime import datetime
from typing import Optional

from ..models import Priority


class ValidationError(Exception):
    """Raised when validation fails."""
    pass


def validate_title(title: str) -> str:
    """
    Validate and normalize a task title.

    Args:
        title: The title to validate.

    Returns:
        The normalized title (trimmed).

    Raises:
        ValidationError: If title is empty or exceeds 100 characters.
    """
    title = title.strip()

    if not title:
        raise ValidationError("Title cannot be empty")

    if len(title) > 100:
        raise ValidationError(f"Title cannot exceed 100 characters (got {len(title)})")

    return title


def validate_description(description: str) -> str:
    """
    Validate and normalize a task description.

    Args:
        description: The description to validate.

    Returns:
        The normalized description (trimmed).

    Raises:
        ValidationError: If description exceeds 500 characters.
    """
    description = description.strip()

    if len(description) > 500:
        raise ValidationError(f"Description cannot exceed 500 characters (got {len(description)})")

    return description


def validate_due_date(due_date: str) -> Optional[str]:
    """
    Validate a due date string.

    Args:
        due_date: The due date to validate (YYYY-MM-DD format or empty).

    Returns:
        The validated due date string, or None if empty.

    Raises:
        ValidationError: If date format is invalid or date doesn't exist.
    """
    due_date = due_date.strip()

    if not due_date:
        return None

    # Check format
    pattern = r"^\d{4}-\d{2}-\d{2}$"
    if not re.match(pattern, due_date):
        raise ValidationError("Due date must be in YYYY-MM-DD format")

    # Check if date is valid (e.g., 2024-02-30 would be invalid)
    try:
        datetime.strptime(due_date, "%Y-%m-%d")
    except ValueError:
        raise ValidationError(f"Invalid date: {due_date}")

    return due_date


def validate_priority(priority: str) -> Priority:
    """
    Validate and convert a priority string to Priority enum.

    Args:
        priority: The priority string (high/medium/low, case-insensitive).

    Returns:
        The corresponding Priority enum value.

    Raises:
        ValidationError: If priority is not one of high/medium/low.
    """
    priority = priority.strip().lower()

    valid_priorities = {"high": Priority.HIGH, "medium": Priority.MEDIUM, "low": Priority.LOW}

    if priority not in valid_priorities:
        raise ValidationError(f"Priority must be one of: high, medium, low (got '{priority}')")

    return valid_priorities[priority]


def validate_categories(categories_str: str) -> list[str]:
    """
    Validate and parse a comma-separated list of categories.

    Args:
        categories_str: Comma-separated category names.

    Returns:
        A list of normalized category names (lowercase, trimmed, unique, no empty strings).
    """
    if not categories_str.strip():
        return []

    # Split by comma, normalize each category
    categories = []
    seen = set()

    for cat in categories_str.split(","):
        cat = cat.strip().lower()
        if cat and cat not in seen:
            categories.append(cat)
            seen.add(cat)

    return categories


def validate_task_id(task_id: str) -> int:
    """
    Validate a task ID string.

    Args:
        task_id: The task ID as a string.

    Returns:
        The task ID as an integer.

    Raises:
        ValidationError: If task ID is not a positive integer.
    """
    task_id = task_id.strip()

    if not task_id:
        raise ValidationError("Task ID cannot be empty")

    try:
        id_int = int(task_id)
    except ValueError:
        raise ValidationError(f"Task ID must be a number (got '{task_id}')")

    if id_int <= 0:
        raise ValidationError(f"Task ID must be a positive number (got {id_int})")

    return id_int
