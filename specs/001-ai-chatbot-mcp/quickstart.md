# Quickstart Guide: AI Chatbot for Todo Management

## Prerequisites

- Python 3.13+
- Node.js 20+
- Docker and Docker Compose (optional, for full stack)
- OpenAI API key
- Git

## Quick Start (Local Development)

### 1. Clone and Setup

```bash
git clone <repository-url>
cd hackathon_2
git checkout 001-ai-chatbot-mcp
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env  # Edit with your values

# Set OpenAI API key and other required variables
export OPENAI_API_KEY=your-openai-api-key
export LLM_PROVIDER=openai
export OPENAI_DEFAULT_MODEL=gpt-4o-mini

# Run backend
uvicorn app.main:app --reload --port 8000
```

Backend will be available at: http://localhost:8000
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env.local  # Edit with your values

# Run frontend
npm run dev
```

Frontend will be available at: http://localhost:3000

## Quick Start (Docker)

Run everything with one command:

```bash
docker-compose up
```

Services:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- PostgreSQL: localhost:5432
- pgAdmin (optional): http://localhost:5050

To include pgAdmin:
```bash
docker-compose --profile tools up
```

## Environment Variables

### Backend (.env)

```bash
# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key
LLM_PROVIDER=openai
OPENAI_DEFAULT_MODEL=gpt-4o-mini

# Database
DATABASE_URL=sqlite:///./hackathon_todo.db  # Dev
# DATABASE_URL=postgresql://user:pass@localhost:5432/hackathon_todo  # Production

# Security
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=http://localhost:3000

# Better Auth (for JWT validation)
BETTER_AUTH_URL=http://localhost:3000

# MCP Configuration
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=8001
```

### Frontend (.env.local)

```bash
# API
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth
BETTER_AUTH_SECRET=your-auth-secret
BETTER_AUTH_URL=http://localhost:3000
DATABASE_URL=postgresql://user:pass@localhost:5432/hackathon_todo
```

## Project Structure

```
hackathon_2/
├── backend/               # FastAPI backend
│   ├── app/
│   │   ├── agents/        # AI agent logic and tools
│   │   │   ├── factory.py # Model factory for Agents SDK
│   │   │   ├── todo_agent.py # Main todo management agent
│   │   │   └── tools/     # MCP tools for task operations
│   │   ├── chatkit/       # ChatKit backend integration
│   │   │   ├── router.py  # ChatKit event routing
│   │   │   └── streaming.py # SSE helpers
│   │   ├── api/           # Additional API endpoints
│   │   ├── models/        # SQLModel entities
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Business logic
│   │   └── core/          # Config, database, security
│   └── tests/
├── frontend/              # Next.js frontend
│   └── src/
│       ├── app/           # App Router pages
│       ├── components/    # UI components
│       └── lib/           # Utilities
├── specs/                 # Specifications
└── docker-compose.yml
```

## Common Commands

### Backend

```bash
# Run tests
cd backend && pytest

# Run with auto-reload
cd backend && uvicorn app.main:app --reload

# Create database tables
cd backend && python -c "from app.core.database import create_tables; create_tables()"

# Run AI agent tests
cd backend && python -m pytest tests/agents/
```

### Frontend

```bash
# Run tests
cd frontend && npm test

# Build for production
cd frontend && npm run build

# Type check
cd frontend && npm run type-check
```

### Docker

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Rebuild after changes
docker-compose up --build
```

## Chatbot Usage Examples

Once the system is running, you can interact with the AI chatbot:

1. **Add a task**: "Add a task to buy groceries"
2. **List tasks**: "Show me all my tasks" or "What's pending?"
3. **Complete task**: "Mark task 3 as complete"
4. **Update task**: "Update that task to include eggs"
5. **Delete task**: "Delete the meeting task"

## MCP Server Architecture

The system uses MCP (Model Context Protocol) server architecture:

1. The AI agent calls MCP tools to perform operations
2. MCP tools are stateless and store state in the database
3. Each tool operation integrates with existing task management functionality
4. Conversation state is maintained in the database between requests

## Troubleshooting

### Port already in use
```bash
# Find process using port
lsof -i :8000  # or :3000
# Kill it
kill -9 <PID>
```

### Database connection issues
```bash
# Check if PostgreSQL is running
docker-compose ps db

# Reset database
docker-compose down -v && docker-compose up
```

### OpenAI API errors
- Ensure OPENAI_API_KEY is set correctly
- Check that the API key has sufficient quota
- Verify the model name is available in your OpenAI account

### ChatKit integration issues
- Verify domain is allowlisted in OpenAI dashboard
- Check that the frontend origin matches backend expectations
- Ensure the domainKey matches between frontend and backend