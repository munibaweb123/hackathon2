---
description: Configure Neon Serverless PostgreSQL connection settings
---

## Neon Database: Configuration

This skill helps configure the Neon Serverless PostgreSQL connection settings.

### Current Configuration

The Neon database uses the following environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `NEON_BASE_URL` | Base URL for SQL API | `https://your-neon-project-url.com/sql` |
| `NEON_API_KEY` | Neon API key for authentication | (required) |
| `NEON_DATABASE` | Database name (for reference) | (optional) |

### Arguments

- `/neon.config show` - Display current configuration
- `/neon.config set baseUrl=<url>` - Set the base URL
- `/neon.config set apiKey=<key>` - Set the API key
- `/neon.config test` - Test the connection
- `/neon.config tables` - List all tables
- `/neon.config schema <table>` - Show table schema

### Configuration File

Create or update `.env` file in the project root:

```bash
# Neon Serverless PostgreSQL Configuration
NEON_BASE_URL=https://your-project-id.neon.tech/sql
NEON_API_KEY=your-neon-api-key-here
NEON_DATABASE=neondb
```

### Getting Your Neon Credentials

1. Go to [Neon Console](https://console.neon.tech)
2. Select your project
3. Navigate to **Settings** > **API Keys**
4. Create or copy your API key
5. Find your project URL in the connection details

### Setting Configuration

**Option 1: Environment Variables**

```bash
export NEON_BASE_URL="https://your-project-id.neon.tech/sql"
export NEON_API_KEY="your-api-key"
```

**Option 2: .env File**

```
NEON_BASE_URL=https://your-project-id.neon.tech/sql
NEON_API_KEY=your-api-key
```

### Testing Connection

```bash
# Load configuration
source .env 2>/dev/null || true

# Test connection with simple query
curl -s -X POST "${NEON_BASE_URL}/query" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${NEON_API_KEY}" \
  -d '{"query": "SELECT 1 as test"}' | jq .
```

### List All Tables

```bash
curl -s -X POST "${NEON_BASE_URL}/query" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${NEON_API_KEY}" \
  -d '{
    "query": "SELECT table_name FROM information_schema.tables WHERE table_schema = '\''public'\''"
  }' | jq '.rows[].table_name'
```

### Show Table Schema

```bash
# Replace 'todos' with your table name
curl -s -X POST "${NEON_BASE_URL}/query" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${NEON_API_KEY}" \
  -d '{
    "query": "SELECT column_name, data_type, is_nullable, column_default FROM information_schema.columns WHERE table_name = '\''todos'\'' ORDER BY ordinal_position"
  }' | jq .
```

### API Skills Summary

| Skill | Description | Example |
|-------|-------------|---------|
| `/neon.query` | Raw SQL execution | `/neon.query SELECT * FROM users` |
| `/neon.select` | Simplified SELECT | `/neon.select users * * 10` |
| `/neon.insert` | Insert records | `/neon.insert users name="John"` |
| `/neon.update` | Update records | `/neon.update users id=1 name="Jane"` |
| `/neon.delete` | Delete records | `/neon.delete users id=1` |

### Troubleshooting

**Connection Refused**
- Verify `NEON_BASE_URL` is correct
- Check if project is active (not suspended)
- Verify region endpoint

**401 Unauthorized**
- Check `NEON_API_KEY` is correct
- Verify API key hasn't expired
- Ensure key has proper permissions

**Database Suspended**
- Free tier projects suspend after inactivity
- Any query will automatically wake it (may take a few seconds)

**Query Timeout**
- Neon has query timeout limits
- Optimize long-running queries
- Consider connection pooling for production

**SSL/TLS Errors**
- Neon requires SSL connections
- Ensure HTTPS in base URL

### Connection Pooling

For production, consider using Neon's connection pooler:

```
# Pooled connection URL format
postgresql://user:password@your-project-id-pooler.region.aws.neon.tech/neondb?sslmode=require
```

### Branching (Neon Feature)

Neon supports database branching:

```bash
# List branches (via Neon API, not SQL API)
curl -s -X GET "https://console.neon.tech/api/v2/projects/${PROJECT_ID}/branches" \
  -H "Authorization: Bearer ${NEON_API_KEY}" | jq .
```

### Usage

```
/neon.config [show|test|tables|schema <table>|set <key>=<value>]
```

**User Input**: $ARGUMENTS

Based on the arguments:
- `show`: Display current environment variable values (mask API key)
- `test`: Execute connection test query
- `tables`: List all tables in the database
- `schema <table>`: Show schema for specified table
- `set key=value`: Provide instructions to update configuration

### Security Best Practices

1. **Never commit API keys** - Add `.env` to `.gitignore`
2. **Use environment variables** - Don't hardcode credentials
3. **Rotate keys regularly** - Create new keys periodically
4. **Least privilege** - Use read-only keys when possible
5. **Monitor usage** - Check Neon dashboard for unusual activity
