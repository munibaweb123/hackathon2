---
id: 008
title: Kubernetes Deployment Best Practices Research
stage: general
date: 2025-12-30
surface: agent
model: claude-sonnet-4-5-20250929
feature: 001-k8s-deployment
branch: 001-k8s-deployment
user: YOusuf Traders
command: research
labels: ["kubernetes", "helm", "deployment", "best-practices", "research", "docker", "containerization"]
links:
  spec: specs/001-k8s-deployment/research.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-k8s-deployment/research.md
tests:
  - none
---

## Prompt

Research and document best practices for the following Kubernetes deployment topics for a Todo Chatbot application (Next.js frontend + FastAPI backend + PostgreSQL):

**Research Topics:**

1. **Integration Testing Strategy for Kubernetes Deployment**
   - Best practices for testing Kubernetes deployments locally
   - Tools and frameworks (helm test, kubeval, conftest, etc.)
   - Testing approaches for service-to-service communication
   - Contract testing between frontend and backend in K8s

2. **Health Check Validation Approach**
   - Kubernetes liveness vs readiness vs startup probes
   - Best practices for FastAPI health endpoints
   - Best practices for Next.js health endpoints
   - Probe configuration (initial delay, timeout, period, failure threshold)

3. **Helm Chart Testing Methodology**
   - Helm chart linting and validation tools
   - Testing Helm templates (helm template, helm lint)
   - Chart testing frameworks (chart-testing, helm unittest)
   - Best practices for values.yaml validation

4. **Kubernetes Resource Types to Manage**
   - Essential resources for web app deployment (Deployment, Service, ConfigMap, Secret, PVC)
   - Optional but recommended resources (HPA, NetworkPolicy, ServiceAccount, Ingress)
   - Resource organization best practices

5. **ConfigMap/Secret Strategy**
   - When to use ConfigMap vs Secret vs environment variables
   - Externalized configuration patterns
   - Managing environment-specific configs (dev vs staging vs prod)
   - Better Auth configuration in Kubernetes (JWT secrets, database credentials)

6. **Background Jobs/Schedulers Support**
   - Running background tasks in Kubernetes (CronJob vs Job vs Deployment)
   - Task schedulers compatibility with Kubernetes (Celery, APScheduler, etc.)
   - Best practices for reminder/notification systems in K8s

**Output Format:**
For each topic, provide:
- Decision/Recommendation
- Rationale (why this approach)
- Alternatives considered (what else was evaluated)
- Implementation guidance (specific tools/patterns to use)

Create a consolidated research.md file at specs/001-k8s-deployment/research.md with all findings.

## Response snapshot

I conducted comprehensive web research on all six Kubernetes deployment topics for the Todo Chatbot application, gathering 2025 best practices from official documentation, industry blogs, and expert recommendations. The research covered:

**1. Integration Testing Strategy:**
- Multi-layered approach: Kubeval/Kubeconform for schema validation, Conftest for policy enforcement, Helm test hooks for lifecycle validation, and KUTTL for integration testing
- Contract testing using Pact for frontend-backend API contracts
- CI/CD integration with GitHub Actions
- Service-to-service communication testing with declarative KUTTL tests

**2. Health Check Validation:**
- Three-tier probe strategy: Startup probes for slow-starting apps, liveness probes for process health, readiness probes for dependency validation
- FastAPI endpoints: `/livez` (liveness), `/readyz` (readiness with DB checks), `/health` (general monitoring)
- Next.js endpoints: `/api/health/live`, `/api/health/ready` (backend connectivity)
- Configuration best practices: conservative initial delays, proper timeout/period settings, separation of liveness and readiness concerns

**3. Helm Chart Testing:**
- Four-layer approach: `helm lint` for syntax, Kubeconform for schema validation, `helm-unittest` for template logic testing, `chart-testing (ct)` for integration
- Values.yaml JSON schema validation
- Snapshot testing support
- CI/CD automation with chart-testing-action

**4. Kubernetes Resource Types:**
- Essential: Deployment, Service, ConfigMap, Secret, Ingress, PVC
- Recommended: HPA, ServiceAccount, NetworkPolicy, PodDisruptionBudget
- Optional: Job (migrations), CronJob (scheduled tasks), ResourceQuota, LimitRange
- Security-first approach with Pod Security Standards

**5. ConfigMap/Secret Strategy:**
- ConfigMaps for non-sensitive config (environment, CORS, feature flags, service endpoints)
- Secrets for sensitive data (DB credentials, JWT secrets, Better Auth secrets)
- External Secrets Operator recommended for production (AWS/GCP Secrets Manager integration)
- Sealed Secrets for GitOps workflows
- Versioned ConfigMaps pattern to trigger rolling updates
- Environment-specific values files (values-dev.yaml, values-prod.yaml)

**6. Background Jobs/Schedulers:**
- Kubernetes CronJob for periodic tasks (daily reminder digests)
- APScheduler embedded in FastAPI for dynamic user-specific reminders with PostgreSQL job store
- FastAPI BackgroundTasks for simple, short-lived async work
- Celery + Redis only for high-volume distributed tasks (>1000/min)
- Decision matrix based on use case complexity and volume

Created a comprehensive 46,000+ character research document at `specs/001-k8s-deployment/research.md` with:
- Detailed decision matrices and alternatives analysis
- Complete implementation examples with code snippets
- YAML templates for all resource types
- Best practices for 2025 with modern tooling
- Phase-based implementation roadmap (MVP → Production → Advanced)
- 30+ sources cited from official Kubernetes docs, industry experts, and recent blog posts

The document provides production-ready guidance for deploying the Todo Chatbot application (Next.js + FastAPI + PostgreSQL + Better Auth) to Kubernetes with Helm charts.

## Outcome

- ✅ Impact: Comprehensive research document created covering all 6 Kubernetes deployment topics with 2025 best practices, implementation examples, and production-ready guidance
- 🧪 Tests: No tests executed - this was a research and documentation task
- 📁 Files: Created specs/001-k8s-deployment/research.md (46,893 characters)
- 🔁 Next prompts: Review research findings, begin implementing Helm charts based on recommendations, create initial chart structure with essential resources
- 🧠 Reflection: Successfully consolidated modern Kubernetes best practices from 30+ authoritative sources into actionable guidance. The phased approach (MVP → Production → Advanced) provides a clear implementation roadmap. Research emphasizes security-first approach with External Secrets Operator, proper health checks with three-tier probe strategy, and starting simple with background jobs (CronJob + APScheduler) before scaling to Celery if needed.

## Evaluation notes (flywheel)

- Failure modes observed: None - research completed successfully with comprehensive coverage
- Graders run and results (PASS/FAIL): N/A - research task
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): Begin practical implementation of Helm chart structure based on research recommendations, starting with essential resources (Deployment, Service, ConfigMap, Secret)
