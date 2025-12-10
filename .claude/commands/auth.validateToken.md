---
description: Validate an authentication token via Better Auth API
---

## Better Auth: Validate Token

This skill validates an authentication token to verify it's still valid and retrieve user information.

### Configuration

**Base URL**: `https://your-better-auth-url.com` (update in `.env` or configure via `/auth.config`)

### Endpoint Details

- **Method**: POST
- **Path**: `/auth/validate`
- **Content-Type**: application/json

### Arguments

Pass the token to validate: `/auth.validateToken [token]`

If no token is provided, uses `BETTER_AUTH_TOKEN` from environment.

**Example**: `/auth.validateToken eyJhbGciOiJIUzI1NiIs...`

### Request Body Schema

```json
{
  "token": "string (required)"
}
```

### Execution

```bash
# Load base URL from environment or use default
BASE_URL="${BETTER_AUTH_BASE_URL:-https://your-better-auth-url.com}"

# Use provided token or fall back to environment variable
TOKEN="${1:-$BETTER_AUTH_TOKEN}"

# Validate token
curl -s -X POST "${BASE_URL}/auth/validate" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "{{TOKEN}}"
  }' | jq .
```

### Expected Response

**Success (200 OK) - Valid Token**:
```json
{
  "valid": true,
  "user": {
    "id": "string",
    "email": "string",
    "name": "string",
    "emailVerified": boolean
  },
  "session": {
    "id": "string",
    "expiresAt": "string (ISO 8601)"
  }
}
```

**Success (200 OK) - Invalid/Expired Token**:
```json
{
  "valid": false,
  "error": "Token expired" | "Invalid token" | "Token revoked"
}
```

### Error Handling

| Status Code | Meaning | Action |
|-------------|---------|--------|
| 200 | Success | Check `valid` field in response |
| 400 | Bad Request | Token not provided |
| 500 | Server Error | Retry or check backend logs |

### Token States

| State | `valid` | Action Required |
|-------|---------|-----------------|
| Valid | `true` | Continue using token |
| Expired | `false` | Re-authenticate with `/auth.signin` |
| Invalid | `false` | Token malformed, re-authenticate |
| Revoked | `false` | Token was invalidated, re-authenticate |

### Usage in Workflows

**Pre-request validation:**
```bash
# Check if current token is valid before making API calls
TOKEN_RESPONSE=$(curl -s -X POST "${BASE_URL}/auth/validate" \
  -H "Content-Type: application/json" \
  -d "{\"token\": \"$BETTER_AUTH_TOKEN\"}")

IS_VALID=$(echo $TOKEN_RESPONSE | jq -r '.valid')

if [ "$IS_VALID" = "true" ]; then
  echo "Token is valid, proceeding..."
else
  echo "Token invalid, please sign in again"
  # Trigger /auth.signin
fi
```

### Usage

```
/auth.validateToken [token]
```

**User Input**: $ARGUMENTS

If a token is provided in arguments, validate that token. Otherwise, validate the token from the `BETTER_AUTH_TOKEN` environment variable.

### Security Notes

- Validate tokens before sensitive operations
- Implement token refresh before expiration
- Log validation failures for security monitoring
