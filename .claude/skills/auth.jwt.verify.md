---
description: JWT verification for Better Auth tokens in Python/FastAPI
---

## Better Auth: JWT Verification (Python)

This skill covers verifying Better Auth JWTs in Python backends, particularly with FastAPI.

### Prerequisites

- Better Auth server with JWT plugin enabled
- Python 3.9+
- Required packages:

```bash
pip install pyjwt httpx cryptography
# or
pip install pyjwt requests cryptography  # for sync version
```

### Basic JWT Verification

```python
# app/auth.py
import os
import httpx
import jwt
from dataclasses import dataclass
from typing import Optional
from fastapi import HTTPException, Header, status

BETTER_AUTH_URL = os.getenv("BETTER_AUTH_URL", "http://localhost:3000")


@dataclass
class User:
    """User data extracted from JWT."""
    id: str
    email: str
    name: Optional[str] = None


# JWKS cache
_jwks_cache: dict = {}


async def get_jwks() -> dict:
    """Fetch JWKS from Better Auth server with caching."""
    global _jwks_cache

    if not _jwks_cache:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BETTER_AUTH_URL}/.well-known/jwks.json")
            response.raise_for_status()
            _jwks_cache = response.json()

    return _jwks_cache


async def verify_token(token: str) -> User:
    """Verify JWT and extract user data."""
    try:
        # Remove Bearer prefix if present
        if token.startswith("Bearer "):
            token = token[7:]

        # Get JWKS
        jwks = await get_jwks()
        public_keys = {}

        for key in jwks.get("keys", []):
            public_keys[key["kid"]] = jwt.algorithms.RSAAlgorithm.from_jwk(key)

        # Get the key ID from the token header
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")

        if not kid or kid not in public_keys:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token key"
            )

        # Verify and decode
        payload = jwt.decode(
            token,
            public_keys[kid],
            algorithms=["RS256"],
            options={"verify_aud": False}  # Adjust based on your setup
        )

        return User(
            id=payload.get("sub"),
            email=payload.get("email"),
            name=payload.get("name"),
        )

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )


async def get_current_user(
    authorization: str = Header(..., alias="Authorization")
) -> User:
    """FastAPI dependency to get current authenticated user."""
    return await verify_token(authorization)
```

### Usage in FastAPI Routes

```python
# app/main.py
from fastapi import FastAPI, Depends
from app.auth import get_current_user, User

app = FastAPI()


@app.get("/api/profile")
async def get_profile(user: User = Depends(get_current_user)):
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
    }


@app.get("/api/tasks")
async def get_tasks(user: User = Depends(get_current_user)):
    # Fetch tasks for user.id
    return {"user_id": user.id, "tasks": []}
```

### JWKS with TTL Cache (Production)

```python
# app/auth.py - Production-ready with proper caching
import os
import time
import httpx
import jwt
from dataclasses import dataclass
from typing import Optional
from fastapi import HTTPException, Header, status

BETTER_AUTH_URL = os.getenv("BETTER_AUTH_URL", "http://localhost:3000")
JWKS_CACHE_TTL = 300  # 5 minutes


@dataclass
class JWKSCache:
    keys: dict
    expires_at: float


_cache: Optional[JWKSCache] = None


async def get_jwks() -> dict:
    """Fetch JWKS with TTL-based caching."""
    global _cache

    now = time.time()

    if _cache and now < _cache.expires_at:
        return _cache.keys

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BETTER_AUTH_URL}/.well-known/jwks.json",
            timeout=10.0
        )
        response.raise_for_status()
        jwks = response.json()

        # Build key lookup
        keys = {}
        for key in jwks.get("keys", []):
            keys[key["kid"]] = jwt.algorithms.RSAAlgorithm.from_jwk(key)

        _cache = JWKSCache(
            keys=keys,
            expires_at=now + JWKS_CACHE_TTL
        )

        return keys


def clear_jwks_cache():
    """Clear the JWKS cache (useful for key rotation)."""
    global _cache
    _cache = None


async def verify_token(token: str) -> User:
    """Verify JWT using cached JWKS."""
    try:
        if token.startswith("Bearer "):
            token = token[7:]

        public_keys = await get_jwks()

        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")

        if not kid or kid not in public_keys:
            # Try refreshing cache on key miss
            clear_jwks_cache()
            public_keys = await get_jwks()

            if kid not in public_keys:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token key"
                )

        payload = jwt.decode(
            token,
            public_keys[kid],
            algorithms=["RS256"],
            options={"verify_aud": False}
        )

        return User(
            id=payload.get("sub"),
            email=payload.get("email"),
            name=payload.get("name"),
        )

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )
```

### Session-Based Verification (Alternative)

If not using JWT mode, verify sessions via API call:

```python
# app/auth.py - Alternative using session API
import os
import httpx
from dataclasses import dataclass
from typing import Optional
from fastapi import HTTPException, Request, status

BETTER_AUTH_URL = os.getenv("BETTER_AUTH_URL", "http://localhost:3000")


@dataclass
class User:
    id: str
    email: str
    name: Optional[str] = None


async def get_current_user(request: Request) -> User:
    """Verify session by calling Better Auth API."""
    cookies = request.cookies

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BETTER_AUTH_URL}/api/auth/get-session",
            cookies=cookies,
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid session"
            )

        data = response.json()
        user_data = data.get("user", {})

        return User(
            id=user_data.get("id"),
            email=user_data.get("email"),
            name=user_data.get("name"),
        )
```

### Custom Claims Extraction

```python
@dataclass
class User:
    """User with custom claims from JWT."""
    id: str
    email: str
    name: Optional[str] = None
    role: Optional[str] = None
    organization_id: Optional[str] = None
    permissions: list[str] = None

    def __post_init__(self):
        if self.permissions is None:
            self.permissions = []


async def verify_token(token: str) -> User:
    """Verify JWT and extract user data with custom claims."""
    try:
        if token.startswith("Bearer "):
            token = token[7:]

        public_keys = await get_jwks()
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")

        if not kid or kid not in public_keys:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token key"
            )

        payload = jwt.decode(
            token,
            public_keys[kid],
            algorithms=["RS256"],
            options={"verify_aud": False}
        )

        return User(
            id=payload.get("sub"),
            email=payload.get("email"),
            name=payload.get("name"),
            role=payload.get("role"),
            organization_id=payload.get("organization_id"),
            permissions=payload.get("permissions", []),
        )

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )
```

### Role-Based Access Control

```python
from functools import wraps
from fastapi import Depends


def require_role(*allowed_roles: str):
    """Decorator/dependency to require specific roles."""
    async def role_checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{user.role}' not authorized"
            )
        return user
    return role_checker


def require_permission(*required_permissions: str):
    """Dependency to require specific permissions."""
    async def permission_checker(user: User = Depends(get_current_user)) -> User:
        missing = set(required_permissions) - set(user.permissions)
        if missing:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permissions: {missing}"
            )
        return user
    return permission_checker


# Usage
@app.get("/api/admin/users")
async def list_users(user: User = Depends(require_role("admin"))):
    return {"users": []}


@app.delete("/api/tasks/{task_id}")
async def delete_task(
    task_id: str,
    user: User = Depends(require_permission("tasks:delete"))
):
    return {"deleted": task_id}
```

### Synchronous Version (Non-Async)

```python
# app/auth_sync.py - For sync FastAPI routes or other frameworks
import os
import requests
import jwt
from dataclasses import dataclass
from typing import Optional
from fastapi import HTTPException, Header, status

BETTER_AUTH_URL = os.getenv("BETTER_AUTH_URL", "http://localhost:3000")

_jwks_cache: dict = {}


def get_jwks_sync() -> dict:
    """Fetch JWKS synchronously."""
    global _jwks_cache

    if not _jwks_cache:
        response = requests.get(
            f"{BETTER_AUTH_URL}/.well-known/jwks.json",
            timeout=10
        )
        response.raise_for_status()

        jwks = response.json()
        for key in jwks.get("keys", []):
            _jwks_cache[key["kid"]] = jwt.algorithms.RSAAlgorithm.from_jwk(key)

    return _jwks_cache


def verify_token_sync(token: str) -> User:
    """Verify JWT synchronously."""
    try:
        if token.startswith("Bearer "):
            token = token[7:]

        public_keys = get_jwks_sync()

        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")

        if not kid or kid not in public_keys:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token key"
            )

        payload = jwt.decode(
            token,
            public_keys[kid],
            algorithms=["RS256"],
            options={"verify_aud": False}
        )

        return User(
            id=payload.get("sub"),
            email=payload.get("email"),
            name=payload.get("name"),
        )

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )


def get_current_user_sync(
    authorization: str = Header(..., alias="Authorization")
) -> User:
    """FastAPI dependency for sync routes."""
    return verify_token_sync(authorization)
```

### Error Handling Patterns

```python
from enum import Enum


class AuthError(str, Enum):
    TOKEN_MISSING = "token_missing"
    TOKEN_EXPIRED = "token_expired"
    TOKEN_INVALID = "token_invalid"
    TOKEN_MALFORMED = "token_malformed"
    JWKS_UNAVAILABLE = "jwks_unavailable"


class AuthException(HTTPException):
    """Custom auth exception with error codes."""

    def __init__(self, error: AuthError, detail: str):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": error.value, "message": detail},
            headers={"WWW-Authenticate": "Bearer"},
        )


async def verify_token(token: str) -> User:
    """Verify JWT with detailed error responses."""
    if not token:
        raise AuthException(AuthError.TOKEN_MISSING, "Authorization header required")

    try:
        if token.startswith("Bearer "):
            token = token[7:]

        public_keys = await get_jwks()
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")

        if not kid or kid not in public_keys:
            raise AuthException(AuthError.TOKEN_INVALID, "Unknown signing key")

        payload = jwt.decode(
            token,
            public_keys[kid],
            algorithms=["RS256"],
            options={"verify_aud": False}
        )

        return User(
            id=payload.get("sub"),
            email=payload.get("email"),
            name=payload.get("name"),
        )

    except httpx.HTTPError:
        raise AuthException(
            AuthError.JWKS_UNAVAILABLE,
            "Unable to verify token - auth server unavailable"
        )
    except jwt.ExpiredSignatureError:
        raise AuthException(AuthError.TOKEN_EXPIRED, "Token has expired")
    except jwt.DecodeError:
        raise AuthException(AuthError.TOKEN_MALFORMED, "Token is malformed")
    except jwt.InvalidTokenError as e:
        raise AuthException(AuthError.TOKEN_INVALID, str(e))
```

### Optional Auth (Allow Unauthenticated)

```python
from typing import Optional


async def get_optional_user(
    authorization: Optional[str] = Header(None, alias="Authorization")
) -> Optional[User]:
    """Returns user if authenticated, None otherwise."""
    if not authorization:
        return None

    try:
        return await verify_token(authorization)
    except HTTPException:
        return None


# Usage
@app.get("/api/posts")
async def get_posts(user: Optional[User] = Depends(get_optional_user)):
    if user:
        # Return personalized content
        return {"posts": [], "user_id": user.id}
    else:
        # Return public content
        return {"posts": []}
```

### Environment Variables

```env
# Required
BETTER_AUTH_URL=http://localhost:3000

# Optional
JWKS_CACHE_TTL=300
```

### Testing

```python
# tests/test_auth.py
import pytest
from unittest.mock import patch, AsyncMock
from app.auth import verify_token, User


@pytest.fixture
def mock_jwks():
    return {
        "keys": [{
            "kid": "test-key",
            "kty": "RSA",
            "n": "...",
            "e": "AQAB",
        }]
    }


@pytest.mark.asyncio
async def test_verify_valid_token(mock_jwks):
    with patch("app.auth.get_jwks", new_callable=AsyncMock) as mock:
        mock.return_value = mock_jwks
        # Test with a valid test token
        # user = await verify_token("Bearer ...")
        # assert user.id == "expected_id"


@pytest.mark.asyncio
async def test_verify_expired_token():
    # Test with expired token
    pass
```

### Usage

```
/auth.jwt.verify [pattern]
```

**User Input**: $ARGUMENTS

Available patterns:
- `basic` - Basic JWT verification
- `cache` - TTL-cached JWKS
- `session` - Session-based verification
- `rbac` - Role-based access control
- `sync` - Synchronous version
- `errors` - Error handling patterns
