# Neon Database Compatibility with Better Auth

## Issue Description

When using Better Auth with Neon's serverless PostgreSQL in development, the application encounters timeout errors:

```
Error: Connection terminated due to connection timeout
Error: Connection terminated unexpectedly
```

## Root Cause

Better Auth's database adapter maintains connection pools that expect persistent connections. Neon's serverless PostgreSQL, however, closes connections after periods of inactivity to optimize costs. This creates a fundamental incompatibility between Better Auth's connection pooling mechanism and Neon's serverless architecture.

## Recommended Solution

### For Development
Use a local PostgreSQL instance for development to avoid timeout issues:

1. Install PostgreSQL locally or use Docker:
   ```bash
   docker run --name postgres-dev -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=hackathon_todo -p 5432:5432 -d postgres:15-alpine
   ```

2. Update your `.env.local` file:
   ```env
   # For local development
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/hackathon_todo
   ```

### For Production
Continue using Neon's serverless PostgreSQL in production with appropriate connection pooling settings.

## Alternative Configuration

If you must use Neon in development, consider these settings in your Better Auth configuration:

```typescript
// In src/lib/auth.ts
import { Pool } from 'pg';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: 1,                    // Minimal connections
  min: 0,
  idleTimeoutMillis: 5000,   // Shorter timeout
  connectionTimeoutMillis: 3000, // Fast timeout
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : undefined,
});
```

## Docker Compose Setup

For a complete local development setup, add this to your `docker-compose.yml`:

```yaml
  db-dev:
    image: postgres:15-alpine
    container_name: hackathon-todo-db-dev
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=hackathon_todo
    ports:
      - "5432:5432"
    volumes:
      - postgres_dev_data:/var/lib/postgresql/data

volumes:
  postgres_dev_data:
```

## Summary

The recommended approach is to use a local PostgreSQL instance for development to avoid timeout issues while maintaining Neon for production deployments.