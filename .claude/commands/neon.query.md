---
description: Execute a raw SQL query on Neon Serverless PostgreSQL
---

## Neon Database: Run Query

This skill executes raw SQL queries against a Neon Serverless PostgreSQL database.

### Configuration

**Base URL**: `https://your-neon-project-url.com/sql` (update in `.env` or configure via `/neon.config`)

### Endpoint Details

- **Method**: POST
- **Path**: `/query`
- **Content-Type**: application/json
- **Authorization**: Bearer token (Neon API Key)

### Arguments

Pass SQL query: `/neon.query <sql_statement>`

**Examples**:
- `/neon.query SELECT * FROM users LIMIT 10`
- `/neon.query SELECT COUNT(*) FROM todos WHERE completed = true`
- `/neon.query SHOW TABLES`

### Request Body Schema

```json
{
  "query": "string (SQL statement)",
  "params": ["array of parameters (optional, for parameterized queries)"]
}
```

### Execution

```bash
# Load configuration from environment
NEON_BASE_URL="${NEON_BASE_URL:-https://your-neon-project-url.com/sql}"
NEON_API_KEY="${NEON_API_KEY}"

# Execute SQL query
curl -s -X POST "${NEON_BASE_URL}/query" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${NEON_API_KEY}" \
  -d '{
    "query": "{{SQL_QUERY}}",
    "params": []
  }' | jq .
```

### Parameterized Queries

For secure queries with user input, use parameterized queries:

```bash
# Example: Find user by email
curl -s -X POST "${NEON_BASE_URL}/query" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${NEON_API_KEY}" \
  -d '{
    "query": "SELECT * FROM users WHERE email = $1",
    "params": ["user@example.com"]
  }' | jq .
```

### Expected Response

**Success (200 OK)**:
```json
{
  "rows": [
    {
      "column1": "value1",
      "column2": "value2"
    }
  ],
  "rowCount": 1,
  "fields": [
    {
      "name": "column1",
      "dataTypeID": 25
    }
  ],
  "command": "SELECT"
}
```

### Error Handling

| Status Code | Meaning | Action |
|-------------|---------|--------|
| 200 | Success | Query executed successfully |
| 400 | Bad Request | Check SQL syntax |
| 401 | Unauthorized | Check API key |
| 403 | Forbidden | Insufficient permissions |
| 500 | Server Error | Check query or retry |

### Common SQL Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `syntax error` | Invalid SQL | Check query syntax |
| `relation does not exist` | Table not found | Verify table name |
| `column does not exist` | Invalid column | Check column names |
| `permission denied` | Insufficient access | Check role permissions |

### Usage

```
/neon.query <sql_statement>
```

**User Input**: $ARGUMENTS

Parse the SQL query from arguments and execute against the Neon database.

### Security Notes

- Always use parameterized queries for user input
- Never interpolate user input directly into SQL
- Use least-privilege database roles
- Audit sensitive queries
