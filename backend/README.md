# Todo Web Backend

A FastAPI backend for the hackathon-todo application with AI-powered chatbot capabilities for natural language task management.

## 🚀 Features

- **REST API**: FastAPI-based API for todo management operations
- **Authentication**: Better Auth integration with JWT token handling
- **AI Chatbot**: Natural language processing for todo management using OpenAI Agents SDK
- **MCP Tools**: Model Context Protocol integration for stateful task operations
- **Database**: SQLModel ORM with PostgreSQL support
- **Real-time Chat**: ChatKit integration for conversational UI

## 🏗️ Architecture

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
└── README.md               # This file
```

## 🛠️ Tech Stack

- **Framework**: FastAPI (Python 3.13+)
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **Database**: PostgreSQL (production) / SQLite (development)
- **Authentication**: Better Auth JWT integration
- **AI Framework**: OpenAI Agents SDK for AI reasoning
- **MCP Server**: Model Context Protocol for tool integration
- **Chat Interface**: ChatKit for conversational UI

## 📋 Environment Variables

Create a `.env` file in the backend directory with the following variables:

```bash
# Application Settings
APP_NAME="Todo Web API"
APP_VERSION="1.0.0"
DEBUG=true

# Database
DATABASE_URL=postgresql://user:pass@localhost/hackathon_todo

# Security
BETTER_AUTH_URL=http://localhost:3000
BETTER_AUTH_SECRET=your-better-auth-secret

# CORS
CORS_ORIGINS=["http://localhost:3000"]

# API Configuration
API_PREFIX=/api

# OpenAI API
OPENAI_API_KEY=your-openai-api-key-here
LLM_PROVIDER=openai
OPENAI_DEFAULT_MODEL=gpt-4o-mini

# AI Configuration
VERBOSE_AI_LOGGING=false
```

## 🚀 Running the Application

### Development

```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Run the backend
uvicorn app.main:app --reload --port 8000
```

### With AI Chatbot

```bash
# Set your OpenAI API key and run the backend
OPENAI_API_KEY=your-openai-api-key uvicorn app.main:app --reload --port 8000
```

### With Docker

```bash
# From the root directory
docker-compose up
```

## 🔧 API Endpoints

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

### Key Endpoints

- `GET /api/tasks` - List all tasks
- `POST /api/tasks` - Create a new task
- `PUT /api/tasks/{id}` - Update a task
- `DELETE /api/tasks/{id}` - Delete a task
- `POST /api/chat/{user_id}` - Chat with the AI assistant
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration

## 🤖 AI Chatbot Integration

The backend includes an AI-powered chatbot that allows users to manage their todo lists through natural language commands. The chatbot uses:

- **OpenAI Agents SDK** for natural language processing
- **MCP (Model Context Protocol) tools** for task operations
- **Conversation state management** with database persistence
- **Context tracking** for reference management

### Supported Natural Language Commands

- "Add a task to buy groceries"
- "Show me all my tasks"
- "Mark task 3 as complete"
- "Delete my task about the meeting"
- "Update my task to set a new due date"
- "Show me tasks due today"
- "List my high priority tasks"

## 🧪 Testing

```bash
# Run all tests
cd backend
pytest

# Run tests with coverage
pytest --cov=app
```

## 🔐 Authentication

The backend uses Better Auth for JWT-based authentication. All protected endpoints require a valid JWT token in the Authorization header:

```
Authorization: Bearer <jwt_token>
```

## 📊 Database Models

The application uses SQLModel for database operations with the following main models:

- `User` - User account information
- `Task` - Todo task with title, description, status, priority, due date
- `Conversation` - Chat conversation tracking
- `Message` - Individual chat messages with context references

## 🚀 Deployment

For production deployment:

1. Set up a PostgreSQL database
2. Configure environment variables
3. Run database migrations
4. Deploy with a WSGI/ASGI server like Gunicorn

```bash
# Production deployment
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run tests (`pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.