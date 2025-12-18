"""Message model for AI Chatbot feature."""

from datetime import datetime
from sqlmodel import Field, SQLModel
from uuid import UUID, uuid4
from enum import Enum
import json
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from .user import User  # Assuming User model exists
    from .conversation import Conversation


class MessageRole(str, Enum):
    """Enumeration for message roles."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageBase(SQLModel):
    """Base model for Message with shared attributes."""
    conversation_id: UUID = Field(index=True, description="Associated conversation ID")
    user_id: str = Field(index=True, description="Message author")
    role: MessageRole = Field(description="Role of the message author")
    content: str = Field(max_length=10000, description="Message text content")


class Message(MessageBase, table=True):
    """Message model representing individual exchanges in a conversation with the AI assistant."""
    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True, description="Unique message identifier")
    conversation_id: UUID = Field(description="Associated conversation ID")
    user_id: str = Field(description="Message author")
    role: MessageRole = Field(description="Role of the message author")
    content: str = Field(max_length=10000, description="Message text content")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Message creation time")
    tool_calls: Optional[str] = Field(None, description="JSON string of tools called by AI")
    tool_responses: Optional[str] = Field(None, description="JSON string of results from tool calls")
    context_references: Optional[str] = Field(None, description="JSON string of context references for conversation tracking")
    sequence_number: Optional[int] = Field(None, description="Sequential number in conversation")


class MessagePublic(MessageBase):
    """Public model for Message without sensitive information."""
    id: UUID
    created_at: datetime
    tool_calls: Optional[str] = None
    tool_responses: Optional[str] = None


class MessageCreate(MessageBase):
    """Model for creating a new Message."""
    pass


class MessageUpdate(SQLModel):
    """Model for updating an existing Message."""
    content: Optional[str] = None
    tool_calls: Optional[str] = None
    tool_responses: Optional[str] = None