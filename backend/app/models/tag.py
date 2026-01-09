"""Tag model for task organization."""

from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .task import Task
    from .task_tag import TaskTag


class Tag(SQLModel, table=True):
    """User-defined label for task organization."""

    __tablename__ = "tags"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(foreign_key="users.id", nullable=False, index=True)
    name: str = Field(max_length=50, nullable=False)
    color: Optional[str] = Field(default=None, max_length=7)  # Hex color code e.g., #FF5733
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    task_tags: List["TaskTag"] = Relationship(back_populates="tag")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "user-123",
                "name": "work",
                "color": "#FF5733",
                "created_at": "2024-12-10T10:00:00Z"
            }
        }
