"""Task service for handling business logic related to tasks."""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlmodel import select, Session
from ..models.task import Task
from ..models.enums import TaskStatus
from uuid import UUID
import logging
import asyncio

from .event_publisher import get_event_publisher, TOPIC_TASK_EVENTS

logger = logging.getLogger(__name__)


def get_tasks_by_user_id(user_id: str) -> List[Task]:
    """
    Retrieve all tasks for a specific user.

    Args:
        user_id: The ID of the user whose tasks to retrieve

    Returns:
        List of Task objects belonging to the user
    """
    from ..core.database import engine
    logger.info(f"DEBUG task_service: Fetching tasks for user_id: '{user_id}'")

    # Use sync Session since we have a sync engine
    with Session(engine) as session:
        # First, let's see what user_ids exist in the tasks table
        all_tasks_stmt = select(Task)
        all_tasks = session.exec(all_tasks_stmt).all()
        logger.info(f"DEBUG task_service: Total tasks in DB: {len(all_tasks)}")
        for t in all_tasks[:5]:  # Log first 5 tasks
            logger.info(f"DEBUG task_service: Task '{t.title}' belongs to user_id: '{t.user_id}'")

        # Now query for the specific user
        statement = select(Task).where(Task.user_id == user_id)
        tasks = session.exec(statement).all()
        logger.info(f"DEBUG task_service: Found {len(tasks)} tasks for user_id '{user_id}'")
        return list(tasks)


def get_task_by_id(task_id: int, user_id: str) -> Optional[Task]:
    """
    Retrieve a specific task by its ID for a specific user.

    Args:
        task_id: The ID of the task to retrieve
        user_id: The ID of the user who owns the task

    Returns:
        Task object if found and belongs to user, None otherwise
    """
    from ..core.database import engine
    with Session(engine) as session:
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        task = session.exec(statement).first()
        return task


def create_task(title: str, description: Optional[str], user_id: str, priority: str = "medium") -> Task:
    """
    Create a new task for a user.

    Args:
        title: Title of the task
        description: Description of the task
        user_id: ID of the user creating the task
        priority: Priority level of the task (low, medium, high)

    Returns:
        Created Task object
    """
    from ..core.database import engine
    from ..models.task import Priority
    with Session(engine) as session:
        task = Task(
            title=title,
            description=description,
            user_id=user_id,
            priority=Priority(priority) if priority in ["low", "medium", "high"] else Priority.MEDIUM
        )
        session.add(task)
        session.commit()
        session.refresh(task)
        return task


def update_task(task_id: int, user_id: str, **updates) -> Optional[Task]:
    """
    Update a task for a user.

    Args:
        task_id: ID of the task to update
        user_id: ID of the user who owns the task
        **updates: Fields to update

    Returns:
        Updated Task object if successful, None if task not found
    """
    from ..core.database import engine
    with Session(engine) as session:
        # First get the task
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        task = session.exec(statement).first()

        if not task:
            return None

        # Update the task with provided fields
        for field, value in updates.items():
            if hasattr(task, field):
                setattr(task, field, value)

        session.commit()
        session.refresh(task)
        return task


def delete_task(task_id: int, user_id: str) -> bool:
    """
    Delete a task for a user.

    Args:
        task_id: ID of the task to delete
        user_id: ID of the user who owns the task

    Returns:
        True if task was deleted, False if task not found
    """
    from ..core.database import engine
    with Session(engine) as session:
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        task = session.exec(statement).first()

        if not task:
            return False

        session.delete(task)
        session.commit()
        return True


def complete_task(task_id: int, user_id: str, completed: bool = True) -> Optional[Task]:
    """
    Mark a task as completed or incomplete.

    Args:
        task_id: ID of the task to update
        user_id: ID of the user who owns the task
        completed: Whether the task is completed (default True)

    Returns:
        Updated Task object if successful, None if task not found
    """
    return update_task(task_id, user_id, completed=completed)


async def publish_task_event(
    event_type: str,
    task: Task,
    correlation_id: Optional[str] = None
) -> bool:
    """
    Publish a task event to the event bus.

    Args:
        event_type: One of 'created', 'updated', 'completed', 'deleted'
        task: The task object
        correlation_id: Optional correlation ID for tracing

    Returns:
        True if published successfully
    """
    publisher = get_event_publisher()

    task_data = {
        "title": task.title,
        "description": task.description,
        "status": task.status.value if hasattr(task, 'status') and task.status else "pending",
        "priority": task.priority.value if hasattr(task, 'priority') and task.priority else "none",
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "reminder_at": task.reminder_at.isoformat() if task.reminder_at else None,
        "tags": [],  # Tags will be added in Phase 3 (US3)
        "recurrence_id": str(task.recurrence_id) if task.recurrence_id else None,
        "parent_task_id": task.parent_task_id,
    }

    return await publisher.publish_task_event(
        event_type=event_type,
        task_id=task.id,
        user_id=task.user_id,
        task_data=task_data,
        correlation_id=correlation_id,
    )


async def publish_reminder_for_task(task: Task) -> bool:
    """
    Publish a reminder event for a task.

    Args:
        task: The task with reminder_at set

    Returns:
        True if published successfully
    """
    if not task.reminder_at or not task.due_date:
        return False

    publisher = get_event_publisher()

    return await publisher.publish_reminder_event(
        task_id=task.id,
        user_id=task.user_id,
        title=task.title,
        due_at=task.due_date,
        remind_at=task.reminder_at,
        notification_preferences={
            "in_app": True,
            "email": True,
        },
        description=task.description,
    )


def create_task_with_reminder(
    title: str,
    user_id: str,
    description: Optional[str] = None,
    priority: str = "medium",
    due_date: Optional[datetime] = None,
    reminder_at: Optional[datetime] = None,
    recurrence_pattern_id: Optional[str] = None,
    tag_ids: Optional[List[str]] = None,
) -> Task:
    """
    Create a new task with optional reminder scheduling, recurrence, and tags.

    Args:
        title: Title of the task
        user_id: ID of the user creating the task
        description: Description of the task
        priority: Priority level of the task (low, medium, high)
        due_date: Due date for the task
        reminder_at: When to send reminder notification
        recurrence_pattern_id: Optional recurrence pattern ID
        tag_ids: Optional list of tag IDs to associate with the task

    Returns:
        Created Task object
    """
    from ..core.database import engine
    from ..models.task import Priority as PriorityEnum
    from ..models.task_tag import TaskTag
    from uuid import UUID

    with Session(engine) as session:
        task = Task(
            title=title,
            description=description,
            user_id=user_id,
            priority=PriorityEnum(priority) if priority in ["low", "medium", "high", "none"] else PriorityEnum.MEDIUM,
            due_date=due_date,
            reminder_at=reminder_at,
            recurrence_id=recurrence_pattern_id,
        )
        session.add(task)
        session.commit()
        session.refresh(task)

        # Add tags to the task if provided
        if tag_ids:
            for tag_id_str in tag_ids:
                try:
                    tag_id = UUID(tag_id_str)
                    task_tag = TaskTag(task_id=task.id, tag_id=tag_id)
                    session.add(task_tag)
                except ValueError:
                    # Skip invalid UUIDs
                    continue
            session.commit()

        # Note: Event publishing should be done by the caller in an async context
        return task


def update_task_with_tags(
    task_id: int,
    user_id: str,
    **updates
) -> Optional[Task]:
    """
    Update a task and optionally update its tags.

    Args:
        task_id: ID of the task to update
        user_id: ID of the user who owns the task
        **updates: Fields to update, including optional 'tag_ids' field

    Returns:
        Updated Task object if successful, None if task not found
    """
    from ..core.database import engine
    from ..models.task_tag import TaskTag
    from uuid import UUID

    with Session(engine) as session:
        # First get the task
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        task = session.exec(statement).first()

        if not task:
            return None

        # Separate tag_ids from other updates
        tag_ids = updates.pop('tag_ids', None)

        # Update the task with provided fields
        for field, value in updates.items():
            if hasattr(task, field):
                if field == 'priority':
                    # Handle priority enum conversion
                    from ..models.task import Priority as PriorityEnum
                    if isinstance(value, str):
                        try:
                            priority_value = PriorityEnum(value)
                            setattr(task, field, priority_value)
                        except ValueError:
                            # If invalid priority, keep the original value
                            pass
                    else:
                        setattr(task, field, value)
                else:
                    setattr(task, field, value)

        session.add(task)
        session.commit()
        session.refresh(task)

        # Update tags if provided
        if tag_ids is not None:
            # First, remove all existing tags
            existing_task_tags = session.exec(
                select(TaskTag).where(TaskTag.task_id == task_id)
            ).all()
            for task_tag in existing_task_tags:
                session.delete(task_tag)

            # Add new tags
            for tag_id_str in tag_ids:
                try:
                    tag_id = UUID(tag_id_str)
                    task_tag = TaskTag(task_id=task_id, tag_id=tag_id)
                    session.add(task_tag)
                except ValueError:
                    # Skip invalid UUIDs
                    continue

            session.commit()

        return task