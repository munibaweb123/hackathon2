"""Thread service for handling business logic related to conversation threads."""
from typing import List, Optional
from sqlmodel import select, Session
from uuid import UUID
from datetime import datetime
from ..models.thread import Thread
from ..core.database import engine


def create_thread(user_id: UUID, title: str = None) -> Thread:
    """
    Create a new conversation thread for a user.

    Args:
        user_id: The ID of the user creating the thread
        title: Optional title for the thread (auto-generated if not provided)

    Returns:
        Created Thread object
    """
    with Session(engine) as session:
        # Auto-generate title if not provided
        if not title:
            title = f"Conversation on {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"

        thread = Thread(
            user_id=user_id,
            title=title
        )
        session.add(thread)
        session.commit()
        session.refresh(thread)
        return thread


def get_thread_by_id(thread_id: UUID) -> Optional[Thread]:
    """
    Retrieve a specific thread by its ID.

    Args:
        thread_id: The ID of the thread to retrieve

    Returns:
        Thread object if found, None otherwise
    """
    with Session(engine) as session:
        statement = select(Thread).where(Thread.id == thread_id)
        result = session.exec(statement)
        thread = result.first()
        return thread


def get_threads_by_user_id(user_id: UUID) -> List[Thread]:
    """
    Retrieve all threads for a specific user.

    Args:
        user_id: The ID of the user whose threads to retrieve

    Returns:
        List of Thread objects belonging to the user
    """
    with Session(engine) as session:
        statement = select(Thread).where(Thread.user_id == user_id)
        result = session.exec(statement)
        threads = list(result.all())
        return threads


def update_thread(thread_id: UUID, **updates) -> Optional[Thread]:
    """
    Update a thread.

    Args:
        thread_id: ID of the thread to update
        **updates: Fields to update

    Returns:
        Updated Thread object if successful, None if thread not found
    """
    with Session(engine) as session:
        statement = select(Thread).where(Thread.id == thread_id)
        result = session.exec(statement)
        thread = result.first()

        if not thread:
            return None

        # Update the thread with provided fields
        for field, value in updates.items():
            if hasattr(thread, field):
                setattr(thread, field, value)

        session.commit()
        session.refresh(thread)
        return thread


def delete_thread(thread_id: UUID) -> bool:
    """
    Delete a thread.

    Args:
        thread_id: ID of the thread to delete

    Returns:
        True if thread was deleted, False if thread not found
    """
    with Session(engine) as session:
        statement = select(Thread).where(Thread.id == thread_id)
        result = session.exec(statement)
        thread = result.first()

        if not thread:
            return False

        session.delete(thread)
        session.commit()
        return True


def update_thread_title(thread_id: UUID, title: str) -> Optional[Thread]:
    """
    Update a thread's title.

    Args:
        thread_id: ID of the thread to update
        title: New title for the thread

    Returns:
        Updated Thread object if successful, None if thread not found
    """
    return update_thread(thread_id, title=title)


def update_thread_metadata(thread_id: UUID, metadata: str) -> Optional[Thread]:
    """
    Update a thread's metadata.

    Args:
        thread_id: ID of the thread to update
        metadata: New metadata for the thread

    Returns:
        Updated Thread object if successful, None if thread not found
    """
    return update_thread(thread_id, metadata=metadata)
