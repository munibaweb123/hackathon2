---
description: Create a new todo item via FastAPI backend
---

## FastAPI Backend: Create Todo

This skill creates a new todo item in the FastAPI backend.

### Configuration

**Base URL**: `https://your-fastapi-url.com` (update in `.env` or configure via `/fastapi.config`)

### Endpoint Details

- **Method**: POST
- **Path**: `/todos`
- **Content-Type**: application/json

### Arguments

Pass todo details as arguments: `/fastapi.createTodo <title> [description] [priority] [due_date]`

**Example**: `/fastapi.createTodo "Buy groceries" "Milk, eggs, bread" high 2024-12-15`

### Request Body Schema

```json
{
  "title": "string (required)",
  "description": "string (optional)",
  "completed": false,
  "priority": "low|medium|high (default: medium)",
  "due_date": "string ISO 8601 (optional)"
}
```

### Execution

```bash
# Load base URL from environment or use default
BASE_URL="${FASTAPI_BASE_URL:-https://your-fastapi-url.com}"

# Optional: Add authorization header if token is set
AUTH_HEADER=""
if [ -n "$FASTAPI_AUTH_TOKEN" ]; then
  AUTH_HEADER="-H \"Authorization: Bearer $FASTAPI_AUTH_TOKEN\""
fi

# Create todo (replace placeholders with actual values)
curl -s -X POST "${BASE_URL}/todos" \
  -H "Content-Type: application/json" \
  $AUTH_HEADER \
  -d '{
    "title": "{{TITLE}}",
    "description": "{{DESCRIPTION}}",
    "priority": "{{PRIORITY}}",
    "due_date": "{{DUE_DATE}}"
  }' | jq .
```

### Expected Response

```json
{
  "id": "string",
  "title": "string",
  "description": "string",
  "completed": false,
  "priority": "low|medium|high",
  "due_date": "string (ISO 8601)",
  "created_at": "string (ISO 8601)",
  "updated_at": "string (ISO 8601)"
}
```

### Error Handling

| Status Code | Meaning | Action |
|-------------|---------|--------|
| 201 | Created | Todo successfully created |
| 400 | Bad Request | Check request body format |
| 401 | Unauthorized | Check auth token |
| 422 | Validation Error | Check required fields |
| 500 | Server Error | Retry or check backend logs |

### Usage

```
/fastapi.createTodo "Task title" "Optional description" medium 2024-12-31
```

**User Input**: $ARGUMENTS

Parse the arguments and construct the appropriate API call based on the input provided.
