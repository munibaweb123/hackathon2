---
description: Sign in a user via Better Auth API
---

## Better Auth: Sign In

This skill authenticates a user and obtains an access token via the Better Auth API.

### Configuration

**Base URL**: `https://your-better-auth-url.com` (update in `.env` or configure via `/auth.config`)

### Endpoint Details

- **Method**: POST
- **Path**: `/auth/signin`
- **Content-Type**: application/json

### Arguments

Pass credentials: `/auth.signin <email> <password>`

**Example**: `/auth.signin user@example.com SecurePass123!`

### Request Body Schema

```json
{
  "email": "string (required)",
  "password": "string (required)",
  "rememberMe": boolean (optional, default: false)
}
```

### Execution

```bash
# Load base URL from environment or use default
BASE_URL="${BETTER_AUTH_BASE_URL:-https://your-better-auth-url.com}"

# Sign in user
curl -s -X POST "${BASE_URL}/auth/signin" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "{{EMAIL}}",
    "password": "{{PASSWORD}}",
    "rememberMe": false
  }' | jq .
```

### Expected Response

**Success (200 OK)**:
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
| 200 | Success | User authenticated, token returned |
| 400 | Bad Request | Check request body format |
| 401 | Unauthorized | Invalid email or password |
| 403 | Forbidden | Account locked or disabled |
| 404 | Not Found | Email not registered |
| 429 | Too Many Requests | Rate limited, wait and retry |
| 500 | Server Error | Retry or check backend logs |

### Token Storage

After successful sign-in, store the token for subsequent authenticated requests:

```bash
# Export token for use in other commands
export BETTER_AUTH_TOKEN="<token-from-response>"

# Or add to .env file
echo "BETTER_AUTH_TOKEN=<token-from-response>" >> .env
```

### Usage

```
/auth.signin <email> <password>
```

**User Input**: $ARGUMENTS

Parse the arguments to extract email and password, then execute the signin request.

### Security Notes

- Never log or display passwords
- Store tokens securely (not in plain text files in production)
- Use HTTPS in production
- Consider token expiration and refresh strategies
