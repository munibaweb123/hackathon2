from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from ..database import get_db_session
from ..services.search_service import SearchService
from ..schemas.task import Task as TaskSchema
from ..auth import get_current_user
from ..models.user import User


router = APIRouter(prefix="/search", tags=["search"])


@router.get("/tasks", response_model=List[TaskSchema])
async def search_tasks(
    q: str = Query(..., min_length=1, max_length=100, description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Number of results to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Search tasks using full-text search

    Args:
        q: Search query string
        limit: Number of results to return (max 100)
        offset: Offset for pagination
        current_user: Authenticated user
        db: Database session

    Returns:
        List of matching tasks
    """
    search_service = SearchService(db)
    tasks = await search_service.search_tasks(
        query=q,
        user_id=current_user.id,
        limit=limit,
        offset=offset
    )

    return tasks