from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from ..models.task import Task
from ..schemas.task import Task as TaskSchema


class SearchService:
    """
    Service for full-text search functionality using PostgreSQL tsvector/tsquery
    """

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def search_tasks(self, query: str, user_id: str, limit: int = 20, offset: int = 0) -> List[Task]:
        """
        Search tasks using PostgreSQL full-text search

        Args:
            query: Search query string
            user_id: User ID to filter tasks
            limit: Maximum number of results to return
            offset: Offset for pagination

        Returns:
            List of matching tasks
        """
        # Convert search query to PostgreSQL tsquery format
        ts_query = func.plainto_tsquery('english', query)

        stmt = (
            select(Task)
            .where(Task.user_id == user_id)
            .where(Task.search_vector.op('@@')(ts_query))
            .order_by(
                func.ts_rank(Task.search_vector, ts_query).desc()
            )
            .limit(limit)
            .offset(offset)
        )

        result = await self.db_session.execute(stmt)
        return result.scalars().all()

    async def filter_tasks(
        self,
        user_id: str,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        tags: Optional[List[str]] = None,
        due_before: Optional[str] = None,
        due_after: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Task]:
        """
        Filter tasks by various criteria

        Args:
            user_id: User ID to filter tasks
            status: Task status to filter by
            priority: Task priority to filter by
            tags: List of tag names to filter by
            due_before: Filter tasks with due date before this date
            due_after: Filter tasks with due date after this date
            limit: Maximum number of results to return
            offset: Offset for pagination

        Returns:
            List of filtered tasks
        """
        stmt = select(Task).where(Task.user_id == user_id)

        if status:
            stmt = stmt.where(Task.status == status)

        if priority:
            stmt = stmt.where(Task.priority == priority)

        if due_before:
            from datetime import datetime
            due_before_dt = datetime.fromisoformat(due_before.replace('Z', '+00:00'))
            stmt = stmt.where(Task.due_date <= due_before_dt)

        if due_after:
            from datetime import datetime
            due_after_dt = datetime.fromisoformat(due_after.replace('Z', '+00:00'))
            stmt = stmt.where(Task.due_date >= due_after_dt)

        stmt = stmt.limit(limit).offset(offset)

        result = await self.db_session.execute(stmt)
        return result.scalars().all()

    async def sort_tasks(
        self,
        user_id: str,
        sort_field: str = "created_at",
        sort_direction: str = "asc",
        limit: int = 20,
        offset: int = 0
    ) -> List[Task]:
        """
        Sort tasks by specified field

        Args:
            user_id: User ID to filter tasks
            sort_field: Field to sort by (due_date, priority, created_at, title)
            sort_direction: Direction of sort (asc or desc)
            limit: Maximum number of results to return
            offset: Offset for pagination

        Returns:
            List of sorted tasks
        """
        stmt = select(Task).where(Task.user_id == user_id)

        # Define allowed sort fields to prevent injection
        allowed_fields = {
            "due_date": Task.due_date,
            "priority": Task.priority,
            "created_at": Task.created_at,
            "title": Task.title
        }

        if sort_field in allowed_fields:
            if sort_direction.lower() == "desc":
                stmt = stmt.order_by(allowed_fields[sort_field].desc())
            else:
                stmt = stmt.order_by(allowed_fields[sort_field])

        stmt = stmt.limit(limit).offset(offset)

        result = await self.db_session.execute(stmt)
        return result.scalars().all()