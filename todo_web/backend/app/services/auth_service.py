"""Authentication service for handling user authentication logic."""

from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlmodel import Session, select
from fastapi import HTTPException, status
import secrets
import logging

from ..core.security import (
    hash_password,
    verify_password,
    validate_password_strength,
    create_access_token,
    create_refresh_token,
    generate_verification_token,
    generate_reset_token
)
from ..models.user import User
from ..schemas.auth import UserRegistrationRequest, UserLoginRequest
from ..core.config import settings


logger = logging.getLogger(__name__)


class AuthService:
    """Service class for handling authentication logic."""

    @staticmethod
    def register_user(user_data: UserRegistrationRequest, db_session: Session) -> Tuple[User, str]:
        """
        Register a new user.

        Args:
            user_data: User registration data
            db_session: Database session

        Returns:
            Tuple of (created user, access token)
        """
        # Check if user with email already exists
        existing_user = db_session.exec(
            select(User).where(User.email == user_data.email)
        ).first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists"
            )

        # Check if username already exists (if provided)
        if user_data.username:
            existing_username = db_session.exec(
                select(User).where(User.username == user_data.username)
            ).first()

            if existing_username:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Username already taken"
                )

        # Validate password strength
        is_valid, message = validate_password_strength(user_data.password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )

        # Hash the password
        hashed_password = hash_password(user_data.password)

        # Generate verification token if needed
        verification_token = generate_verification_token()
        verification_expires = datetime.utcnow() + timedelta(hours=24)  # 24 hours

        # Create new user
        new_user = User(
            email=user_data.email,
            username=user_data.username,
            password_hash=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            is_verified=False,  # User needs to verify email
            verification_token=verification_token,
            verification_expires=verification_expires
        )

        db_session.add(new_user)
        db_session.commit()
        db_session.refresh(new_user)

        # Create access token for the new user
        access_token_data = {
            "user_id": new_user.id,
            "email": new_user.email
        }
        access_token = create_access_token(
            data=access_token_data,
            expires_delta=timedelta(hours=1)
        )

        return new_user, access_token

    @staticmethod
    def authenticate_user(login_data: UserLoginRequest, db_session: Session) -> Tuple[Optional[User], Optional[str], Optional[str]]:
        """
        Authenticate user with email and password.

        Args:
            login_data: User login data
            db_session: Database session

        Returns:
            Tuple of (user, access_token, refresh_token) or (None, None, None) if authentication fails
        """
        # Find user by email
        user = db_session.exec(
            select(User).where(User.email == login_data.email)
        ).first()

        if not user or not user.password_hash:
            # Don't reveal if user exists or not for security
            return None, None, None

        # Verify password
        if not verify_password(login_data.password, user.password_hash):
            return None, None, None

        # Check if account is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is deactivated"
            )

        # Update last login time
        user.last_login_at = datetime.utcnow()
        db_session.add(user)
        db_session.commit()

        # Create tokens
        token_data = {
            "user_id": user.id,
            "email": user.email
        }

        access_token = create_access_token(
            data=token_data,
            expires_delta=timedelta(hours=1)
        )

        refresh_token = create_refresh_token(
            data=token_data,
            expires_delta=timedelta(days=7)
        )

        return user, access_token, refresh_token

    @staticmethod
    def create_password_reset_token(email: str, db_session: Session) -> bool:
        """
        Create a password reset token for a user.

        Args:
            email: User's email
            db_session: Database session

        Returns:
            True if token was created successfully, False otherwise
        """
        user = db_session.exec(
            select(User).where(User.email == email)
        ).first()

        if not user:
            # For security, don't reveal if email exists
            return True  # Return True to indicate the request was processed

        # Generate reset token and expiration
        reset_token = generate_reset_token()
        reset_expires = datetime.utcnow() + timedelta(hours=1)  # 1 hour

        user.password_reset_token = reset_token
        user.password_reset_expires = reset_expires

        db_session.add(user)
        db_session.commit()

        # In a real application, send email with reset link here
        # send_password_reset_email(user.email, reset_token)

        return True

    @staticmethod
    def reset_user_password(token: str, new_password: str, db_session: Session) -> bool:
        """
        Reset user password using a reset token.

        Args:
            token: Password reset token
            new_password: New password
            db_session: Database session

        Returns:
            True if password was reset successfully, False otherwise
        """
        # Find user with the reset token
        user = db_session.exec(
            select(User).where(User.password_reset_token == token)
        ).first()

        if not user:
            return False

        # Check if token has expired
        if user.password_reset_expires and user.password_reset_expires < datetime.utcnow():
            return False

        # Validate new password strength
        is_valid, message = validate_password_strength(new_password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )

        # Hash the new password
        hashed_password = hash_password(new_password)

        # Update user password and clear reset token
        user.password_hash = hashed_password
        user.password_reset_token = None
        user.password_reset_expires = None

        db_session.add(user)
        db_session.commit()

        return True

    @staticmethod
    def verify_user_token(token: str, db_session: Session) -> Optional[User]:
        """
        Verify a user token and return the user if valid.

        Args:
            token: User token to verify
            db_session: Database session

        Returns:
            User object if token is valid, None otherwise
        """
        from ..core.auth import verify_token as decode_jwt_token

        payload = decode_jwt_token(token)
        if not payload:
            return None

        user_id = payload.get("user_id")
        if not user_id:
            return None

        user = db_session.exec(
            select(User).where(User.id == user_id)
        ).first()

        return user

    @staticmethod
    def update_user_profile(user_id: str, profile_data: dict, db_session: Session) -> Optional[User]:
        """
        Update user profile information.

        Args:
            user_id: ID of the user to update
            profile_data: Profile data to update
            db_session: Database session

        Returns:
            Updated user object or None if update failed
        """
        user = db_session.exec(
            select(User).where(User.id == user_id)
        ).first()

        if not user:
            return None

        # Check if username is being updated and if it's already taken
        if profile_data.get('username') and profile_data['username'] != user.username:
            existing_user = db_session.exec(
                select(User).where(User.username == profile_data['username'])
            ).first()

            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Username already taken"
                )

        # Update user fields
        for field, value in profile_data.items():
            if hasattr(user, field) and value is not None:
                setattr(user, field, value)

        # Update the updated_at timestamp
        user.updated_at = datetime.utcnow()

        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        return user

    @staticmethod
    def verify_email_token(token: str, db_session: Session) -> bool:
        """
        Verify an email verification token.

        Args:
            token: Email verification token
            db_session: Database session

        Returns:
            True if verification was successful, False otherwise
        """
        user = db_session.exec(
            select(User).where(User.verification_token == token)
        ).first()

        if not user:
            return False

        # Check if token has expired
        if user.verification_expires and user.verification_expires < datetime.utcnow():
            return False

        # Update user verification status
        user.is_verified = True
        user.verification_token = None
        user.verification_expires = None

        db_session.add(user)
        db_session.commit()

        return True