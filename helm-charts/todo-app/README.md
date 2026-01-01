# Todo App Helm Chart

Helm chart for deploying the Todo Chatbot application to Kubernetes.

## Prerequisites

- Kubernetes 1.27+
- Helm 3.14+
- Docker Desktop 4.53+ (for local development)
- Minikube 1.32+ (for local Kubernetes cluster)

## Quick Start

### 1. Start Minikube

```bash
minikube start --cpus=2 --memory=4096 --disk-size=20g --driver=docker
```

### 2. Build Docker Images

```bash
# Configure shell to use Minikube's Docker daemon
eval $(minikube docker-env)

# Build images
cd ../../  # Return to project root
./scripts/build-images.sh v1.0.0
```

### 3. Install the Chart

```bash
# From project root
helm install todo-app ./helm-charts/todo-app

# Or with specific values file
helm install todo-app ./helm-charts/todo-app -f ./helm-charts/todo-app/values-dev.yaml
```

### 4. Access the Application

```bash
# Get frontend URL
minikube service todo-app-frontend

# Or use port-forward
kubectl port-forward svc/todo-app-frontend 3000:3000
# Visit http://localhost:3000
```

## Configuration

The following table lists the configurable parameters of the Todo App chart and their default values.

### Global Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `global.environment` | Environment name | `development` |

### Backend Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `backend.replicaCount` | Number of backend replicas | `1` |
| `backend.image.repository` | Backend image repository | `todo-backend` |
| `backend.image.tag` | Backend image tag | `v1.0.0` |
| `backend.image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `backend.service.type` | Service type | `ClusterIP` |
| `backend.service.port` | Service port | `8000` |
| `backend.resources.limits.cpu` | CPU limit | `500m` |
| `backend.resources.limits.memory` | Memory limit | `512Mi` |
| `backend.logLevel` | Log level | `INFO` |

### Frontend Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `frontend.replicaCount` | Number of frontend replicas | `1` |
| `frontend.image.repository` | Frontend image repository | `todo-frontend` |
| `frontend.image.tag` | Frontend image tag | `v1.0.0` |
| `frontend.service.type` | Service type | `NodePort` |
| `frontend.service.port` | Service port | `3000` |
| `frontend.service.nodePort` | NodePort value | `30000` |

### Database Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `database.internal.enabled` | Enable internal PostgreSQL | `true` |
| `database.internal.image` | PostgreSQL image | `postgres:15-alpine` |
| `database.internal.persistence.enabled` | Enable persistence | `true` |
| `database.internal.persistence.size` | PVC size | `1Gi` |
| `database.internal.persistence.storageClass` | Storage class | `standard` |

## Values Files

### Development (values-dev.yaml)

- 1 replica per service
- NodePort service for frontend
- Internal PostgreSQL with persistence
- Debug logging
- Minimal resources

### Production (values-prod.yaml)

- 3 replicas per service
- LoadBalancer service for frontend
- External managed database
- Warning-level logging
- Production-grade resources
- Autoscaling enabled (3-20 replicas)
- Ingress with TLS

## Common Operations

### Upgrade

```bash
# Upgrade with new image version
helm upgrade todo-app ./helm-charts/todo-app \
  --set backend.image.tag=v1.0.1 \
  --set frontend.image.tag=v1.0.1 \
  --reuse-values
```

### Rollback

```bash
# Rollback to previous version
helm rollback todo-app

# Rollback to specific revision
helm rollback todo-app 2
```

### Uninstall

```bash
helm uninstall todo-app

# Delete PVCs (WARNING: This deletes all data)
kubectl delete pvc -l app.kubernetes.io/name=todo-app
```

### Scale

```bash
# Scale backend
kubectl scale deployment todo-app-backend --replicas=3

# Or via Helm
helm upgrade todo-app ./helm-charts/todo-app \
  --set backend.replicaCount=3 \
  --reuse-values
```

## Health Checks

The chart includes comprehensive health probes:

- **Startup Probe**: Checks if application started (30 attempts, 2s interval)
- **Liveness Probe**: Checks if application is alive (10s interval)
- **Readiness Probe**: Checks if application can serve traffic (5s interval)

### Backend Health Endpoints

- `/livez` - Simple liveness check
- `/readyz` - Readiness check with database validation
- `/health` - General health with version info

### Frontend Health Endpoints

- `/api/health/live` - Liveness check
- `/api/health/ready` - Readiness check with backend connectivity
- `/api/health` - General health endpoint

## Security

The chart implements security best practices:

- **Non-root users**: All containers run as non-root
- **Drop capabilities**: ALL Linux capabilities dropped
- **No privilege escalation**: Explicitly disabled
- **Security contexts**: Pod and container-level security

## Troubleshooting

### Pods not starting

```bash
# Check pod status
kubectl get pods -l app.kubernetes.io/name=todo-app

# Describe pod for events
kubectl describe pod <pod-name>

# Check logs
kubectl logs <pod-name>
```

### Service not accessible

```bash
# Check service endpoints
kubectl get endpoints

# Check service configuration
kubectl describe service/todo-app-frontend
```

### Database connection issues

```bash
# Check database pod
kubectl logs deployment/todo-app-postgres

# Test connection from backend
kubectl exec -it deployment/todo-app-backend -- curl http://todo-app-postgres:5432
```

## Development

### Template Validation

```bash
# Lint chart
helm lint ./helm-charts/todo-app

# Dry run to see generated manifests
helm install todo-app ./helm-charts/todo-app --dry-run --debug

# Template specific resources
helm template todo-app ./helm-charts/todo-app --show-only templates/deployment-backend.yaml
```

### Testing

```bash
# Run Helm tests
helm test todo-app

# Manual health check
kubectl port-forward svc/todo-app-backend 8000:8000
curl http://localhost:8000/livez
curl http://localhost:8000/readyz
```

## Chart Structure

```
helm-charts/todo-app/
├── Chart.yaml              # Chart metadata
├── values.yaml             # Default values
├── values-dev.yaml         # Development overrides
├── values-prod.yaml        # Production overrides
├── .helmignore             # Files to ignore
└── templates/
    ├── _helpers.tpl        # Helper templates
    ├── NOTES.txt           # Post-install notes
    ├── deployment-backend.yaml
    ├── deployment-frontend.yaml
    ├── deployment-postgres.yaml
    ├── service-backend.yaml
    ├── service-frontend.yaml
    ├── service-postgres.yaml
    ├── pvc-postgres.yaml
    └── serviceaccount.yaml
```

## License

See the main project LICENSE file.
