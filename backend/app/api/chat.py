"""Chat API endpoints for AI Chatbot feature."""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.agents.core.todo_agent import run_chatbot_agent


router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/{user_id}")
async def chat_with_bot(
    user_id: str,
    message_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Send message to AI chatbot and get response.

    Args:
        user_id: User identifier
        message_data: Message data containing the user's natural language message and optional conversation_id
        current_user: Authenticated user

    Returns:
        AI assistant response with conversation ID and tool calls
    """
    # Verify that the user_id matches the authenticated user
    # current_user might be a dict depending on the auth implementation
    current_user_id = current_user.get('user_id') if isinstance(current_user, dict) else getattr(current_user, 'id', None)
    if current_user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this user's chat")

    try:
        # Extract the actual message and conversation ID from the message data
        user_text = message_data.get("message", "")
        conversation_id = message_data.get("conversation_id", None)

        if not user_text:
            raise HTTPException(status_code=400, detail="Message content is required")

        # Process the message through the AI agent
        response = await run_chatbot_agent(
            user_text=user_text,
            user_id=user_id,
            conversation_id=conversation_id
        )

        # Return the response
        return {
            "conversation_id": conversation_id or 1,  # This should be dynamic in real implementation
            "response": response,
            "tool_calls": []  # This would be populated based on actual tool calls made
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat request: {str(e)}")


@router.get("/{user_id}/history")
async def get_chat_history(
    user_id: str,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Retrieve chat history for the user.

    Args:
        user_id: User identifier
        current_user: Authenticated user

    Returns:
        Chat history with conversations and messages
    """
    # Verify that the user_id matches the authenticated user
    # current_user might be a dict depending on the auth implementation
    current_user_id = current_user.get('user_id') if isinstance(current_user, dict) else getattr(current_user, 'id', None)
    if current_user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this user's chat history")

    # In a real implementation, this would fetch conversation history from the database
    # For now, returning an empty history
    return {
        "conversations": [],
        "messages": []
    }