"""API endpoints for conversation management in AI Chatbot feature."""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from app.auth.dependencies import get_current_user
from app.models.conversation import Conversation
from app.models.message import Message
from app.core.database import get_session
from sqlmodel import Session, select
from uuid import UUID


router = APIRouter(prefix="/api", tags=["Conversations"])


@router.get("/conversations")
async def list_user_conversations(
    current_user: str = Depends(get_current_user),
    db_session: Session = Depends(get_session)
) -> List[Dict[str, Any]]:
    """
    Retrieve all conversations for the authenticated user.

    Args:
        current_user: Authenticated user ID
        db_session: Database session

    Returns:
        List of user's conversations
    """
    try:
        # Query for conversations belonging to the user
        statement = select(Conversation).where(Conversation.user_id == current_user)
        conversations = db_session.exec(statement).all()

        # Convert to dictionaries
        result = []
        for conv in conversations:
            result.append({
                "id": str(conv.id),
                "user_id": conv.user_id,
                "created_at": conv.created_at.isoformat() if conv.created_at else None,
                "updated_at": conv.updated_at.isoformat() if conv.updated_at else None
            })

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving conversations: {str(e)}")


@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: UUID,
    current_user: str = Depends(get_current_user),
    db_session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """
    Retrieve details of a specific conversation including message history.

    Args:
        conversation_id: Conversation identifier
        current_user: Authenticated user ID
        db_session: Database session

    Returns:
        Conversation details with message history
    """
    try:
        # Get the conversation
        conversation_statement = select(Conversation).where(
            Conversation.id == conversation_id
        ).where(Conversation.user_id == current_user)

        conversation = db_session.exec(conversation_statement).first()

        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # Get messages in the conversation
        message_statement = select(Message).where(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at)

        messages = db_session.exec(message_statement).all()

        # Convert to dictionaries
        message_list = []
        for msg in messages:
            message_list.append({
                "id": str(msg.id),
                "conversation_id": str(msg.conversation_id),
                "user_id": msg.user_id,
                "role": msg.role.value,
                "content": msg.content,
                "created_at": msg.created_at.isoformat() if msg.created_at else None,
                "tool_calls": msg.tool_calls,
                "tool_responses": msg.tool_responses
            })

        # Return conversation with messages
        return {
            "id": str(conversation.id),
            "user_id": conversation.user_id,
            "created_at": conversation.created_at.isoformat() if conversation.created_at else None,
            "updated_at": conversation.updated_at.isoformat() if conversation.updated_at else None,
            "messages": message_list
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving conversation: {str(e)}")