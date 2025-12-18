"""Conversation model for AI Chatbot feature."""

from datetime import datetime
from sqlmodel import Field, SQLModel
from uuid import UUID, uuid4
import pydantic
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User  # Assuming User model exists


class ConversationBase(SQLModel):
    """Base model for Conversation with shared attributes."""
    user_id: str = Field(index=True, description="Owner of the conversation")


class Conversation(ConversationBase, table=True):
    """Conversation model representing a chat session between user and AI assistant."""
    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True, description="Unique conversation identifier")
    user_id: str = Field(description="Owner of the conversation")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Conversation creation time")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last interaction time")


class ConversationPublic(ConversationBase):
    """Public model for Conversation without sensitive information."""
    id: UUID
    created_at: datetime
    updated_at: datetime


class ConversationCreate(ConversationBase):
    """Model for creating a new Conversation."""
    pass


class ConversationUpdate(SQLModel):
    """Model for updating an existing Conversation."""
    updated_at: datetime | None = None