"""OpenAI Agents SDK tools with @function_tool decorators for ChatKit integration."""

from agents import function_tool, RunContextWrapper
from app.chatkit.agents import AgentContext
from app.chatkit.widgets import ListView, ListViewItem, Text, Row, Col, Badge
from sqlmodel import Session, select
from app.models.task import Task
from app.models.user import User
from app.core.database import get_session
from typing import Optional
from datetime import datetime


def ensure_user_exists(session: Session, user_id: str) -> User:
    """
    Ensure a user exists in the database, creating a placeholder if needed.

    Args:
        session: Database session
        user_id: The Better Auth user ID

    Returns:
        The User object
    """
    user = session.get(User, user_id)
    if not user:
        user = User(
            id=user_id,
            email=f"{user_id}@placeholder.local",
            name="User",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        session.add(user)
        session.commit()
        session.refresh(user)
    return user


def create_task_list_widget(tasks: list[dict]) -> ListView:
    """Create a ListView widget for tasks."""

    if not tasks:
        return ListView(
            children=[
                ListViewItem(
                    children=[
                        Text(
                            value="No tasks found",
                            color="secondary",
                            italic=True
                        )
                    ]
                )
            ],
            status={"text": "Tasks (0)", "icon": "list"}
        )

    list_items = []
    for task in tasks:
        # Create a row for each task with checkbox and text
        task_children = [
            Text(
                value="☐ " if not task.get("completed", False) else "☑ ",
                size="lg"
            ),  # Simple text-based representation of checkbox
            Text(
                value=task["title"],
                size="sm",
                weight="semibold",
                lineThrough=task.get("completed", False),
                color="emphasis" if not task.get("completed", False) else "secondary"
            )
        ]

        list_items.append(
            ListViewItem(
                children=task_children,
                gap=2
            )
        )

    completed_count = sum(1 for t in tasks if t.get("completed"))
    pending_count = len(tasks) - completed_count

    return ListView(
        children=list_items,
        status={
            "text": f"Tasks ({len(tasks)}) - {pending_count} pending, {completed_count} done",
            "icon": "check-circle"
        }
    )


@function_tool
async def list_tasks(
    ctx: RunContextWrapper[AgentContext],
    status: str = "all"
) -> None:
    """List user's tasks and display in a widget.

    Args:
        status: Filter by status - 'all', 'pending', or 'completed'.
    """
    # Get user_id from request context
    user_id = ctx.context.request_context.get("user_id")

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

        # Create and stream widget
        widget = create_task_list_widget(result)
        await ctx.context.stream_widget(widget)

    finally:
        session.close()


@function_tool
async def add_task(
    ctx: RunContextWrapper[AgentContext],
    title: str,
    description: Optional[str] = None
) -> str:
    """Create a new task.

    Args:
        title: The title of the task.
        description: Optional description.
    """
    user_id = ctx.context.request_context.get("user_id")

    session_gen = get_session()
    session: Session = next(session_gen)

    try:
        # Ensure the user exists
        ensure_user_exists(session, user_id)

        # Create new task
        db_task = Task(
            title=title,
            description=description,
            completed=False,
            user_id=user_id
        )

        session.add(db_task)
        session.commit()
        session.refresh(db_task)

        return f"Created task: {db_task.title} (ID: {db_task.id})"

    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def find_task_by_title(session: Session, user_id: str, title: str) -> Optional[Task]:
    """
    Find a task by title (case-insensitive, partial match).
    Returns the best matching task or None if no match found.
    """
    # First try exact match (case-insensitive)
    query = select(Task).where(
        Task.user_id == user_id,
        Task.title.ilike(title)
    )
    task = session.exec(query).first()
    if task:
        return task

    # Try partial match (title contains the search term)
    query = select(Task).where(
        Task.user_id == user_id,
        Task.title.ilike(f"%{title}%")
    )
    tasks = session.exec(query).all()

    if len(tasks) == 1:
        return tasks[0]
    elif len(tasks) > 1:
        # Return the one with shortest title (most specific match)
        return min(tasks, key=lambda t: len(t.title))

    return None


@function_tool
async def complete_task(
    ctx: RunContextWrapper[AgentContext],
    task_id: Optional[int] = None,
    task_title: Optional[str] = None
) -> str:
    """Mark a task as complete.

    Args:
        task_id: The ID of the task to complete (optional if task_title provided).
        task_title: The title of the task to complete (optional if task_id provided).
    """
    if task_id is None and task_title is None:
        return "Please provide either a task ID or task title."

    user_id = ctx.context.request_context.get("user_id")

    session_gen = get_session()
    session: Session = next(session_gen)

    try:
        task = None

        # Find the task by ID if provided
        if task_id is not None:
            task = session.get(Task, task_id)
            if not task:
                return f"Task with ID {task_id} not found."
        # Otherwise find by title
        elif task_title is not None:
            task = find_task_by_title(session, user_id, task_title)
            if not task:
                return f"Task with title '{task_title}' not found."

        # Verify ownership
        if task.user_id != user_id:
            return f"You don't have permission to modify this task."

        # Mark as completed
        task.completed = True
        session.add(task)
        session.commit()
        session.refresh(task)

        return f"Completed task: {task.title}"

    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


@function_tool
async def delete_task(
    ctx: RunContextWrapper[AgentContext],
    task_id: Optional[int] = None,
    task_title: Optional[str] = None
) -> str:
    """Delete a task from the user's list.

    Args:
        task_id: The ID of the task to delete (optional if task_title provided).
        task_title: The title of the task to delete (optional if task_id provided).
    """
    if task_id is None and task_title is None:
        return "Please provide either a task ID or task title."

    user_id = ctx.context.request_context.get("user_id")

    session_gen = get_session()
    session: Session = next(session_gen)

    try:
        task = None

        # Find the task by ID if provided
        if task_id is not None:
            task = session.get(Task, task_id)
            if not task:
                return f"Task with ID {task_id} not found."
        # Otherwise find by title
        elif task_title is not None:
            task = find_task_by_title(session, user_id, task_title)
            if not task:
                return f"Task with title '{task_title}' not found."

        # Verify ownership
        if task.user_id != user_id:
            return f"You don't have permission to delete this task."

        deleted_title = task.title
        session.delete(task)
        session.commit()

        return f"Deleted task: {deleted_title}"

    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


@function_tool
async def update_task(
    ctx: RunContextWrapper[AgentContext],
    task_id: Optional[int] = None,
    task_title: Optional[str] = None,
    title: Optional[str] = None,
    description: Optional[str] = None
) -> str:
    """Update a task's title or description.

    Args:
        task_id: The ID of the task to update (optional if task_title provided).
        task_title: The current title of the task to find and update (optional if task_id provided).
        title: New title for the task (optional).
        description: New description for the task (optional).
    """
    if task_id is None and task_title is None:
        return "Please provide either a task ID or task title to identify the task."

    user_id = ctx.context.request_context.get("user_id")

    if not title and description is None:
        return "Please provide a title or description to update."

    session_gen = get_session()
    session: Session = next(session_gen)

    try:
        task = None

        # Find the task by ID if provided
        if task_id is not None:
            task = session.get(Task, task_id)
            if not task:
                return f"Task with ID {task_id} not found."
        # Otherwise find by title
        elif task_title is not None:
            task = find_task_by_title(session, user_id, task_title)
            if not task:
                return f"Task with title '{task_title}' not found."

        # Verify ownership
        if task.user_id != user_id:
            return f"You don't have permission to update this task."

        # Update fields
        if title:
            task.title = title
        if description is not None:
            task.description = description

        session.add(task)
        session.commit()
        session.refresh(task)

        return f"Updated task: {task.title}"

    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
