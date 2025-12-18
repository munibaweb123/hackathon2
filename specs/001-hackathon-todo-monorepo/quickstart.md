# Quickstart Guide: Hackathon Todo Monorepo

## Prerequisites

- Python 3.13+
- Node.js 20+
- Docker and Docker Compose (optional, for full stack)
- Git

## Quick Start (Local Development)

### 1. Clone and Setup

```bash
git clone <repository-url>
cd hackathon_2
git checkout 001-hackathon-todo-monorepo
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
│   │   ├── api/          # Route handlers
│   │   ├── auth/         # Auth middleware
│   │   ├── core/         # Config, database
│   │   ├── models/       # SQLModel entities
│   │   ├── schemas/      # Pydantic schemas
│   │   └── services/     # Business logic
│   └── tests/
├── frontend/              # Next.js frontend
│   └── src/
│       ├── app/          # App Router pages
│       ├── components/   # UI components
│       ├── hooks/        # Custom hooks
│       └── lib/          # Utilities
├── specs/                 # Specifications
├── src/                   # Console app (Phase 1)
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

## Authentication Flow

1. User registers/logs in via Better Auth on frontend
2. Better Auth creates session and issues JWT
3. Frontend includes JWT in API requests
4. Backend validates JWT via Better Auth JWKS endpoint
5. Protected endpoints return user-specific data

## API Quick Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /health | Health check |
| GET | /api/auth/me | Current user |
| GET | /api/tasks | List tasks |
| POST | /api/tasks | Create task |
| GET | /api/tasks/{id} | Get task |
| PATCH | /api/tasks/{id} | Update task |
| DELETE | /api/tasks/{id} | Delete task |
| GET | /api/reminders | List reminders |
| POST | /api/reminders | Create reminder |
| DELETE | /api/reminders/{id} | Delete reminder |
| GET | /api/preferences | Get preferences |
| PUT | /api/preferences | Update preferences |

Full API documentation: http://localhost:8000/docs

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

### Better Auth token issues
- Ensure BETTER_AUTH_URL matches frontend URL
- Check that CORS_ORIGINS includes frontend URL
- Verify JWT secret is consistent between services
