"""Thread model for ChatKit implementation."""
from datetime import datetime
from sqlmodel import Field, SQLModel
from uuid import UUID, uuid4
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .user import User  # Assuming User model exists


class ThreadBase(SQLModel):
    """Base model for Thread with shared attributes."""
    user_id: UUID = Field(index=True, description="Owner of the thread")
    title: str = Field(max_length=200, description="Human-readable title for the thread")


class Thread(ThreadBase, table=True):
    """Thread model representing a conversation session with unique ID, created/updated timestamps, and associated user."""
    __tablename__ = "threads"

    id: UUID = Field(default_factory=uuid4, primary_key=True, description="Unique identifier for the thread")
    user_id: UUID = Field(description="Reference to the user who owns this thread")
    title: str = Field(max_length=200, description="Human-readable title for the thread (auto-generated from first message or user-provided)")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the thread was created")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the thread was last updated")
    thread_metadata: Optional[str] = Field(None, description="Additional data about the thread (e.g., conversation context, preferences)")


class ThreadPublic(ThreadBase):
    """Public model for Thread without sensitive information."""
    id: UUID
    created_at: datetime
    updated_at: datetime


class ThreadCreate(ThreadBase):
    """Model for creating a new Thread."""
    pass


class ThreadUpdate(SQLModel):
    """Model for updating an existing Thread."""
    title: Optional[str] = None
    thread_metadata: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)