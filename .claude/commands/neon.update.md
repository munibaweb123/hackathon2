---
description: Update records in Neon PostgreSQL tables
---

## Neon Database: Update

This skill updates existing records in Neon Serverless PostgreSQL tables.

### Configuration

**Base URL**: `https://your-neon-project-url.com/sql` (configure via `/neon.config`)

### Arguments

Syntax: `/neon.update <table> <where_column=value> <set_column=new_value ...>`

**Examples**:
- `/neon.update users id=123 name="Jane Doe"`
- `/neon.update todos id=abc-123 completed=true`
- `/neon.update todos user_id=456 completed=true priority="low"`

### Request Format

The skill constructs an UPDATE query with parameterized values:

```sql
UPDATE table_name
SET column1 = $1, column2 = $2
WHERE id = $3
RETURNING *
```

### Execution

```bash
# Load configuration
NEON_BASE_URL="${NEON_BASE_URL:-https://your-neon-project-url.com/sql}"
NEON_API_KEY="${NEON_API_KEY}"

# Example: Update a todo
curl -s -X POST "${NEON_BASE_URL}/query" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${NEON_API_KEY}" \
  -d '{
    "query": "UPDATE todos SET completed = $1, updated_at = NOW() WHERE id = $2 RETURNING *",
    "params": [true, "abc-123"]
  }' | jq .
```

### Expected Response

**Success (200 OK)**:
```json
{
  "rows": [
    {
      "id": "abc-123",
      "title": "Buy milk",
      "completed": true,
      "updated_at": "2024-12-10T10:30:00Z"
    }
  ],
  "rowCount": 1,
  "command": "UPDATE"
}
```

### Argument Structure

| Position | Description | Required |
|----------|-------------|----------|
| 1st | Table name | Yes |
| 2nd | WHERE condition (column=value) | Yes |
| 3rd+ | SET values (column=new_value) | Yes (at least one) |

### Update Multiple Columns

```
/neon.update todos id=abc-123 completed=true priority="high" updated_at="2024-12-10"
```

### Update Multiple Rows

For bulk updates with complex conditions, use `/neon.query`:

```
/neon.query UPDATE todos SET completed = true WHERE user_id = 'user-123' AND due_date < NOW() RETURNING *
```

### Error Handling

| Status Code | Meaning | Action |
|-------------|---------|--------|
| 200 | Success | Records updated |
| 400 | Bad Request | Check column names/values |
| 401 | Unauthorized | Check API key |
| 404 | Not Found | No matching records |
| 422 | Validation Error | Check constraints |
| 500 | Server Error | Check query |

### Common Patterns

**Mark todo complete:**
```
/neon.update todos id=abc-123 completed=true
```

**Update user profile:**
```
/neon.update users id=user-123 name="New Name" email="new@email.com"
```

**Soft delete:**
```
/neon.update users id=user-123 deleted_at="2024-12-10T00:00:00Z"
```

**Increment counter (use raw query):**
```
/neon.query UPDATE stats SET view_count = view_count + 1 WHERE page_id = 'home' RETURNING *
```

### Safety Features

- **RETURNING ***: Always returns updated record for verification
- **Parameterized queries**: Prevents SQL injection
- **rowCount**: Verify expected number of updates

### Usage

```
/neon.update <table> <where_column=value> <set_column=new_value ...>
```

**User Input**: $ARGUMENTS

Parse arguments:
1. First arg: table name (required)
2. Second arg: WHERE clause (column=value) - identifies which row(s)
3. Remaining args: SET values (column=new_value)

Construct parameterized UPDATE query with RETURNING *.

### Security Notes

- Always include a WHERE clause to avoid updating all rows
- Verify rowCount matches expected updates
- Use parameterized queries (handled automatically)
- Consider adding updated_at timestamp
