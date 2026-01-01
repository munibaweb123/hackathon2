# Docker Build and Runtime Interfaces
**Feature**: 001-k8s-deployment
**Created**: 2025-12-30

## Overview

This document defines the Docker build and runtime contracts for the Todo Chatbot application components. Each service has specific requirements for Dockerfile structure, environment variables, exposed ports, and health check endpoints.

---

## 1. Frontend (Next.js) Docker Interface

### Build Requirements

#### Dockerfile Structure (Multi-Stage Build)

```dockerfile
# Stage 1: Dependencies
FROM node:20-alpine AS deps
WORKDIR /app

# Install dependencies based on package manager
COPY package.json package-lock.json* ./
RUN npm ci --only=production

# Stage 2: Builder
FROM node:20-alpine AS builder
WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Build arguments
ARG NEXT_PUBLIC_API_URL
ARG NEXT_PUBLIC_APP_VERSION
ARG NODE_ENV=production

ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_APP_VERSION=$NEXT_PUBLIC_APP_VERSION
ENV NODE_ENV=$NODE_ENV

# Build Next.js application
RUN npm run build

# Stage 3: Runner
FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production

# Add non-root user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1000 nextjs

# Copy built application
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
COPY --from=builder --chown=nextjs:nodejs /app/public ./public

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
```

#### Build Arguments

| Argument | Required | Default | Description | Example |
|----------|----------|---------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Yes | - | Backend API endpoint | `http://todo-backend:8000` |
| `NEXT_PUBLIC_APP_VERSION` | No | `1.0.0` | Application version | `v1.2.3` |
| `NODE_ENV` | No | `production` | Node environment | `production`, `development` |

#### Build Commands

```bash
# Build for local development (Docker)
docker build \
  --build-arg NEXT_PUBLIC_API_URL=http://localhost:8000 \
  --build-arg NEXT_PUBLIC_APP_VERSION=dev \
  -t todo-frontend:dev \
  ./frontend

# Build for Minikube (using Minikube's Docker daemon)
eval $(minikube docker-env)
docker build \
  --build-arg NEXT_PUBLIC_API_URL=http://todo-backend:8000 \
  --build-arg NEXT_PUBLIC_APP_VERSION=v1.0.0 \
  -t todo-frontend:v1.0.0 \
  ./frontend

# Build for production
docker build \
  --build-arg NEXT_PUBLIC_API_URL=https://api.todo.example.com \
  --build-arg NEXT_PUBLIC_APP_VERSION=v1.0.0 \
  --platform linux/amd64 \
  -t ghcr.io/yourorg/todo-frontend:v1.0.0 \
  ./frontend
```

### Runtime Requirements

#### Environment Variables

| Variable | Required | Default | Description | Example |
|----------|----------|---------|-------------|---------|
| `NODE_ENV` | Yes | `production` | Node.js environment | `production`, `development` |
| `PORT` | No | `3000` | HTTP server port | `3000` |
| `HOSTNAME` | No | `0.0.0.0` | Bind address | `0.0.0.0`, `localhost` |
| `BETTER_AUTH_SECRET` | Yes | - | Better Auth secret key (32+ chars) | `<32-char-random-string>` |
| `BETTER_AUTH_URL` | Yes | - | Application base URL | `https://todo.example.com` |
| `BETTER_AUTH_TRUST_HOST` | No | `false` | Trust proxy headers | `true` (for Kubernetes) |
| `DATABASE_URL` | Yes | - | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `NEXT_PUBLIC_API_URL` | Build-time | - | Backend API URL (baked into build) | `http://todo-backend:8000` |

#### Exposed Ports

| Port | Protocol | Purpose |
|------|----------|---------|
| 3000 | TCP | HTTP server for Next.js application |

#### Health Check Endpoints

| Endpoint | Method | Purpose | Success Code | Response Time |
|----------|--------|---------|--------------|---------------|
| `/api/health/live` | GET | Liveness probe (process running) | 200 | <100ms |
| `/api/health/ready` | GET | Readiness probe (backend connectivity) | 200 | <500ms |
| `/api/health` | GET | General health (version info) | 200 | <100ms |

#### Health Endpoint Implementations

```typescript
// app/api/health/live/route.ts
export async function GET() {
  return Response.json({ status: 'alive' }, { status: 200 });
}

// app/api/health/ready/route.ts
export async function GET() {
  try {
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://todo-backend:8000';
    const response = await fetch(`${backendUrl}/health`, {
      signal: AbortSignal.timeout(5000),
    });

    if (!response.ok) {
      return Response.json(
        { status: 'not_ready', reason: 'backend_unavailable' },
        { status: 503 }
      );
    }

    return Response.json({ status: 'ready' }, { status: 200 });
  } catch (error) {
    return Response.json(
      { status: 'not_ready', reason: error.message },
      { status: 503 }
    );
  }
}

// app/api/health/route.ts
export async function GET() {
  return Response.json({
    status: 'healthy',
    version: process.env.NEXT_PUBLIC_APP_VERSION || '1.0.0',
    service: 'todo-frontend',
  });
}
```

#### Volume Mounts

| Mount Path | Purpose | Type | Required |
|------------|---------|------|----------|
| `/tmp` | Temporary files | emptyDir | Yes |
| `/.next/cache` | Next.js cache | emptyDir | Recommended |

#### User and Security

- Container MUST run as non-root user (UID 1000, GID 1001)
- Read-only root filesystem (with writable `/tmp`)
- Drop all Linux capabilities
- No privilege escalation

---

## 2. Backend (FastAPI) Docker Interface

### Build Requirements

#### Dockerfile Structure (Multi-Stage Build)

```dockerfile
# Stage 1: Builder
FROM python:3.13-slim AS builder
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runner
FROM python:3.13-slim AS runner
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/* \
    && addgroup --system --gid 1001 appgroup \
    && adduser --system --uid 1000 --gid 1001 appuser

# Copy Python packages from builder
COPY --from=builder --chown=appuser:appgroup /root/.local /home/appuser/.local

# Copy application code
COPY --chown=appuser:appgroup ./app /app/app
COPY --chown=appuser:appgroup ./alembic /app/alembic
COPY --chown=appuser:appgroup ./alembic.ini /app/

# Set PATH for user-installed packages
ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

USER appuser

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/livez')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Build Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `PYTHON_VERSION` | No | `3.13` | Python version |
| `REQUIREMENTS_FILE` | No | `requirements.txt` | Requirements file path |

#### Build Commands

```bash
# Build for local development
docker build -t todo-backend:dev ./backend

# Build for Minikube
eval $(minikube docker-env)
docker build -t todo-backend:v1.0.0 ./backend

# Build for production
docker build \
  --platform linux/amd64 \
  -t ghcr.io/yourorg/todo-backend:v1.0.0 \
  ./backend
```

### Runtime Requirements

#### Environment Variables

| Variable | Required | Default | Description | Example |
|----------|----------|---------|-------------|---------|
| `DATABASE_URL` | Yes | - | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `JWT_SECRET` | Yes | - | JWT signing key (32+ chars) | `<32-char-random-string>` |
| `JWT_ALGORITHM` | No | `HS256` | JWT signing algorithm | `HS256`, `RS256` |
| `JWT_EXPIRATION` | No | `3600` | JWT expiration in seconds | `3600` |
| `ENVIRONMENT` | No | `production` | Application environment | `development`, `staging`, `production` |
| `CORS_ORIGINS` | No | `*` | CORS allowed origins | `https://todo.example.com` |
| `LOG_LEVEL` | No | `INFO` | Logging level | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `LOG_FORMAT` | No | `json` | Log output format | `json`, `text` |

#### Exposed Ports

| Port | Protocol | Purpose |
|------|----------|---------|
| 8000 | TCP | HTTP server for FastAPI application |

#### Health Check Endpoints

| Endpoint | Method | Purpose | Success Code | Response Time |
|----------|--------|---------|--------------|---------------|
| `/livez` | GET | Liveness probe (app process running) | 200 | <100ms |
| `/readyz` | GET | Readiness probe (database connectivity) | 200 | <500ms |
| `/health` | GET | General health (version, service info) | 200 | <100ms |

#### Health Endpoint Implementations

```python
# app/api/health.py
from fastapi import APIRouter, status, Response
from sqlmodel import Session, select
from app.core.database import engine
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/livez", status_code=status.HTTP_200_OK)
async def liveness():
    """
    Liveness probe - checks if the application process is running.
    Should NEVER check external dependencies.
    """
    return {"status": "alive"}

@router.get("/readyz", status_code=status.HTTP_200_OK)
async def readiness():
    """
    Readiness probe - checks if the app can serve traffic.
    Validates database connectivity and critical dependencies.
    """
    health_status = {
        "status": "ready",
        "checks": {}
    }

    # Check database connection
    try:
        with Session(engine) as session:
            session.exec(select(1)).first()
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status["checks"]["database"] = "unhealthy"
        health_status["status"] = "not_ready"
        return Response(
            content=str(health_status),
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )

    return health_status

@router.get("/health", status_code=status.HTTP_200_OK)
async def health():
    """
    General health endpoint for monitoring/observability.
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "todo-backend"
    }
```

#### Volume Mounts

| Mount Path | Purpose | Type | Required |
|------------|---------|------|----------|
| `/tmp` | Temporary files | emptyDir | Yes |

#### User and Security

- Container MUST run as non-root user (UID 1000, GID 1001)
- Read-only root filesystem (with writable `/tmp`)
- Drop all Linux capabilities
- No privilege escalation

---

## 3. PostgreSQL Docker Interface

### Build Requirements

#### Base Image

```dockerfile
# Use official PostgreSQL Alpine image
FROM postgres:15-alpine

# Optional: Custom initialization scripts
COPY ./init-scripts/*.sql /docker-entrypoint-initdb.d/
```

#### Build Commands

```bash
# Use official PostgreSQL image (no custom build needed)
docker pull postgres:15-alpine
```

### Runtime Requirements

#### Environment Variables

| Variable | Required | Default | Description | Example |
|----------|----------|---------|-------------|---------|
| `POSTGRES_USER` | Yes | - | Database superuser | `todo_user` |
| `POSTGRES_PASSWORD` | Yes | - | Superuser password | `<secure-password>` |
| `POSTGRES_DB` | Yes | - | Default database name | `todo_db` |
| `PGDATA` | No | `/var/lib/postgresql/data` | Data directory | `/var/lib/postgresql/data/pgdata` |

#### Exposed Ports

| Port | Protocol | Purpose |
|------|----------|---------|
| 5432 | TCP | PostgreSQL database server |

#### Health Check

```bash
# Liveness check
pg_isready -U $POSTGRES_USER -d $POSTGRES_DB

# Readiness check (same as liveness for PostgreSQL)
pg_isready -U $POSTGRES_USER -d $POSTGRES_DB
```

#### Volume Mounts

| Mount Path | Purpose | Type | Required |
|------------|---------|------|----------|
| `/var/lib/postgresql/data` | Database files | PVC | Yes |

#### Configuration Files (Optional)

Create custom `postgresql.conf` for production tuning:

```conf
# postgresql.conf (mounted as ConfigMap)
max_connections = 100
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 2621kB
min_wal_size = 1GB
max_wal_size = 4GB
```

---

## 4. Docker Compose Interface (Local Development)

### docker-compose.yml

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: todo-postgres
    environment:
      POSTGRES_USER: todo_user
      POSTGRES_PASSWORD: todo_password
      POSTGRES_DB: todo_db
      PGDATA: /var/lib/postgresql/data/pgdata
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U todo_user -d todo_db"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: todo-backend
    environment:
      DATABASE_URL: postgresql://todo_user:todo_password@postgres:5432/todo_db
      JWT_SECRET: dev-jwt-secret-min-32-characters-long
      ENVIRONMENT: development
      CORS_ORIGINS: http://localhost:3000
      LOG_LEVEL: DEBUG
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - ./backend/app:/app/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        NEXT_PUBLIC_API_URL: http://localhost:8000
        NEXT_PUBLIC_APP_VERSION: dev
    container_name: todo-frontend
    environment:
      BETTER_AUTH_SECRET: dev-better-auth-secret-min-32-chars
      BETTER_AUTH_URL: http://localhost:3000
      BETTER_AUTH_TRUST_HOST: "true"
      DATABASE_URL: postgresql://todo_user:todo_password@postgres:5432/todo_db
    ports:
      - "3000:3000"
    depends_on:
      - backend
    volumes:
      - ./frontend/src:/app/src
      - ./frontend/public:/app/public

volumes:
  postgres_data:
```

### Usage Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and start
docker-compose up --build -d

# Run database migrations
docker-compose exec backend alembic upgrade head

# Access PostgreSQL shell
docker-compose exec postgres psql -U todo_user -d todo_db

# Stop and remove volumes (data loss)
docker-compose down -v
```

---

## 5. Image Build Best Practices

### Multi-Stage Builds

- Use multi-stage builds to minimize final image size
- Separate builder stage from runner stage
- Only copy necessary artifacts to final stage

### Layer Caching

```dockerfile
# Good: Copy only dependency files first
COPY package.json package-lock.json ./
RUN npm ci

# Then copy application code
COPY . .

# Bad: Copying everything invalidates cache on any file change
COPY . .
RUN npm install
```

### Security Scanning

```bash
# Scan image for vulnerabilities
docker scan todo-backend:v1.0.0

# Use Trivy
trivy image todo-backend:v1.0.0

# Use Grype
grype todo-backend:v1.0.0
```

### Image Tagging Strategy

| Tag Type | Format | Use Case | Example |
|----------|--------|----------|---------|
| **Latest** | `latest` | Local development only | `todo-frontend:latest` |
| **Version** | `v{major}.{minor}.{patch}` | Production releases | `todo-frontend:v1.2.3` |
| **Git SHA** | `git-{short-sha}` | Traceability | `todo-frontend:git-abc1234` |
| **Branch** | `{branch-name}` | Feature branches | `todo-frontend:feature-auth` |
| **Semantic + SHA** | `v{version}-{sha}` | Production with traceability | `todo-frontend:v1.0.0-abc1234` |

---

## 6. Kubernetes Integration

### Image Pull Configuration

```yaml
# Using image pull secrets
apiVersion: v1
kind: Secret
metadata:
  name: ghcr-pull-secret
type: kubernetes.io/dockerconfigjson
data:
  .dockerconfigjson: <base64-encoded-docker-config>

---
# Deployment using pull secret
spec:
  template:
    spec:
      imagePullSecrets:
        - name: ghcr-pull-secret
      containers:
        - name: backend
          image: ghcr.io/yourorg/todo-backend:v1.0.0
          imagePullPolicy: IfNotPresent
```

### Resource Constraints

```yaml
containers:
  - name: backend
    image: ghcr.io/yourorg/todo-backend:v1.0.0
    resources:
      limits:
        cpu: 1000m      # 1 CPU core
        memory: 1Gi     # 1 GiB RAM
      requests:
        cpu: 250m       # 0.25 CPU cores
        memory: 256Mi   # 256 MiB RAM
```

### Security Context

```yaml
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 1000
    seccompProfile:
      type: RuntimeDefault
  containers:
    - name: backend
      securityContext:
        allowPrivilegeEscalation: false
        readOnlyRootFilesystem: true
        capabilities:
          drop:
            - ALL
```

---

## 7. CI/CD Integration

### GitHub Actions Build Workflow

```yaml
name: Build and Push Docker Images

on:
  push:
    branches:
      - main
    tags:
      - 'v*'

jobs:
  build-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/${{ github.repository }}/todo-backend
          tags: |
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha,prefix={{version}}-,suffix=

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: ./backend
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

---

## Summary

This document defines the complete Docker interface contracts for:

1. **Frontend (Next.js)** - Multi-stage build, health endpoints, runtime configuration
2. **Backend (FastAPI)** - Multi-stage build, health checks, database connectivity
3. **PostgreSQL** - Standard image, configuration, persistence
4. **Docker Compose** - Local development environment
5. **Build Best Practices** - Security, caching, tagging
6. **Kubernetes Integration** - Pull secrets, resources, security
7. **CI/CD** - Automated builds and publishing

All components follow production-ready patterns with proper security, health checks, and observability.
