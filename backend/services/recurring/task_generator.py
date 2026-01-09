"""Task generator for recurring tasks.

This module handles the creation of new task instances when recurring tasks
are completed, based on their recurrence pattern.
"""

import logging
from datetime import datetime, date
from typing import Dict, Any, Optional

from sqlmodel import Session, select
from uuid import UUID

logger = logging.getLogger(__name__)


async def generate_next_occurrence(
    original_task_id: int,
    user_id: str,
    task_data: Dict[str, Any]
) -> bool:
    """
    Generate the next occurrence of a recurring task.

    Args:
        original_task_id: The ID of the original recurring task
        user_id: The user ID who owns the task
        task_data: The task data including recurrence information

    Returns:
        True if the next occurrence was generated successfully, False otherwise
    """
    try:
        # Import here to avoid circular imports
        from ...core.database import engine
        from ...models.task import Task
        from ...models.recurrence import RecurrencePattern
        from ...models.enums import RecurrenceStatus, TaskStatus
        from ...utils.recurrence import calculate_next_occurrence, is_recurring_task_expired

        with Session(engine) as session:
            # Get the recurrence pattern for this task
            recurrence_id_str = task_data.get("recurrence_id")
            if not recurrence_id_str:
                logger.warning(f"Task {original_task_id} has no recurrence pattern ID")
                return False

            try:
                recurrence_id = UUID(recurrence_id_str)
            except ValueError:
                logger.error(f"Invalid recurrence ID format: {recurrence_id_str}")
                return False

            # Fetch the recurrence pattern
            recurrence_pattern = session.get(RecurrencePattern, recurrence_id)
            if not recurrence_pattern:
                logger.error(f"Recurrence pattern {recurrence_id} not found for task {original_task_id}")
                return False

            # Check if the recurrence pattern is still active
            if recurrence_pattern.status != RecurrenceStatus.ACTIVE:
                logger.info(f"Recurrence pattern {recurrence_id} is not active, skipping generation")
                return False

            # Check if the recurrence has expired
            if is_recurring_task_expired({"recurrence_end_date": recurrence_pattern.end_date}):
                logger.info(f"Recurrence pattern {recurrence_id} has expired, updating status")
                recurrence_pattern.status = RecurrenceStatus.COMPLETED
                session.add(recurrence_pattern)
                session.commit()
                return False

            # Calculate the next occurrence date
            current_due_date = task_data.get("due_date")
            if not current_due_date:
                logger.warning(f"No due date found for task {original_task_id}, cannot calculate next occurrence")
                return False

            # Convert to datetime if it's a string
            if isinstance(current_due_date, str):
                current_due_date = datetime.fromisoformat(current_due_date.replace('Z', '+00:00'))

            next_due_date = calculate_next_occurrence(
                start_date=current_due_date,
                pattern=recurrence_pattern.frequency,
                interval=recurrence_pattern.interval
            )

            # Check if the next occurrence is within the recurrence window
            if recurrence_pattern.end_date and next_due_date.date() > recurrence_pattern.end_date:
                logger.info(f"Next occurrence for task {original_task_id} exceeds end date, completing recurrence")
                recurrence_pattern.status = RecurrenceStatus.COMPLETED
                session.add(recurrence_pattern)
                session.commit()
                return False

            # Create the next occurrence task
            next_task = Task(
                title=task_data.get("title", ""),
                description=task_data.get("description"),
                user_id=user_id,
                status=TaskStatus.PENDING,
                priority=task_data.get("priority", "medium"),
                due_date=next_due_date,
                reminder_at=task_data.get("reminder_at"),  # Preserve reminder settings
                recurrence_id=recurrence_pattern.id,
                parent_task_id=original_task_id,  # Link to the original task
                completed=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            session.add(next_task)
            session.commit()
            session.refresh(next_task)

            logger.info(f"Generated next occurrence for recurring task {original_task_id}: new task {next_task.id}")
            return True

    except Exception as e:
        logger.exception(f"Error generating next occurrence for task {original_task_id}: {e}")
        return False


async def cleanup_expired_recurrences() -> int:
    """
    Clean up expired recurrence patterns that should no longer generate tasks.

    Returns:
        Number of recurrence patterns updated to COMPLETED status
    """
    try:
        from ...core.database import engine
        from ...models.recurrence import RecurrencePattern
        from ...models.enums import RecurrenceStatus

        with Session(engine) as session:
            # Find active recurrence patterns that have exceeded their end date
            current_date = date.today()
            expired_patterns = session.exec(
                select(RecurrencePattern)
                .where(
                    RecurrencePattern.status == RecurrenceStatus.ACTIVE,
                    RecurrencePattern.end_date.is_not(None),
                    RecurrencePattern.end_date < current_date
                )
            ).all()

            updated_count = 0
            for pattern in expired_patterns:
                pattern.status = RecurrenceStatus.COMPLETED
                session.add(pattern)
                updated_count += 1

            if updated_count > 0:
                session.commit()
                logger.info(f"Updated {updated_count} expired recurrence patterns to COMPLETED status")

            return updated_count

    except Exception as e:
        logger.exception(f"Error cleaning up expired recurrences: {e}")
        return 0