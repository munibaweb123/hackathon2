# Quickstart: Better Auth + FastAPI JWT Integration

## Setup Overview

This guide explains how to set up JWT-based authentication between Better Auth frontend and FastAPI backend for secure task management.

## Prerequisites

- Node.js 18+ for frontend
- Python 3.13+ for backend
- Better Auth configured in Next.js frontend
- FastAPI backend running

## Environment Variables

Set these environment variables in both frontend and backend:

```bash
BETTER_AUTH_SECRET=your-super-secret-jwt-key-here
```

## Frontend Setup

1. Configure Better Auth with JWT plugin:

```typescript
// src/services/auth/better-auth-config.ts
import { betterAuth } from "better-auth";
import { jwt } from "better-auth/plugins";

export const auth = betterAuth({
  secret: process.env.BETTER_AUTH_SECRET,
  plugins: [
    jwt({
      secret: process.env.BETTER_AUTH_SECRET,
    }),
  ],
});
```

2. Update API client to include JWT tokens:

```typescript
// src/services/auth/api-client.ts
const makeAuthenticatedRequest = async (url: string, options = {}) => {
  const token = await getJWTToken(); // Get token from Better Auth

  return fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${token}`,
    },
  });
};
```

## Backend Setup

1. Create JWT middleware:

```python
# backend/src/auth/middleware.py
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

security = HTTPBearer()

async def verify_jwt_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            settings.BETTER_AUTH_SECRET,
            algorithms=["HS256"]
        )
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

2. Apply authentication to task endpoints:

```python
# backend/src/api/task_routes.py
@app.get("/api/{user_id}/tasks")
async def get_user_tasks(
    user_id: str,
    current_user: dict = Depends(verify_jwt_token)
):
    # Ensure user can only access their own tasks
    if current_user['user_id'] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Return user's tasks
    return get_tasks_for_user(user_id)
```

## Testing the Integration

1. Start both frontend and backend services
2. Register and login a user through the frontend
3. Make API requests to task endpoints
4. Verify that:
   - Requests without tokens return 401
   - Requests with valid tokens work correctly
   - Users can only access their own tasks
   - Expired tokens return appropriate errors

## Troubleshooting

- If getting 401 errors, verify that `BETTER_AUTH_SECRET` is identical in both frontend and backend
- Check that JWT tokens are properly included in Authorization header as "Bearer [token]"
- Ensure token expiration is handled appropriately