"""MCP tool for deleting tasks in the AI Chatbot feature."""

from sqlmodel import Session, select
from app.models.task import Task
from app.core.database import get_session
from typing import Dict, Any, Optional, List
from uuid import UUID


def find_task_by_title(session: Session, user_id: str, title: str) -> Optional[Task]:
    """
    Find a task by title (case-insensitive, partial match).
    Returns the best matching task or None if no match found.
    """
    # First try exact match (case-insensitive)
    statement = select(Task).where(
        Task.user_id == user_id,
        Task.title.ilike(title)
    )
    task = session.exec(statement).first()
    if task:
        return task

    # Try partial match (title contains the search term)
    statement = select(Task).where(
        Task.user_id == user_id,
        Task.title.ilike(f"%{title}%")
    )
    tasks = session.exec(statement).all()

    if len(tasks) == 1:
        return tasks[0]
    elif len(tasks) > 1:
        # Return the one with shortest title (most specific match)
        return min(tasks, key=lambda t: len(t.title))

    return None


def delete_task(user_id: str, task_id: Optional[int] = None, task_title: Optional[str] = None) -> Dict[str, Any]:
    """
    MCP tool to remove a task from the user's task list.

    Args:
        user_id: The ID of the user who owns the task
        task_id: The ID of the task to delete (optional if task_title provided)
        task_title: The title of the task to delete (optional if task_id provided)

    Returns:
        Dictionary with task_id, status, and title of the deleted task
    """
    if task_id is None and task_title is None:
        raise ValueError("Either task_id or task_title must be provided")

    # Get database session
    session_gen = get_session()
    session: Session = next(session_gen)

    try:
        task = None

        # Find the task by ID if provided
        if task_id is not None:
            statement = select(Task).where(Task.id == task_id).where(Task.user_id == user_id)
            task = session.exec(statement).first()
            if not task:
                raise ValueError(f"Task with ID {task_id} not found for user {user_id}")
        # Otherwise find by title
        elif task_title is not None:
            task = find_task_by_title(session, user_id, task_title)
            if not task:
                raise ValueError(f"Task with title '{task_title}' not found for user {user_id}")

        # Delete the task
        session.delete(task)
        session.commit()

        # Return success response
        return {
            "task_id": task.id,
            "status": "deleted",
            "title": task.title
        }
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


# Example usage:
# result = delete_task(user_id="user123", task_id=2)
# print(result)  # {'task_id': 2, 'status': 'deleted', 'title': 'Old task'}