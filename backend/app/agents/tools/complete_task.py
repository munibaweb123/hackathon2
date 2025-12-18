"""MCP tool for completing tasks in the AI Chatbot feature."""

from sqlmodel import Session, select
from app.models.task import Task
from app.core.database import get_session
from typing import Dict, Any
from uuid import UUID


def complete_task(user_id: str, task_id: int) -> Dict[str, Any]:
    """
    MCP tool to mark a task as complete.

    Args:
        user_id: The ID of the user who owns the task
        task_id: The ID of the task to mark as complete

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

        # Update the task to mark as completed
        task.completed = True

        # Commit the changes
        session.add(task)
        session.commit()
        session.refresh(task)

        # Return success response
        return {
            "task_id": task.id,
            "status": "completed",
            "title": task.title
        }
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


# Example usage:
# result = complete_task(user_id="user123", task_id=3)
# print(result)  # {'task_id': 3, 'status': 'completed', 'title': 'Call mom'}