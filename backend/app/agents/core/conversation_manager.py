"""Conversation state management for AI Chatbot feature."""

from sqlmodel import Session
from app.models.conversation import Conversation, ConversationCreate
from app.models.message import Message, MessageCreate, MessageRole
from app.core.database import get_session
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime


class ConversationManager:
    """Manage conversation state and history for the AI agent."""

    def __init__(self, user_id: str):
        """
        Initialize the conversation manager.

        Args:
            user_id: The ID of the current user
        """
        self.user_id = user_id

    def get_or_create_conversation(self, conversation_id: Optional[str] = None) -> Conversation:
        """
        Get an existing conversation or create a new one.

        Args:
            conversation_id: Optional conversation ID to retrieve

        Returns:
            Conversation object
        """
        session_gen = get_session()
        session: Session = next(session_gen)

        try:
            if conversation_id:
                # Try to get existing conversation
                conversation = session.get(Conversation, conversation_id)
                if conversation and conversation.user_id == self.user_id:
                    # Update the last interaction time
                    conversation.updated_at = datetime.utcnow()
                    session.add(conversation)
                    session.commit()
                    return conversation

            # Create a new conversation
            conversation_create = ConversationCreate(user_id=self.user_id)
            db_conversation = Conversation.model_validate(conversation_create)
            session.add(db_conversation)
            session.commit()
            session.refresh(db_conversation)

            return db_conversation
        finally:
            session.close()

    def add_message_to_conversation(self, conversation_id: UUID, role: MessageRole, content: str) -> Message:
        """
        Add a message to the conversation history.

        Args:
            conversation_id: The ID of the conversation
            role: The role of the message (user, assistant, system)
            content: The content of the message

        Returns:
            Message object that was added
        """
        session_gen = get_session()
        session: Session = next(session_gen)

        try:
            # Create a new message
            message_create = MessageCreate(
                conversation_id=conversation_id,
                user_id=self.user_id,
                role=role,
                content=content
            )

            # Get the latest sequence number in the conversation
            from sqlmodel import select
            from app.models.message import Message as MessageModel

            stmt = select(MessageModel).where(
                MessageModel.conversation_id == conversation_id
            ).order_by(MessageModel.sequence_number.desc()).limit(1)

            last_message = session.exec(stmt).first()
            next_seq_num = (last_message.sequence_number + 1) if last_message else 1

            db_message = MessageModel.model_validate(message_create)
            db_message.sequence_number = next_seq_num
            session.add(db_message)
            session.commit()
            session.refresh(db_message)

            return db_message
        finally:
            session.close()

    def get_conversation_history(self, conversation_id: UUID, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve the conversation history.

        Args:
            conversation_id: The ID of the conversation
            limit: Maximum number of messages to return

        Returns:
            List of message dictionaries
        """
        session_gen = get_session()
        session: Session = next(session_gen)

        try:
            # Query for messages in the conversation, ordered by creation time
            from sqlalchemy import desc
            from sqlmodel import select

            statement = (
                select(Message)
                .where(Message.conversation_id == conversation_id)
                .order_by(desc(Message.created_at))
                .limit(limit)
            )

            messages = session.exec(statement).all()

            # Convert to dictionaries and reverse to get chronological order
            result = []
            for msg in reversed(messages):
                result.append({
                    "id": msg.id,
                    "role": msg.role.value,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat() if msg.created_at else None,
                    "tool_calls": msg.tool_calls,
                    "tool_responses": msg.tool_responses
                })

            return result
        finally:
            session.close()

    def update_conversation_context(self, conversation_id: UUID, context_data: Dict[str, Any]) -> None:
        """
        Update the conversation context with additional data.

        Args:
            conversation_id: The ID of the conversation
            context_data: Dictionary with context information
        """
        # This would typically store context in a separate context table
        # For now, we'll just update the conversation's updated_at timestamp
        session_gen = get_session()
        session: Session = next(session_gen)

        try:
            conversation = session.get(Conversation, conversation_id)
            if conversation and conversation.user_id == self.user_id:
                conversation.updated_at = datetime.utcnow()
                session.add(conversation)
                session.commit()
        finally:
            session.close()