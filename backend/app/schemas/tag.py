"""Tag schemas for API requests/responses."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class TagCreate(BaseModel):
    """Schema for creating a new tag."""

    name: str = Field(..., min_length=1, max_length=50, description="Tag name")
    color: Optional[str] = Field(None, pattern=r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', description="Hex color code (e.g., #FF5733)")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "work",
                "color": "#3498db"
            }
        }


class TagUpdate(BaseModel):
    """Schema for updating an existing tag."""

    name: Optional[str] = Field(None, min_length=1, max_length=50, description="Tag name")
    color: Optional[str] = Field(None, pattern=r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', description="Hex color code (e.g., #FF5733)")


class TagResponse(BaseModel):
    """Schema for tag response."""

    id: str  # UUID as string
    name: str
    color: Optional[str] = None
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "work",
                "color": "#3498db",
                "user_id": "user-123",
                "created_at": "2024-12-10T10:00:00Z"
            }
        }


class TaskTagCreate(BaseModel):
    """Schema for adding a tag to a task."""

    tag_id: str  # UUID as string


class TaskTagResponse(BaseModel):
    """Schema for task-tag relationship response."""

    task_id: int
    tag_id: str  # UUID as string
    created_at: datetime

    class Config:
        from_attributes = True