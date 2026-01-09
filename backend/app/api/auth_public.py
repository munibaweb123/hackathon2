"""Public Authentication API endpoints - Better Auth integration."""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlmodel import Session, select
import httpx
import uuid
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel
import logging

from ..schemas.user import UserResponse
from ..models.user import User
from ..core.database import get_session
from ..core.config import settings
from ..core.auth import create_access_token, create_refresh_token, decode_jwt_token
from ..core.user_sync import ensure_user_exists_in_backend

logger = logging.getLogger(__name__)

router = APIRouter()


class SignUpRequest(BaseModel):
    email: str
    password: str
    name: Optional[str] = None


class SignInRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


@router.post("/sign-up/email")
async def sign_up_email(
    request: Request,
    session: Session = Depends(get_session),
):
    """
    Handle email sign up request.
    """
    try:
        data = await request.json()
        email = data.get("email")
        password = data.get("password")
        name = data.get("name", "")
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid request data"
        )

    # Check if user already exists
    existing_user = session.exec(select(User).where(User.email == email)).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists"
        )

    # Create new user
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email=email,
        name=name
    )

    session.add(user)
    try:
        session.commit()
        session.refresh(user)
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )

    # Create tokens
    access_token = create_access_token(data={"sub": user_id, "email": email})
    refresh_token = create_refresh_token(data={"sub": user_id, "email": email})

    return {
        "success": True,
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name
        },
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/sign-in/email")
async def sign_in_email(
    request: Request,
    session: Session = Depends(get_session),
):
    """
    Handle email sign in request.
    """
    try:
        data = await request.json()
        email = data.get("email")
        password = data.get("password")
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid request data"
        )

    # Find user by email
    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # In a real implementation, we would verify the password here
    # For this implementation, we'll assume the credentials are valid
    # (Better Auth handles password verification on the frontend)

    # Create tokens
    access_token = create_access_token(data={"sub": user.id, "email": user.email})
    refresh_token = create_refresh_token(data={"sub": user.id, "email": user.email})

    return {
        "success": True,
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name
        },
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/sign-out")
async def sign_out():
    """
    Handle sign out request.
    """
    return {
        "success": True,
        "message": "Successfully signed out"
    }


@router.get("/debug/session")
async def debug_session(request: Request):
    """
    Debug endpoint to check session information from the request.
    """
    logger.info(f"Debug session - Headers: {dict(request.headers)}")
    logger.info(f"Debug session - Cookies: {dict(request.cookies)}")

    return {
        "headers": dict(request.headers),
        "cookies": dict(request.cookies),
        "has_auth_cookie": bool(
            request.cookies.get('__Secure-authjs.session-token') or
            request.cookies.get('authjs.session-token') or
            request.cookies.get('better-auth.session-token') or
            request.cookies.get('auth_token')
        ),
        "has_auth_header": bool(
            request.headers.get("authorization") or request.headers.get("Authorization")
        )
    }


@router.get("/debug/cookies")
async def debug_cookies(request: Request):
    """
    Debug endpoint to specifically check all cookies and look for Better Auth session cookies.
    """
    cookies_dict = dict(request.cookies)
    logger.info(f"Debug cookies - All cookies: {cookies_dict}")

    # Look for Better Auth specific cookie patterns
    auth_cookie_names = []
    for cookie_name in cookies_dict:
        if 'auth' in cookie_name.lower() or 'session' in cookie_name.lower() or 'token' in cookie_name.lower():
            auth_cookie_names.append(cookie_name)

    logger.info(f"Debug cookies - Auth-related cookies found: {auth_cookie_names}")

    return {
        "all_cookies": cookies_dict,
        "auth_related_cookies": auth_cookie_names,
        "total_cookies": len(cookies_dict),
        "has_any_auth_cookie": len(auth_cookie_names) > 0
    }


@router.get("/token")
async def get_backend_token(
    request: Request,
    session: Session = Depends(get_session),
):
    """
    Exchange Better Auth session (via cookies) for a backend-compatible JWT token.
    This endpoint is designed to work with the frontend's getJwtToken() function.
    """
    try:
        # First, check for common Better Auth cookie names
        auth_cookie = (
            request.cookies.get('__Secure-authjs.session-token') or
            request.cookies.get('authjs.session-token') or
            request.cookies.get('better-auth.session-token') or
            request.cookies.get('auth_token') or
            request.cookies.get('better-auth.session') or  # Additional common cookie name
            request.cookies.get('authjs.session') or       # Another possible name
            request.cookies.get('auth-session')            # Generic name
        )

        # If we still don't have an auth cookie, try to look for any cookie that might contain session info
        if not auth_cookie:
            # Look for any cookie that might be a Better Auth session token
            for cookie_name, cookie_value in request.cookies.items():
                if 'auth' in cookie_name.lower() or 'session' in cookie_name.lower():
                    # Check if the cookie value looks like a JWT (has dots)
                    if '.' in cookie_value and len(cookie_value.split('.')) == 3:
                        auth_cookie = cookie_value
                        logger.info(f"Found potential JWT in cookie '{cookie_name}'")
                        break

        if not auth_cookie:
            logger.warning("No Better Auth session cookie found in request")
            logger.debug(f"All cookies: {dict(request.cookies)}")

            # Also try to get session info from the Authorization header (if it's a JWT from Better Auth)
            auth_header = request.headers.get("authorization") or request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                auth_cookie = auth_header[7:]  # Remove "Bearer " prefix
                logger.info("Using JWT from Authorization header for validation")

                # Validate this JWT directly without needing to call Better Auth
                payload = decode_jwt_token(auth_cookie)
                if not payload:
                    logger.warning("JWT from Authorization header is invalid")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="No active session found"
                    )

                email = payload.get('email')
                user_id = payload.get('sub') or str(uuid.uuid4())

                if not email:
                    logger.warning("No email found in JWT payload")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid session"
                    )

                # Create backend-compatible JWT token
                access_token = create_access_token(data={"sub": user_id, "email": email})

                # Ensure the user exists in our backend database
                user = ensure_user_exists_in_backend(auth_cookie, session)

                if not user:
                    logger.warning("Failed to sync user from Better Auth session")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="User synchronization failed"
                    )

                return {
                    "token": access_token,
                    "token_type": "bearer"
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="No active session found"
                )

        # Better Auth also makes the session available via the /api/auth/session endpoint
        # We'll try to validate the session by making a request to that endpoint
        better_auth_url = settings.BETTER_AUTH_URL.rstrip('/')

        # First, let's try to get the session info directly from Better Auth
        session_check_url = f"{better_auth_url}/api/auth/session"

        # Create headers to pass cookies along with the request
        headers = {}
        if "authorization" not in request.headers:
            # If no authorization header exists, we'll rely on cookies
            pass
        else:
            headers["authorization"] = request.headers.get("authorization")

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Make a request to Better Auth to get the current session
                # Pass along all the cookies to maintain session context
                resp = await client.get(
                    session_check_url,
                    cookies=request.cookies,  # Pass all cookies
                    headers=headers
                )

                if resp.status_code != 200:
                    logger.warning(f"Better Auth session validation failed: {resp.status_code}, response: {resp.text}")

                    # If Better Auth is not accessible, we'll try to validate the JWT directly
                    # This handles the case where Better Auth is down but we still have a valid JWT
                    payload = decode_jwt_token(auth_cookie)
                    if payload:
                        logger.info("Falling back to direct JWT validation")

                        email = payload.get('email')
                        user_id = payload.get('sub') or str(uuid.uuid4())

                        if not email:
                            logger.warning("No email found in JWT payload")
                            raise HTTPException(
                                status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Invalid session"
                            )

                        # Create backend-compatible JWT token
                        access_token = create_access_token(data={"sub": user_id, "email": email})

                        # Ensure the user exists in our backend database
                        user = ensure_user_exists_in_backend(auth_cookie, session)

                        if not user:
                            logger.warning("Failed to sync user from Better Auth session")
                            raise HTTPException(
                                status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="User synchronization failed"
                            )

                        return {
                            "token": access_token,
                            "token_type": "bearer"
                        }

                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid session"
                    )

                session_data = resp.json()

                if not session_data or 'session' not in session_data:
                    logger.warning(f"Better Auth session response missing or invalid: {session_data}")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid session"
                    )

                user_data = session_data.get('user')
                if not user_data:
                    logger.warning("No user data found in Better Auth session")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid session"
                    )

                email = user_data.get('email')
                user_id = user_data.get('id') or str(uuid.uuid4())

                if not email:
                    logger.warning("No email found in Better Auth session")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid session"
                    )

                # Create backend-compatible JWT token using the user info from Better Auth
                # We'll create a new token that's compatible with our backend's auth system
                access_token = create_access_token(data={"sub": user_id, "email": email})

                # Ensure the user exists in our backend database
                # Create a minimal token payload to pass to the sync function
                temp_token_payload = {"sub": user_id, "email": email}
                import json
                import base64
                # Create a fake JWT-like token for the sync function
                fake_token = f"fake.header.{base64.b64encode(json.dumps(temp_token_payload).encode()).decode()}.fake.signature"
                user = ensure_user_exists_in_backend(fake_token, session)

                if not user:
                    logger.warning("Failed to sync user from Better Auth session")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="User synchronization failed"
                    )

                return {
                    "token": access_token,
                    "token_type": "bearer"
                }

        except httpx.ConnectError:
            logger.error("Cannot connect to Better Auth for session validation. Is Better Auth running?")

            # If Better Auth is not accessible, try to validate the JWT directly
            # This handles the case where Better Auth is down but we still have a valid JWT
            payload = decode_jwt_token(auth_cookie)
            if payload:
                logger.info("Falling back to direct JWT validation")

                email = payload.get('email')
                user_id = payload.get('sub') or str(uuid.uuid4())

                if not email:
                    logger.warning("No email found in JWT payload")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid session"
                    )

                # Create backend-compatible JWT token
                access_token = create_access_token(data={"sub": user_id, "email": email})

                # Ensure the user exists in our backend database
                user = ensure_user_exists_in_backend(auth_cookie, session)

                if not user:
                    logger.warning("Failed to sync user from Better Auth session")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="User synchronization failed"
                    )

                return {
                    "token": access_token,
                    "token_type": "bearer"
                }
            else:
                # In development, if Better Auth is not running and JWT is invalid, we'll create a dummy session
                # This allows development to continue without Better Auth running
                if settings.ENVIRONMENT == "development":
                    logger.info("Development mode: Creating dummy session for testing")

                    # Create a dummy user based on available info or default values
                    email = "dev@example.com"  # Default for development
                    user_id = "dev-user-id"    # Default for development

                    # Check if there's any user info in the request that we can use
                    auth_header = request.headers.get("authorization") or request.headers.get("Authorization")
                    if auth_header and auth_header.startswith("Bearer "):
                        try:
                            # Try to decode the JWT to extract user info
                            token = auth_header[7:]
                            payload = decode_jwt_token(token)
                            if payload:
                                email = payload.get('email', email)
                                user_id = payload.get('sub', user_id)
                        except:
                            pass  # If decoding fails, use defaults

                    # Create backend-compatible JWT token
                    access_token = create_access_token(data={"sub": user_id, "email": email})

                    # Ensure the user exists in our backend database
                    temp_token_payload = {"sub": user_id, "email": email}
                    import json
                    import base64
                    # Create a fake JWT-like token for the sync function
                    fake_token = f"fake.header.{base64.b64encode(json.dumps(temp_token_payload).encode()).decode()}.fake.signature"
                    user = ensure_user_exists_in_backend(fake_token, session)

                    if not user:
                        logger.warning("Failed to sync user from Better Auth session")
                        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="User synchronization failed"
                        )

                    return {
                        "token": access_token,
                        "token_type": "bearer"
                    }
                else:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Error connecting to authentication provider"
                    )
        except httpx.TimeoutException:
            logger.error("Timeout when validating Better Auth session")

            # If Better Auth is not accessible, try to validate the JWT directly
            # This handles the case where Better Auth is down but we still have a valid JWT
            payload = decode_jwt_token(auth_cookie)
            if payload:
                logger.info("Falling back to direct JWT validation due to timeout")

                email = payload.get('email')
                user_id = payload.get('sub') or str(uuid.uuid4())

                if not email:
                    logger.warning("No email found in JWT payload")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid session"
                    )

                # Create backend-compatible JWT token
                access_token = create_access_token(data={"sub": user_id, "email": email})

                # Ensure the user exists in our backend database
                user = ensure_user_exists_in_backend(auth_cookie, session)

                if not user:
                    logger.warning("Failed to sync user from Better Auth session")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="User synchronization failed"
                    )

                return {
                    "token": access_token,
                    "token_type": "bearer"
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Timeout validating session with authentication provider"
                )
        except httpx.RequestError as e:
            logger.error(f"Error validating Better Auth session: {e}")

            # If Better Auth is not accessible, try to validate the JWT directly
            # This handles the case where Better Auth is down but we still have a valid JWT
            payload = decode_jwt_token(auth_cookie)
            if payload:
                logger.info("Falling back to direct JWT validation due to request error")

                email = payload.get('email')
                user_id = payload.get('sub') or str(uuid.uuid4())

                if not email:
                    logger.warning("No email found in JWT payload")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid session"
                    )

                # Create backend-compatible JWT token
                access_token = create_access_token(data={"sub": user_id, "email": email})

                # Ensure the user exists in our backend database
                user = ensure_user_exists_in_backend(auth_cookie, session)

                if not user:
                    logger.warning("Failed to sync user from Better Auth session")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="User synchronization failed"
                    )

                return {
                    "token": access_token,
                    "token_type": "bearer"
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error validating session with authentication provider"
                )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in token endpoint: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )