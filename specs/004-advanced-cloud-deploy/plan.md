# Implementation Plan: Phase V - Advanced Cloud Deployment

**Branch**: `004-advanced-cloud-deploy` | **Date**: 2026-01-04 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-advanced-cloud-deploy/spec.md`

## Summary

Implement advanced task management features (recurring tasks, due dates, reminders, priorities, tags, search/filter/sort), evolve to event-driven microservices architecture using Kafka (Redpanda Cloud) and Dapr, deploy locally on Minikube and to production-grade managed Kubernetes (DOKS/GKE/AKS) with CI/CD, monitoring, and logging.

## Technical Context

**Language/Version**: Python 3.13+ (backend), TypeScript/Node.js 20+ (frontend)
**Primary Dependencies**: FastAPI, SQLModel, Dapr SDK, aiokafka, Next.js 14, Better Auth, Tailwind CSS
**Storage**: PostgreSQL (Neon Serverless), Redpanda Cloud (Kafka-compatible)
**Testing**: pytest (backend), Jest/Vitest (frontend), k6 (load testing)
**Target Platform**: Kubernetes (Minikube local, DOKS/GKE/AKS production)
**Project Type**: Web application (monorepo with backend + frontend + microservices)
**Performance Goals**: <500ms p95 latency, 100 concurrent users, 60s max reminder delivery
**Constraints**: 99.5% uptime, <2s search, <5s real-time sync, 15min CI/CD pipeline
**Scale/Scope**: 10,000 tasks per user, 3 microservices (notification, recurring, audit)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Basic Task Management | PASS | FR-001 to FR-009 cover CRUD, status toggle, due dates |
| II. Task Organization & Usability | PASS | FR-005 (priorities), FR-006 (tags), FR-007-009 (search/filter/sort) |
| III. Advanced Task Automation | PASS | FR-003/004 (recurring), FR-002 (reminders with notifications) |
| Governance | PASS | All FRs traceable to constitution principles |

**Gate Result**: PASSED - All constitution principles satisfied.

## Project Structure

### Documentation (this feature)

```text
specs/004-advanced-cloud-deploy/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (OpenAPI specs)
│   ├── tasks-api.yaml
│   ├── notifications-api.yaml
│   └── events-schema.yaml
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── api/
│   │   ├── tasks.py           # Task CRUD endpoints
│   │   ├── reminders.py       # Reminder management
│   │   └── search.py          # Search/filter/sort endpoints
│   ├── models/
│   │   ├── task.py            # Extended Task model
│   │   ├── recurrence.py      # RecurrencePattern model
│   │   └── audit.py           # AuditLog model
│   ├── services/
│   │   ├── task_service.py    # Business logic
│   │   ├── event_publisher.py # Kafka/Dapr event publishing
│   │   └── search_service.py  # Full-text search
│   ├── events/
│   │   ├── handlers.py        # Event subscription handlers
│   │   └── schemas.py         # Event payload schemas
│   └── dapr/
│       └── components/        # Dapr component configs
├── services/
│   ├── notification/          # Notification microservice
│   │   ├── main.py
│   │   ├── email_sender.py
│   │   └── websocket_broadcaster.py
│   ├── recurring/             # Recurring task microservice
│   │   ├── main.py
│   │   └── task_generator.py
│   └── audit/                 # Audit log microservice
│       ├── main.py
│       └── log_writer.py
└── tests/
    ├── unit/
    ├── integration/
    └── e2e/

frontend/
├── src/
│   ├── app/
│   │   ├── tasks/
│   │   │   ├── page.tsx       # Task list with filters
│   │   │   └── [id]/page.tsx  # Task detail with recurrence
│   │   └── settings/
│   │       └── notifications/ # Notification preferences
│   ├── components/
│   │   ├── tasks/
│   │   │   ├── TaskForm.tsx   # Due date, recurrence, priority
│   │   │   ├── TaskFilters.tsx
│   │   │   └── TagSelector.tsx
│   │   └── notifications/
│   │       └── NotificationBadge.tsx
│   ├── hooks/
│   │   ├── use-realtime-sync.ts
│   │   └── use-notifications.ts
│   └── services/
│       └── websocket-client.ts
└── tests/

infra/
├── helm/
│   ├── todo-app/              # Main Helm chart
│   │   ├── Chart.yaml
│   │   ├── values.yaml
│   │   └── templates/
│   │       ├── backend-deployment.yaml
│   │       ├── frontend-deployment.yaml
│   │       ├── notification-deployment.yaml
│   │       ├── recurring-deployment.yaml
│   │       └── audit-deployment.yaml
│   └── dapr-components/       # Dapr component definitions
│       ├── pubsub.yaml        # Kafka/Redpanda
│       ├── statestore.yaml    # PostgreSQL
│       ├── bindings.yaml      # Cron triggers
│       └── secrets.yaml       # K8s secrets
├── docker/
│   ├── backend.Dockerfile
│   ├── frontend.Dockerfile
│   └── docker-compose.local.yml
├── minikube/
│   └── setup.sh
└── cloud/
    ├── doks/
    ├── gke/
    └── aks/

.github/
└── workflows/
    ├── ci.yml                 # Test & lint
    ├── cd-staging.yml         # Deploy to staging
    └── cd-production.yml      # Deploy to production
```

**Structure Decision**: Web application with monorepo structure. Backend contains main API plus 3 microservices (notification, recurring, audit). Frontend is Next.js 14. Infrastructure code in `/infra` with Helm charts for Kubernetes and Dapr components.

## Complexity Tracking

> No constitution violations requiring justification.

| Aspect | Justification |
|--------|---------------|
| 3 Microservices | Required by FR-011/012/013 for event-driven architecture; each handles distinct domain |
| Dapr Sidecars | Required by FR-017/018 for infrastructure abstraction; reduces vendor lock-in |
| Kafka/Redpanda | Required by FR-010/014 for event streaming; enables real-time sync and decoupling |

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              KUBERNETES CLUSTER                              │
│                                                                              │
│  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────────────────┐│
│  │    Frontend     │   │    Backend      │   │        KAFKA TOPICS         ││
│  │    (Next.js)    │──▶│   (FastAPI)     │──▶│  task-events | reminders    ││
│  │    + Dapr       │   │    + Dapr       │   │  task-updates               ││
│  └─────────────────┘   └────────┬────────┘   └──────────┬──────────────────┘│
│                                 │                       │                    │
│         ┌───────────────────────┼───────────────────────┘                    │
│         │                       │                                            │
│         ▼                       ▼                       ▼                    │
│  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐            │
│  │  Notification   │   │   Recurring     │   │     Audit       │            │
│  │    Service      │   │     Service     │   │    Service      │            │
│  │    + Dapr       │   │    + Dapr       │   │    + Dapr       │            │
│  └────────┬────────┘   └─────────────────┘   └─────────────────┘            │
│           │                                                                  │
│           ▼                                                                  │
│  ┌─────────────────┐                                                         │
│  │  Email + WS     │                                                         │
│  │  Notifications  │                                                         │
│  └─────────────────┘                                                         │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                         DAPR COMPONENTS                                  ││
│  │  pubsub.kafka | state.postgresql | bindings.cron | secretstores.k8s    ││
│  └─────────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
            ┌─────────────┐                 ┌─────────────┐
            │  Neon DB    │                 │  Redpanda   │
            │ (PostgreSQL)│                 │   Cloud     │
            └─────────────┘                 └─────────────┘
```

## Kafka Topics & Event Flow

| Topic | Producer | Consumer(s) | Purpose |
|-------|----------|-------------|---------|
| task-events | Backend API | Recurring Service, Audit Service | All task CRUD operations |
| reminders | Backend API | Notification Service | Scheduled reminder triggers |
| task-updates | Backend API | WebSocket Service | Real-time client sync |

## Dapr Components

| Component | Type | Purpose |
|-----------|------|---------|
| kafka-pubsub | pubsub.kafka | Event streaming via Redpanda |
| statestore | state.postgresql | Conversation/task state |
| reminder-cron | bindings.cron | Scheduled reminder checks |
| kubernetes-secrets | secretstores.kubernetes | API keys, DB credentials |

## Deployment Strategy

### Local (Minikube)
1. Install Minikube and Dapr CLI
2. Deploy Dapr to Minikube: `dapr init -k`
3. Deploy Redpanda (single node) via Helm
4. Deploy application via Helm charts

### Production (DOKS/GKE/AKS)
1. Provision managed Kubernetes cluster
2. Configure kubectl context
3. Install Dapr with production config
4. Connect to Redpanda Cloud
5. Deploy via GitHub Actions CI/CD

## CI/CD Pipeline

```yaml
Stages:
  1. Test (pytest, jest, lint)
  2. Build (Docker images)
  3. Push (Container registry)
  4. Deploy Staging (auto on PR merge)
  5. Integration Tests
  6. Deploy Production (manual approval)
```

## Monitoring & Observability

| Component | Tool | Purpose |
|-----------|------|---------|
| Metrics | Prometheus + Grafana | CPU, memory, latency dashboards |
| Logging | Loki or Cloud-native | Centralized log aggregation |
| Tracing | Jaeger (via Dapr) | Distributed tracing |
| Alerting | Prometheus Alertmanager | Incident notifications |
