"""MCP tool for adding tasks in the AI Chatbot feature."""

from sqlmodel import Session
from app.models.task import Task
from app.models.user import User
from app.core.database import get_session
from typing import Dict, Any, Optional
from datetime import datetime


def ensure_user_exists(session: Session, user_id: str) -> User:
    """
    Ensure a user exists in the database, creating a placeholder if needed.

    This handles the case where a user authenticates via Better Auth but
    hasn't been synced to the local users table yet.

    Args:
        session: Database session
        user_id: The Better Auth user ID

    Returns:
        The User object
    """
    user = session.get(User, user_id)
    if not user:
        # Create a placeholder user record
        # The email uses a placeholder format - will be updated on next full auth sync
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


def add_task(user_id: str, title: str, description: Optional[str] = None, conversation_id: Optional[str] = None, message_id: Optional[str] = None) -> Dict[str, Any]:
    """
    MCP tool to add a new task to the user's task list.

    Args:
        user_id: The ID of the user creating the task
        title: The title of the task
        description: Optional description of the task
        conversation_id: Optional conversation ID for context tracking
        message_id: Optional message ID for context tracking

    Returns:
        Dictionary with task_id, status, and title of the created task
    """
    # Get database session
    session_gen = get_session()
    session: Session = next(session_gen)

    try:
        # Ensure the user exists in the database (handles Better Auth sync)
        ensure_user_exists(session, user_id)

        # Create a new task directly with the model (TaskCreate schema doesn't include user_id)
        db_task = Task(
            title=title,
            description=description,
            completed=False,
            user_id=user_id
        )

        # Add to database
        session.add(db_task)
        session.commit()
        session.refresh(db_task)

        # If conversation and message IDs are provided, track the task reference
        if conversation_id and message_id:
            try:
                from app.services.context_service import ContextTrackingService
                context_service = ContextTrackingService(user_id=user_id)
                # Convert string IDs to appropriate types if needed
                from uuid import UUID
                conv_uuid = UUID(conversation_id) if isinstance(conversation_id, str) else conversation_id
                msg_uuid = UUID(message_id) if isinstance(message_id, str) else message_id
                context_service.track_task_reference(conv_uuid, db_task.id, msg_uuid)
            except ImportError:
                # If context service is not available, just continue without tracking
                pass
            except Exception:
                # If tracking fails, continue without tracking (don't break the main functionality)
                pass

        # Return success response
        return {
            "task_id": db_task.id,
            "status": "created",
            "title": db_task.title
        }
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


# Example usage:
# result = add_task(user_id="user123", title="Buy groceries", description="Milk, eggs, bread")
# print(result)  # {'task_id': 1, 'status': 'created', 'title': 'Buy groceries'}