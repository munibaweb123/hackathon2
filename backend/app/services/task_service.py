"""Task service for handling business logic related to tasks."""
from typing import List, Optional
from sqlmodel import select, Session
from ..models.task import Task
from uuid import UUID
import logging

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