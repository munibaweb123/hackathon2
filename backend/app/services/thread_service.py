"""Thread service for handling business logic related to conversation threads."""
from typing import List, Optional, Dict, Any
from sqlmodel import select, Session
from uuid import UUID
from datetime import datetime, timedelta
import logging
from ..models.thread import Thread
from ..core.database import engine

logger = logging.getLogger(__name__)

# Default data retention settings (T082)
DEFAULT_RETENTION_DAYS = 90  # 90 days default retention
MIN_RETENTION_DAYS = 7  # Minimum 7 days retention
MAX_RETENTION_DAYS = 365  # Maximum 1 year retention


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


# Data Retention Functions (T082)

def get_old_threads(
    retention_days: int = DEFAULT_RETENTION_DAYS,
    user_id: Optional[UUID] = None
) -> List[Thread]:
    """
    Get threads older than the specified retention period.

    Args:
        retention_days: Number of days to retain conversations (default: 90)
        user_id: Optional user ID to filter threads for a specific user

    Returns:
        List of Thread objects older than the retention period
    """
    # Validate retention days
    retention_days = max(MIN_RETENTION_DAYS, min(retention_days, MAX_RETENTION_DAYS))

    cutoff_date = datetime.utcnow() - timedelta(days=retention_days)

    with Session(engine) as session:
        statement = select(Thread).where(Thread.updated_at < cutoff_date)

        if user_id:
            statement = statement.where(Thread.user_id == user_id)

        result = session.exec(statement)
        threads = list(result.all())
        return threads


def delete_old_threads(
    retention_days: int = DEFAULT_RETENTION_DAYS,
    user_id: Optional[UUID] = None,
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Delete threads older than the specified retention period.

    Args:
        retention_days: Number of days to retain conversations (default: 90)
        user_id: Optional user ID to filter threads for a specific user
        dry_run: If True, only count threads that would be deleted without actually deleting

    Returns:
        Dictionary with deletion results:
        - deleted_count: Number of threads deleted (or would be deleted if dry_run)
        - retention_days: The retention period used
        - cutoff_date: The date used as the cutoff
        - dry_run: Whether this was a dry run
    """
    # Validate retention days
    retention_days = max(MIN_RETENTION_DAYS, min(retention_days, MAX_RETENTION_DAYS))

    cutoff_date = datetime.utcnow() - timedelta(days=retention_days)

    with Session(engine) as session:
        statement = select(Thread).where(Thread.updated_at < cutoff_date)

        if user_id:
            statement = statement.where(Thread.user_id == user_id)

        result = session.exec(statement)
        threads = list(result.all())

        deleted_count = len(threads)

        if not dry_run:
            for thread in threads:
                session.delete(thread)
            session.commit()
            logger.info(f"Deleted {deleted_count} old conversation threads (retention: {retention_days} days)")

        return {
            "deleted_count": deleted_count,
            "retention_days": retention_days,
            "cutoff_date": cutoff_date.isoformat(),
            "dry_run": dry_run
        }


def get_conversation_statistics(user_id: Optional[UUID] = None) -> Dict[str, Any]:
    """
    Get statistics about conversation threads.

    Args:
        user_id: Optional user ID to filter statistics for a specific user

    Returns:
        Dictionary with conversation statistics:
        - total_threads: Total number of threads
        - threads_last_7_days: Threads created in the last 7 days
        - threads_last_30_days: Threads created in the last 30 days
        - threads_older_than_90_days: Threads older than 90 days (candidates for deletion)
        - oldest_thread_date: Date of the oldest thread
        - newest_thread_date: Date of the newest thread
    """
    now = datetime.utcnow()

    with Session(engine) as session:
        # Build base query
        base_statement = select(Thread)
        if user_id:
            base_statement = base_statement.where(Thread.user_id == user_id)

        all_threads = list(session.exec(base_statement).all())

        if not all_threads:
            return {
                "total_threads": 0,
                "threads_last_7_days": 0,
                "threads_last_30_days": 0,
                "threads_older_than_90_days": 0,
                "oldest_thread_date": None,
                "newest_thread_date": None
            }

        # Calculate statistics
        threads_last_7 = sum(1 for t in all_threads if t.created_at > now - timedelta(days=7))
        threads_last_30 = sum(1 for t in all_threads if t.created_at > now - timedelta(days=30))
        threads_older_90 = sum(1 for t in all_threads if t.updated_at < now - timedelta(days=90))

        dates = [t.created_at for t in all_threads if t.created_at]
        oldest = min(dates) if dates else None
        newest = max(dates) if dates else None

        return {
            "total_threads": len(all_threads),
            "threads_last_7_days": threads_last_7,
            "threads_last_30_days": threads_last_30,
            "threads_older_than_90_days": threads_older_90,
            "oldest_thread_date": oldest.isoformat() if oldest else None,
            "newest_thread_date": newest.isoformat() if newest else None
        }


def archive_old_threads(
    retention_days: int = DEFAULT_RETENTION_DAYS,
    user_id: Optional[UUID] = None
) -> Dict[str, Any]:
    """
    Archive old threads by marking them with archived metadata.
    This is a softer approach than deletion that preserves data.

    Args:
        retention_days: Number of days to retain active conversations
        user_id: Optional user ID to filter threads for a specific user

    Returns:
        Dictionary with archival results
    """
    # Validate retention days
    retention_days = max(MIN_RETENTION_DAYS, min(retention_days, MAX_RETENTION_DAYS))

    cutoff_date = datetime.utcnow() - timedelta(days=retention_days)

    with Session(engine) as session:
        statement = select(Thread).where(Thread.updated_at < cutoff_date)

        if user_id:
            statement = statement.where(Thread.user_id == user_id)

        result = session.exec(statement)
        threads = list(result.all())

        archived_count = 0
        for thread in threads:
            # Mark thread as archived in metadata
            current_metadata = thread.metadata or ""
            if "archived" not in current_metadata:
                thread.metadata = f"{current_metadata}|archived:{datetime.utcnow().isoformat()}"
                session.add(thread)
                archived_count += 1

        session.commit()
        logger.info(f"Archived {archived_count} old conversation threads (retention: {retention_days} days)")

        return {
            "archived_count": archived_count,
            "retention_days": retention_days,
            "cutoff_date": cutoff_date.isoformat()
        }
