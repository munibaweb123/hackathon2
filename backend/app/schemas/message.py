"""Schema for Message model for AI Chatbot feature."""

from datetime import datetime
from pydantic import BaseModel
from uuid import UUID
from enum import Enum
from typing import List, Optional, Dict, Any


class MessageRole(str, Enum):
    """Enumeration for message roles."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageBase(BaseModel):
    """Base schema for Message with shared attributes."""
    conversation_id: UUID
    user_id: str
    role: MessageRole
    content: str


class Message(MessageBase):
    """Schema for Message response with all attributes."""
    id: UUID
    created_at: datetime
    tool_calls: Optional[str] = None
    tool_responses: Optional[str] = None
    context_references: Optional[str] = None
    sequence_number: Optional[int] = None

    class Config:
        from_attributes = True


class MessageCreate(MessageBase):
    """Schema for creating a new Message."""
    pass


class MessageUpdate(BaseModel):
    """Schema for updating an existing Message."""
    content: Optional[str] = None
    tool_calls: Optional[str] = None
    tool_responses: Optional[str] = None


class MessagePublic(MessageBase):
    """Public schema for Message without sensitive information."""
    id: UUID
    created_at: datetime
    tool_calls: Optional[str] = None
    tool_responses: Optional[str] = None