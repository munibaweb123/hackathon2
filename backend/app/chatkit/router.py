"""ChatKit router for AI Chatbot feature."""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, Any, Optional
from app.auth.dependencies import get_current_user  # Assuming this exists
from app.agents.todo_agent import run_chatbot_agent
from app.schemas.message import MessageCreate
from app.models.conversation import ConversationCreate
from app.core.database import get_session
from sqlmodel import Session
from uuid import UUID
import json


router = APIRouter(prefix="/chatkit", tags=["ChatKit"])


async def handle_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle incoming ChatKit events.

    Args:
        event: The event from ChatKit with type and payload

    Returns:
        Dictionary response for ChatKit
    """
    event_type = event.get("type")

    if event_type == "user_message":
        return await handle_user_message(event)
    elif event_type == "action_invoked":
        return await handle_action(event)
    else:
        # Log and return a no-op or simple message
        return {"type": "message", "content": "Unsupported event type."}


async def handle_user_message(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle user message events from ChatKit.

    Args:
        event: The user message event

    Returns:
        Dictionary response for the user
    """
    try:
        # Extract the user's text
        user_text = event.get("content", "")
        user_id = event.get("user_id", "")
        conversation_id = event.get("conversation_id")

        # Validate input
        if not user_text:
            raise HTTPException(status_code=400, detail="Message content is required")

        # Call the appropriate agent with the user's input
        response = await run_chatbot_agent(user_text, user_id, conversation_id)

        # Return the agent's output mapped into ChatKit's expected structure
        return {
            "type": "message",
            "content": response,
            "user_id": user_id
        }
    except Exception as e:
        # Log the error appropriately
        print(f"Error handling user message: {str(e)}")
        return {
            "type": "message",
            "content": f"Sorry, I encountered an error: {str(e)}",
            "user_id": event.get("user_id", "")
        }


async def handle_action(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle action invocation events from ChatKit.

    Args:
        event: The action invocation event

    Returns:
        Dictionary response for the action
    """
    try:
        # Extract action details
        action_name = event.get("action_name", "")
        action_params = event.get("params", {})

        # Process the action based on its name
        if action_name == "create_task":
            # Handle task creation action
            title = action_params.get("title", "")
            description = action_params.get("description", "")

            # This would typically call the appropriate MCP tool
            # For now, return a placeholder response
            return {
                "type": "action_response",
                "status": "success",
                "message": f"Task '{title}' created successfully"
            }
        else:
            return {
                "type": "action_response",
                "status": "unknown_action",
                "message": f"Unknown action: {action_name}"
            }
    except Exception as e:
        # Log the error appropriately
        print(f"Error handling action: {str(e)}")
        return {
            "type": "action_response",
            "status": "error",
            "message": f"Error processing action: {str(e)}"
        }


@router.post("/api")
async def chatkit_api(
    event: Dict[str, Any],
    current_user: str = Depends(get_current_user),
    db_session: Session = Depends(get_session)
):
    """
    Main ChatKit API endpoint to handle all events from the frontend.

    Args:
        event: The event from ChatKit frontend
        current_user: The authenticated user
        db_session: Database session

    Returns:
        Response appropriate for the event type
    """
    try:
        # Ensure the event is associated with the correct user
        event["user_id"] = current_user

        # Process the event based on its type
        result = await handle_event(event)

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/upload")
async def upload_file():
    """
    Upload endpoint for file uploads if needed.

    Returns:
        Response with upload status and file URL
    """
    # This endpoint would handle file uploads if the frontend uses direct upload strategy
    # For now, returning a placeholder response
    raise HTTPException(status_code=501, detail="File upload endpoint not implemented yet")