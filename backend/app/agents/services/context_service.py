"""Context tracking service for AI Chatbot feature."""

from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime
from app.core.database import get_session
from app.models.message import Message
from sqlmodel import Session, select
import json


class ContextTrackingService:
    """Service to track conversation context and references for maintaining context across exchanges."""

    def __init__(self, user_id: str):
        """
        Initialize the context tracking service.

        Args:
            user_id: The ID of the current user
        """
        self.user_id = user_id

    def track_task_reference(self, conversation_id: UUID, task_id: int, message_id: UUID) -> None:
        """
        Track a reference to a specific task in the conversation.

        Args:
            conversation_id: The conversation ID
            task_id: The ID of the task being referenced
            message_id: The message ID that contains the reference
        """
        session_gen = get_session()
        session: Session = next(session_gen)

        try:
            # Get the message
            message = session.get(Message, message_id)

            if message:
                # Load existing context references or create new dict
                context_refs = {}
                if message.context_references:
                    try:
                        context_refs = json.loads(message.context_references)
                    except json.JSONDecodeError:
                        context_refs = {}

                # Add the task reference
                if "task_references" not in context_refs:
                    context_refs["task_references"] = []

                # Add the task reference with timestamp
                context_refs["task_references"].append({
                    "task_id": task_id,
                    "referenced_at": datetime.utcnow().isoformat(),
                    "message_id": str(message_id)
                })

                # Save back to the message
                message.context_references = json.dumps(context_refs)
                session.add(message)
                session.commit()
        finally:
            session.close()

    def get_recent_task_reference(self, conversation_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Get the most recently referenced task in the conversation.

        Args:
            conversation_id: The conversation ID

        Returns:
            Dictionary with task reference info or None if no recent reference
        """
        session_gen = get_session()
        session: Session = next(session_gen)

        try:
            # Get the most recent message with context references in this conversation
            statement = (
                select(Message)
                .where(Message.conversation_id == conversation_id)
                .where(Message.context_references.is_not(None))
                .order_by(Message.created_at.desc())
            )

            messages = session.exec(statement).all()

            # Look through messages to find the most recent task reference
            for message in messages:
                if message.context_references:
                    try:
                        context_refs = json.loads(message.context_references)

                        if "task_references" in context_refs and context_refs["task_references"]:
                            # Return the most recent task reference
                            return context_refs["task_references"][-1]
                    except json.JSONDecodeError:
                        continue

            return None
        finally:
            session.close()

    def get_conversation_context_window(self, conversation_id: UUID, window_size: int = 10) -> List[Dict[str, Any]]:
        """
        Get the context window for the conversation (last N exchanges).

        Args:
            conversation_id: The conversation ID
            window_size: Number of recent exchanges to return

        Returns:
            List of message dictionaries in chronological order
        """
        session_gen = get_session()
        session: Session = next(session_gen)

        try:
            # Get the most recent messages in the conversation
            statement = (
                select(Message)
                .where(Message.conversation_id == conversation_id)
                .order_by(Message.created_at.desc())
                .limit(window_size)
            )

            messages = session.exec(statement).all()

            # Convert to dictionaries and reverse to get chronological order
            result = []
            for msg in reversed(messages):
                msg_dict = {
                    "id": str(msg.id),
                    "role": msg.role.value,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat() if msg.created_at else None,
                    "context_references": msg.context_references
                }
                result.append(msg_dict)

            return result
        finally:
            session.close()

    def track_entity_reference(self, conversation_id: UUID, entity_type: str, entity_id: Any, message_id: UUID) -> None:
        """
        Track a reference to a specific entity in the conversation.

        Args:
            conversation_id: The conversation ID
            entity_type: Type of entity (e.g., "task", "user", "project")
            entity_id: The ID of the entity being referenced
            message_id: The message ID that contains the reference
        """
        session_gen = get_session()
        session: Session = next(session_gen)

        try:
            # Get the message
            message = session.get(Message, message_id)

            if message:
                # Load existing context references or create new dict
                context_refs = {}
                if message.context_references:
                    try:
                        context_refs = json.loads(message.context_references)
                    except json.JSONDecodeError:
                        context_refs = {}

                # Add the entity reference
                if f"{entity_type}_references" not in context_refs:
                    context_refs[f"{entity_type}_references"] = []

                # Add the entity reference with timestamp
                context_refs[f"{entity_type}_references"].append({
                    "entity_id": entity_id,
                    "type": entity_type,
                    "referenced_at": datetime.utcnow().isoformat(),
                    "message_id": str(message_id)
                })

                # Save back to the message
                message.context_references = json.dumps(context_refs)
                session.add(message)
                session.commit()
        finally:
            session.close()

    def update_conversation_sequence(self, message_id: UUID, sequence_number: int) -> None:
        """
        Update the sequence number for a message in the conversation.

        Args:
            message_id: The message ID to update
            sequence_number: The sequence number to assign
        """
        session_gen = get_session()
        session: Session = next(session_gen)

        try:
            # Get the message
            message = session.get(Message, message_id)

            if message:
                # Update the sequence number
                message.sequence_number = sequence_number
                session.add(message)
                session.commit()
        finally:
            session.close()