"""TaskTag junction model for many-to-many relationship between tasks and tags."""

from typing import Optional, TYPE_CHECKING
from uuid import UUID
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .task import Task
    from .tag import Tag


class TaskTag(SQLModel, table=True):
    """Junction table for task-tag many-to-many relationship."""

    __tablename__ = "task_tags"

    task_id: int = Field(foreign_key="tasks.id", primary_key=True, nullable=False)
    tag_id: UUID = Field(foreign_key="tags.id", primary_key=True, nullable=False)

    # Relationships
    task: Optional["Task"] = Relationship(back_populates="task_tags")
    tag: Optional["Tag"] = Relationship(back_populates="task_tags")
