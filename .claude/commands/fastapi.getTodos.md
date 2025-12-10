---
description: Fetch all todos from FastAPI backend
---

## FastAPI Backend: Get All Todos

This skill fetches all todo items from the FastAPI backend.

### Configuration

**Base URL**: `https://your-fastapi-url.com` (update in `.env` or configure via `/fastapi.config`)

### Endpoint Details

- **Method**: GET
- **Path**: `/todos`
- **Authentication**: Bearer token (if configured)

### Execution

Execute the following curl command to fetch all todos:

```bash
# Load base URL from environment or use default
BASE_URL="${FASTAPI_BASE_URL:-https://your-fastapi-url.com}"

# Optional: Add authorization header if token is set
AUTH_HEADER=""
if [ -n "$FASTAPI_AUTH_TOKEN" ]; then
  AUTH_HEADER="-H \"Authorization: Bearer $FASTAPI_AUTH_TOKEN\""
fi

# Fetch all todos
curl -s -X GET "${BASE_URL}/todos" \
  -H "Content-Type: application/json" \
  $AUTH_HEADER | jq .
```

### Expected Response

```json
{
  "todos": [
    {
      "id": "string",
      "title": "string",
      "description": "string",
      "completed": boolean,
      "due_date": "string (ISO 8601)",
      "priority": "low|medium|high",
      "created_at": "string (ISO 8601)",
      "updated_at": "string (ISO 8601)"
    }
  ],
  "total": number
}
```

### Error Handling

| Status Code | Meaning | Action |
|-------------|---------|--------|
| 200 | Success | Parse and display todos |
| 401 | Unauthorized | Check auth token |
| 500 | Server Error | Retry or check backend logs |

### Usage

Run `/fastapi.getTodos` to fetch and display all todo items from the backend.

$ARGUMENTS
