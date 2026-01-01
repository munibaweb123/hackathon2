# Data Model: Kubernetes Deployment Configuration
**Feature**: 001-k8s-deployment
**Created**: 2025-12-30
**Status**: Draft

## Overview

This document defines the data entities and relationships for Kubernetes deployment configuration of the Todo Chatbot application. The deployment consists of containerized frontend (Next.js), backend (FastAPI), and database (PostgreSQL) components managed through Helm charts.

---

## 1. Docker Image Entity

Represents containerized application artifacts that encapsulate runtime dependencies and application code.

### Attributes

| Attribute | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| name | string | Yes | Image name without registry prefix | `todo-frontend` |
| repository | string | Yes | Full registry path | `ghcr.io/yourorg/todo-frontend` |
| tag | string | Yes | Image version tag | `v1.2.3`, `latest`, `git-abc123` |
| registry | string | No | Container registry URL | `ghcr.io`, `docker.io` |
| buildContext | string | Yes | Path to build directory | `./frontend`, `./backend` |
| dockerfilePath | string | Yes | Path to Dockerfile | `./frontend/Dockerfile` |
| buildArgs | map[string]string | No | Build-time variables | `NODE_ENV=production` |
| labels | map[string]string | No | Image metadata labels | `version=1.0.0`, `component=frontend` |
| platform | string | No | Target platform | `linux/amd64`, `linux/arm64` |
| createdAt | datetime | Auto | Image build timestamp | `2025-12-30T10:00:00Z` |
| size | integer | Auto | Image size in bytes | `524288000` |

### Relationships

- **Belongs to Service**: Each Docker image is built for and used by a specific service (Frontend, Backend, PostgreSQL)
- **Used by Deployment**: Kubernetes Deployment references the image by repository:tag
- **Stored in Registry**: Images are pushed to a container registry (Docker Hub, GHCR, etc.)

### Business Rules

- Image tags MUST follow semantic versioning for production releases
- `latest` tag SHOULD only be used for local development
- Git commit SHA SHOULD be included in image labels for traceability
- Multi-stage builds MUST be used to minimize image size
- Base images MUST be scanned for vulnerabilities before deployment

### Example

```yaml
# Frontend Image
name: todo-frontend
repository: ghcr.io/yourorg/todo-frontend
tag: v1.2.3-abc1234
registry: ghcr.io
buildContext: ./frontend
dockerfilePath: ./frontend/Dockerfile
buildArgs:
  NODE_ENV: production
  NEXT_PUBLIC_API_URL: http://todo-backend:8000
labels:
  version: 1.2.3
  component: frontend
  git-commit: abc1234
platform: linux/amd64
```

---

## 2. Helm Chart Entity

Represents a package of Kubernetes manifest templates with configurable values for deploying the application.

### Attributes

| Attribute | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| name | string | Yes | Chart name | `todo-app` |
| version | string | Yes | Chart version (SemVer) | `1.0.0` |
| appVersion | string | Yes | Application version | `v1.2.3` |
| description | string | Yes | Chart description | `Todo Chatbot application deployment` |
| apiVersion | string | Yes | Helm API version | `v2` |
| type | string | Yes | Chart type | `application` |
| kubeVersion | string | No | Required Kubernetes version | `>=1.27.0` |
| keywords | []string | No | Search keywords | `[todo, chatbot, fastapi, nextjs]` |
| maintainers | []Maintainer | No | Chart maintainers | See Maintainer entity |
| dependencies | []Dependency | No | Chart dependencies | `[postgresql:12.0.0]` |
| templates | []string | Yes | Template file paths | See Templates section |
| valuesSchema | JSONSchema | No | Values validation schema | See Values Schema |

### Values Schema Structure

```yaml
# Default values for production
global:
  environment: production  # development, staging, production

backend:
  replicaCount: integer (1-20)
  image:
    repository: string (required)
    tag: string (default: Chart.appVersion)
    pullPolicy: enum[IfNotPresent, Always, Never]
  service:
    type: enum[ClusterIP, NodePort, LoadBalancer]
    port: integer (1-65535)
  resources:
    limits:
      cpu: string (e.g., "1000m")
      memory: string (e.g., "1Gi")
    requests:
      cpu: string
      memory: string
  autoscaling:
    enabled: boolean
    minReplicas: integer
    maxReplicas: integer
    targetCPUUtilizationPercentage: integer (1-100)
  logLevel: enum[DEBUG, INFO, WARNING, ERROR]

frontend:
  replicaCount: integer (1-20)
  image:
    repository: string (required)
    tag: string
    pullPolicy: enum[IfNotPresent, Always, Never]
  service:
    type: enum[ClusterIP, NodePort, LoadBalancer]
    port: integer (1-65535)
  resources:
    limits:
      cpu: string
      memory: string
    requests:
      cpu: string
      memory: string
  autoscaling:
    enabled: boolean
    minReplicas: integer
    maxReplicas: integer
    targetCPUUtilizationPercentage: integer

database:
  external:
    enabled: boolean
    host: string
    port: integer (1-65535)
    database: string
    username: string
  internal:
    enabled: boolean
    persistence:
      enabled: boolean
      size: string (e.g., "10Gi")
      storageClass: string

ingress:
  enabled: boolean
  className: string (e.g., "nginx")
  host: string (required if enabled)
  annotations: map[string]string
  tls:
    - secretName: string
      hosts: []string

networkPolicy:
  enabled: boolean

serviceAccount:
  create: boolean
  annotations: map[string]string
  name: string

secrets:
  databaseUrl: string (required, from external source)
  jwtSecret: string (required, from external source)
  betterAuthSecret: string (required, from external source)
```

### Templates (Kubernetes Resources)

| Template File | Resource Kind | Purpose |
|--------------|---------------|---------|
| `deployment-frontend.yaml` | Deployment | Next.js frontend pods |
| `deployment-backend.yaml` | Deployment | FastAPI backend pods |
| `deployment-postgres.yaml` | Deployment | PostgreSQL database pods |
| `service-frontend.yaml` | Service | Frontend service endpoint |
| `service-backend.yaml` | Service | Backend service endpoint |
| `service-postgres.yaml` | Service | Database service endpoint |
| `configmap.yaml` | ConfigMap | Non-sensitive configuration |
| `secret.yaml` | Secret | Sensitive credentials |
| `ingress.yaml` | Ingress | External access with TLS |
| `pvc-postgres.yaml` | PersistentVolumeClaim | Database storage |
| `hpa-backend.yaml` | HorizontalPodAutoscaler | Backend auto-scaling |
| `hpa-frontend.yaml` | HorizontalPodAutoscaler | Frontend auto-scaling |
| `networkpolicy-backend.yaml` | NetworkPolicy | Backend network isolation |
| `networkpolicy-frontend.yaml` | NetworkPolicy | Frontend network isolation |
| `serviceaccount.yaml` | ServiceAccount | RBAC identity |
| `pdb-backend.yaml` | PodDisruptionBudget | HA during updates |
| `job-migration.yaml` | Job | Database migrations |
| `cronjob-daily-reminders.yaml` | CronJob | Scheduled reminder tasks |
| `tests/test-connection.yaml` | Pod | Helm test hooks |

### Dependencies

Chart dependencies can include external charts (e.g., Bitnami PostgreSQL):

```yaml
dependencies:
  - name: postgresql
    version: 12.0.0
    repository: https://charts.bitnami.com/bitnami
    condition: database.internal.enabled
```

### Relationships

- **Contains Multiple Kubernetes Resources**: Each Helm chart packages multiple resource templates
- **References Docker Images**: Deployment templates reference Docker images
- **Manages Values**: Chart provides configurable values for customization
- **Creates Releases**: Helm chart installation creates a Release

### Business Rules

- Chart version MUST be incremented for any template changes
- appVersion SHOULD match the application's semantic version
- All templates MUST pass `helm lint` validation
- Values schema MUST be provided to validate user inputs
- Breaking changes MUST increment major version
- Templates MUST include resource requests and limits
- Secrets MUST NOT be hardcoded in values.yaml

### Example

```yaml
# Chart.yaml
apiVersion: v2
name: todo-app
version: 1.0.0
appVersion: v1.2.3
description: Todo Chatbot application with AI-powered task management
type: application
kubeVersion: ">=1.27.0"
keywords:
  - todo
  - chatbot
  - fastapi
  - nextjs
maintainers:
  - name: DevOps Team
    email: devops@example.com
dependencies:
  - name: postgresql
    version: 12.0.0
    repository: https://charts.bitnami.com/bitnami
    condition: database.internal.enabled
```

---

## 3. Kubernetes Deployment Entity

Represents a Kubernetes Deployment resource that manages ReplicaSets and pod lifecycle.

### Attributes

| Attribute | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| name | string | Yes | Deployment name | `todo-backend` |
| namespace | string | Yes | Kubernetes namespace | `default`, `production` |
| replicas | integer | Yes | Desired number of pods | `3` |
| selector | LabelSelector | Yes | Pod selection criteria | `app=todo,component=backend` |
| template | PodTemplateSpec | Yes | Pod template specification | See Pod Template |
| strategy | DeploymentStrategy | Yes | Update strategy | `RollingUpdate`, `Recreate` |
| minReadySeconds | integer | No | Min time before ready | `10` |
| progressDeadlineSeconds | integer | No | Rollout timeout | `600` |
| revisionHistoryLimit | integer | No | ReplicaSet history | `10` |
| paused | boolean | No | Pause rollouts | `false` |

### Pod Template Specification

```yaml
template:
  metadata:
    labels:
      app: todo-app
      component: backend
      version: v1.2.3
    annotations:
      checksum/config: sha256sum-of-configmap
      checksum/secret: sha256sum-of-secret
  spec:
    serviceAccountName: todo-app
    securityContext:
      runAsNonRoot: true
      runAsUser: 1000
      fsGroup: 1000
    containers:
      - name: fastapi
        image: ghcr.io/yourorg/todo-backend:v1.2.3
        imagePullPolicy: IfNotPresent
        ports:
          - name: http
            containerPort: 8000
            protocol: TCP
        env:
          - name: DATABASE_URL
            valueFrom:
              secretKeyRef:
                name: todo-app-secret
                key: database-url
          - name: ENVIRONMENT
            valueFrom:
              configMapKeyRef:
                name: todo-app-config
                key: environment
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
          limits:
            cpu: "1000m"
            memory: "1Gi"
          requests:
            cpu: "250m"
            memory: "256Mi"
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

### Deployment Strategy

```yaml
# RollingUpdate strategy (recommended)
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxUnavailable: 1        # Max pods unavailable during update
    maxSurge: 1              # Max extra pods during update

# Recreate strategy (downtime)
strategy:
  type: Recreate
```

### Relationships

- **Creates ReplicaSet**: Deployment manages one or more ReplicaSets
- **Manages Pods**: ReplicaSet ensures desired number of pod replicas
- **Uses ConfigMap**: Pods mount configuration from ConfigMap
- **Uses Secret**: Pods mount sensitive data from Secret
- **References Service**: Service routes traffic to pods via label selector
- **Scaled by HPA**: HorizontalPodAutoscaler adjusts replica count
- **Protected by PDB**: PodDisruptionBudget limits disruptions

### Business Rules

- Replica count MUST be >= 1 for critical services
- Replica count SHOULD be >= 2 for production high availability
- Rolling update strategy MUST be used for zero-downtime deployments
- All containers MUST define resource requests and limits
- Security context MUST set `runAsNonRoot: true`
- Containers SHOULD use read-only root filesystem where possible
- Health probes (startup, liveness, readiness) MUST be configured
- Pod annotations MUST include checksums of ConfigMap/Secret for auto-reload
- Labels MUST follow Kubernetes recommended labels (app, component, version)

### Example

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-backend
  namespace: default
  labels:
    app.kubernetes.io/name: todo-app
    app.kubernetes.io/component: backend
    app.kubernetes.io/version: v1.2.3
spec:
  replicas: 3
  selector:
    matchLabels:
      app.kubernetes.io/name: todo-app
      app.kubernetes.io/component: backend
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
  template:
    # See Pod Template Specification above
```

---

## 4. Kubernetes Service Entity

Represents a Kubernetes Service resource that provides stable network endpoints for pods.

### Attributes

| Attribute | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| name | string | Yes | Service name | `todo-backend` |
| namespace | string | Yes | Kubernetes namespace | `default` |
| type | string | Yes | Service type | `ClusterIP`, `NodePort`, `LoadBalancer` |
| clusterIP | string | Auto | Cluster-internal IP | `10.96.0.10` |
| ports | []ServicePort | Yes | Port mappings | See ServicePort |
| selector | map[string]string | Yes | Pod selection labels | `app=todo,component=backend` |
| sessionAffinity | string | No | Session stickiness | `None`, `ClientIP` |
| externalTrafficPolicy | string | No | External traffic routing | `Cluster`, `Local` |

### ServicePort Structure

```yaml
ports:
  - name: http
    protocol: TCP
    port: 8000           # Service port (internal to cluster)
    targetPort: 8000     # Container port (or port name from pod)
    nodePort: 30080      # External port (only for NodePort/LoadBalancer)
```

### Service Types

| Type | Use Case | Accessibility | Example |
|------|----------|---------------|---------|
| **ClusterIP** | Internal service-to-service | Cluster-internal only | Backend API, Database |
| **NodePort** | Development/testing | Accessible via Node IP + port | Frontend in Minikube |
| **LoadBalancer** | Production external access | Cloud provider load balancer | Production frontend |
| **ExternalName** | External service alias | DNS CNAME | External database |

### Relationships

- **Routes to Pods**: Service forwards traffic to pods matching selector labels
- **Used by Ingress**: Ingress routes external traffic to services
- **Discovered via DNS**: Kubernetes DNS creates records (e.g., `todo-backend.default.svc.cluster.local`)
- **Referenced by Deployments**: Application code uses service DNS name
- **Load Balanced**: Distributes traffic across healthy pod replicas

### Business Rules

- Service name MUST match deployment naming convention
- ClusterIP type SHOULD be used for internal services
- NodePort type MAY be used for Minikube local access
- LoadBalancer type SHOULD be used for production external access
- Port names MUST be lowercase alphanumeric + hyphen
- Selector labels MUST match deployment pod labels
- Health checks MUST be configured to route only to ready pods

### Example

```yaml
# Backend Service (ClusterIP - internal)
apiVersion: v1
kind: Service
metadata:
  name: todo-backend
  namespace: default
  labels:
    app.kubernetes.io/name: todo-app
    app.kubernetes.io/component: backend
spec:
  type: ClusterIP
  ports:
    - port: 8000
      targetPort: http
      protocol: TCP
      name: http
  selector:
    app.kubernetes.io/name: todo-app
    app.kubernetes.io/component: backend

---
# Frontend Service (NodePort - Minikube access)
apiVersion: v1
kind: Service
metadata:
  name: todo-frontend
  namespace: default
  labels:
    app.kubernetes.io/name: todo-app
    app.kubernetes.io/component: frontend
spec:
  type: NodePort
  ports:
    - port: 3000
      targetPort: http
      protocol: TCP
      name: http
      nodePort: 30000
  selector:
    app.kubernetes.io/name: todo-app
    app.kubernetes.io/component: frontend
```

---

## 5. ConfigMap Entity

Represents non-sensitive configuration data for applications.

### Attributes

| Attribute | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| name | string | Yes | ConfigMap name | `todo-app-config` |
| namespace | string | Yes | Kubernetes namespace | `default` |
| data | map[string]string | Yes | Key-value configuration | See Data section |
| binaryData | map[string][]byte | No | Binary data (base64) | Configuration files |
| immutable | boolean | No | Prevent modifications | `false` (default) |

### Data Structure

```yaml
data:
  # Environment configuration
  environment: "production"

  # CORS configuration
  cors-origins: "https://todo.example.com"

  # Feature flags
  feature-reminders-enabled: "true"
  feature-ai-chatbot-enabled: "true"

  # Service endpoints (internal Kubernetes DNS)
  backend-url: "http://todo-backend:8000"
  database-host: "postgres.example.com"
  database-port: "5432"
  database-name: "todo_db"

  # Logging configuration
  log-level: "INFO"
  log-format: "json"

  # JWT configuration (non-sensitive)
  jwt-expiration: "3600"
  jwt-algorithm: "HS256"
```

### Usage Patterns

**1. Environment Variables:**
```yaml
env:
  - name: ENVIRONMENT
    valueFrom:
      configMapKeyRef:
        name: todo-app-config
        key: environment
```

**2. Volume Mount (for configuration files):**
```yaml
volumeMounts:
  - name: config-volume
    mountPath: /etc/config
    readOnly: true
volumes:
  - name: config-volume
    configMap:
      name: todo-app-config
```

### Relationships

- **Mounted into Deployments**: Pods consume ConfigMap data as environment variables or files
- **Versioned for Updates**: Changing ConfigMap triggers pod restart when checksum annotation is used
- **Namespace Scoped**: Only accessible within the same namespace

### Business Rules

- ConfigMap MUST NOT contain sensitive data (use Secret instead)
- ConfigMap names SHOULD include version suffix for immutability (`app-config-v2`)
- Size limit: 1MB maximum per ConfigMap
- Pod annotations MUST include ConfigMap checksum to trigger updates
- All values MUST be strings (numbers/booleans as quoted strings)
- Environment-specific values SHOULD be in separate ConfigMaps

### Example

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: todo-app-config
  namespace: default
  labels:
    app.kubernetes.io/name: todo-app
data:
  environment: "production"
  cors-origins: "https://todo.example.com"
  feature-reminders-enabled: "true"
  backend-url: "http://todo-backend:8000"
  log-level: "INFO"
```

---

## 6. Secret Entity

Represents sensitive configuration data stored securely in Kubernetes.

### Attributes

| Attribute | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| name | string | Yes | Secret name | `todo-app-secret` |
| namespace | string | Yes | Kubernetes namespace | `default` |
| type | string | Yes | Secret type | `Opaque`, `kubernetes.io/tls` |
| data | map[string][]byte | No | Base64-encoded values | See Data section |
| stringData | map[string]string | No | Plain-text values (auto-encoded) | See StringData section |
| immutable | boolean | No | Prevent modifications | `false` |

### Secret Types

| Type | Use Case | Data Keys |
|------|----------|-----------|
| **Opaque** | Generic secrets (default) | Custom keys |
| **kubernetes.io/tls** | TLS certificates | `tls.crt`, `tls.key` |
| **kubernetes.io/dockerconfigjson** | Container registry auth | `.dockerconfigjson` |
| **kubernetes.io/basic-auth** | Basic auth credentials | `username`, `password` |
| **kubernetes.io/ssh-auth** | SSH private key | `ssh-privatekey` |

### StringData Structure (Opaque secrets)

```yaml
stringData:
  # Database credentials
  database-url: "postgresql://user:password@postgres.example.com:5432/todo_db"
  database-username: "todo_user"
  database-password: "SuperSecretPassword123!"

  # JWT signing key (32+ characters)
  jwt-secret: "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"

  # Better Auth secrets
  better-auth-secret: "x9y8z7w6v5u4t3s2r1q0p9o8n7m6l5k4"
  better-auth-trust-host: "true"

  # External API keys (optional)
  openai-api-key: "sk-proj-xyz123..."
```

### Usage Patterns

**1. Environment Variables:**
```yaml
env:
  - name: DATABASE_URL
    valueFrom:
      secretKeyRef:
        name: todo-app-secret
        key: database-url
```

**2. Volume Mount:**
```yaml
volumeMounts:
  - name: secret-volume
    mountPath: /etc/secrets
    readOnly: true
volumes:
  - name: secret-volume
    secret:
      secretName: todo-app-secret
```

### Security Best Practices

| Practice | Implementation |
|----------|----------------|
| **External Secret Management** | Use External Secrets Operator with AWS/GCP Secret Manager |
| **Sealed Secrets** | Encrypt secrets with Sealed Secrets for GitOps |
| **RBAC** | Restrict secret access with Role-Based Access Control |
| **Rotation** | Rotate secrets periodically (30-90 days) |
| **Auditing** | Enable audit logs for secret access |
| **Encryption at Rest** | Enable Kubernetes secret encryption |

### Relationships

- **Mounted into Deployments**: Pods consume Secret data as environment variables or files
- **Referenced by External Secrets**: ExternalSecret syncs from cloud secret managers
- **Protected by RBAC**: Access controlled by Kubernetes RBAC policies
- **Namespace Scoped**: Only accessible within the same namespace

### Business Rules

- Secrets MUST NOT be committed to Git repositories
- Secrets SHOULD be provided via `--set` flags or external secret management
- Production secrets MUST use External Secrets Operator or Sealed Secrets
- Secret size limit: 1MB maximum
- All secret keys MUST be lowercase with hyphens (kebab-case)
- JWT secret MUST be at least 32 characters
- Database passwords MUST meet complexity requirements
- Secrets MUST be rotated periodically

### Example

```yaml
# Basic Kubernetes Secret (not recommended for production)
apiVersion: v1
kind: Secret
metadata:
  name: todo-app-secret
  namespace: default
  labels:
    app.kubernetes.io/name: todo-app
type: Opaque
stringData:
  database-url: "postgresql://todo_user:SecurePass123@postgres:5432/todo_db"
  jwt-secret: "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
  better-auth-secret: "x9y8z7w6v5u4t3s2r1q0p9o8n7m6l5k4"

---
# External Secret (recommended for production)
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: todo-app-secret
  namespace: default
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secrets-manager
    kind: SecretStore
  target:
    name: todo-app-secret
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
```

---

## 7. PersistentVolumeClaim Entity

Represents a request for persistent storage in Kubernetes.

### Attributes

| Attribute | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| name | string | Yes | PVC name | `postgres-data` |
| namespace | string | Yes | Kubernetes namespace | `default` |
| storageClassName | string | No | Storage class name | `standard`, `fast-ssd` |
| accessModes | []string | Yes | Access mode | `[ReadWriteOnce]` |
| resources.requests.storage | string | Yes | Storage size | `10Gi`, `100Gi` |
| volumeName | string | Auto | Bound PV name | `pv-abc123` |
| volumeMode | string | No | Filesystem or Block | `Filesystem` (default) |
| selector | LabelSelector | No | PV selection criteria | `type: fast-ssd` |

### Access Modes

| Mode | Abbreviation | Description | Use Case |
|------|--------------|-------------|----------|
| **ReadWriteOnce** | RWO | Single node read-write | Database, stateful apps |
| **ReadOnlyMany** | ROX | Multiple nodes read-only | Shared config, static content |
| **ReadWriteMany** | RWX | Multiple nodes read-write | Shared logs, media files |
| **ReadWriteOncePod** | RWOP | Single pod read-write | High security requirements |

### Storage Classes

Storage classes define different storage tiers and provisioners:

| Storage Class | Provisioner | Performance | Use Case |
|--------------|-------------|-------------|----------|
| `standard` | Local/Default | Standard HDD | Development, non-critical |
| `fast-ssd` | SSD provisioner | High IOPS | Production databases |
| `retain` | Manual | N/A | Persistent backups |
| `hostpath` | Minikube | Local disk | Local development only |

### Relationships

- **Bound to PersistentVolume**: PVC is fulfilled by a matching PV
- **Mounted into Pods**: Deployment mounts PVC for persistent storage
- **Managed by StorageClass**: Dynamic provisioning creates PV automatically
- **Used by StatefulSet**: StatefulSet can create PVC per replica

### Business Rules

- PostgreSQL MUST use PVC with RWO access mode
- Storage size SHOULD be calculated based on data growth estimates
- Production databases MUST use SSD-backed storage classes
- PVCs SHOULD have reclaim policy "Retain" for production data
- Backups MUST be performed before PVC deletion
- Storage requests SHOULD include 30% growth buffer
- Minikube development MAY use hostPath storage class

### Example

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-data
  namespace: default
  labels:
    app.kubernetes.io/name: todo-app
    app.kubernetes.io/component: postgres
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: fast-ssd
  resources:
    requests:
      storage: 10Gi
  selector:
    matchLabels:
      type: ssd

---
# Usage in Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-postgres
spec:
  template:
    spec:
      containers:
        - name: postgres
          volumeMounts:
            - name: postgres-storage
              mountPath: /var/lib/postgresql/data
              subPath: pgdata
      volumes:
        - name: postgres-storage
          persistentVolumeClaim:
            claimName: postgres-data
```

---

## Entity Relationships Diagram

```
┌─────────────────┐
│  Docker Image   │
│                 │
│ - repository    │
│ - tag           │
│ - buildContext  │
└────────┬────────┘
         │
         │ used by
         ▼
┌─────────────────────────────────────────────────────┐
│              Helm Chart                             │
│                                                     │
│ - name: todo-app                                    │
│ - version: 1.0.0                                    │
│ - templates: [Deployment, Service, ConfigMap, ...]│
│ - values: {backend, frontend, database}            │
└──────────┬──────────────────────────────────────────┘
           │
           │ creates
           ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Deployment    │───►│   ReplicaSet     │───►│      Pod        │
│                 │    │                  │    │                 │
│ - replicas: 3   │    │ - desired: 3     │    │ - containers    │
│ - strategy      │    │ - current: 3     │    │ - volumes       │
└────────┬────────┘    └──────────────────┘    └─────────┬───────┘
         │                                                │
         │ mounts                                         │
         ▼                                                │
┌─────────────────┐    ┌──────────────────┐             │
│   ConfigMap     │    │     Secret       │◄────────────┘
│                 │    │                  │
│ - environment   │    │ - database-url   │
│ - cors-origins  │    │ - jwt-secret     │
└─────────────────┘    └──────────────────┘

         ┌─────────────────┐
         │    Service      │
         │                 │
         │ - type: ClusterIP│
         │ - port: 8000    │
         └────────┬────────┘
                  │
                  │ routes to
                  ▼
         ┌─────────────────┐
         │      Pods       │
         │  (via selector) │
         └────────┬────────┘
                  │
                  │ protected by
                  ▼
         ┌─────────────────┐
         │ NetworkPolicy   │
         │                 │
         │ - ingress rules │
         │ - egress rules  │
         └─────────────────┘

┌─────────────────┐
│     Ingress     │
│                 │
│ - host: todo.com│
│ - tls: enabled  │
└────────┬────────┘
         │
         │ routes to
         ▼
┌─────────────────┐
│    Service      │
│ (frontend)      │
└─────────────────┘

┌─────────────────┐    ┌──────────────────┐
│      PVC        │───►│   PersistentVol  │
│                 │    │                  │
│ - size: 10Gi    │    │ - hostPath/EBS   │
└────────┬────────┘    └──────────────────┘
         │
         │ mounted by
         ▼
┌─────────────────┐
│  PostgreSQL Pod │
│                 │
│ /var/lib/pg/data│
└─────────────────┘
```

---

## Data Validation Rules

### Image Tags
- Format: `v{major}.{minor}.{patch}[-{prerelease}][+{build}]`
- Examples: `v1.0.0`, `v1.2.3-rc1`, `v1.0.0+abc1234`

### Resource Limits
```yaml
# CPU format
cpu: "100m"   # 0.1 cores
cpu: "1"      # 1 core
cpu: "2000m"  # 2 cores

# Memory format
memory: "128Mi"  # 128 mebibytes
memory: "1Gi"    # 1 gibibyte
memory: "512M"   # 512 megabytes

# Storage format
storage: "10Gi"   # 10 gibibytes
storage: "100Mi"  # 100 mebibytes
```

### Label Conventions
```yaml
# Recommended Kubernetes labels
app.kubernetes.io/name: todo-app
app.kubernetes.io/instance: release-name
app.kubernetes.io/version: v1.2.3
app.kubernetes.io/component: backend
app.kubernetes.io/part-of: todo-system
app.kubernetes.io/managed-by: Helm
```

---

## Environment-Specific Configurations

### Development
- Replicas: 1
- Resources: Minimal (100m CPU, 128Mi memory)
- Storage: emptyDir or hostPath
- Autoscaling: Disabled
- NetworkPolicy: Disabled
- Ingress: NodePort or localhost

### Staging
- Replicas: 2
- Resources: Moderate (250m CPU, 256Mi memory)
- Storage: Standard persistent volumes
- Autoscaling: Enabled (2-5 replicas)
- NetworkPolicy: Enabled
- Ingress: Staging domain with TLS

### Production
- Replicas: 3+
- Resources: Production-grade (500m+ CPU, 512Mi+ memory)
- Storage: Fast SSD persistent volumes
- Autoscaling: Enabled (3-20 replicas)
- NetworkPolicy: Enabled with strict rules
- Ingress: Production domain with TLS
- PodDisruptionBudget: Enabled
- ServiceAccount: Enabled with RBAC

---

## Summary

This data model defines seven core entities for Kubernetes deployment:

1. **Docker Image** - Containerized application artifacts
2. **Helm Chart** - Kubernetes package with templates and values
3. **Deployment** - Manages pod replicas and rolling updates
4. **Service** - Stable network endpoints for pods
5. **ConfigMap** - Non-sensitive configuration data
6. **Secret** - Sensitive credentials and keys
7. **PersistentVolumeClaim** - Persistent storage requests

These entities work together to deploy a production-ready Todo Chatbot application on Kubernetes with proper security, scalability, and observability.
