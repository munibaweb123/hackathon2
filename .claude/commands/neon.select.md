---
description: Execute SELECT queries on Neon PostgreSQL with helper syntax
---

## Neon Database: Select

This skill provides a simplified interface for SELECT queries on Neon Serverless PostgreSQL.

### Configuration

**Base URL**: `https://your-neon-project-url.com/sql` (configure via `/neon.config`)

### Arguments

Simplified syntax: `/neon.select <table> [columns] [where] [limit]`

**Examples**:
- `/neon.select users` - Select all from users
- `/neon.select users id,name,email` - Select specific columns
- `/neon.select todos * completed=true` - With WHERE clause
- `/neon.select todos * * 10` - With LIMIT

### Full Syntax

```
/neon.select <table> [columns] [where_clause] [limit] [order_by]
```

| Parameter | Description | Default |
|-----------|-------------|---------|
| `table` | Table name (required) | - |
| `columns` | Comma-separated columns or `*` | `*` |
| `where_clause` | WHERE conditions (key=value) | (none) |
| `limit` | Max rows to return | (none) |
| `order_by` | Column to sort by | (none) |

### Execution

```bash
# Load configuration
NEON_BASE_URL="${NEON_BASE_URL:-https://your-neon-project-url.com/sql}"
NEON_API_KEY="${NEON_API_KEY}"

# Build and execute SELECT query
TABLE="{{TABLE}}"
COLUMNS="{{COLUMNS:-*}}"
WHERE="{{WHERE_CLAUSE}}"
LIMIT="{{LIMIT}}"

# Construct query
QUERY="SELECT ${COLUMNS} FROM ${TABLE}"
[ -n "$WHERE" ] && QUERY="${QUERY} WHERE ${WHERE}"
[ -n "$LIMIT" ] && QUERY="${QUERY} LIMIT ${LIMIT}"

curl -s -X POST "${NEON_BASE_URL}/query" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${NEON_API_KEY}" \
  -d "{\"query\": \"${QUERY}\"}" | jq .
```

### Expected Response

```json
{
  "rows": [
    {
      "id": "uuid",
      "name": "string",
      "email": "string",
      "created_at": "timestamp"
    }
  ],
  "rowCount": 1,
  "command": "SELECT"
}
```

### Common Query Patterns

**Select all users:**
```
/neon.select users
```

**Select specific columns:**
```
/neon.select users id,name,email
```

**Filter with WHERE:**
```
/neon.select todos * "completed = true"
```

**With LIMIT:**
```
/neon.select todos * * 10
```

**Complex WHERE:**
```
/neon.select todos * "completed = false AND priority = 'high'"
```

**With ORDER BY (via raw query):**
```
/neon.query SELECT * FROM todos ORDER BY created_at DESC LIMIT 10
```

### Error Handling

| Status Code | Meaning | Action |
|-------------|---------|--------|
| 200 | Success | Data returned |
| 400 | Bad Request | Check table/column names |
| 401 | Unauthorized | Check API key |
| 500 | Server Error | Verify query syntax |

### Usage

```
/neon.select <table> [columns] [where] [limit]
```

**User Input**: $ARGUMENTS

Parse arguments to construct SELECT query:
1. First arg: table name (required)
2. Second arg: columns (default: *)
3. Third arg: WHERE clause (optional)
4. Fourth arg: LIMIT (optional)

For complex queries, use `/neon.query` directly.
