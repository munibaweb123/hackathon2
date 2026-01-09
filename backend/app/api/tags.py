"""Tag API endpoints - CRUD operations for tags."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from ..core.database import get_session
from ..core.auth import get_current_user, AuthenticatedUser
from ..models.tag import Tag
from ..schemas.tag import TagCreate, TagUpdate, TagResponse
from ..services.tag_service import get_tag_service

router = APIRouter()


@router.get("/tags", response_model=List[TagResponse])
async def list_tags(
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> List[TagResponse]:
    """List all tags for the authenticated user."""
    tag_service = get_tag_service(session)
    tags = tag_service.get_tags_by_user_id(current_user.id)
    return [TagResponse.from_orm(tag) for tag in tags]


@router.post("/tags", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag_data: TagCreate,
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> TagResponse:
    """Create a new tag for the authenticated user."""
    tag_service = get_tag_service(session)
    try:
        tag = tag_service.create_tag(tag_data, current_user.id)
        return TagResponse.from_orm(tag)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/tags/{tag_id}", response_model=TagResponse)
async def get_tag(
    tag_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> TagResponse:
    """Get a specific tag by ID."""
    tag_service = get_tag_service(session)
    tag = tag_service.get_tag_by_id(tag_id, current_user.id)

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )

    return TagResponse.from_orm(tag)


@router.put("/tags/{tag_id}", response_model=TagResponse)
async def update_tag(
    tag_id: str,
    tag_data: TagUpdate,
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> TagResponse:
    """Update an existing tag."""
    tag_service = get_tag_service(session)
    tag = tag_service.update_tag(tag_id, current_user.id, tag_data)

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )

    return TagResponse.from_orm(tag)


@router.delete("/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> None:
    """Delete a tag."""
    tag_service = get_tag_service(session)
    success = tag_service.delete_tag(tag_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )


@router.post("/tasks/{task_id}/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def add_tag_to_task(
    task_id: int,
    tag_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> None:
    """Add a tag to a task."""
    tag_service = get_tag_service(session)
    success = tag_service.add_tag_to_task(task_id, tag_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to add tag to task",
        )


@router.delete("/tasks/{task_id}/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_tag_from_task(
    task_id: int,
    tag_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> None:
    """Remove a tag from a task."""
    tag_service = get_tag_service(session)
    success = tag_service.remove_tag_from_task(task_id, tag_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to remove tag from task",
        )