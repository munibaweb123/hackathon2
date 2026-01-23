"""Search service using PostgreSQL full-text search with tsvector/tsquery."""

from typing import List, Optional
from datetime import datetime
from sqlmodel import Session, select, col, or_, and_
from sqlalchemy import func, text

from ..models.task import Task
from ..models.enums import Priority, TaskStatus
from ..models.tag import Tag
from ..models.task_tag import TaskTag
import logging

logger = logging.getLogger(__name__)


class SearchService:
    """Service for searching tasks using PostgreSQL full-text search."""

    def __init__(self, session: Session):
        self.session = session

    def search_tasks(
        self,
        user_id: str,
        query: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        tag_ids: Optional[List[str]] = None,
        due_before: Optional[datetime] = None,
        due_after: Optional[datetime] = None,
        sort_by: str = "created_at",
        order: str = "desc",
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[List[Task], int]:
        """
        Search tasks with full-text search and multiple filters.

        Args:
            user_id: The user's ID
            query: Full-text search query (searches title and description)
            status: Filter by status ('pending', 'completed', 'all')
            priority: Filter by priority ('low', 'medium', 'high', 'none')
            tag_ids: Filter by tag IDs (tasks matching ANY of the tags)
            due_before: Filter tasks due before this date
            due_after: Filter tasks due after this date
            sort_by: Sort field ('created_at', 'due_date', 'priority', 'title')
            order: Sort order ('asc', 'desc')
            page: Page number (1-indexed)
            page_size: Number of results per page

        Returns:
            Tuple of (list of tasks, total count)
        """
        # Base query - filter by user
        statement = select(Task).where(Task.user_id == user_id)

        # Full-text search on title and description
        if query and query.strip():
            search_term = query.strip()
            # Use ILIKE for simple case-insensitive partial matching
            # This works well for smaller datasets and doesn't require tsvector setup
            search_pattern = f"%{search_term}%"
            statement = statement.where(
                or_(
                    Task.title.ilike(search_pattern),
                    Task.description.ilike(search_pattern)
                )
            )

        # Status filter
        if status and status != "all":
            if status == "completed":
                statement = statement.where(Task.completed == True)
            elif status == "pending":
                statement = statement.where(Task.completed == False)

        # Priority filter
        if priority and priority != "all":
            try:
                priority_enum = Priority(priority)
                statement = statement.where(Task.priority == priority_enum)
            except ValueError:
                logger.warning(f"Invalid priority value: {priority}")

        # Date range filters
        if due_after:
            statement = statement.where(Task.due_date >= due_after)
        if due_before:
            statement = statement.where(Task.due_date <= due_before)

        # Tag filter - tasks that have ANY of the specified tags
        if tag_ids and len(tag_ids) > 0:
            # Subquery to find task IDs that have any of the specified tags
            from uuid import UUID
            valid_tag_ids = []
            for tag_id in tag_ids:
                try:
                    valid_tag_ids.append(UUID(tag_id))
                except ValueError:
                    continue

            if valid_tag_ids:
                tag_subquery = (
                    select(TaskTag.task_id)
                    .where(TaskTag.tag_id.in_(valid_tag_ids))
                    .distinct()
                )
                statement = statement.where(Task.id.in_(tag_subquery))

        # Get total count before pagination
        count_statement = statement
        total = len(self.session.exec(count_statement).all())

        # Sorting
        sort_column = {
            "created_at": Task.created_at,
            "due_date": Task.due_date,
            "priority": Task.priority,
            "title": Task.title,
            "updated_at": Task.updated_at,
        }.get(sort_by, Task.created_at)

        if order == "asc":
            statement = statement.order_by(col(sort_column).asc())
        else:
            statement = statement.order_by(col(sort_column).desc())

        # Pagination
        offset = (page - 1) * page_size
        statement = statement.offset(offset).limit(page_size)

        # Execute query
        tasks = self.session.exec(statement).all()

        return list(tasks), total

    def search_with_tsvector(
        self,
        user_id: str,
        query: str,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[List[Task], int]:
        """
        Advanced full-text search using PostgreSQL tsvector.

        This method uses PostgreSQL's native full-text search capabilities
        for better performance on large datasets.

        Note: Requires search_vector column to be set up with trigger.
        """
        if not query or not query.strip():
            return [], 0

        search_term = query.strip()

        # Convert search term to tsquery format
        # Split words and join with & for AND matching
        words = search_term.split()
        tsquery_str = " & ".join(words)

        try:
            # Use raw SQL for tsvector search
            sql = text("""
                SELECT * FROM tasks
                WHERE user_id = :user_id
                AND (
                    to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, ''))
                    @@ plainto_tsquery('english', :query)
                )
                ORDER BY ts_rank(
                    to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, '')),
                    plainto_tsquery('english', :query)
                ) DESC
                LIMIT :limit OFFSET :offset
            """)

            count_sql = text("""
                SELECT COUNT(*) FROM tasks
                WHERE user_id = :user_id
                AND (
                    to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, ''))
                    @@ plainto_tsquery('english', :query)
                )
            """)

            offset = (page - 1) * page_size

            # Execute count query
            count_result = self.session.exec(count_sql, {"user_id": user_id, "query": search_term})
            total = count_result.scalar() or 0

            # Execute search query
            result = self.session.exec(sql, {
                "user_id": user_id,
                "query": search_term,
                "limit": page_size,
                "offset": offset
            })

            tasks = result.all()
            return list(tasks), total

        except Exception as e:
            logger.error(f"tsvector search failed, falling back to ILIKE: {e}")
            # Fallback to ILIKE search
            return self.search_tasks(
                user_id=user_id,
                query=query,
                page=page,
                page_size=page_size
            )


def get_search_service(session: Session) -> SearchService:
    """Factory function to create a SearchService instance."""
    return SearchService(session)
