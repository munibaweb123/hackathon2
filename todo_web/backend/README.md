# Todo Web Backend - FastAPI

RESTful API backend for the Todo Web Application with Better Auth JWT authentication and Neon PostgreSQL database.

## Technology Stack

- **Framework**: FastAPI
- **ORM**: SQLModel
- **Database**: Neon Serverless PostgreSQL
- **Authentication**: Better Auth JWT verification
- **Server**: Uvicorn

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── health.py       # Health check endpoint
│   │   └── tasks.py        # Task CRUD endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   ├── auth.py         # JWT verification middleware
│   │   ├── config.py       # Application settings
│   │   └── database.py     # Neon PostgreSQL connection
│   ├── models/
│   │   ├── __init__.py
│   │   ├── task.py         # Task SQLModel
│   │   └── user.py         # User SQLModel
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── task.py         # Task Pydantic schemas
│   │   └── user.py         # User Pydantic schemas
│   ├── __init__.py
│   └── main.py             # FastAPI application
├── requirements.txt
├── run.py                  # Development server script
├── .env.example            # Environment variables template
└── README.md
```

## Setup

### 1. Create Virtual Environment

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate   # Windows
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your actual values
```

**Required environment variables:**

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | Neon PostgreSQL connection string |
| `BETTER_AUTH_SECRET` | Same secret as frontend Better Auth |
| `CORS_ORIGINS` | Frontend URL(s) for CORS |

### 4. Get Neon Database URL

1. Go to [Neon Console](https://console.neon.tech)
2. Create a project (or select existing)
3. Copy the connection string from Connection Details
4. Add `?sslmode=require` if not present

### 5. Run Development Server

```bash
python run.py
# or
uvicorn app.main:app --reload --port 8000
```

Server will be available at `http://localhost:8000`

## API Documentation

Interactive docs available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

All task endpoints require a valid JWT token in the `Authorization: Bearer <token>` header.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/api/{user_id}/tasks` | List all tasks |
| POST | `/api/{user_id}/tasks` | Create a new task |
| GET | `/api/{user_id}/tasks/{id}` | Get task details |
| PUT | `/api/{user_id}/tasks/{id}` | Update a task |
| DELETE | `/api/{user_id}/tasks/{id}` | Delete a task |
| PATCH | `/api/{user_id}/tasks/{id}/complete` | Toggle completion |

### Query Parameters for List Tasks

| Parameter | Type | Description |
|-----------|------|-------------|
| `status` | string | Filter: `completed` or `pending` |
| `sort` | string | Sort by: `created_at`, `due_date`, `priority`, `title` |
| `order` | string | Order: `asc` or `desc` |
| `page` | int | Page number (default: 1) |
| `page_size` | int | Items per page (default: 50, max: 100) |

### Example Requests

**Create Task:**
```bash
curl -X POST http://localhost:8000/api/{user_id}/tasks \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries", "priority": "high"}'
```

**List Tasks:**
```bash
curl http://localhost:8000/api/{user_id}/tasks?status=pending&sort=due_date \
  -H "Authorization: Bearer {token}"
```

## Authentication Flow

1. User signs in via Better Auth on frontend
2. Frontend receives JWT token
3. Frontend sends token with each API request
4. Backend verifies JWT using shared `BETTER_AUTH_SECRET`
5. Backend extracts user ID from token
6. Backend verifies path user_id matches token user_id
7. Backend returns only that user's data

## Security Features

- JWT token verification
- User isolation (each user only sees their own tasks)
- Path-based access control
- CORS protection
- SQL injection prevention via SQLModel/parameterized queries

## Development

### Running Tests

```bash
pytest
```

### Database Migrations

SQLModel creates tables automatically on startup. For schema changes:
1. Update models in `app/models/`
2. Restart the server

For production, consider using Alembic for migrations.
