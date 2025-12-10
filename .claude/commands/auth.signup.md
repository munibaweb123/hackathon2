---
description: Register a new user via Better Auth API
---

## Better Auth: Sign Up

This skill registers a new user account via the Better Auth API.

### Configuration

**Base URL**: `https://your-better-auth-url.com` (update in `.env` or configure via `/auth.config`)

### Endpoint Details

- **Method**: POST
- **Path**: `/auth/signup`
- **Content-Type**: application/json

### Arguments

Pass user details: `/auth.signup <email> <password> [name]`

**Example**: `/auth.signup user@example.com SecurePass123! "John Doe"`

### Request Body Schema

```json
{
  "email": "string (required)",
  "password": "string (required)",
  "name": "string (optional)",
  "metadata": {
    "source": "string (optional)"
  }
}
```

### Execution

```bash
# Load base URL from environment or use default
BASE_URL="${BETTER_AUTH_BASE_URL:-https://your-better-auth-url.com}"

# Create new user account
curl -s -X POST "${BASE_URL}/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "{{EMAIL}}",
    "password": "{{PASSWORD}}",
    "name": "{{NAME}}"
  }' | jq .
```

### Expected Response

**Success (201 Created)**:
```json
{
  "user": {
    "id": "string",
    "email": "string",
    "name": "string",
    "emailVerified": boolean,
    "createdAt": "string (ISO 8601)",
    "updatedAt": "string (ISO 8601)"
  },
  "session": {
    "id": "string",
    "userId": "string",
    "token": "string",
    "expiresAt": "string (ISO 8601)"
  }
}
```

### Error Handling

| Status Code | Meaning | Action |
|-------------|---------|--------|
| 201 | Created | User registered successfully |
| 400 | Bad Request | Check request body format |
| 409 | Conflict | Email already registered |
| 422 | Validation Error | Check email/password requirements |
| 500 | Server Error | Retry or check backend logs |

### Password Requirements

Typical requirements (verify with your backend):
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character

### Usage

```
/auth.signup <email> <password> [name]
```

**User Input**: $ARGUMENTS

Parse the arguments to extract email, password, and optional name, then execute the signup request.

### Security Notes

- Never log or display passwords
- Store returned tokens securely
- Use HTTPS in production
