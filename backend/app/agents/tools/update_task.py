"""MCP tool for updating tasks in the AI Chatbot feature."""

from sqlmodel import Session, select
from app.models.task import Task
from app.core.database import get_session
from typing import Dict, Any, Optional
from uuid import UUID


def update_task(
    user_id: str,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    MCP tool to modify task title or description.

    Args:
        user_id: The ID of the user who owns the task
        task_id: The ID of the task to update
        title: New title for the task (optional)
        description: New description for the task (optional)

    Returns:
        Dictionary with task_id, status, and title of the updated task
    """
    # Get database session
    session_gen = get_session()
    session: Session = next(session_gen)

    try:
        # Find the task by ID and user ID
        statement = select(Task).where(Task.id == task_id).where(Task.user_id == user_id)
        task = session.exec(statement).first()

        if not task:
            raise ValueError(f"Task with ID {task_id} not found for user {user_id}")

        # Update the task fields if provided
        if title is not None:
            task.title = title
        if description is not None:
            task.description = description

        # Commit the changes
        session.add(task)
        session.commit()
        session.refresh(task)

        # Return success response
        return {
            "task_id": task.id,
            "status": "updated",
            "title": task.title
        }
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


# Example usage:
# result = update_task(user_id="user123", task_id=1, title="Buy groceries and fruits")
# print(result)  # {'task_id': 1, 'status': 'updated', 'title': 'Buy groceries and fruits'}