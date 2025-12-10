---
description: Update an existing todo item via FastAPI backend
---

## FastAPI Backend: Update Todo

This skill updates an existing todo item in the FastAPI backend.

### Configuration

**Base URL**: `https://your-fastapi-url.com` (update in `.env` or configure via `/fastapi.config`)

### Endpoint Details

- **Method**: PUT
- **Path**: `/todos/{id}`
- **Content-Type**: application/json

### Arguments

Pass todo ID and fields to update: `/fastapi.updateTodo <id> [field=value ...]`

**Examples**:
- `/fastapi.updateTodo abc123 completed=true`
- `/fastapi.updateTodo abc123 title="Updated title" priority=high`
- `/fastapi.updateTodo abc123 description="New description" due_date=2024-12-20`

### Request Body Schema

```json
{
  "title": "string (optional)",
  "description": "string (optional)",
  "completed": "boolean (optional)",
  "priority": "low|medium|high (optional)",
  "due_date": "string ISO 8601 (optional)"
}
```

Only include fields that need to be updated.

### Execution

```bash
# Load base URL from environment or use default
BASE_URL="${FASTAPI_BASE_URL:-https://your-fastapi-url.com}"
TODO_ID="{{TODO_ID}}"

# Optional: Add authorization header if token is set
AUTH_HEADER=""
if [ -n "$FASTAPI_AUTH_TOKEN" ]; then
  AUTH_HEADER="-H \"Authorization: Bearer $FASTAPI_AUTH_TOKEN\""
fi

# Update todo (include only fields being updated)
curl -s -X PUT "${BASE_URL}/todos/${TODO_ID}" \
  -H "Content-Type: application/json" \
  $AUTH_HEADER \
  -d '{
    "title": "{{TITLE}}",
    "description": "{{DESCRIPTION}}",
    "completed": {{COMPLETED}},
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
  "completed": boolean,
  "priority": "low|medium|high",
  "due_date": "string (ISO 8601)",
  "created_at": "string (ISO 8601)",
  "updated_at": "string (ISO 8601)"
}
```

### Error Handling

| Status Code | Meaning | Action |
|-------------|---------|--------|
| 200 | Success | Todo successfully updated |
| 400 | Bad Request | Check request body format |
| 401 | Unauthorized | Check auth token |
| 404 | Not Found | Todo ID does not exist |
| 422 | Validation Error | Check field values |
| 500 | Server Error | Retry or check backend logs |

### Usage

```
/fastapi.updateTodo <todo-id> [field=value ...]
```

**User Input**: $ARGUMENTS

Parse the arguments to extract:
1. The todo ID (first argument)
2. Field=value pairs to update

Then construct and execute the appropriate API call.
