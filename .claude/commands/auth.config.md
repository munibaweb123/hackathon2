---
description: Configure Better Auth API connection settings
---

## Better Auth: Configuration

This skill helps configure the Better Auth API connection settings for authentication operations.

### Current Configuration

The Better Auth API uses the following environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `BETTER_AUTH_BASE_URL` | Base URL for the Auth API | `https://your-better-auth-url.com` |
| `BETTER_AUTH_TOKEN` | Current session token | (none) |

### Arguments

- `/auth.config show` - Display current configuration
- `/auth.config set baseUrl=<url>` - Set the base URL
- `/auth.config set token=<token>` - Set the current token
- `/auth.config test` - Test the connection
- `/auth.config clear` - Clear stored token

### Configuration File

Create or update `.env` file in the project root:

```bash
# Better Auth Configuration
BETTER_AUTH_BASE_URL=https://your-better-auth-url.com
BETTER_AUTH_TOKEN=your-session-token-here
```

### Setting Configuration

**Option 1: Environment Variables**

```bash
export BETTER_AUTH_BASE_URL="https://auth.example.com"
export BETTER_AUTH_TOKEN="your-token-here"
```

**Option 2: .env File**

Create/update `.env`:
```
BETTER_AUTH_BASE_URL=https://auth.example.com
BETTER_AUTH_TOKEN=your-token-here
```

### Testing Connection

```bash
# Load configuration
source .env 2>/dev/null || true
BASE_URL="${BETTER_AUTH_BASE_URL:-https://your-better-auth-url.com}"

# Test health/status endpoint (if available)
curl -s -X GET "${BASE_URL}/auth/health" | jq .

# Test token validation (if token is set)
if [ -n "$BETTER_AUTH_TOKEN" ]; then
  curl -s -X POST "${BASE_URL}/auth/validate" \
    -H "Content-Type: application/json" \
    -d "{\"token\": \"$BETTER_AUTH_TOKEN\"}" | jq .
fi
```

### API Endpoints Summary

| Skill | Method | Endpoint | Description |
|-------|--------|----------|-------------|
| `/auth.signup` | POST | `/auth/signup` | Register new user |
| `/auth.signin` | POST | `/auth/signin` | Authenticate user |
| `/auth.validateToken` | POST | `/auth/validate` | Validate session token |

### Integration with FastAPI Backend

To use authentication with the FastAPI Todo backend:

1. Sign in to get a token:
   ```
   /auth.signin user@example.com password123
   ```

2. Set the token for FastAPI requests:
   ```bash
   export FASTAPI_AUTH_TOKEN="$BETTER_AUTH_TOKEN"
   ```

3. Now FastAPI skills will use the authenticated token

### Troubleshooting

**Connection Refused**
- Verify `BETTER_AUTH_BASE_URL` is correct
- Check if the auth server is running
- Verify network/firewall settings

**401 Unauthorized**
- Invalid credentials during signin
- Check email/password are correct

**403 Forbidden**
- Account may be locked or disabled
- Contact administrator

**Token Validation Fails**
- Token may have expired
- Re-authenticate with `/auth.signin`

**CORS Errors**
- Auth server needs to allow requests from your origin
- Check CORS configuration on the auth server

### Security Best Practices

1. **Never commit tokens** - Add `.env` to `.gitignore`
2. **Use HTTPS** - Always use secure connections in production
3. **Token rotation** - Regularly refresh tokens
4. **Secure storage** - Don't store tokens in plain text files in production
5. **Monitor failures** - Log and alert on repeated auth failures

### Usage

```
/auth.config [show|test|set <key>=<value>|clear]
```

**User Input**: $ARGUMENTS

Based on the arguments:
- `show`: Display current environment variable values (mask token)
- `test`: Execute connection test to the auth server
- `set key=value`: Provide instructions to update configuration
- `clear`: Remove stored token from environment
