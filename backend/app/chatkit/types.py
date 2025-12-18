"""Typed helpers for ChatKit events in AI Chatbot feature."""

from pydantic import BaseModel
from typing import Dict, Any, Optional, List, Union
from uuid import UUID
from enum import Enum


class ChatEventType(str, Enum):
    """Enumeration for ChatKit event types."""
    USER_MESSAGE = "user_message"
    ACTION_INVOKED = "action_invoked"
    SYSTEM_MESSAGE = "system_message"


class UserRoleType(str, Enum):
    """Enumeration for user roles."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class UserMessageEvent(BaseModel):
    """Schema for user message events."""
    type: ChatEventType = ChatEventType.USER_MESSAGE
    user_id: str
    content: str
    conversation_id: Optional[Union[int, str]] = None
    timestamp: Optional[str] = None


class ActionInvokedEvent(BaseModel):
    """Schema for action invocation events."""
    type: ChatEventType = ChatEventType.ACTION_INVOKED
    user_id: str
    action_name: str
    params: Dict[str, Any]
    conversation_id: Optional[Union[int, str]] = None


class SystemMessageEvent(BaseModel):
    """Schema for system message events."""
    type: ChatEventType = ChatEventType.SYSTEM_MESSAGE
    content: str
    timestamp: Optional[str] = None


class ChatResponse(BaseModel):
    """Schema for ChatKit responses."""
    type: str
    content: str
    user_id: Optional[str] = None
    conversation_id: Optional[Union[int, str]] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_responses: Optional[List[Dict[str, Any]]] = None


class ErrorMessage(BaseModel):
    """Schema for error responses."""
    type: str = "error"
    content: str
    error_code: Optional[str] = None


class ActionResponse(BaseModel):
    """Schema for action responses."""
    type: str = "action_response"
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None


class ConversationState(BaseModel):
    """Schema for conversation state tracking."""
    conversation_id: Union[int, str]
    user_id: str
    context: Dict[str, Any]
    last_message_timestamp: Optional[str] = None
    active: bool = True