"""Message model for ChatKit implementation."""
from datetime import datetime
from sqlmodel import Field, SQLModel
from uuid import UUID, uuid4
from typing import TYPE_CHECKING, Optional
from enum import Enum

if TYPE_CHECKING:
    from .thread import Thread  # Assuming Thread model exists


class MessageRole(str, Enum):
    """Enumeration for message roles."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageBase(SQLModel):
    """Base model for Message with shared attributes."""
    thread_id: UUID = Field(index=True, description="Reference to the thread this message belongs to")
    role: MessageRole = Field(description="Role of the message sender (user|assistant|system)")
    content: str = Field(max_length=10000, description="The text content of the message")


class Message(MessageBase, table=True):
    """Message model representing an individual message within a conversation thread."""
    __tablename__ = "chatkit_messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True, description="Unique identifier for the message")
    thread_id: UUID = Field(description="Reference to the thread this message belongs to")
    role: MessageRole = Field(description="Role of the message sender (user|assistant|system)")
    content: str = Field(max_length=10000, description="The text content of the message")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the message was created")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the message was last updated")
    message_metadata: Optional[str] = Field(None, description="Additional data about the message (e.g., widget data, action info)")


class MessagePublic(MessageBase):
    """Public model for Message without sensitive information."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    message_metadata: Optional[str] = None


class MessageCreate(MessageBase):
    """Model for creating a new Message."""
    user_id: str  # Adding user_id for message creation


class MessageUpdate(SQLModel):
    """Model for updating an existing Message."""
    content: Optional[str] = None
    message_metadata: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)