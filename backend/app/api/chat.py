"""Chat API endpoints for AI Chatbot feature with ChatKit integration."""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse, Response
from typing import Dict, Any
from app.core.auth import get_current_user, AuthenticatedUser
from app.models.user import User
from app.agents.core.todo_agent import run_chatbot_agent
from app.chatkit.server import get_chatkit_server
from app.chatkit.server_interface import StreamingResult


router = APIRouter(prefix="/chat", tags=["Chat"])


# =============================================================================
# ChatKit API Endpoint (New - Recommended)
# =============================================================================

@router.post("/chatkit")
async def chatkit_api(
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user)
) -> Response:
    """
    Main ChatKit API endpoint for streaming chat with widgets.

    This endpoint handles all ChatKit operations including:
    - Creating/managing threads
    - Processing user messages
    - Streaming assistant responses with widgets

    Args:
        request: The incoming HTTP request with ChatKit payload
        current_user: Authenticated user from JWT

    Returns:
        StreamingResponse for SSE events or JSON response
    """
    try:
        # Get user_id from authenticated user
        user_id = current_user.id
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found in token")

        # Create context with user information
        context = {
            "user_id": user_id,
            "user_info": {"email": current_user.email, "name": current_user.name},
        }

        # Get the ChatKit server instance
        server = get_chatkit_server()

        # Process the request body
        body = await request.body()

        # Process through ChatKit server
        result = await server.process(body, context=context)

        # Return appropriate response type
        if isinstance(result, StreamingResult):
            async def generate():
                async for chunk in result:
                    yield chunk

            return StreamingResponse(
                generate(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no",  # Disable nginx buffering
                }
            )

        return Response(
            content=result.json if hasattr(result, 'json') else str(result),
            media_type="application/json"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing ChatKit request: {str(e)}"
        )


@router.post("/chatkit/upload")
async def chatkit_upload(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Handle file uploads for ChatKit.

    Args:
        request: The incoming HTTP request with file data
        current_user: Authenticated user from JWT

    Returns:
        Upload result with file URL
    """
    # For now, return a placeholder - implement file upload logic as needed
    raise HTTPException(
        status_code=501,
        detail="File upload not implemented yet"
    )


# =============================================================================
# Legacy Chat API Endpoints (Backwards Compatible)
# =============================================================================

@router.post("/{user_id}")
async def chat_with_bot(
    user_id: str,
    message_data: Dict[str, Any],
    current_user: AuthenticatedUser = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Send message to AI chatbot and get response (Legacy endpoint).

    Note: Consider migrating to /chat/chatkit for widget support.

    Args:
        user_id: User identifier
        message_data: Message data containing the user's natural language message and optional conversation_id
        current_user: Authenticated user

    Returns:
        AI assistant response with conversation ID and tool calls
    """
    # Verify that the user_id matches the authenticated user
    current_user_id = current_user.id
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
    current_user: AuthenticatedUser = Depends(get_current_user)
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
    current_user_id = current_user.id
    if current_user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this user's chat history")

    # In a real implementation, this would fetch conversation history from the database
    # For now, returning an empty history
    return {
        "conversations": [],
        "messages": []
    }
