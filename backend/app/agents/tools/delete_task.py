"""MCP tool for deleting tasks in the AI Chatbot feature."""

from sqlmodel import Session, select
from app.models.task import Task
from app.core.database import get_session
from typing import Dict, Any
from uuid import UUID


def delete_task(user_id: str, task_id: int) -> Dict[str, Any]:
    """
    MCP tool to remove a task from the user's task list.

    Args:
        user_id: The ID of the user who owns the task
        task_id: The ID of the task to delete

    Returns:
        Dictionary with task_id, status, and title of the deleted task
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