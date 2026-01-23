"""Search API endpoints for full-text search and advanced filtering."""

from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from pydantic import BaseModel

from ..core.database import get_session
from ..core.auth import get_current_user, AuthenticatedUser
from ..services.search_service import get_search_service
from ..schemas.task import TaskResponse

router = APIRouter()


class SearchResponse(BaseModel):
    """Response model for search results."""
    tasks: List[TaskResponse]
    total: int
    page: int
    page_size: int
    query: Optional[str] = None


@router.get("/search", response_model=SearchResponse)
async def search_tasks(
    q: Optional[str] = Query(None, description="Search query for title and description"),
    status: Optional[str] = Query(None, description="Filter by status: 'pending', 'completed', or 'all'"),
    priority: Optional[str] = Query(None, description="Filter by priority: 'low', 'medium', 'high', 'none', or 'all'"),
    tags: Optional[str] = Query(None, description="Comma-separated list of tag IDs to filter by"),
    due_before: Optional[datetime] = Query(None, description="Filter tasks due before this date (ISO format)"),
    due_after: Optional[datetime] = Query(None, description="Filter tasks due after this date (ISO format)"),
    sort_by: str = Query("created_at", description="Sort by: 'created_at', 'due_date', 'priority', 'title'"),
    order: str = Query("desc", description="Sort order: 'asc' or 'desc'"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Results per page"),
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> SearchResponse:
    """
    Search tasks with full-text search and advanced filtering.

    This endpoint provides comprehensive search and filter capabilities:

    - **q**: Full-text search in task title and description
    - **status**: Filter by completion status
    - **priority**: Filter by priority level
    - **tags**: Filter by one or more tags (comma-separated tag IDs)
    - **due_before/due_after**: Filter by due date range
    - **sort_by**: Sort results by various fields
    - **order**: Ascending or descending sort order

    Examples:
    - `/search?q=meeting` - Search for tasks containing "meeting"
    - `/search?status=pending&priority=high` - Get high priority pending tasks
    - `/search?due_after=2024-01-01&due_before=2024-12-31` - Tasks due in 2024
    - `/search?tags=uuid1,uuid2` - Tasks with specific tags
    """
    # Parse comma-separated tag IDs
    tag_ids = None
    if tags:
        tag_ids = [t.strip() for t in tags.split(",") if t.strip()]

    # Get search service
    search_service = get_search_service(session)

    # Perform search
    tasks, total = search_service.search_tasks(
        user_id=current_user.id,
        query=q,
        status=status,
        priority=priority,
        tag_ids=tag_ids,
        due_before=due_before,
        due_after=due_after,
        sort_by=sort_by,
        order=order,
        page=page,
        page_size=page_size,
    )

    return SearchResponse(
        tasks=[TaskResponse.model_validate(task) for task in tasks],
        total=total,
        page=page,
        page_size=page_size,
        query=q,
    )


@router.get("/search/suggestions", response_model=List[str])
async def get_search_suggestions(
    q: str = Query(..., min_length=2, description="Partial search query"),
    limit: int = Query(5, ge=1, le=10, description="Maximum number of suggestions"),
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> List[str]:
    """
    Get search suggestions based on partial query.

    Returns a list of task titles that match the partial query.
    Useful for autocomplete functionality.
    """
    from sqlmodel import select
    from ..models.task import Task

    # Search for matching task titles
    statement = (
        select(Task.title)
        .where(Task.user_id == current_user.id)
        .where(Task.title.ilike(f"%{q}%"))
        .distinct()
        .limit(limit)
    )

    results = session.exec(statement).all()
    return list(results)
