# Implementation Plan: Local Kubernetes Deployment

**Branch**: `001-k8s-deployment` | **Date**: 2025-12-30 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-k8s-deployment/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Deploy the Phase III Todo Chatbot application to a local Kubernetes cluster using Minikube, with containerized frontend and backend services managed via Helm charts. The implementation focuses on creating production-ready Dockerfiles, Kubernetes manifests, Helm charts with configurable values, and integration with AI-assisted DevOps tools (Docker AI/Gordon, kubectl-ai, Kagent) for enhanced developer experience. The deployment must maintain all Phase III functionality while supporting local development workflows including health checks, rolling updates, and persistent storage.

## Technical Context

**Language/Version**:
- Frontend: Node.js 20+ (Next.js 14)
- Backend: Python 3.13+ (FastAPI)
- Infrastructure: Bash scripting for automation

**Primary Dependencies**:
- Docker Desktop 4.53+ (container runtime)
- Minikube (local Kubernetes cluster)
- kubectl (Kubernetes CLI)
- Helm 3.x (package manager)
- kubectl-ai (AI-assisted kubectl - optional)
- Kagent (AI-powered Kubernetes operations - optional)
- Docker AI Agent/Gordon (AI-assisted Docker - optional)

**Storage**:
- PostgreSQL (running as Kubernetes deployment with PersistentVolumeClaim)
- Local Minikube persistent volumes for database data

**Testing**:
- NEEDS CLARIFICATION: Integration testing strategy for Kubernetes deployment
- NEEDS CLARIFICATION: Health check validation approach
- NEEDS CLARIFICATION: Helm chart testing methodology

**Target Platform**:
- Local development: Minikube on Windows/macOS/Linux
- Minimum: 8GB RAM, 4 CPU cores allocated to Minikube

**Project Type**: Web application (frontend + backend + database)

**Performance Goals**:
- Docker image build: <5 minutes for both services
- Helm deployment: <3 minutes to running state
- API response time: <1 second under local load (50 concurrent requests)
- Full deployment cycle: <15 minutes (build, deploy, test, update, rollback)

**Constraints**:
- Local resources only (no cloud dependencies)
- Single-node Minikube cluster (no multi-node testing)
- NodePort service type for external access (LoadBalancer optional with tunnel)
- AI tools optional with standard CLI fallbacks

**Scale/Scope**:
- 2 application services (frontend, backend)
- 1 database service (PostgreSQL)
- 3-5 Helm charts (app umbrella chart + subcharts)
- NEEDS CLARIFICATION: Number of Kubernetes resource types to manage
- NEEDS CLARIFICATION: ConfigMap/Secret strategy for environment-specific config

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Alignment with Constitution Principles

**I. Basic Task Management** ✅ PASS
- Requirement: Application must provide core functionality for managing todo items
- Compliance: FR-015 explicitly states "Application MUST maintain all Phase III Todo Chatbot functionality when deployed to Kubernetes"
- Impact: Kubernetes deployment is infrastructure-only; all task management features from Phase III remain unchanged

**II. Task Organization & Usability** ✅ PASS
- Requirement: Application should offer features that enhance task organization and user experience
- Compliance: All Phase III organization features (priorities, categories, search, filtering, sorting) are preserved through the containerization
- Impact: No changes to application logic; deployment layer is transparent to end users

**III. Advanced Task Automation & Reminders** ✅ PASS
- Requirement: Application may implement advanced features for task automation and reminders
- Compliance: Phase III chatbot features including recurring tasks and reminders are maintained via FR-015
- Impact: Kubernetes deployment must support background jobs/schedulers from Phase III (requires investigation in research phase)

### Complexity Assessment

**No violations detected** - This feature is purely infrastructure/deployment focused and does not modify application functionality. All constitution principles are satisfied by maintaining Phase III feature parity.

## Project Structure

### Documentation (this feature)

```text
specs/001-k8s-deployment/
├── spec.md                           # Feature specification
├── plan.md                           # This file (implementation plan)
├── research.md                       # Phase 0: Best practices research
├── data-model.md                     # Phase 1: Kubernetes entities and relationships
├── quickstart.md                     # Phase 1: Deployment guide
├── contracts/
│   ├── kubernetes-resources.yaml    # Complete K8s resource definitions
│   ├── helm-values-schema.yaml      # JSON schema for values.yaml
│   └── docker-interfaces.md         # Docker build/run contracts
└── checklists/
    └── requirements.md               # Quality validation checklist
```

### Source Code (repository root)

```text
specs/[###-feature]/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

This feature adds Kubernetes deployment infrastructure to the existing monorepo structure:

```text
backend/                              # Existing FastAPI backend
├── app/
│   ├── api/                         # API routes
│   ├── core/                        # Config, database, security
│   ├── models/                      # SQLModel entities
│   └── services/                    # Business logic
├── Dockerfile                        # NEW: Multi-stage production Dockerfile
├── .dockerignore                     # NEW: Docker build exclusions
└── requirements.txt                  # Existing dependencies

frontend/                             # Existing Next.js frontend
├── src/
│   ├── app/                         # Next.js 14 App Router
│   ├── components/                  # React components
│   └── lib/                         # Utilities
├── Dockerfile                        # NEW: Multi-stage production Dockerfile
├── .dockerignore                     # NEW: Docker build exclusions
└── package.json                      # Existing dependencies

helm-charts/                          # NEW: Helm chart directory
└── todo-app/                         # Main application chart
    ├── Chart.yaml                    # Chart metadata
    ├── values.yaml                   # Default configuration
    ├── values-dev.yaml               # Development overrides
    ├── values-prod.yaml              # Production overrides
    ├── templates/
    │   ├── _helpers.tpl              # Template helpers
    │   ├── backend-deployment.yaml   # Backend Deployment
    │   ├── backend-service.yaml      # Backend Service
    │   ├── frontend-deployment.yaml  # Frontend Deployment
    │   ├── frontend-service.yaml     # Frontend Service
    │   ├── postgres-deployment.yaml  # PostgreSQL Deployment
    │   ├── postgres-service.yaml     # PostgreSQL Service
    │   ├── postgres-pvc.yaml         # Persistent Volume Claim
    │   ├── configmap.yaml            # Application configuration
    │   ├── secret.yaml               # Credentials (template)
    │   ├── ingress.yaml              # Ingress (optional)
    │   ├── hpa.yaml                  # HorizontalPodAutoscaler (optional)
    │   ├── networkpolicy.yaml        # NetworkPolicy (optional)
    │   ├── serviceaccount.yaml       # ServiceAccount (optional)
    │   ├── migration-job.yaml        # Database migration Job
    │   └── cronjob.yaml              # Scheduled tasks CronJob
    └── tests/
        └── deployment_test.yaml      # Helm test hooks

k8s/                                  # NEW: Raw Kubernetes manifests (reference)
├── base/                             # Base manifests
│   ├── namespace.yaml
│   ├── configmap.yaml
│   └── secret-template.yaml
└── overlays/                         # Kustomize overlays (optional)
    ├── dev/
    └── prod/

scripts/                              # NEW: Deployment automation
├── build-images.sh                   # Build Docker images for Minikube
├── deploy.sh                         # Deploy to Minikube with Helm
├── health-check.sh                   # Verify deployment health
└── cleanup.sh                        # Clean up resources

.github/                              # NEW: CI/CD workflows
└── workflows/
    ├── docker-build.yml              # Build and push Docker images
    └── helm-test.yml                 # Helm chart validation

docker-compose.yml                    # NEW: Local development (before K8s)
.env.example                          # NEW: Environment variable template
```

**Structure Decision**:

This is a **web application deployment** (Option 2 extended) with the following additions:

1. **Dockerfiles** added to existing `backend/` and `frontend/` directories for containerization
2. **helm-charts/** directory for Helm-based Kubernetes deployments
3. **k8s/** directory for reference Kubernetes manifests and Kustomize overlays
4. **scripts/** directory for deployment automation
5. **docker-compose.yml** for local development workflow before Minikube

The existing monorepo structure (backend/ + frontend/) is preserved, with deployment infrastructure added as new top-level directories. This approach:
- Keeps application code separate from deployment configuration
- Allows independent versioning of Helm charts
- Supports multiple deployment targets (Minikube, cloud providers)
- Enables gradual migration from local development to containerized deployment

**Key Directories Explained:**

- **backend/Dockerfile**: Multi-stage build (builder → runner) with health check endpoints
- **frontend/Dockerfile**: Multi-stage Next.js build optimized for production
- **helm-charts/todo-app/**: Umbrella chart managing all application components
- **helm-charts/todo-app/templates/**: Kubernetes resource templates with configurable values
- **scripts/**: Bash automation for common deployment tasks (build, deploy, verify, cleanup)

## Complexity Tracking

No violations - Constitution Check passed. This is purely infrastructure deployment with no application logic changes.

## Post-Design Constitution Re-evaluation

*Re-checked after Phase 1 design completion*

**I. Basic Task Management** ✅ PASS (Confirmed)
- Design artifacts (data-model.md, contracts/) confirm no changes to task management functionality
- All Kubernetes resources preserve application behavior through containerization
- Health check endpoints added but do not modify task operations

**II. Task Organization & Usability** ✅ PASS (Confirmed)
- Helm charts maintain all Phase III organization features
- ConfigMap/Secret management preserves environment configuration
- No UI or API changes that would affect user experience

**III. Advanced Task Automation & Reminders** ✅ PASS (Confirmed)
- CronJob resource defined in contracts/kubernetes-resources.yaml supports scheduled tasks
- APScheduler integration documented in research.md for recurring reminders
- Background job support confirmed via Kubernetes Job and CronJob resources

**Final Verdict**: ✅ All constitution principles satisfied. No complexity violations introduced.

**Architectural Decisions Made**:
1. Helm-based deployment over raw Kubernetes manifests (improved configuration management)
2. Multi-stage Docker builds (optimized image size and security)
3. Three-tier health check strategy (startup/liveness/readiness probes)
4. CronJob + APScheduler for background tasks (versus Celery complexity)
5. ConfigMap/Secret externalization (environment-specific configuration)

**ADR Recommendation**: 📋 Consider documenting the following architectural decisions:
- "Helm vs Kustomize vs Raw Manifests for K8s deployment"
- "Health check strategy for microservices in Kubernetes"
- "Background task execution architecture (CronJob vs Celery)"

Run `/sp.adr <decision-title>` to document these decisions if needed.
