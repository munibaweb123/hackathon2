"""Cookie-based authentication for Better Auth integration."""

from typing import Optional
import httpx
from fastapi import Depends, HTTPException, status, Request
from pydantic import BaseModel
from sqlmodel import Session, select

from .config import settings
from .database import get_session
from ..models.user import User


class AuthenticatedUser(BaseModel):
    """Authenticated user data passed to endpoints."""

    id: str
    email: Optional[str] = None
    name: Optional[str] = None


async def validate_session_with_better_auth(cookies: dict[str, str]) -> dict:
    """
    Validate session by calling Better Auth's session endpoint.

    Better Auth stores session in cookies. We forward these cookies
    to the Better Auth server to validate and get user info.

    Args:
        cookies: Request cookies dictionary

    Returns:
        Session data with user info

    Raises:
        HTTPException: If session is invalid or expired
    """
    # Better Auth session cookie name - try different possible names
    session_cookie = cookies.get("better-auth.session_token") or cookies.get("session_token")

    if not session_cookie:
        # Debug: Log available cookies (only in debug mode)
        if settings.DEBUG:
            print(f"DEBUG: Available cookies: {list(cookies.keys())}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No session cookie found",
        )

    try:
        # Call Better Auth server to validate session
        # Include proper headers that might be required by Better Auth
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.BETTER_AUTH_URL}/api/auth/session",
                cookies={"better-auth.session_token": session_cookie},
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "FastAPI-Backend/1.0",
                    "Accept": "application/json",
                },
                timeout=10.0,
            )

            if settings.DEBUG:
                print(f"DEBUG: Session validation request to {settings.BETTER_AUTH_URL}/api/auth/session")
                print(f"DEBUG: Session cookie sent: {'***' if session_cookie else 'None'}")
                print(f"DEBUG: Response status: {response.status_code}")
                print(f"DEBUG: Response headers: {dict(response.headers)}")
                if response.status_code != 200:
                    print(f"DEBUG: Response content: {response.text}")

            if response.status_code != 200:
                # If the session endpoint returns 404, try the get-session endpoint that we know works
                if response.status_code == 404:
                    print("DEBUG: Session endpoint not found, trying get-session endpoint")
                    response = await client.get(
                        f"{settings.BETTER_AUTH_URL}/api/auth/get-session",
                        cookies={"better-auth.session_token": session_cookie},
                        headers={
                            "Content-Type": "application/json",
                            "User-Agent": "FastAPI-Backend/1.0",
                            "Accept": "application/json",
                        },
                        timeout=10.0,
                    )

                    print(f"DEBUG: Get-session endpoint response status: {response.status_code}")
                    if response.status_code != 200:
                        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"Invalid or expired session. Status: {response.status_code}",
                        )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=f"Invalid or expired session. Status: {response.status_code}",
                    )

            data = response.json()

            if not data or not data.get("user"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid session: no user data",
                )

            return data

    except httpx.RequestError as e:
        if settings.DEBUG:
            print(f"DEBUG: Request error during session validation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Authentication service unavailable: {str(e)}",
        )
    except Exception as e:
        if settings.DEBUG:
            print(f"DEBUG: Unexpected error during session validation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Session validation failed: {str(e)}",
        )


async def get_current_user(
    request: Request,
    session: Session = Depends(get_session),
) -> AuthenticatedUser:
    """
    Dependency to get the current authenticated user from session cookie.

    Args:
        request: FastAPI request object (to access cookies)
        session: Database session

    Returns:
        AuthenticatedUser with user data

    Raises:
        HTTPException: If session is invalid or user not found
    """
    # Get cookies from request
    cookies = dict(request.cookies)

    # Validate session with Better Auth server
    session_data = await validate_session_with_better_auth(cookies)
    user_data = session_data.get("user", {})

    user_id = user_data.get("id")
    user_email = user_data.get("email")
    user_name = user_data.get("name")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session: missing user ID",
        )

    # Get or create user in database (sync with Better Auth)
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()

    if not user:
        # Create user record if it doesn't exist (first time from Better Auth)
        user = User(
            id=user_id,
            email=user_email or "",
            name=user_name,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

    return AuthenticatedUser(
        id=user.id,
        email=user.email,
        name=user.name,
    )


def verify_user_access(user_id_from_path: str, current_user: AuthenticatedUser) -> None:
    """
    Verify that the authenticated user has access to the requested resource.

    Args:
        user_id_from_path: User ID from URL path
        current_user: Currently authenticated user

    Raises:
        HTTPException: If user doesn't have access
    """
    if user_id_from_path != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You can only access your own resources",
        )
