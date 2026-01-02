"""Base ChatKit server interface for the todo application."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, TypeVar, Optional, AsyncIterator
from pydantic import BaseModel
from .types import ChatKitRequest, ChatKitActionRequest, ChatKitResponse, ChatKitActionResponse


# Define a type variable for context
ContextType = TypeVar('ContextType', bound=Dict[str, Any])


class StreamingResult:
    """Represents a streaming result from the ChatKit server."""

    def __init__(self, stream: AsyncIterator[Dict[str, Any]]):
        self.stream = stream

    async def __aiter__(self):
        async for item in self.stream:
            yield f"data: {item}\n\n"


class ChatKitServer(ABC):
    """Base ChatKit server interface following OpenAI ChatKit SDK patterns with proper respond() and action() methods."""

    def __init__(self):
        """Initialize the ChatKit server."""
        pass

    @abstractmethod
    async def respond(self, thread_id: str, input: str, user_id: str) -> Dict[str, Any]:
        """
        Handle user input and generate response with widgets.

        Args:
            thread_id: Unique identifier for the conversation thread
            input: User's input message
            user_id: Unique identifier for the authenticated user

        Returns:
            dict: Response containing status and any immediate data
        """
        pass

    @abstractmethod
    async def action(self, thread_id: str, action: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        Handle user interactions with widgets (button clicks, form submissions).

        Args:
            thread_id: Unique identifier for the conversation thread
            action: Action data including type and payload
            user_id: Unique identifier for the authenticated user

        Returns:
            dict: Response containing status and any immediate data
        """
        pass

    @abstractmethod
    async def process_respond_request(self, request: ChatKitRequest, user_id: str) -> ChatKitResponse:
        """
        Process a respond request from the API endpoint.

        Args:
            request: ChatKit request containing thread_id and input
            user_id: Unique identifier for the authenticated user

        Returns:
            ChatKitResponse with status and thread_id
        """
        pass

    @abstractmethod
    async def process_action_request(self, request: ChatKitActionRequest, user_id: str) -> ChatKitActionResponse:
        """
        Process an action request from the API endpoint.

        Args:
            request: ChatKit action request containing thread_id and action
            user_id: Unique identifier for the authenticated user

        Returns:
            ChatKitActionResponse with status and thread_id
        """
        pass