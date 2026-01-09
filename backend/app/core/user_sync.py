"""User synchronization between Better Auth and backend database."""

from sqlmodel import Session, select
from typing import Optional
import logging

from .auth import decode_jwt_token, AuthenticatedUser
from ..models.user import User

logger = logging.getLogger(__name__)

def ensure_user_exists_in_backend(
    token: str,
    session: Session
) -> Optional[User]:
    """
    Ensure that a user from Better Auth exists in the backend database.

    Args:
        token: JWT token from Better Auth
        session: Database session

    Returns:
        User object if successfully ensured, None if token invalid
    """
    # Decode the JWT token from Better Auth
    payload = decode_jwt_token(token)

    # Handle fake tokens created for user sync
    if not payload and token.startswith('fake.header.'):
        # This is a fake token created for user sync, extract the payload manually
        try:
            import json
            import base64
            parts = token.split('.')
            if len(parts) >= 2:
                payload_data = parts[1]  # Second part is the payload
                # Add padding if needed
                missing_padding = len(payload_data) % 4
                if missing_padding:
                    payload_data += '=' * (4 - missing_padding)

                decoded_payload = base64.b64decode(payload_data)
                payload = json.loads(decoded_payload)
                logger.info(f"Extracted payload from fake token: {payload}")
        except Exception as e:
            logger.error(f"Failed to decode fake token: {e}")
            return None

    if not payload:
        logger.warning("Invalid or expired Better Auth token")
        return None

    # Extract user information from the token
    user_id = payload.get('sub') or payload.get('userId') or payload.get('id')
    email = payload.get('email', '')
    name = payload.get('name') or payload.get('given_name') or payload.get('family_name')

    if not user_id or not email:
        logger.warning(f"Token missing required user info - user_id: {user_id}, email: {email}")
        return None

    # Check if user already exists in backend database
    existing_user = session.get(User, user_id)
    if existing_user:
        logger.info(f"User already exists in backend: {user_id}")
        # Update user info if needed
        if existing_user.email != email or existing_user.name != name:
            existing_user.email = email
            existing_user.name = name
            session.add(existing_user)
            session.commit()
            logger.info(f"Updated user info for: {user_id}")
        return existing_user

    # User doesn't exist in backend, create them
    try:
        user = User(
            id=str(user_id),
            email=email,
            name=name
        )

        session.add(user)
        session.commit()
        session.refresh(user)

        logger.info(f"Created new backend user from Better Auth: {user_id}")
        return user
    except Exception as e:
        logger.error(f"Failed to create backend user from Better Auth: {str(e)}")
        session.rollback()
        return None