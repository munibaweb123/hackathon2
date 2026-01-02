"""Schema definitions for ChatKit Message model."""
from datetime import datetime
from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class MessageRole(str):
    """Enumeration for message roles."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageBase(BaseModel):
    """Base schema for Message with shared attributes."""
    thread_id: UUID
    role: MessageRole
    content: str


class MessageCreate(MessageBase):
    """Schema for creating a new Message."""
    user_id: str


class MessageUpdate(BaseModel):
    """Schema for updating an existing Message."""
    content: Optional[str] = None


class MessagePublic(MessageBase):
    """Public schema for Message with essential information."""
    id: UUID
    user_id: str
    created_at: datetime
    updated_at: datetime
    metadata: Optional[str] = None