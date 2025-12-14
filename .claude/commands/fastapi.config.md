---
description: Configure FastAPI backend connection settings
---

## FastAPI Backend: Configuration

This skill helps configure the FastAPI backend connection settings for the Todo App.

### Current Configuration

The FastAPI backend uses the following environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `FASTAPI_BASE_URL` | Base URL for the API | `https://your-fastapi-url.com` |
| `FASTAPI_AUTH_TOKEN` | Bearer token for authentication | (none) |

### Arguments

- `/fastapi.config show` - Display current configuration
- `/fastapi.config set baseUrl=<url>` - Set the base URL
- `/fastapi.config set authToken=<token>` - Set the auth token
- `/fastapi.config test` - Test the connection

### Configuration File

Create or update `.env` file in the project root:

```bash
# FastAPI Backend Configuration
FASTAPI_BASE_URL=https://your-fastapi-url.com
FASTAPI_AUTH_TOKEN=your-bearer-token-here
```

### Setting Configuration

**Option 1: Environment Variables**

```bash
export FASTAPI_BASE_URL="https://api.example.com"
export FASTAPI_AUTH_TOKEN="your-token-here"
```

**Option 2: .env File**

Create/update `.env`:
```
FASTAPI_BASE_URL=https://api.example.com
FASTAPI_AUTH_TOKEN=your-token-here
```

### Testing Connection

```bash
# Load configuration
source .env 2>/dev/null || true
BASE_URL="${FASTAPI_BASE_URL:-https://your-fastapi-url.com}"

# Test health endpoint
curl -s -X GET "${BASE_URL}/health" | jq .

# Test todos endpoint
curl -s -X GET "${BASE_URL}/todos" \
  -H "Content-Type: application/json" \
  ${FASTAPI_AUTH_TOKEN:+-H "Authorization: Bearer $FASTAPI_AUTH_TOKEN"} | jq .
```

### API Endpoints Summary

| Skill | Method | Endpoint | Description |
|-------|--------|----------|-------------|
| `/fastapi.getTodos` | GET | `/todos` | Fetch all todos |
| `/fastapi.createTodo` | POST | `/todos` | Create new todo |
| `/fastapi.updateTodo` | PUT | `/todos/{id}` | Update existing todo |
| `/fastapi.deleteTodo` | DELETE | `/todos/{id}` | Delete a todo |

### Troubleshooting

**Connection Refused**
- Verify the BASE_URL is correct
- Check if the backend server is running
- Verify network/firewall settings

**401 Unauthorized**
- Check FASTAPI_AUTH_TOKEN is set correctly
- Verify token hasn't expired
- Ensure token has proper permissions

**404 Not Found**
- Verify the endpoint path is correct
- Check API version in URL if applicable

**CORS Errors**
- Backend needs to allow requests from your origin
- Check CORS configuration on FastAPI server

### Usage

```
/fastapi.config [show|test|set <key>=<value>]
```

**User Input**: $ARGUMENTS

Based on the arguments:
- `show`: Display current environment variable values
- `test`: Execute connection test to the backend
- `set key=value`: Provide instructions to update configuration
