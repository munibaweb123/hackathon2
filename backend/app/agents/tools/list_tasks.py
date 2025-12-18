"""MCP tool for listing tasks in the AI Chatbot feature."""

from sqlmodel import Session, select
from app.models.task import Task
from app.core.database import get_session
from typing import Dict, Any, List, Optional
from uuid import UUID


def list_tasks(user_id: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    MCP tool to retrieve tasks from the user's task list.

    Args:
        user_id: The ID of the user whose tasks to retrieve
        status: Filter by status (all, pending, completed) - defaults to all

    Returns:
        Array of task objects matching the criteria
    """
    # Get database session
    session_gen = get_session()
    session: Session = next(session_gen)

    try:
        # Build query based on status filter
        query = select(Task).where(Task.user_id == user_id)

        if status:
            if status.lower() == "pending":
                query = query.where(Task.completed == False)
            elif status.lower() == "completed":
                query = query.where(Task.completed == True)
            # If status is "all" or any other value, return all tasks (no additional filter)

        # Execute query
        tasks = session.exec(query).all()

        # Convert tasks to dictionaries
        result = []
        for task in tasks:
            task_dict = {
                "id": task.id,
                "title": task.title,
                "completed": task.completed,
            }

            if task.description:
                task_dict["description"] = task.description

            result.append(task_dict)

        return result
    except Exception as e:
        raise e
    finally:
        session.close()


# Example usage:
# tasks = list_tasks(user_id="user123", status="pending")
# print(tasks)  # [{"id": 1, "title": "Buy groceries", "completed": False}, ...]