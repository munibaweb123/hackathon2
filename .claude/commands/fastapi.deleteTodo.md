---
description: Delete a todo item via FastAPI backend
---

## FastAPI Backend: Delete Todo

This skill deletes a todo item from the FastAPI backend.

### Configuration

**Base URL**: `https://your-fastapi-url.com` (update in `.env` or configure via `/fastapi.config`)

### Endpoint Details

- **Method**: DELETE
- **Path**: `/todos/{id}`

### Arguments

Pass the todo ID to delete: `/fastapi.deleteTodo <id>`

**Example**: `/fastapi.deleteTodo abc123`

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

# Delete todo
curl -s -X DELETE "${BASE_URL}/todos/${TODO_ID}" \
  -H "Content-Type: application/json" \
  $AUTH_HEADER | jq .
```

### Expected Response

**Success (204 No Content)**: Empty response body

**Or Success (200 OK)**:
```json
{
  "message": "Todo deleted successfully",
  "id": "string"
}
```

### Error Handling

| Status Code | Meaning | Action |
|-------------|---------|--------|
| 200/204 | Success | Todo successfully deleted |
| 401 | Unauthorized | Check auth token |
| 404 | Not Found | Todo ID does not exist |
| 500 | Server Error | Retry or check backend logs |

### Usage

```
/fastapi.deleteTodo <todo-id>
```

**User Input**: $ARGUMENTS

Parse the arguments to extract the todo ID, then execute the DELETE request.

### Safety Note

This operation is irreversible. Consider implementing soft-delete on the backend for data recovery.
