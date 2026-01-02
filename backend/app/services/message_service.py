"""Message service for handling business logic related to conversation messages."""
from typing import List, Optional
from sqlmodel import select, Session
from uuid import UUID
from datetime import datetime, timedelta
from ..models.chatkit_message import Message
from ..core.database import engine


def get_messages_by_thread_id(thread_id: UUID, limit: int = 20, offset: int = 0) -> List[Message]:
    """
    Retrieve messages for a specific thread.

    Args:
        thread_id: The ID of the thread whose messages to retrieve
        limit: Maximum number of messages to return (default 20)
        offset: Number of messages to skip (for pagination)

    Returns:
        List of Message objects for the thread
    """
    with Session(engine) as session:
        statement = select(Message).where(Message.thread_id == thread_id).order_by(Message.created_at.desc()).offset(offset).limit(limit)
        result = session.exec(statement)
        messages = list(result.all())
        return messages


def get_recent_messages_by_thread_id(thread_id: UUID, hours: int = 24, limit: int = 20) -> List[Message]:
    """
    Retrieve recent messages for a specific thread within a time window.

    Args:
        thread_id: The ID of the thread whose messages to retrieve
        hours: Number of hours to look back (default 24)
        limit: Maximum number of messages to return (default 20)

    Returns:
        List of Message objects for the thread within the time window
    """
    since_time = datetime.utcnow() - timedelta(hours=hours)

    with Session(engine) as session:
        statement = select(Message).where(
            Message.thread_id == thread_id,
            Message.created_at >= since_time
        ).order_by(Message.created_at.desc()).limit(limit)
        result = session.exec(statement)
        messages = list(result.all())
        return messages


def create_message(content: str, thread_id: UUID, user_id: str, role: str = "user") -> Message:
    """
    Create a new message in a thread.

    Args:
        content: Content of the message
        thread_id: ID of the thread to add the message to
        user_id: ID of the user sending the message
        role: Role of the message sender (user, assistant, system)

    Returns:
        Created Message object
    """
    with Session(engine) as session:
        message = Message(
            content=content,
            thread_id=thread_id,
            user_id=user_id,
            role=role
        )
        session.add(message)
        session.commit()
        session.refresh(message)
        return message


def get_conversation_context(thread_id: UUID, limit: int = 20) -> List[Message]:
    """
    Get the most recent messages in a thread for conversation context.

    Args:
        thread_id: The ID of the thread to get context for
        limit: Maximum number of messages to return (default 20)

    Returns:
        List of Message objects ordered from newest to oldest
    """
    return get_messages_by_thread_id(thread_id, limit=limit)


def get_paginated_messages_by_thread_id(thread_id: UUID, limit: int = 20, offset: int = 0) -> List[Message]:
    """
    Retrieve messages for a specific thread with pagination support.

    Args:
        thread_id: The ID of the thread whose messages to retrieve
        limit: Maximum number of messages to return (default 20)
        offset: Number of messages to skip (for pagination)

    Returns:
        List of Message objects for the thread
    """
    return get_messages_by_thread_id(thread_id, limit=limit, offset=offset)


def delete_message(message_id: UUID) -> bool:
    """
    Delete a message by its ID.

    Args:
        message_id: ID of the message to delete

    Returns:
        True if message was deleted, False if not found
    """
    with Session(engine) as session:
        statement = select(Message).where(Message.id == message_id)
        result = session.exec(statement)
        message = result.first()

        if not message:
            return False

        session.delete(message)
        session.commit()
        return True


def update_message(message_id: UUID, **updates) -> Optional[Message]:
    """
    Update a message by its ID.

    Args:
        message_id: ID of the message to update
        **updates: Fields to update

    Returns:
        Updated Message object if successful, None if not found
    """
    with Session(engine) as session:
        statement = select(Message).where(Message.id == message_id)
        result = session.exec(statement)
        message = result.first()

        if not message:
            return None

        # Update the message with provided fields
        for field, value in updates.items():
            if hasattr(message, field):
                setattr(message, field, value)

        session.commit()
        session.refresh(message)
        return message
