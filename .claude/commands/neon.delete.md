---
description: Delete records from Neon PostgreSQL tables
---

## Neon Database: Delete

This skill deletes records from Neon Serverless PostgreSQL tables.

### Configuration

**Base URL**: `https://your-neon-project-url.com/sql` (configure via `/neon.config`)

### Arguments

Syntax: `/neon.delete <table> <where_column=value>`

**Examples**:
- `/neon.delete todos id=abc-123`
- `/neon.delete sessions user_id=user-456`

### Request Format

The skill constructs a DELETE query with parameterized values:

```sql
DELETE FROM table_name
WHERE column = $1
RETURNING *
```

### Execution

```bash
# Load configuration
NEON_BASE_URL="${NEON_BASE_URL:-https://your-neon-project-url.com/sql}"
NEON_API_KEY="${NEON_API_KEY}"

# Example: Delete a todo
curl -s -X POST "${NEON_BASE_URL}/query" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${NEON_API_KEY}" \
  -d '{
    "query": "DELETE FROM todos WHERE id = $1 RETURNING *",
    "params": ["abc-123"]
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
      "completed": false,
      "created_at": "2024-12-01T10:00:00Z"
    }
  ],
  "rowCount": 1,
  "command": "DELETE"
}
```

**No rows deleted (200 OK)**:
```json
{
  "rows": [],
  "rowCount": 0,
  "command": "DELETE"
}
```

### Argument Structure

| Position | Description | Required |
|----------|-------------|----------|
| 1st | Table name | Yes |
| 2nd | WHERE condition (column=value) | Yes |

### Delete Multiple Rows

For deleting with complex conditions, use `/neon.query`:

```
/neon.query DELETE FROM todos WHERE completed = true AND created_at < '2024-01-01' RETURNING *
```

**Delete all completed todos for a user:**
```
/neon.query DELETE FROM todos WHERE user_id = 'user-123' AND completed = true RETURNING id
```

### Error Handling

| Status Code | Meaning | Action |
|-------------|---------|--------|
| 200 | Success | Records deleted (check rowCount) |
| 400 | Bad Request | Check table/column names |
| 401 | Unauthorized | Check API key |
| 409 | Conflict | Foreign key constraint |
| 500 | Server Error | Check query |

### Common Patterns

**Delete by ID:**
```
/neon.delete todos id=abc-123
```

**Delete user sessions:**
```
/neon.delete sessions user_id=user-456
```

**Cascade delete (if configured):**
```
/neon.delete users id=user-123
```

**Bulk delete old records (use raw query):**
```
/neon.query DELETE FROM logs WHERE created_at < NOW() - INTERVAL '30 days' RETURNING id
```

### Soft Delete Alternative

Consider soft delete instead of hard delete:

```
/neon.update users id=user-123 deleted_at="2024-12-10T00:00:00Z"
```

### Safety Features

- **RETURNING ***: Returns deleted records for verification/logging
- **Parameterized queries**: Prevents SQL injection
- **rowCount**: Verify expected number of deletions
- **WHERE required**: Prevents accidental full table delete

### Foreign Key Considerations

If deleting records that are referenced by other tables:

| Strategy | Description |
|----------|-------------|
| CASCADE | Automatically deletes referencing records |
| RESTRICT | Prevents deletion if references exist |
| SET NULL | Sets foreign key to NULL |

Check your schema constraints before deleting.

### Usage

```
/neon.delete <table> <where_column=value>
```

**User Input**: $ARGUMENTS

Parse arguments:
1. First arg: table name (required)
2. Second arg: WHERE clause (column=value) - required for safety

Construct parameterized DELETE query with RETURNING *.

### Security Notes

- **Always include WHERE clause** - this skill requires it
- Verify rowCount matches expected deletions
- Consider soft delete for recoverable data
- Log deleted records for audit trail
- This operation is irreversible (unless you have backups)
