# Backend Development Guidelines

This is the FastAPI backend for the hackathon-todo application.

## Technology Stack

- **Framework**: FastAPI (Python 3.13+)
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **Database**: PostgreSQL (production) / SQLite (development)
- **Authentication**: Better Auth JWT integration
- **AI Framework**: OpenAI Agents SDK for AI reasoning
- **MCP Server**: Model Context Protocol for tool integration
- **Chat Interface**: ChatKit for conversational UI

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── agents/              # AI agent logic and MCP tools
│   │   ├── factory.py       # Model factory for OpenAI Agents SDK
│   │   ├── todo_agent.py    # Main todo management agent
│   │   └── tools/           # MCP tools for task operations (add_task, list_tasks, etc.)
│   ├── chatkit/             # ChatKit backend integration
│   │   ├── router.py        # ChatKit event routing and handlers
│   │   ├── streaming.py     # Server-sent events helpers
│   │   └── types.py         # Typed helpers for ChatKit events
│   ├── api/                 # Route handlers (tasks, auth, reminders, etc.)
│   ├── auth/                # Authentication middleware & utils
│   ├── core/                # Config, database, security, JWKS
│   ├── models/              # SQLModel entities
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic
│   └── utils/               # Utilities (recurrence, reminder scheduler)
├── tests/                   # Backend tests
├── .env                     # Environment variables
├── .env.example             # Environment variables template
├── requirements.txt         # Python dependencies
├── pyproject.toml          # Project metadata and build config
└── CLAUDE.md               # This file
```

## Code Standards

### API Design

- Use RESTful conventions for endpoint naming
- Always return proper HTTP status codes
- Use Pydantic models for request/response validation
- Include OpenAPI documentation for all endpoints

### Database

- Use SQLModel for all database models
- Always use async sessions for database operations
- Include proper indexes on frequently queried fields
- Use migrations for schema changes (Alembic)

### Error Handling

- Use HTTPException for client errors (4xx)
- Log server errors (5xx) with proper context
- Return consistent error response format:

```json
{
  "detail": "Error message",
  "code": "ERROR_CODE"
}
```

### Authentication

- Validate JWT tokens on protected endpoints
- Use dependency injection for authentication
- Never store plain text passwords
- Implement rate limiting on auth endpoints

## Running the Backend

```bash
# Development
cd backend && uvicorn app.main:app --reload --port 8000

# Production
cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000

# With Docker
docker-compose up

# For AI Chatbot Development
cd backend && OPENAI_API_KEY=your-api-key uvicorn app.main:app --reload --port 8000
```

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/hackathon_todo

# Security
SECRET_KEY=your-secret-key
CORS_ORIGINS=http://localhost:3000

# Authentication
BETTER_AUTH_URL=http://localhost:3000
BETTER_AUTH_SECRET=your-better-auth-secret

# OpenAI API
OPENAI_API_KEY=your-openai-api-key
LLM_PROVIDER=openai
OPENAI_DEFAULT_MODEL=gpt-4o-mini

# MCP Server
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=8001
```

## References

- API Contract: `@specs/api/rest-endpoints.md`
- Database Schema: `@specs/database/schema.md`
- Task Features: `@specs/features/task-crud.md`
