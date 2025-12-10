---
description: Insert records into Neon PostgreSQL tables
---

## Neon Database: Insert

This skill inserts new records into Neon Serverless PostgreSQL tables.

### Configuration

**Base URL**: `https://your-neon-project-url.com/sql` (configure via `/neon.config`)

### Arguments

Syntax: `/neon.insert <table> <column=value ...>`

**Examples**:
- `/neon.insert users name="John Doe" email="john@example.com"`
- `/neon.insert todos title="Buy milk" completed=false priority="high"`

### Request Format

The skill constructs an INSERT query with parameterized values for safety.

```sql
INSERT INTO table_name (column1, column2, ...)
VALUES ($1, $2, ...)
RETURNING *
```

### Execution

```bash
# Load configuration
NEON_BASE_URL="${NEON_BASE_URL:-https://your-neon-project-url.com/sql}"
NEON_API_KEY="${NEON_API_KEY}"

# Example: Insert a new user
curl -s -X POST "${NEON_BASE_URL}/query" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${NEON_API_KEY}" \
  -d '{
    "query": "INSERT INTO users (name, email) VALUES ($1, $2) RETURNING *",
    "params": ["John Doe", "john@example.com"]
  }' | jq .
```

### Expected Response

**Success (200 OK)**:
```json
{
  "rows": [
    {
      "id": "generated-uuid",
      "name": "John Doe",
      "email": "john@example.com",
      "created_at": "2024-12-10T10:30:00Z"
    }
  ],
  "rowCount": 1,
  "command": "INSERT"
}
```

### Data Type Handling

| Type | Format | Example |
|------|--------|---------|
| String | Quoted | `name="John"` |
| Number | Unquoted | `age=25` |
| Boolean | true/false | `completed=false` |
| NULL | null | `deleted_at=null` |
| Date | ISO format | `due_date="2024-12-31"` |
| JSON | JSON string | `metadata='{"key":"value"}'` |

### Bulk Insert

For multiple records, use `/neon.query` with VALUES list:

```
/neon.query INSERT INTO todos (title, completed) VALUES ('Task 1', false), ('Task 2', false), ('Task 3', false) RETURNING *
```

### Error Handling

| Status Code | Meaning | Action |
|-------------|---------|--------|
| 200 | Success | Record inserted |
| 400 | Bad Request | Check column names/values |
| 401 | Unauthorized | Check API key |
| 409 | Conflict | Duplicate key violation |
| 422 | Validation Error | Check constraints |
| 500 | Server Error | Check query |

### Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `duplicate key` | Unique constraint | Use different value |
| `null value in column` | NOT NULL constraint | Provide required value |
| `foreign key violation` | Invalid reference | Check referenced ID exists |
| `check constraint` | Value out of range | Verify value constraints |

### Usage

```
/neon.insert <table> <column=value ...>
```

**User Input**: $ARGUMENTS

Parse arguments:
1. First arg: table name (required)
2. Remaining args: column=value pairs

Construct parameterized INSERT query with RETURNING * to return the created record.

### Security Notes

- Always use parameterized queries (handled automatically)
- Validate input data types before insertion
- Respect database constraints and foreign keys
