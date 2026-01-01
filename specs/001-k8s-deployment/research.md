# Kubernetes Deployment Best Practices Research
## Todo Chatbot Application (Next.js + FastAPI + PostgreSQL)

**Research Date:** 2025-12-30
**Application Stack:** Next.js 14 (Frontend), FastAPI (Backend), PostgreSQL (Database), Better Auth (Authentication)
**Deployment Target:** Kubernetes with Helm Charts

---

## 1. Integration Testing Strategy for Kubernetes Deployment

### Decision/Recommendation

**Multi-layered testing approach combining:**
- **Kubeval/Kubeconform** for schema validation of Kubernetes manifests
- **Conftest** for custom policy enforcement using OPA Rego
- **Helm test hooks** for lifecycle validation (post-install, post-upgrade)
- **KUTTL** for declarative integration testing of complete deployments
- **Contract testing** using Pact for frontend-backend API contracts
- Integration into CI/CD pipelines (GitHub Actions/GitLab CI)

### Rationale

Modern Kubernetes testing requires validation at multiple levels to catch different types of issues:

1. **Static validation** catches syntax and schema errors before deployment
2. **Policy enforcement** ensures security and compliance requirements are met
3. **Integration tests** validate service-to-service communication works correctly
4. **Contract tests** prevent breaking changes between frontend and backend APIs

The 2025 best practice is to implement testing as part of automated CI/CD pipelines to provide quick feedback on every commit or pull request.

### Alternatives Considered

| Approach | Pros | Cons | Decision |
|----------|------|------|----------|
| Manual kubectl apply testing | Simple, no tooling required | Error-prone, not repeatable, no CI integration | ❌ Rejected |
| Only Helm lint | Fast, built-in | Only validates template syntax, misses runtime issues | ❌ Insufficient alone |
| Full E2E testing only | Most realistic | Slow, expensive, late feedback | ❌ Too slow for every PR |
| Multi-layer approach | Catches issues early, fast feedback, comprehensive | Requires multiple tools | ✅ **Recommended** |

### Implementation Guidance

#### A. Schema Validation with Kubeconform

```bash
# Install kubeconform (preferred over kubeval in 2025)
brew install kubeconform

# Validate rendered Helm templates
helm template my-app ./charts/my-app | kubeconform -strict -summary

# Validate with CRD support
kubeconform -schema-location default \
  -schema-location 'https://raw.githubusercontent.com/datreeio/CRDs-catalog/main/{{.Group}}/{{.ResourceKind}}_{{.ResourceAPIVersion}}.json' \
  -summary manifest.yaml
```

**Why Kubeconform over Kubeval:** Kubeconform supports CRD validation and is actively maintained as of 2025, while Kubeval is deprecated.

#### B. Policy Enforcement with Conftest

```bash
# Install conftest
brew install conftest

# Example policy (policy/deployment.rego)
package main

deny[msg] {
  input.kind == "Deployment"
  not input.spec.template.spec.securityContext.runAsNonRoot
  msg := "Containers must not run as root"
}

deny[msg] {
  input.kind == "Deployment"
  not input.spec.template.spec.containers[_].resources.limits
  msg := "Containers must have resource limits"
}

# Run policy checks
helm template ./charts/my-app | conftest test -p policy/ -
```

#### C. Helm Test Hooks

Create test pods that run post-deployment validation:

```yaml
# templates/tests/test-connection.yaml
apiVersion: v1
kind: Pod
metadata:
  name: "{{ include "app.fullname" . }}-test-connection"
  annotations:
    "helm.sh/hook": test
spec:
  containers:
    - name: wget
      image: busybox
      command: ['wget']
      args: ['{{ include "app.fullname" . }}:{{ .Values.service.port }}/health']
  restartPolicy: Never
```

```bash
# Run Helm tests
helm test my-release
```

#### D. Contract Testing with Pact

For Next.js frontend and FastAPI backend:

```typescript
// Frontend (consumer) contract test
import { PactV3 } from '@pact-foundation/pact';

const provider = new PactV3({
  consumer: 'nextjs-frontend',
  provider: 'fastapi-backend',
});

describe('Task API Contract', () => {
  it('should get tasks list', async () => {
    await provider
      .given('tasks exist')
      .uponReceiving('a request for tasks')
      .withRequest({
        method: 'GET',
        path: '/api/tasks',
        headers: { Authorization: 'Bearer token' },
      })
      .willRespondWith({
        status: 200,
        body: [
          { id: 1, title: 'Task 1', completed: false }
        ],
      });

    // Test implementation
  });
});
```

```python
# Backend (provider) verification
from pact import Verifier

verifier = Verifier(provider='fastapi-backend',
                   provider_base_url='http://localhost:8000')

verifier.verify_pacts('./pacts/nextjs-frontend-fastapi-backend.json')
```

#### E. CI/CD Integration (GitHub Actions)

```yaml
# .github/workflows/k8s-test.yml
name: Kubernetes Testing

on: [pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Validate manifests with Kubeconform
        run: |
          helm template ./charts/todo-app | kubeconform -strict -summary

      - name: Run policy checks with Conftest
        run: |
          helm template ./charts/todo-app | conftest test -p policy/ -

      - name: Lint Helm chart
        run: helm lint ./charts/todo-app

      - name: Run Helm unit tests
        uses: helm/chart-testing-action@v2
        with:
          command: lint
          config: ct-config.yaml
```

#### F. Service-to-Service Communication Testing

For testing Next.js → FastAPI → PostgreSQL communication in Kubernetes:

```yaml
# Use KUTTL for declarative integration tests
# tests/e2e/00-install.yaml
apiVersion: kuttl.dev/v1beta1
kind: TestStep
commands:
  - command: helm install todo-app ./charts/todo-app
    namespaced: true

# tests/e2e/01-assert.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-frontend
status:
  readyReplicas: 1
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-backend
status:
  readyReplicas: 1
---
# tests/e2e/02-test-api.yaml
apiVersion: v1
kind: Pod
metadata:
  name: api-test
spec:
  containers:
    - name: curl
      image: curlimages/curl
      command:
        - sh
        - -c
        - |
          curl -f http://todo-backend:8000/health &&
          curl -f http://todo-frontend:3000/api/health
  restartPolicy: Never
```

---

## 2. Health Check Validation Approach

### Decision/Recommendation

**Implement three-tier probe strategy:**

1. **Startup Probe** - For slow-starting applications (ML models, large initializations)
2. **Liveness Probe** - Basic process health check
3. **Readiness Probe** - Deep dependency validation (database, external services)

**FastAPI Health Endpoints:**
- `/livez` - Liveness probe (app process running)
- `/readyz` - Readiness probe (dependencies healthy)
- `/health` - General health endpoint for monitoring

**Next.js Health Endpoints:**
- `/api/health/live` - Process health
- `/api/health/ready` - Backend connectivity check

### Rationale

**Separation of Concerns:** Liveness probes should check only if the application process is running, while readiness probes validate that the service can handle traffic. This prevents cascading failures where a temporary database issue causes unnecessary pod restarts.

**Startup Probes Prevent Premature Restarts:** Applications that load large ML models or perform extensive initialization need startup probes to avoid being killed during legitimate startup time.

**2025 Best Practice:** With increasing adoption of service meshes and AI/ML workloads, health probes must consider not just binary uptime but partial failures, timeouts, and dependency health.

### Alternatives Considered

| Approach | Pros | Cons | Decision |
|----------|------|------|----------|
| Single /health endpoint for all probes | Simple, one endpoint | Can't distinguish liveness vs readiness | ❌ Rejected |
| Liveness checks dependencies | Comprehensive | Causes unnecessary restarts on transient DB issues | ❌ Dangerous |
| No startup probe | Simpler configuration | Slow apps get killed during startup | ❌ Risk for ML/AI apps |
| Three-tier probe strategy | Proper separation, handles all cases | More endpoints to maintain | ✅ **Recommended** |

### Implementation Guidance

#### A. FastAPI Health Endpoints

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

    # Check Redis (if using for sessions/cache)
    # try:
    #     redis_client.ping()
    #     health_status["checks"]["redis"] = "healthy"
    # except Exception as e:
    #     health_status["checks"]["redis"] = "unhealthy"
    #     health_status["status"] = "degraded"  # Still serve traffic

    return health_status

@router.get("/health", status_code=status.HTTP_200_OK)
async def health():
    """
    General health endpoint for monitoring/observability.
    Can include metrics, versions, etc.
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "todo-backend"
    }
```

#### B. Next.js Health Endpoints

```typescript
// app/api/health/live/route.ts
export async function GET() {
  return Response.json({ status: 'alive' }, { status: 200 });
}

// app/api/health/ready/route.ts
export async function GET() {
  try {
    // Check backend connectivity
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://todo-backend:8000';
    const response = await fetch(`${backendUrl}/health`, {
      signal: AbortSignal.timeout(5000), // 5s timeout
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

#### C. Kubernetes Probe Configuration

```yaml
# Frontend Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-frontend
spec:
  template:
    spec:
      containers:
        - name: nextjs
          image: todo-frontend:latest
          ports:
            - containerPort: 3000
          startupProbe:
            httpGet:
              path: /api/health/live
              port: 3000
            failureThreshold: 30    # 30 failures * 2s = 60s max startup time
            periodSeconds: 2
          livenessProbe:
            httpGet:
              path: /api/health/live
              port: 3000
            initialDelaySeconds: 10
            periodSeconds: 10
            timeoutSeconds: 3
            failureThreshold: 3     # Restart after 3 consecutive failures
          readinessProbe:
            httpGet:
              path: /api/health/ready
              port: 3000
            initialDelaySeconds: 5
            periodSeconds: 5
            timeoutSeconds: 5
            failureThreshold: 3     # Remove from load balancer after 3 failures

# Backend Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-backend
spec:
  template:
    spec:
      containers:
        - name: fastapi
          image: todo-backend:latest
          ports:
            - containerPort: 8000
          startupProbe:
            httpGet:
              path: /livez
              port: 8000
            failureThreshold: 30
            periodSeconds: 2
          livenessProbe:
            httpGet:
              path: /livez
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 10
            timeoutSeconds: 3
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /readyz
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 5
            timeoutSeconds: 5
            failureThreshold: 3
          resources:
            requests:
              memory: "256Mi"
              cpu: "250m"
            limits:
              memory: "512Mi"
              cpu: "500m"
```

#### D. Probe Configuration Best Practices (2025)

1. **Start Conservative, Tune Based on Metrics:**
   - Begin with longer `initialDelaySeconds` and `periodSeconds`
   - Monitor probe failures in production
   - Gradually reduce delays as you gain confidence

2. **Timeout Considerations:**
   - `timeoutSeconds` should be less than `periodSeconds`
   - For database checks, account for query latency (3-5s timeout)
   - Never set timeout > 10s for web applications

3. **Failure Threshold Tuning:**
   - `failureThreshold: 3` is typical for most apps
   - For critical services with known cold starts, increase to 5-10
   - Combined with `periodSeconds`, determines total grace period

4. **Common Pitfall - Avoid:**
   ```yaml
   # ❌ BAD: Liveness probe checks database
   livenessProbe:
     httpGet:
       path: /health  # This checks DB, Redis, etc.
   ```

   **Result:** Temporary DB connection issue → Liveness fails → Pod restarts → More load on DB → Cascading failure

   ```yaml
   # ✅ GOOD: Liveness checks only process health
   livenessProbe:
     httpGet:
       path: /livez  # Only checks if process is alive
   readinessProbe:
     httpGet:
       path: /readyz  # Checks dependencies
   ```

---

## 3. Helm Chart Testing Methodology

### Decision/Recommendation

**Four-layer Helm chart testing approach:**

1. **helm lint** - Template syntax validation
2. **Kubeconform** - Kubernetes schema validation
3. **helm-unittest** - Unit testing for template logic (conditions, loops)
4. **chart-testing (ct)** - Integration testing for full chart lifecycle

All integrated into CI/CD with chart-testing-action for automated validation on pull requests.

### Rationale

**Defense in Depth:** Each layer catches different types of issues:
- `helm lint` catches basic template errors quickly
- Kubeconform validates against Kubernetes API schemas
- `helm-unittest` validates conditional logic and value handling
- `chart-testing (ct)` simulates real installation scenarios

**2025 Best Practice:** The Helm community has converged on this multi-layer approach, with `helm-unittest` and `ct` becoming standard tools in the ecosystem.

### Alternatives Considered

| Approach | Pros | Cons | Decision |
|----------|------|------|----------|
| helm lint only | Fast, built-in | Misses logic errors, no K8s validation | ❌ Insufficient |
| Manual testing with kind | Realistic | Slow, not repeatable, hard to CI | ❌ Too manual |
| Snapshot testing only | Catches unintended changes | Doesn't validate correctness | ❌ Incomplete |
| Four-layer approach | Comprehensive, fast feedback | More tooling to learn | ✅ **Recommended** |

### Implementation Guidance

#### A. Directory Structure

```
charts/todo-app/
├── Chart.yaml
├── values.yaml
├── values-dev.yaml
├── values-staging.yaml
├── values-prod.yaml
├── templates/
│   ├── _helpers.tpl
│   ├── deployment-frontend.yaml
│   ├── deployment-backend.yaml
│   ├── service-frontend.yaml
│   ├── service-backend.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── ingress.yaml
│   └── tests/
│       └── test-connection.yaml
├── tests/
│   ├── deployment_test.yaml        # helm-unittest tests
│   ├── service_test.yaml
│   └── ingress_test.yaml
└── ci/
    ├── ct-config.yaml               # chart-testing config
    └── lintconf.yaml
```

#### B. Helm Lint

```bash
# Basic linting
helm lint charts/todo-app

# Lint with specific values file
helm lint charts/todo-app -f charts/todo-app/values-prod.yaml

# Strict mode (treat warnings as errors)
helm lint --strict charts/todo-app
```

#### C. Kubeconform Validation

```bash
# Validate rendered templates
helm template todo-app charts/todo-app | kubeconform -strict -summary

# With custom values
helm template todo-app charts/todo-app -f values-prod.yaml | \
  kubeconform -strict -summary -verbose

# CI script
#!/bin/bash
set -e

echo "Validating Helm templates with Kubeconform..."

for values_file in charts/todo-app/values*.yaml; do
  echo "Testing with $values_file"
  helm template todo-app charts/todo-app -f "$values_file" | \
    kubeconform -strict -summary
done

echo "✅ All templates validated successfully"
```

#### D. Helm Unittest

Install helm-unittest plugin:
```bash
helm plugin install https://github.com/helm-unittest/helm-unittest
```

Example unit test:
```yaml
# charts/todo-app/tests/deployment_test.yaml
suite: test deployment
templates:
  - deployment-backend.yaml
tests:
  - it: should create deployment with correct name
    asserts:
      - isKind:
          of: Deployment
      - equal:
          path: metadata.name
          value: RELEASE-NAME-todo-backend

  - it: should set replica count from values
    set:
      backend.replicaCount: 3
    asserts:
      - equal:
          path: spec.replicas
          value: 3

  - it: should include database env vars
    asserts:
      - contains:
          path: spec.template.spec.containers[0].env
          content:
            name: DATABASE_URL
            valueFrom:
              secretKeyRef:
                name: RELEASE-NAME-todo-secret
                key: database-url

  - it: should not run as root
    asserts:
      - equal:
          path: spec.template.spec.securityContext.runAsNonRoot
          value: true

  - it: should have resource limits when production mode
    set:
      environment: production
      backend.resources.limits.cpu: "1000m"
      backend.resources.limits.memory: "1Gi"
    asserts:
      - equal:
          path: spec.template.spec.containers[0].resources.limits.cpu
          value: "1000m"
      - equal:
          path: spec.template.spec.containers[0].resources.limits.memory
          value: "1Gi"

  - it: should enable HPA when autoscaling is enabled
    template: hpa-backend.yaml
    set:
      backend.autoscaling.enabled: true
      backend.autoscaling.minReplicas: 2
      backend.autoscaling.maxReplicas: 10
    asserts:
      - isKind:
          of: HorizontalPodAutoscaler
      - equal:
          path: spec.minReplicas
          value: 2
      - equal:
          path: spec.maxReplicas
          value: 10

# Test ingress configuration
  - it: should create ingress with correct host
    template: ingress.yaml
    set:
      ingress.enabled: true
      ingress.hosts[0].host: todo.example.com
    asserts:
      - isKind:
          of: Ingress
      - equal:
          path: spec.rules[0].host
          value: todo.example.com

  - it: should enable TLS when configured
    template: ingress.yaml
    set:
      ingress.enabled: true
      ingress.tls[0].secretName: todo-tls
      ingress.tls[0].hosts[0]: todo.example.com
    asserts:
      - equal:
          path: spec.tls[0].secretName
          value: todo-tls
```

Run unit tests:
```bash
# Run all tests
helm unittest charts/todo-app

# Run with color output and verbose
helm unittest -c -f 'tests/*.yaml' charts/todo-app

# Update snapshots
helm unittest -u charts/todo-app
```

#### E. Chart Testing (ct)

Configuration file:
```yaml
# charts/todo-app/ci/ct-config.yaml
chart-dirs:
  - charts
target-branch: main
validate-maintainers: false
chart-repos:
  - bitnami=https://charts.bitnami.com/bitnami
helm-extra-args: --timeout 600s
```

```bash
# Install ct
brew install chart-testing

# Lint changed charts
ct lint --config charts/todo-app/ci/ct-config.yaml

# Install and test charts in kind cluster
ct install --config charts/todo-app/ci/ct-config.yaml
```

#### F. Values Validation

Create a JSON schema for values.yaml:
```yaml
# charts/todo-app/values.schema.json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["backend", "frontend", "database"],
  "properties": {
    "backend": {
      "type": "object",
      "required": ["replicaCount", "image"],
      "properties": {
        "replicaCount": {
          "type": "integer",
          "minimum": 1,
          "maximum": 20
        },
        "image": {
          "type": "object",
          "required": ["repository", "tag"],
          "properties": {
            "repository": { "type": "string" },
            "tag": { "type": "string" }
          }
        }
      }
    },
    "environment": {
      "type": "string",
      "enum": ["development", "staging", "production"]
    }
  }
}
```

Helm automatically validates values against this schema.

#### G. CI/CD Integration

```yaml
# .github/workflows/helm-test.yml
name: Lint and Test Helm Charts

on:
  pull_request:
    paths:
      - 'charts/**'

jobs:
  lint-test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Helm
        uses: azure/setup-helm@v4
        with:
          version: v3.14.0

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install Kubeconform
        run: |
          wget https://github.com/yannh/kubeconform/releases/latest/download/kubeconform-linux-amd64.tar.gz
          tar xf kubeconform-linux-amd64.tar.gz
          sudo mv kubeconform /usr/local/bin/

      - name: Install helm-unittest
        run: |
          helm plugin install https://github.com/helm-unittest/helm-unittest

      - name: Run helm lint
        run: |
          helm lint charts/todo-app
          helm lint charts/todo-app -f charts/todo-app/values-prod.yaml

      - name: Run Kubeconform validation
        run: |
          helm template todo-app charts/todo-app | kubeconform -strict -summary

      - name: Run helm-unittest
        run: |
          helm unittest -c charts/todo-app

      - name: Set up chart-testing
        uses: helm/chart-testing-action@v2

      - name: Run chart-testing (lint)
        run: ct lint --config charts/todo-app/ci/ct-config.yaml

      - name: Create kind cluster
        uses: helm/kind-action@v1

      - name: Run chart-testing (install)
        run: ct install --config charts/todo-app/ci/ct-config.yaml
```

---

## 4. Kubernetes Resource Types to Manage

### Decision/Recommendation

**Essential Resources (Must Have):**
- **Deployment** - For frontend and backend applications
- **Service** - For internal communication and load balancing
- **ConfigMap** - For non-sensitive configuration
- **Secret** - For sensitive data (DB credentials, JWT secrets)
- **Ingress** - For external access with TLS
- **PersistentVolumeClaim** - For PostgreSQL data persistence

**Recommended Resources:**
- **HorizontalPodAutoscaler (HPA)** - For auto-scaling based on CPU/memory
- **ServiceAccount** - For RBAC and security isolation
- **NetworkPolicy** - For network segmentation and security
- **PodDisruptionBudget (PDB)** - For high availability during updates

**Optional Resources:**
- **Job** - For database migrations
- **CronJob** - For scheduled reminder notifications
- **ResourceQuota** - For namespace resource limits (multi-tenant clusters)
- **LimitRange** - For enforcing resource constraints

### Rationale

**Essential resources** form the minimum viable deployment for a web application. Without these, the application cannot function or will lack basic security/persistence.

**Recommended resources** enhance production-readiness by providing:
- Automatic scaling (HPA)
- Security isolation (ServiceAccount, NetworkPolicy)
- High availability (PDB)

**Optional resources** address specific needs:
- Database migrations during deployment (Job)
- Background tasks (CronJob)
- Multi-tenancy constraints (ResourceQuota, LimitRange)

**2025 Best Practice:** Modern deployments prioritize security (NetworkPolicy, ServiceAccount) and operability (HPA, PDB) from the start rather than adding them later.

### Alternatives Considered

| Approach | Pros | Cons | Decision |
|----------|------|------|----------|
| Minimal (Deployment + Service only) | Simple, fast to deploy | No persistence, poor security | ❌ Not production-ready |
| StatefulSet for backend | Stable network identity | Unnecessary complexity for stateless apps | ❌ Overkill for API |
| DaemonSet for services | Runs on every node | Wrong use case for web apps | ❌ Not applicable |
| Deployment + full recommended set | Production-ready, secure, scalable | More resources to manage | ✅ **Recommended** |

### Implementation Guidance

#### A. Essential Resources Structure

```
charts/todo-app/templates/
├── deployment-frontend.yaml      # Next.js deployment
├── deployment-backend.yaml       # FastAPI deployment
├── deployment-postgres.yaml      # PostgreSQL (if not using external DB)
├── service-frontend.yaml         # ClusterIP service for frontend
├── service-backend.yaml          # ClusterIP service for backend
├── service-postgres.yaml         # ClusterIP service for database
├── configmap.yaml                # Application configuration
├── secret.yaml                   # Sensitive credentials
├── ingress.yaml                  # External access with TLS
└── pvc-postgres.yaml             # Persistent storage for PostgreSQL
```

#### B. Deployment Template Example

```yaml
# deployment-backend.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "todo-app.fullname" . }}-backend
  labels:
    {{- include "todo-app.labels" . | nindent 4 }}
    app.kubernetes.io/component: backend
spec:
  {{- if not .Values.backend.autoscaling.enabled }}
  replicas: {{ .Values.backend.replicaCount }}
  {{- end }}
  selector:
    matchLabels:
      {{- include "todo-app.selectorLabels" . | nindent 6 }}
      app.kubernetes.io/component: backend
  template:
    metadata:
      annotations:
        checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
        checksum/secret: {{ include (print $.Template.BasePath "/secret.yaml") . | sha256sum }}
      labels:
        {{- include "todo-app.selectorLabels" . | nindent 8 }}
        app.kubernetes.io/component: backend
    spec:
      serviceAccountName: {{ include "todo-app.serviceAccountName" . }}
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      containers:
        - name: fastapi
          image: "{{ .Values.backend.image.repository }}:{{ .Values.backend.image.tag | default .Chart.AppVersion }}"
          imagePullPolicy: {{ .Values.backend.image.pullPolicy }}
          ports:
            - name: http
              containerPort: 8000
              protocol: TCP
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: {{ include "todo-app.fullname" . }}-secret
                  key: database-url
            - name: JWT_SECRET
              valueFrom:
                secretKeyRef:
                  name: {{ include "todo-app.fullname" . }}-secret
                  key: jwt-secret
            - name: ENVIRONMENT
              valueFrom:
                configMapKeyRef:
                  name: {{ include "todo-app.fullname" . }}-config
                  key: environment
            - name: LOG_LEVEL
              value: {{ .Values.backend.logLevel | quote }}
          livenessProbe:
            httpGet:
              path: /livez
              port: http
            initialDelaySeconds: 10
            periodSeconds: 10
            timeoutSeconds: 3
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /readyz
              port: http
            initialDelaySeconds: 5
            periodSeconds: 5
            timeoutSeconds: 5
            failureThreshold: 3
          resources:
            {{- toYaml .Values.backend.resources | nindent 12 }}
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop:
                - ALL
          volumeMounts:
            - name: tmp
              mountPath: /tmp
      volumes:
        - name: tmp
          emptyDir: {}
```

#### C. Service Template Example

```yaml
# service-backend.yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ include "todo-app.fullname" . }}-backend
  labels:
    {{- include "todo-app.labels" . | nindent 4 }}
    app.kubernetes.io/component: backend
spec:
  type: {{ .Values.backend.service.type }}
  ports:
    - port: {{ .Values.backend.service.port }}
      targetPort: http
      protocol: TCP
      name: http
  selector:
    {{- include "todo-app.selectorLabels" . | nindent 4 }}
    app.kubernetes.io/component: backend
```

#### D. Ingress Template Example

```yaml
# ingress.yaml
{{- if .Values.ingress.enabled -}}
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {{ include "todo-app.fullname" . }}
  labels:
    {{- include "todo-app.labels" . | nindent 4 }}
  annotations:
    {{- if .Values.ingress.className }}
    kubernetes.io/ingress.class: {{ .Values.ingress.className }}
    {{- end }}
    {{- if .Values.ingress.tls }}
    cert-manager.io/cluster-issuer: {{ .Values.ingress.certManager.clusterIssuer | default "letsencrypt-prod" }}
    {{- end }}
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
    {{- with .Values.ingress.annotations }}
    {{- toYaml . | nindent 4 }}
    {{- end }}
spec:
  {{- if .Values.ingress.tls }}
  tls:
    {{- range .Values.ingress.tls }}
    - hosts:
        {{- range .hosts }}
        - {{ . | quote }}
        {{- end }}
      secretName: {{ .secretName }}
    {{- end }}
  {{- end }}
  rules:
    - host: {{ .Values.ingress.host }}
      http:
        paths:
          - path: /api
            pathType: Prefix
            backend:
              service:
                name: {{ include "todo-app.fullname" . }}-backend
                port:
                  number: {{ .Values.backend.service.port }}
          - path: /
            pathType: Prefix
            backend:
              service:
                name: {{ include "todo-app.fullname" . }}-frontend
                port:
                  number: {{ .Values.frontend.service.port }}
{{- end }}
```

#### E. HorizontalPodAutoscaler Template

```yaml
# hpa-backend.yaml
{{- if .Values.backend.autoscaling.enabled }}
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {{ include "todo-app.fullname" . }}-backend
  labels:
    {{- include "todo-app.labels" . | nindent 4 }}
    app.kubernetes.io/component: backend
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {{ include "todo-app.fullname" . }}-backend
  minReplicas: {{ .Values.backend.autoscaling.minReplicas }}
  maxReplicas: {{ .Values.backend.autoscaling.maxReplicas }}
  metrics:
    {{- if .Values.backend.autoscaling.targetCPUUtilizationPercentage }}
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: {{ .Values.backend.autoscaling.targetCPUUtilizationPercentage }}
    {{- end }}
    {{- if .Values.backend.autoscaling.targetMemoryUtilizationPercentage }}
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: {{ .Values.backend.autoscaling.targetMemoryUtilizationPercentage }}
    {{- end }}
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Percent
          value: 50
          periodSeconds: 15
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
        - type: Percent
          value: 100
          periodSeconds: 15
        - type: Pods
          value: 4
          periodSeconds: 15
      selectPolicy: Max
{{- end }}
```

#### F. NetworkPolicy Template

```yaml
# networkpolicy-backend.yaml
{{- if .Values.networkPolicy.enabled }}
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: {{ include "todo-app.fullname" . }}-backend
  labels:
    {{- include "todo-app.labels" . | nindent 4 }}
spec:
  podSelector:
    matchLabels:
      {{- include "todo-app.selectorLabels" . | nindent 6 }}
      app.kubernetes.io/component: backend
  policyTypes:
    - Ingress
    - Egress
  ingress:
    # Allow traffic from frontend
    - from:
        - podSelector:
            matchLabels:
              {{- include "todo-app.selectorLabels" . | nindent 14 }}
              app.kubernetes.io/component: frontend
      ports:
        - protocol: TCP
          port: 8000
    # Allow traffic from ingress controller
    - from:
        - namespaceSelector:
            matchLabels:
              name: ingress-nginx
      ports:
        - protocol: TCP
          port: 8000
  egress:
    # Allow DNS
    - to:
        - namespaceSelector:
            matchLabels:
              name: kube-system
      ports:
        - protocol: UDP
          port: 53
    # Allow database access
    - to:
        - podSelector:
            matchLabels:
              {{- include "todo-app.selectorLabels" . | nindent 14 }}
              app.kubernetes.io/component: postgres
      ports:
        - protocol: TCP
          port: 5432
    # Allow external API calls (if needed)
    - to:
        - namespaceSelector: {}
      ports:
        - protocol: TCP
          port: 443
{{- end }}
```

#### G. PodDisruptionBudget Template

```yaml
# pdb-backend.yaml
{{- if .Values.backend.podDisruptionBudget.enabled }}
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: {{ include "todo-app.fullname" . }}-backend
  labels:
    {{- include "todo-app.labels" . | nindent 4 }}
    app.kubernetes.io/component: backend
spec:
  {{- if .Values.backend.podDisruptionBudget.minAvailable }}
  minAvailable: {{ .Values.backend.podDisruptionBudget.minAvailable }}
  {{- else }}
  maxUnavailable: {{ .Values.backend.podDisruptionBudget.maxUnavailable | default 1 }}
  {{- end }}
  selector:
    matchLabels:
      {{- include "todo-app.selectorLabels" . | nindent 6 }}
      app.kubernetes.io/component: backend
{{- end }}
```

#### H. Database Migration Job

```yaml
# job-migration.yaml
{{- if .Values.migration.enabled }}
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ include "todo-app.fullname" . }}-migration-{{ .Release.Revision }}
  labels:
    {{- include "todo-app.labels" . | nindent 4 }}
  annotations:
    "helm.sh/hook": pre-upgrade,pre-install
    "helm.sh/hook-weight": "-5"
    "helm.sh/hook-delete-policy": before-hook-creation
spec:
  template:
    metadata:
      labels:
        {{- include "todo-app.selectorLabels" . | nindent 8 }}
        app.kubernetes.io/component: migration
    spec:
      restartPolicy: OnFailure
      serviceAccountName: {{ include "todo-app.serviceAccountName" . }}
      containers:
        - name: migration
          image: "{{ .Values.backend.image.repository }}:{{ .Values.backend.image.tag | default .Chart.AppVersion }}"
          command:
            - alembic
            - upgrade
            - head
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: {{ include "todo-app.fullname" . }}-secret
                  key: database-url
          resources:
            limits:
              cpu: 500m
              memory: 512Mi
            requests:
              cpu: 100m
              memory: 128Mi
{{- end }}
```

#### I. Values File Organization

```yaml
# values.yaml (production defaults)
global:
  environment: production

backend:
  replicaCount: 3
  image:
    repository: ghcr.io/yourorg/todo-backend
    tag: ""  # Defaults to chart appVersion
    pullPolicy: IfNotPresent

  service:
    type: ClusterIP
    port: 8000

  resources:
    limits:
      cpu: 1000m
      memory: 1Gi
    requests:
      cpu: 250m
      memory: 256Mi

  autoscaling:
    enabled: true
    minReplicas: 3
    maxReplicas: 10
    targetCPUUtilizationPercentage: 70
    targetMemoryUtilizationPercentage: 80

  podDisruptionBudget:
    enabled: true
    minAvailable: 2

  logLevel: INFO

frontend:
  replicaCount: 2
  image:
    repository: ghcr.io/yourorg/todo-frontend
    tag: ""
    pullPolicy: IfNotPresent

  service:
    type: ClusterIP
    port: 3000

  resources:
    limits:
      cpu: 500m
      memory: 512Mi
    requests:
      cpu: 100m
      memory: 128Mi

  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 8
    targetCPUUtilizationPercentage: 70

database:
  # For managed PostgreSQL (recommended)
  external:
    enabled: true
    host: postgres.example.com
    port: 5432
    database: todo_db
    username: todo_user
    # Password in secret

  # For in-cluster PostgreSQL (development only)
  internal:
    enabled: false
    persistence:
      enabled: true
      size: 10Gi
      storageClass: standard

ingress:
  enabled: true
  className: nginx
  host: todo.example.com
  annotations:
    nginx.ingress.kubernetes.io/rate-limit: "100"
  tls:
    - secretName: todo-tls
      hosts:
        - todo.example.com
  certManager:
    enabled: true
    clusterIssuer: letsencrypt-prod

networkPolicy:
  enabled: true

serviceAccount:
  create: true
  annotations: {}
  name: ""

migration:
  enabled: true

config:
  corsOrigins: "https://todo.example.com"
  jwtExpiration: 3600

secrets:
  # Override these with --set or external secret management
  databaseUrl: ""  # postgresql://user:pass@host:5432/db
  jwtSecret: ""  # Random 32-byte string
  betterAuthSecret: ""  # Better Auth secret key
```

---

## 5. ConfigMap/Secret Strategy

### Decision/Recommendation

**Configuration Hierarchy:**

1. **Secrets (for sensitive data):**
   - Database credentials (PostgreSQL connection string)
   - JWT signing keys
   - Better Auth secret keys
   - API keys for external services
   - TLS certificates (if not using cert-manager)

2. **ConfigMaps (for non-sensitive data):**
   - Environment name (dev/staging/prod)
   - CORS allowed origins
   - Feature flags
   - Service endpoints (internal Kubernetes DNS)
   - Logging configuration

3. **Environment Variables in Deployment:**
   - Container-specific settings
   - Reference to ConfigMap/Secret keys

**External Secret Management (Recommended for Production):**
- **External Secrets Operator** with AWS Secrets Manager, GCP Secret Manager, or HashiCorp Vault
- Secrets stored outside Kubernetes, synced automatically
- Eliminates secrets from Git repositories

**Environment-Specific Configuration:**
- Use separate values files: `values-dev.yaml`, `values-staging.yaml`, `values-prod.yaml`
- Version ConfigMaps with suffix (e.g., `app-config-v2`) to trigger rolling updates

### Rationale

**Security First:** Storing secrets in Kubernetes Secrets is better than hardcoding, but still base64-encoded (not encrypted by default). External secret management provides true encryption and audit trails.

**Separation of Concerns:** ConfigMaps for configuration, Secrets for credentials. This makes it clear what's sensitive and what's not, and allows different RBAC policies.

**Versioned ConfigMaps:** Changing a ConfigMap doesn't trigger a pod restart unless using a version suffix in the name. This pattern ensures configuration updates deploy atomically with application updates.

**2025 Best Practice:** External Secrets Operator has become the de facto standard for production Kubernetes deployments, with Sealed Secrets as an alternative for GitOps workflows.

### Alternatives Considered

| Approach | Pros | Cons | Decision |
|----------|------|------|----------|
| Hardcoded in code | Simple | Insecure, inflexible | ❌ Unacceptable |
| Environment variables only | Works | No separation of sensitive data, hard to manage | ❌ Poor practice |
| Kubernetes Secrets only | Built-in, simple | Base64 only, secrets in Git if not careful | ⚠️ OK for dev |
| External Secrets Operator | Secure, auditable, centralized | Additional complexity | ✅ **Recommended for prod** |
| Sealed Secrets | GitOps-friendly | Can't rotate without re-encrypting | ✅ Good for GitOps |

### Implementation Guidance

#### A. ConfigMap Structure

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ include "todo-app.fullname" . }}-config
  labels:
    {{- include "todo-app.labels" . | nindent 4 }}
data:
  # Environment configuration
  environment: {{ .Values.global.environment | quote }}

  # CORS configuration
  cors-origins: {{ .Values.config.corsOrigins | quote }}

  # Feature flags
  feature-reminders-enabled: {{ .Values.features.reminders | quote }}
  feature-ai-chatbot-enabled: {{ .Values.features.aiChatbot | quote }}

  # Service endpoints (internal Kubernetes DNS)
  backend-url: "http://{{ include "todo-app.fullname" . }}-backend:8000"
  database-host: {{ .Values.database.external.host | quote }}
  database-port: {{ .Values.database.external.port | quote }}
  database-name: {{ .Values.database.external.database | quote }}

  # Logging configuration
  log-level: {{ .Values.backend.logLevel | quote }}
  log-format: "json"

  # JWT configuration (non-sensitive)
  jwt-expiration: {{ .Values.config.jwtExpiration | quote }}
  jwt-algorithm: "HS256"
```

#### B. Secret Structure

```yaml
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: {{ include "todo-app.fullname" . }}-secret
  labels:
    {{- include "todo-app.labels" . | nindent 4 }}
type: Opaque
stringData:
  # Database credentials
  database-url: {{ .Values.secrets.databaseUrl | required "Database URL is required" | quote }}
  database-username: {{ .Values.database.external.username | quote }}
  database-password: {{ .Values.secrets.databasePassword | required "Database password is required" | quote }}

  # JWT signing key
  jwt-secret: {{ .Values.secrets.jwtSecret | required "JWT secret is required" | quote }}

  # Better Auth secrets
  better-auth-secret: {{ .Values.secrets.betterAuthSecret | required "Better Auth secret is required" | quote }}
  better-auth-trust-host: "true"

  # Optional: External API keys
  {{- if .Values.secrets.openaiApiKey }}
  openai-api-key: {{ .Values.secrets.openaiApiKey | quote }}
  {{- end }}
```

**Important:** Never commit actual secrets to values.yaml. Use `--set` flags or external secret management.

#### C. Using ConfigMap and Secret in Deployment

```yaml
# deployment-backend.yaml (excerpt)
spec:
  template:
    spec:
      containers:
        - name: fastapi
          env:
            # From ConfigMap
            - name: ENVIRONMENT
              valueFrom:
                configMapKeyRef:
                  name: {{ include "todo-app.fullname" . }}-config
                  key: environment
            - name: CORS_ORIGINS
              valueFrom:
                configMapKeyRef:
                  name: {{ include "todo-app.fullname" . }}-config
                  key: cors-origins
            - name: LOG_LEVEL
              valueFrom:
                configMapKeyRef:
                  name: {{ include "todo-app.fullname" . }}-config
                  key: log-level

            # From Secret
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: {{ include "todo-app.fullname" . }}-secret
                  key: database-url
            - name: JWT_SECRET
              valueFrom:
                secretKeyRef:
                  name: {{ include "todo-app.fullname" . }}-secret
                  key: jwt-secret
            - name: BETTER_AUTH_SECRET
              valueFrom:
                secretKeyRef:
                  name: {{ include "todo-app.fullname" . }}-secret
                  key: better-auth-secret

          # Alternative: Mount as files
          volumeMounts:
            - name: config-volume
              mountPath: /etc/config
              readOnly: true
            - name: secret-volume
              mountPath: /etc/secrets
              readOnly: true

      volumes:
        - name: config-volume
          configMap:
            name: {{ include "todo-app.fullname" . }}-config
        - name: secret-volume
          secret:
            secretName: {{ include "todo-app.fullname" . }}-secret
```

#### D. Environment-Specific Values Files

```yaml
# values-dev.yaml
global:
  environment: development

backend:
  replicaCount: 1
  resources:
    limits:
      cpu: 500m
      memory: 512Mi
    requests:
      cpu: 100m
      memory: 128Mi
  autoscaling:
    enabled: false
  logLevel: DEBUG

frontend:
  replicaCount: 1
  autoscaling:
    enabled: false

database:
  external:
    enabled: false
  internal:
    enabled: true
    persistence:
      enabled: false  # Use emptyDir for dev

ingress:
  enabled: true
  host: todo-dev.local
  tls: []

networkPolicy:
  enabled: false

features:
  reminders: true
  aiChatbot: false

---
# values-prod.yaml
global:
  environment: production

backend:
  replicaCount: 3
  resources:
    limits:
      cpu: 2000m
      memory: 2Gi
    requests:
      cpu: 500m
      memory: 512Mi
  autoscaling:
    enabled: true
    minReplicas: 3
    maxReplicas: 20
  logLevel: INFO
  podDisruptionBudget:
    enabled: true
    minAvailable: 2

frontend:
  replicaCount: 2
  autoscaling:
    enabled: true

database:
  external:
    enabled: true
    host: postgres.production.example.com

ingress:
  enabled: true
  host: todo.example.com
  tls:
    - secretName: todo-tls
      hosts:
        - todo.example.com

networkPolicy:
  enabled: true

features:
  reminders: true
  aiChatbot: true
```

Deploy with:
```bash
helm upgrade --install todo-app ./charts/todo-app \
  -f charts/todo-app/values-prod.yaml \
  --set secrets.databaseUrl="$DATABASE_URL" \
  --set secrets.jwtSecret="$JWT_SECRET" \
  --set secrets.betterAuthSecret="$BETTER_AUTH_SECRET"
```

#### E. External Secrets Operator (Production Recommendation)

Install External Secrets Operator:
```bash
helm repo add external-secrets https://charts.external-secrets.io
helm install external-secrets external-secrets/external-secrets -n external-secrets-system --create-namespace
```

Create SecretStore (AWS Secrets Manager example):
```yaml
# secretstore.yaml
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: aws-secrets-manager
  namespace: default
spec:
  provider:
    aws:
      service: SecretsManager
      region: us-east-1
      auth:
        jwt:
          serviceAccountRef:
            name: external-secrets-sa
```

Create ExternalSecret:
```yaml
# externalsecret.yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: {{ include "todo-app.fullname" . }}-secret
  labels:
    {{- include "todo-app.labels" . | nindent 4 }}
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secrets-manager
    kind: SecretStore
  target:
    name: {{ include "todo-app.fullname" . }}-secret
    creationPolicy: Owner
  data:
    - secretKey: database-url
      remoteRef:
        key: todo-app/production
        property: database_url

    - secretKey: jwt-secret
      remoteRef:
        key: todo-app/production
        property: jwt_secret

    - secretKey: better-auth-secret
      remoteRef:
        key: todo-app/production
        property: better_auth_secret
```

Benefits:
- Secrets never stored in Kubernetes or Git
- Automatic rotation when secrets change in AWS/GCP/Vault
- Audit trail in cloud provider's secret manager
- RBAC at secret provider level

#### F. Sealed Secrets (GitOps Alternative)

For GitOps workflows where you want to commit encrypted secrets:

```bash
# Install Sealed Secrets controller
kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.24.0/controller.yaml

# Install kubeseal CLI
brew install kubeseal

# Create sealed secret
echo -n "my-secret-value" | kubectl create secret generic my-secret \
  --dry-run=client --from-file=password=/dev/stdin -o yaml | \
  kubeseal -o yaml > sealed-secret.yaml

# Commit sealed-secret.yaml to Git safely
```

#### G. Better Auth Configuration in Kubernetes

Better Auth requires specific environment variables:

```yaml
# Frontend deployment environment
env:
  - name: BETTER_AUTH_SECRET
    valueFrom:
      secretKeyRef:
        name: {{ include "todo-app.fullname" . }}-secret
        key: better-auth-secret
  - name: BETTER_AUTH_URL
    value: "https://{{ .Values.ingress.host }}"
  - name: BETTER_AUTH_TRUST_HOST
    value: "true"  # Required for production behind proxy
  - name: DATABASE_URL
    valueFrom:
      secretKeyRef:
        name: {{ include "todo-app.fullname" . }}-secret
        key: database-url

# Backend deployment environment (if using Better Auth backend)
env:
  - name: JWT_SECRET
    valueFrom:
      secretKeyRef:
        name: {{ include "todo-app.fullname" . }}-secret
        key: jwt-secret
  - name: JWKS_URL
    value: "https://{{ .Values.ingress.host }}/.well-known/jwks.json"
```

**Important:** Better Auth's `BETTER_AUTH_SECRET` must be:
- At least 32 characters
- Cryptographically random
- Same across all frontend replicas
- Rotated periodically

Generate with:
```bash
openssl rand -base64 32
```

---

## 6. Background Jobs/Schedulers Support

### Decision/Recommendation

**Use Case Based Selection:**

1. **Scheduled Reminders/Notifications:**
   - **Kubernetes CronJob** - For periodic tasks (daily reminder checks)
   - **Deployment + APScheduler** - For in-app scheduling with dynamic intervals

2. **Asynchronous Background Tasks:**
   - **Celery + Redis** - For complex distributed task queues (if needed)
   - **FastAPI BackgroundTasks** - For simple, short-lived async tasks

3. **Workflow Orchestration:**
   - **Argo Workflows** - For complex DAGs and multi-step pipelines (future)

**Recommended for Todo Chatbot:**
- **Kubernetes CronJob** for daily reminder notifications
- **APScheduler** embedded in FastAPI backend for user-specific reminder scheduling
- **FastAPI BackgroundTasks** for email/push notifications

### Rationale

**Kubernetes CronJob Benefits:**
- Runs containers on-demand, releases resources when complete
- Built into Kubernetes, no additional infrastructure
- Perfect for periodic cleanup, backups, scheduled notifications

**APScheduler Benefits:**
- Lightweight, runs inside FastAPI application
- Supports persistent job store (PostgreSQL)
- Good for dynamic scheduling (user sets reminder for specific time)
- No separate worker infrastructure needed for simple use cases

**Celery Trade-offs:**
- Requires Redis/RabbitMQ broker (additional infrastructure)
- Requires Celery worker pods running 24/7
- Celery beat for scheduling
- Overkill for simple reminder system, but necessary for:
  - High-volume async tasks (>1000/min)
  - Complex task chains and workflows
  - Task retries with exponential backoff
  - Distributed task processing

**2025 Best Practice:** Start simple with CronJob + APScheduler. Introduce Celery only when you need distributed task processing or high-volume async operations.

### Alternatives Considered

| Approach | Best For | Infrastructure | Complexity | Decision |
|----------|----------|----------------|------------|----------|
| System cron in container | Very simple schedules | None | Low | ❌ Not cloud-native |
| APScheduler | In-app scheduling, dynamic times | None | Low | ✅ **Recommended** |
| Kubernetes CronJob | Periodic tasks, cleanup | Native K8s | Low | ✅ **Recommended** |
| Celery + Redis | High-volume async tasks | Redis + workers | High | ⚠️ If needed later |
| Argo Workflows | Complex DAGs, pipelines | Argo controller | High | ❌ Overkill for now |
| Apache Airflow | Enterprise workflow orchestration | Multiple services | Very High | ❌ Too complex |

### Implementation Guidance

#### A. APScheduler in FastAPI for Dynamic Reminders

```python
# app/services/scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Job store configuration (persists to PostgreSQL)
jobstores = {
    'default': SQLAlchemyJobStore(url='postgresql://user:pass@postgres:5432/todo_db')
}

executors = {
    'default': AsyncIOExecutor(),
}

job_defaults = {
    'coalesce': False,
    'max_instances': 3,
    'misfire_grace_time': 300  # 5 minutes
}

scheduler = AsyncIOScheduler(
    jobstores=jobstores,
    executors=executors,
    job_defaults=job_defaults,
    timezone='UTC'
)

# Task functions
async def send_task_reminder(task_id: int, user_id: int):
    """Send reminder notification for a specific task."""
    logger.info(f"Sending reminder for task {task_id} to user {user_id}")
    # Implementation: send email, push notification, etc.
    from app.services.notification import send_notification
    await send_notification(user_id, f"Reminder: Task #{task_id} is due")

def schedule_task_reminder(task_id: int, user_id: int, remind_at: datetime):
    """Schedule a reminder for a task at specific time."""
    scheduler.add_job(
        send_task_reminder,
        'date',  # Run once at specific time
        run_date=remind_at,
        args=[task_id, user_id],
        id=f'task_reminder_{task_id}',
        replace_existing=True,
        misfire_grace_time=300
    )
    logger.info(f"Scheduled reminder for task {task_id} at {remind_at}")

def schedule_recurring_task(task_id: int, user_id: int, cron_expression: str):
    """Schedule recurring reminders using cron expression."""
    scheduler.add_job(
        send_task_reminder,
        'cron',
        **parse_cron_expression(cron_expression),
        args=[task_id, user_id],
        id=f'task_recurring_{task_id}',
        replace_existing=True
    )

def cancel_task_reminder(task_id: int):
    """Cancel a scheduled reminder."""
    try:
        scheduler.remove_job(f'task_reminder_{task_id}')
        logger.info(f"Cancelled reminder for task {task_id}")
    except Exception as e:
        logger.warning(f"Could not cancel reminder for task {task_id}: {e}")

# Startup and shutdown
def start_scheduler():
    """Start the scheduler on app startup."""
    if not scheduler.running:
        scheduler.start()
        logger.info("APScheduler started")

def shutdown_scheduler():
    """Shutdown scheduler on app shutdown."""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("APScheduler shutdown")
```

```python
# app/main.py
from fastapi import FastAPI
from app.services.scheduler import start_scheduler, shutdown_scheduler

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    start_scheduler()

@app.on_event("shutdown")
async def shutdown_event():
    shutdown_scheduler()

# API endpoint to create reminder
from app.services.scheduler import schedule_task_reminder

@app.post("/tasks/{task_id}/reminders")
async def create_reminder(
    task_id: int,
    remind_at: datetime,
    current_user: User = Depends(get_current_user)
):
    schedule_task_reminder(task_id, current_user.id, remind_at)
    return {"message": "Reminder scheduled", "remind_at": remind_at}
```

**Deployment Considerations:**
- All FastAPI replicas will load scheduler from PostgreSQL
- Use `misfire_grace_time` to handle pod restarts
- Set `coalesce=True` to prevent duplicate executions
- Use `max_instances` to limit concurrent job executions

#### B. Kubernetes CronJob for Daily Reminder Digest

```yaml
# cronjob-daily-reminders.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: {{ include "todo-app.fullname" . }}-daily-reminders
  labels:
    {{- include "todo-app.labels" . | nindent 4 }}
    app.kubernetes.io/component: cronjob
spec:
  # Run every day at 8:00 AM UTC
  schedule: "0 8 * * *"
  timeZone: "UTC"  # Kubernetes 1.27+
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 3
  concurrencyPolicy: Forbid  # Don't run if previous job still running
  startingDeadlineSeconds: 300  # Skip if 5min late
  jobTemplate:
    spec:
      backoffLimit: 3  # Retry up to 3 times on failure
      activeDeadlineSeconds: 600  # Kill job if runs longer than 10min
      template:
        metadata:
          labels:
            {{- include "todo-app.selectorLabels" . | nindent 12 }}
            app.kubernetes.io/component: cronjob
        spec:
          restartPolicy: OnFailure
          serviceAccountName: {{ include "todo-app.serviceAccountName" . }}
          containers:
            - name: send-reminders
              image: "{{ .Values.backend.image.repository }}:{{ .Values.backend.image.tag }}"
              command:
                - python
                - -m
                - app.tasks.send_daily_reminders
              env:
                - name: DATABASE_URL
                  valueFrom:
                    secretKeyRef:
                      name: {{ include "todo-app.fullname" . }}-secret
                      key: database-url
                - name: LOG_LEVEL
                  value: INFO
              resources:
                limits:
                  cpu: 500m
                  memory: 512Mi
                requests:
                  cpu: 100m
                  memory: 128Mi
              securityContext:
                runAsNonRoot: true
                runAsUser: 1000
                allowPrivilegeEscalation: false
                readOnlyRootFilesystem: true
```

```python
# app/tasks/send_daily_reminders.py
"""
CronJob script to send daily reminder digest.
Run by Kubernetes CronJob, not by FastAPI.
"""
import asyncio
from sqlmodel import Session, select
from app.core.database import engine
from app.models import Task, User
from app.services.notification import send_email
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def send_daily_reminders():
    """Send daily reminder digest to users with tasks due today."""
    logger.info("Starting daily reminder job")

    today = datetime.utcnow().date()
    tomorrow = today + timedelta(days=1)

    with Session(engine) as session:
        # Get all tasks due today
        statement = select(Task).where(
            Task.due_date >= today,
            Task.due_date < tomorrow,
            Task.completed == False
        )
        tasks = session.exec(statement).all()

        # Group by user
        user_tasks = {}
        for task in tasks:
            if task.user_id not in user_tasks:
                user_tasks[task.user_id] = []
            user_tasks[task.user_id].append(task)

        # Send digest to each user
        for user_id, tasks in user_tasks.items():
            user = session.get(User, user_id)
            if user and user.email:
                logger.info(f"Sending reminder to {user.email} ({len(tasks)} tasks)")
                await send_email(
                    to=user.email,
                    subject="Daily Task Reminder",
                    body=format_reminder_email(tasks)
                )

    logger.info(f"Daily reminder job completed. Sent to {len(user_tasks)} users")

def format_reminder_email(tasks):
    """Format tasks into email body."""
    lines = ["You have the following tasks due today:\n"]
    for task in tasks:
        lines.append(f"- {task.title} (Priority: {task.priority})")
    return "\n".join(lines)

if __name__ == "__main__":
    asyncio.run(send_daily_reminders())
```

#### C. FastAPI BackgroundTasks for Immediate Async Work

```python
# app/api/tasks.py
from fastapi import BackgroundTasks

async def send_task_created_notification(user_email: str, task_title: str):
    """Background task to send notification."""
    # This runs asynchronously after response is sent
    await send_email(
        to=user_email,
        subject="Task Created",
        body=f"Task '{task_title}' has been created"
    )

@router.post("/tasks", status_code=201)
async def create_task(
    task: TaskCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    # Create task synchronously
    db_task = Task.from_orm(task)
    db_task.user_id = current_user.id
    session.add(db_task)
    session.commit()

    # Send notification in background
    background_tasks.add_task(
        send_task_created_notification,
        current_user.email,
        task.title
    )

    return db_task
```

**When to Use BackgroundTasks:**
- Short-lived async work (< 10 seconds)
- Work that doesn't need retries
- Work that can be lost if pod crashes (not critical)

**When NOT to Use:**
- Long-running tasks (> 30 seconds)
- Tasks requiring retries
- Critical operations that must complete

#### D. Celery Setup (If Needed Later)

Only implement if you need:
- High-volume async tasks (>1000/min)
- Complex task chains
- Distributed task processing

```yaml
# deployment-celery-worker.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "todo-app.fullname" . }}-celery-worker
spec:
  replicas: {{ .Values.celery.worker.replicaCount }}
  selector:
    matchLabels:
      app.kubernetes.io/component: celery-worker
  template:
    spec:
      containers:
        - name: celery-worker
          image: "{{ .Values.backend.image.repository }}:{{ .Values.backend.image.tag }}"
          command:
            - celery
            - -A
            - app.celery_app
            - worker
            - --loglevel=info
            - --concurrency=4
          env:
            - name: CELERY_BROKER_URL
              value: "redis://{{ include "todo-app.fullname" . }}-redis:6379/0"
            - name: CELERY_RESULT_BACKEND
              value: "redis://{{ include "todo-app.fullname" . }}-redis:6379/0"
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: {{ include "todo-app.fullname" . }}-secret
                  key: database-url
          resources:
            limits:
              cpu: 1000m
              memory: 1Gi
            requests:
              cpu: 250m
              memory: 256Mi

---
# deployment-celery-beat.yaml (scheduler)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "todo-app.fullname" . }}-celery-beat
spec:
  replicas: 1  # Only one beat instance
  selector:
    matchLabels:
      app.kubernetes.io/component: celery-beat
  template:
    spec:
      containers:
        - name: celery-beat
          image: "{{ .Values.backend.image.repository }}:{{ .Values.backend.image.tag }}"
          command:
            - celery
            - -A
            - app.celery_app
            - beat
            - --loglevel=info
          env:
            - name: CELERY_BROKER_URL
              value: "redis://{{ include "todo-app.fullname" . }}-redis:6379/0"
```

```python
# app/celery_app.py
from celery import Celery
from celery.schedules import crontab

celery_app = Celery(
    "todo_app",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0"
)

# Configure task routes
celery_app.conf.task_routes = {
    'app.tasks.send_email': {'queue': 'notifications'},
    'app.tasks.process_data': {'queue': 'processing'},
}

# Scheduled tasks
celery_app.conf.beat_schedule = {
    'send-daily-reminders': {
        'task': 'app.tasks.send_daily_reminders',
        'schedule': crontab(hour=8, minute=0),  # 8:00 AM daily
    },
}

@celery_app.task(bind=True, max_retries=3)
def send_task_reminder(self, task_id: int):
    try:
        # Send reminder logic
        pass
    except Exception as exc:
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
```

#### E. Decision Matrix

| Scenario | Recommended Solution | Rationale |
|----------|---------------------|-----------|
| Daily digest emails at 8 AM | **Kubernetes CronJob** | Periodic, predictable schedule |
| User sets reminder for task | **APScheduler** | Dynamic time, persisted to DB |
| Send email after task creation | **FastAPI BackgroundTasks** | Simple, short-lived, non-critical |
| Process 10,000 notifications/hour | **Celery + Redis** | High volume, needs queuing |
| Complex multi-step workflow | **Argo Workflows** | Complex DAGs, multi-container |

#### F. Monitoring and Observability

```yaml
# servicemonitor.yaml (if using Prometheus)
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: {{ include "todo-app.fullname" . }}-cronjob
spec:
  selector:
    matchLabels:
      app.kubernetes.io/component: cronjob
  endpoints:
    - port: metrics
      interval: 30s
```

Add metrics to CronJob:
```python
# app/tasks/send_daily_reminders.py
from prometheus_client import Counter, Histogram, push_to_gateway
import time

reminders_sent = Counter('daily_reminders_sent_total', 'Total reminders sent')
job_duration = Histogram('daily_reminder_job_duration_seconds', 'Job duration')

async def send_daily_reminders():
    start_time = time.time()
    try:
        # ... send reminders ...
        reminders_sent.inc(len(user_tasks))
    finally:
        duration = time.time() - start_time
        job_duration.observe(duration)

        # Push to Prometheus Pushgateway
        push_to_gateway(
            'prometheus-pushgateway:9091',
            job='daily_reminders',
            registry=...
        )
```

---

## Summary and Recommendations

### Immediate Actions (MVP Deployment)

1. **Testing:**
   - Implement `helm lint` + Kubeconform in CI/CD
   - Create basic helm-unittest tests for deployment templates
   - Add Conftest policies for security (no root, resource limits)

2. **Health Checks:**
   - Implement `/livez` and `/readyz` endpoints in FastAPI
   - Add `/api/health/live` and `/api/health/ready` in Next.js
   - Configure startup, liveness, and readiness probes

3. **Helm Resources:**
   - Essential: Deployment, Service, ConfigMap, Secret, Ingress, PVC
   - Recommended: HPA, ServiceAccount, NetworkPolicy

4. **Configuration:**
   - Use ConfigMaps for non-sensitive config
   - Use Secrets for credentials (with --set in CI/CD)
   - Create environment-specific values files

5. **Background Jobs:**
   - Start with Kubernetes CronJob for daily reminders
   - Use APScheduler for user-specific reminder scheduling
   - Use FastAPI BackgroundTasks for simple async work

### Phase 2 Enhancements (Production Hardening)

1. **Testing:**
   - Add chart-testing (ct) for full lifecycle tests
   - Implement Pact contract testing for API
   - Set up KUTTL for service-to-service integration tests

2. **Security:**
   - Implement External Secrets Operator with AWS/GCP Secrets Manager
   - Enable Pod Security Standards (restricted)
   - Add PodDisruptionBudgets for HA

3. **Observability:**
   - Add Prometheus ServiceMonitors
   - Implement distributed tracing (Jaeger/Tempo)
   - Set up log aggregation (Loki/ELK)

4. **Scaling:**
   - Fine-tune HPA based on production metrics
   - Implement cluster autoscaling
   - Add pod topology spread constraints

### Phase 3 Advanced Features (If Needed)

1. **Complex Workflows:**
   - Migrate to Celery if task volume > 1000/min
   - Implement Argo Workflows for complex pipelines

2. **Service Mesh:**
   - Consider Istio/Linkerd for mTLS, traffic management
   - Implement circuit breakers and retries at mesh level

3. **GitOps:**
   - Implement ArgoCD/FluxCD for declarative deployments
   - Use Sealed Secrets for secret management in Git

---

## References and Sources

### Integration Testing
- [Using Conftest and Kubeval With Helm](https://garethr.dev/2019/08/using-conftest-and-kubeval-with-helm/)
- [Helm Chart Testing Tools Overview](https://cloudentity.com/developers/blog/helm_chart_testing_tools/)
- [Kubernetes Testing: From clusters, operators to CRDs](https://seifrajhi.github.io/blog/testing-kubernetes-clusters-and-components/)
- [Best Microservices Testing Tools for Kubernetes in 2025](https://www.signadot.com/articles/best-microservices-testing-solution-for-kubernetes-in-2025)

### Health Checks
- [Liveness, Readiness, and Startup Probes | Kubernetes](https://kubernetes.io/docs/concepts/configuration/liveness-readiness-startup-probes/)
- [Configure Liveness, Readiness and Startup Probes | Kubernetes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
- [Kubernetes Liveness vs. Readiness vs. Startup Probes](https://mihir-rajput.medium.com/kubernetes-liveness-vs-d93ec282c2de)
- [Kubernetes Health Checks with FastAPI](https://www.codingeasypeasy.com/blog/kubernetes-health-checks-with-fastapi-ensuring-application-reliability-and-availability)
- [How to Build Resilient Backends with Kubernetes: 7 Lessons from 2025](https://www.growin.com/blog/resilient-backends-kubernetes-2025/)

### Helm Testing
- [Ensuring Effective Helm Charts with Linting, Testing, and Diff Checks](https://dev.to/hkhelil/ensuring-effective-helm-charts-with-linting-testing-and-diff-checks-ni0)
- [helm-unittest/helm-unittest](https://github.com/helm-unittest/helm-unittest)
- [helm/chart-testing](https://github.com/helm/chart-testing)
- [Chart Tests | Helm](https://helm.sh/docs/topics/chart_tests/)

### Kubernetes Resources & Configuration
- [Kubernetes Configuration Good Practices](https://kubernetes.io/blog/2025/11/25/configuration-good-practices/)
- [14 Kubernetes Best Practices You Must Know in 2025](https://komodor.com/learn/14-kubernetes-best-practices-you-must-know-in-2025/)
- [ConfigMaps | Kubernetes](https://kubernetes.io/docs/concepts/configuration/configmap/)
- [Secrets | Kubernetes](https://kubernetes.io/docs/concepts/configuration/secret/)
- [Kubernetes ConfigMap: Examples, Usage & Best Practices Guide](https://devtron.ai/blog/kubernetes-configmaps-secrets/)

### Secret Management
- [ConfigMaps and Secrets in Kubernetes](https://www.domsoria.com/en/2025/11/configmaps-and-secrets-in-kubernetes-examples-as-environment-variables-and-files/)
- [Kubernetes Secrets Management](https://www.metricfire.com/blog/kubernetes-secrets-management/)
- [Kubernetes Secrets: The Ultimate Guide (2025)](https://www.plural.sh/blog/kubernetes-secret-guide/)
- [Vault Secrets Operator on GKE deployment guide](https://medium.com/google-cloud/vault-secrets-operator-on-gke-deployment-guide-f4793cdfb25e)

### Background Jobs & Schedulers
- [Task Scheduling and Background Jobs in Python — The Ultimate Guide](https://blog.naveenpn.com/task-scheduling-and-background-jobs-in-python-the-ultimate-guide)
- [Python Jobs & Workers — A Complete, Practical Guide](https://medium.com/@dynamicy/python-jobs-workers-a-complete-practical-guide-cf842cfe33d7)
- [Kubernetes CronJobs Guide: Use Cases & Best Practices](https://www.groundcover.com/learn/kubernetes/kubernetes-cronjob)
- [The Ultimate Kubernetes CronJob Guide](https://cronitor.io/guides/kubernetes-cron-jobs)
- [How to Schedule Simple Tasks Using APScheduler](https://www.kubeblogs.com/how-to-schedule-simple-tasks-using-apscheduler-a-devops-focused-guide/)

### Service Mesh & Communication
- [Service Mesh in Kubernetes: Enhancing Microservices Management](https://konghq.com/blog/engineering/using-service-mesh-in-kubernetes-enviroment)
- [Best Service Mesh Solutions: Top 8 Tools in 2025](https://www.tigera.io/learn/guides/service-mesh/service-mesh-solutions/)

### Next.js & FastAPI
- [How to Add a Health Check Endpoint to Your Next.js Application](https://hyperping.com/blog/nextjs-health-check-endpoint)
- [Building Effective Healthcheck Endpoints in Modern Backend Systems](https://dev.to/bhavyasethafk/building-effective-healthcheck-endpoints-in-modern-backend-systems-1noi)
- [Next.js FastAPI Template](https://nextfastapi.com/)

---

**Document Version:** 1.0
**Last Updated:** 2025-12-30
**Next Review:** After MVP deployment to staging
