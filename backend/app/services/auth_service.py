"""Authentication service for handling Better Auth integration."""

from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any
from sqlmodel import Session, select
from fastapi import HTTPException, status, Request
import secrets
import logging
import httpx

from ..core.security import (
    create_access_token,
    create_refresh_token,
)
from ..models.user import User
from ..schemas.auth import UserRegistrationRequest, UserLoginRequest
from ..core.config import settings
from ..core.auth import verify_token as decode_jwt_token


logger = logging.getLogger(__name__)


class AuthService:
    """Service class for handling Better Auth integration."""

    @staticmethod
    async def register_user(user_data: UserRegistrationRequest, request: Request) -> Tuple[Optional[User], str]:
        """
        Register a new user through Better Auth.

        Args:
            user_data: User registration data
            request: FastAPI request object for session validation

        Returns:
            Tuple of (user object if created in backend, access token) or (None, None) if registration fails
        """
        # In this architecture, Better Auth handles registration
        # We'll validate with Better Auth and potentially create a local user record

        # Make request to Better Auth to register the user
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                cookies_dict = dict(request.cookies)

                # Make request to Better Auth registration endpoint
                response = await client.post(
                    f"{settings.BETTER_AUTH_URL}/api/auth/sign-up/email",
                    json={
                        "email": user_data.email,
                        "password": user_data.password,
                        "name": f"{user_data.first_name or ''} {user_data.last_name or ''}".strip() or user_data.email.split('@')[0]
                    },
                    cookies=cookies_dict,
                    headers={"accept": "application/json", "content-type": "application/json"}
                )

                if response.status_code != 200:
                    logger.warning(f"Better Auth registration failed: {response.text}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Registration failed"
                    )

                # After successful registration, validate the session
                session_response = await client.get(
                    f"{settings.BETTER_AUTH_URL}/api/auth/session",
                    cookies=cookies_dict,
                    headers={"accept": "application/json"}
                )

                if session_response.status_code == 200:
                    session_data = session_response.json()
                    if session_data.get("user"):
                        user_info = session_data["user"]

                        # Create a minimal local user record if needed for backend operations
                        # This is just to have a local reference; the actual user data comes from Better Auth
                        local_user = User(
                            id=user_info.get("id", ""),
                            email=user_info.get("email", user_data.email),
                            name=user_info.get("name"),
                            image=user_info.get("image"),
                            email_verified=user_info.get("emailVerified"),
                            created_at=datetime.utcnow(),
                            updated_at=datetime.utcnow()
                        )

                        # Create backend token for API access
                        access_token_data = {
                            "user_id": user_info.get("id", ""),
                            "email": user_info.get("email", user_data.email)
                        }
                        access_token = create_access_token(
                            data=access_token_data,
                            expires_delta=timedelta(hours=1)
                        )

                        return local_user, access_token
        except Exception as e:
            logger.error(f"Better Auth registration error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Registration failed"
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed"
        )

    @staticmethod
    async def authenticate_user(login_data: UserLoginRequest, request: Request) -> Tuple[Optional[User], Optional[str], Optional[str]]:
        """
        Authenticate user through Better Auth.

        Args:
            login_data: User login data
            request: FastAPI request object for session validation

        Returns:
            Tuple of (user object, access token, refresh token) or (None, None, None) if authentication fails
        """
        # Authenticate with Better Auth
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                cookies_dict = dict(request.cookies)

                # Make request to Better Auth login endpoint
                response = await client.post(
                    f"{settings.BETTER_AUTH_URL}/api/auth/sign-in/email",
                    json={
                        "email": login_data.email,
                        "password": login_data.password
                    },
                    cookies=cookies_dict,
                    headers={"accept": "application/json", "content-type": "application/json"}
                )

                if response.status_code != 200:
                    logger.info(f"Better Auth login failed: {response.text}")
                    return None, None, None

                # Validate the session after login
                session_response = await client.get(
                    f"{settings.BETTER_AUTH_URL}/api/auth/session",
                    cookies=cookies_dict,
                    headers={"accept": "application/json"}
                )

                if session_response.status_code == 200:
                    session_data = session_response.json()
                    if session_data.get("user"):
                        user_info = session_data["user"]

                        # Create a minimal local user record if needed for backend operations
                        local_user = User(
                            id=user_info.get("id", ""),
                            email=user_info.get("email", login_data.email),
                            name=user_info.get("name"),
                            image=user_info.get("image"),
                            email_verified=user_info.get("emailVerified"),
                            created_at=datetime.utcnow(),
                            updated_at=datetime.utcnow()
                        )

                        # Create backend tokens for API access
                        token_data = {
                            "user_id": user_info.get("id", ""),
                            "email": user_info.get("email", login_data.email)
                        }

                        access_token = create_access_token(
                            data=token_data,
                            expires_delta=timedelta(hours=1)
                        )

                        refresh_token = create_refresh_token(
                            data=token_data,
                            expires_delta=timedelta(days=7)
                        )

                        return local_user, access_token, refresh_token
        except Exception as e:
            logger.error(f"Better Auth authentication error: {e}")
            return None, None, None

        return None, None, None

    @staticmethod
    def verify_user_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Verify a user token from Better Auth.

        Args:
            token: User token to verify

        Returns:
            User payload if token is valid, None otherwise
        """
        payload = decode_jwt_token(token)
        return payload

    @staticmethod
    async def create_password_reset_token(email: str, request: Request) -> bool:
        """
        Initiate password reset through Better Auth.

        Args:
            email: User's email
            request: FastAPI request object for session validation

        Returns:
            True if reset token creation was initiated successfully
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                cookies_dict = dict(request.cookies)

                # Make request to Better Auth forgot password endpoint
                response = await client.post(
                    f"{settings.BETTER_AUTH_URL}/api/auth/forgot-password",
                    json={"email": email},
                    cookies=cookies_dict,
                    headers={"accept": "application/json", "content-type": "application/json"}
                )

                # Return True regardless of whether email exists for security
                return True
        except Exception as e:
            logger.error(f"Better Auth password reset error: {e}")
            return False

    @staticmethod
    async def reset_user_password(token: str, new_password: str, request: Request) -> bool:
        """
        Reset user password through Better Auth.

        Args:
            token: Password reset token
            new_password: New password
            request: FastAPI request object for session validation

        Returns:
            True if password was reset successfully
        """
        # Better Auth typically handles password reset through a flow that involves
        # sending a reset link to the user's email, so this method may need adjustment
        # based on Better Auth's specific implementation
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                cookies_dict = dict(request.cookies)

                # This is a simplified approach - Better Auth's actual implementation
                # may vary based on their reset password flow
                response = await client.post(
                    f"{settings.BETTER_AUTH_URL}/api/auth/reset-password",
                    json={
                        "token": token,
                        "newPassword": new_password
                    },
                    cookies=cookies_dict,
                    headers={"accept": "application/json", "content-type": "application/json"}
                )

                return response.status_code == 200
        except Exception as e:
            logger.error(f"Better Auth password reset error: {e}")
            return False