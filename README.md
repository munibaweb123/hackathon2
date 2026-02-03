# Hackathon Todo Application

A comprehensive full-stack todo application demonstrating progressive software development from a simple console app to a cloud-native distributed system. Built as a multi-phase hackathon project showcasing modern development practices.

## Project Overview

| Phase | Name | Status | Description |
|-------|------|--------|-------------|
| Phase I | Console App | ✅ Completed | CLI-based todo app with in-memory/JSON storage |
| Phase II | Web App | ✅ Completed | Full-stack REST API with authentication |
| Phase III | AI Chatbot | ✅ Completed | Natural language task management |
| Phase IV | Kubernetes | ✅ Completed | Local K8s deployment with Helm charts |
| Phase V | Cloud Deploy | 🚧 In Progress | Production cloud deployment with event-driven architecture |

---

## Phase I: Console Application

A feature-rich command-line todo application built with Python 3.13+ and UV package manager.

### Features
- Add, view, update, and delete tasks
- Mark tasks as complete/incomplete
- Set priority levels (high/medium/low)
- Organize tasks with categories
- Search tasks by keyword
- Filter tasks by status, priority, category, date range
- Sort tasks by due date, priority, title, or creation date
- **Recurring Tasks**: Daily, weekly, monthly, or custom intervals
- **Due Time Support**: Set specific times alongside dates
- **Reminder Notifications**: Console notifications before deadlines
- **Persistent Storage**: JSON file storage

### Tech Stack
- **Language**: Python 3.13+
- **Package Manager**: UV
- **Console UI**: Rich (tables, panels, formatting)
- **Date Handling**: python-dateutil
- **Storage**: JSON files

### Usage
```bash
cd src/todo_app
uv run python -m todo_app
```

---

## Phase II: Web Application

Full-stack web application with REST API, authentication, and modern frontend.

### Architecture
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    Frontend     │────▶│     Backend     │────▶│    Database     │
│   Next.js 14    │     │    FastAPI      │     │   PostgreSQL    │
│   TypeScript    │     │    SQLModel     │     │   (Neon Cloud)  │
│   Tailwind CSS  │     │   Better Auth   │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### Backend Features
- RESTful API with FastAPI
- JWT authentication via Better Auth
- SQLModel ORM with PostgreSQL
- Task CRUD operations with user isolation
- Alembic database migrations
- Structured JSON logging

### Frontend Features
- Next.js 14 with App Router
- TypeScript for type safety
- Tailwind CSS for styling
- ShadCN UI components
- Better Auth session management
- Responsive design

### Tech Stack
| Component | Technology |
|-----------|------------|
| Backend Framework | FastAPI |
| ORM | SQLModel |
| Database | PostgreSQL (Neon Serverless) |
| Authentication | Better Auth |
| Frontend Framework | Next.js 14 |
| Styling | Tailwind CSS |
| UI Components | ShadCN |

### Running Locally
```bash
# Backend
cd backend
uv sync
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

### Docker Compose
```bash
docker-compose up
```

---

## Phase III: AI Chatbot

AI-powered chatbot interface for managing todos through natural language.

### Features
- Natural language task management
- Conversation context maintenance
- Multi-turn conversations
- Intelligent intent recognition
- Real-time task operations

### Supported Commands
- "Add a task to buy groceries"
- "Show me all my tasks"
- "What's pending?"
- "Mark task 3 as complete"
- "Update that task to include eggs"
- "What have I completed?"

### Architecture
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│     User        │────▶│   AI Chatbot    │────▶│   Task Service  │
│   Interface     │     │  OpenAI/MCP     │     │   (FastAPI)     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │  Conversation   │
                        │    Storage      │
                        └─────────────────┘
```

### Tech Stack
- **AI Framework**: OpenAI Agents SDK
- **Protocol**: MCP (Model Context Protocol)
- **Backend**: FastAPI with existing task services
- **Storage**: PostgreSQL for conversations

---

## Phase IV: Kubernetes Deployment

Local Kubernetes deployment using Minikube with AI-assisted DevOps tools.

### Features
- Containerized frontend and backend
- Helm charts for deployment management
- AI-assisted DevOps with kubectl-ai and Kagent
- Health checks and readiness probes
- Persistent volume storage
- Rolling updates with zero downtime

### Architecture
```
┌─────────────────────────────────────────────────────┐
│                  Minikube Cluster                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │  Frontend   │  │   Backend   │  │ PostgreSQL  │  │
│  │    Pod      │  │    Pod      │  │    Pod      │  │
│  │  (NodePort) │  │  (Service)  │  │   (PVC)     │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────┘
```

### Prerequisites
- Docker Desktop 4.53+
- Minikube
- kubectl
- Helm 3.x
- kubectl-ai (optional)
- Kagent (optional)

### Deployment Commands
```bash
# Start Minikube
minikube start --memory=4096 --cpus=2

# Build images in Minikube
eval $(minikube docker-env)
docker build -t todo-backend:latest ./backend
docker build -t todo-frontend:latest ./frontend

# Deploy with Helm
helm install todo-app ./helm-charts

# Access the application
minikube service todo-frontend
```

### AI-Assisted Operations
```bash
# Using kubectl-ai
kubectl-ai "deploy the todo frontend with 2 replicas"
kubectl-ai "check why the pods are failing"

# Using Kagent
kagent "analyze the cluster health"
kagent "optimize resource allocation"
```

---

## Phase V: Advanced Cloud Deployment

Production-ready cloud-native deployment with event-driven architecture.

### Features

#### Advanced Task Features
- Due dates with time precision
- Reminder notifications (in-app & email)
- Recurring tasks (daily, weekly, monthly, custom)
- Priority levels (High, Medium, Low, None)
- Tags for organization
- Full-text search
- Advanced filtering and sorting
- Real-time sync across devices

#### Event-Driven Architecture
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Task Events │────▶│   Kafka     │────▶│ Consumers   │
│  (Pub/Sub)  │     │ (Redpanda)  │     │             │
└─────────────┘     └─────────────┘     └─────────────┘
                                               │
              ┌────────────────────────────────┼────────────────────────────────┐
              ▼                                ▼                                ▼
     ┌─────────────────┐              ┌─────────────────┐              ┌─────────────────┐
     │  Notification   │              │   Recurring     │              │   Audit Log     │
     │    Service      │              │  Task Service   │              │    Service      │
     └─────────────────┘              └─────────────────┘              └─────────────────┘
```

#### Infrastructure
- **Runtime**: Dapr (Distributed Application Runtime)
- **Messaging**: Redpanda Cloud (Kafka-compatible)
- **Cloud Providers**: DigitalOcean (DOKS), Google Cloud (GKE), or Azure (AKS)
- **CI/CD**: GitHub Actions
- **Monitoring**: Cloud-native observability stack

### Tech Stack
| Component | Technology |
|-----------|------------|
| Event Broker | Redpanda Cloud (Kafka) |
| Service Mesh | Dapr |
| Container Orchestration | Kubernetes (DOKS/GKE/AKS) |
| CI/CD | GitHub Actions |
| Monitoring | Cloud-native solutions |
| Database | PostgreSQL (Neon Serverless) |

### Local Development with Dapr
```bash
# Initialize Dapr
dapr init

# Run with Dapr sidecar
dapr run --app-id todo-backend --app-port 8000 -- uvicorn app.main:app
```

### Cloud Deployment
```bash
# Deploy to GKE
gcloud container clusters get-credentials todo-cluster --zone us-central1-a
helm install todo-app ./helm-charts -f values-production.yaml

# Deploy to DOKS
doctl kubernetes cluster kubeconfig save todo-cluster
helm install todo-app ./helm-charts -f values-production.yaml

# Deploy to AKS
az aks get-credentials --resource-group todo-rg --name todo-cluster
helm install todo-app ./helm-charts -f values-production.yaml
```

---

## Project Structure

```
hackathon_2/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/               # Route handlers
│   │   ├── auth/              # Authentication
│   │   ├── core/              # Config, database
│   │   ├── models/            # SQLModel entities
│   │   ├── schemas/           # Pydantic schemas
│   │   └── services/          # Business logic
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                   # Next.js frontend
│   ├── src/
│   │   ├── app/               # App Router pages
│   │   ├── components/        # UI components
│   │   ├── hooks/             # Custom hooks
│   │   ├── lib/               # Utilities
│   │   └── services/          # Service layer
│   ├── Dockerfile
│   └── package.json
├── src/                        # Console app (Phase I)
│   └── todo_app/
├── specs/                      # Feature specifications
│   ├── 001-todo-console-app/
│   ├── 001-hackathon-todo-monorepo/
│   ├── 001-ai-chatbot-mcp/
│   ├── 001-k8s-deployment/
│   └── 004-advanced-cloud-deploy/
├── helm-charts/                # Kubernetes Helm charts
├── k8s/                        # Kubernetes manifests
├── .github/workflows/          # CI/CD pipelines
├── docker-compose.yml
└── README.md
```

---

## Quick Start

### Prerequisites
- Python 3.13+
- Node.js 20+
- Docker & Docker Compose
- UV package manager

### Development Setup
```bash
# Clone the repository
git clone https://github.com/munibaweb123/hackathon2.git
cd hackathon_2

# Start with Docker Compose (recommended)
docker-compose up

# Or run services individually:

# Backend
cd backend
uv sync
uvicorn app.main:app --reload

# Frontend (in another terminal)
cd frontend
npm install
npm run dev
```

### Access Points
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgresql://user:pass@host:5432/db
BETTER_AUTH_SECRET=your-secret-key
BETTER_AUTH_URL=http://localhost:3000
FRONTEND_URL=http://localhost:3000
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=your-secret-key
```

---

## Testing

```bash
# Backend tests
cd backend
uv run pytest

# With coverage
uv run pytest --cov=app --cov-report=term-missing

# Frontend tests
cd frontend
npm test
```

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

MIT License - See [LICENSE](LICENSE) for details.

---

## Author

**Muniba Ahmed**
- GitHub: [@munibaweb123](https://github.com/munibaweb123)
