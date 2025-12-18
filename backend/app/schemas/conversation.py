"""Schema for Conversation model for AI Chatbot feature."""

from datetime import datetime
from pydantic import BaseModel
from uuid import UUID
from typing import List, Optional


class ConversationBase(BaseModel):
    """Base schema for Conversation with shared attributes."""
    user_id: str


class Conversation(ConversationBase):
    """Schema for Conversation response with all attributes."""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConversationCreate(ConversationBase):
    """Schema for creating a new Conversation."""
    pass


class ConversationUpdate(BaseModel):
    """Schema for updating an existing Conversation."""
    updated_at: Optional[datetime] = None


class ConversationPublic(ConversationBase):
    """Public schema for Conversation without sensitive information."""
    id: UUID
    created_at: datetime
    updated_at: datetime