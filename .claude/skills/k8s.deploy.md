# Skill: k8s.deploy

Deploy applications to the local Kubernetes cluster using Helm or kubectl.

## Description

This skill covers deploying applications to Minikube, including building images, loading them into the cluster, and using Helm charts.

## Prerequisites

- Minikube running (`k8s.start`)
- Helm installed (for Helm deployments)
- Docker images ready or Dockerfiles available

## Instructions

### Step 1: Build and Load Docker Images

Minikube has its own Docker daemon. You need to either:

**Option A: Use Minikube's Docker daemon directly**
```bash
# Point shell to Minikube's Docker
eval $(minikube docker-env)

# Build images (they'll be available in Minikube)
docker build -t myapp-backend:latest ./backend
docker build -t myapp-frontend:latest ./frontend

# Reset to host Docker when done
eval $(minikube docker-env -u)
```

**Option B: Build locally and load into Minikube**
```bash
# Build with host Docker
docker build -t myapp-backend:latest ./backend
docker build -t myapp-frontend:latest ./frontend

# Load images into Minikube
minikube image load myapp-backend:latest
minikube image load myapp-frontend:latest
```

### Step 2: Deploy with Helm

```bash
# Install/upgrade the release
helm upgrade --install todo-app ./helm-charts/todo-app \
  --namespace default \
  --set backend.image.tag=latest \
  --set frontend.image.tag=latest \
  -f ./helm-charts/todo-app/values-dev.yaml

# Check deployment status
helm status todo-app
```

### Step 3: Deploy with kubectl (without Helm)

```bash
# Apply manifests
kubectl apply -f ./k8s/

# Or apply specific files
kubectl apply -f ./k8s/deployment.yaml
kubectl apply -f ./k8s/service.yaml
```

### Step 4: Verify Deployment

```bash
# Check pods
kubectl get pods -w

# Check services
kubectl get services

# Check deployments
kubectl get deployments

# Describe a specific resource for details
kubectl describe deployment myapp-backend
```

## Full Deployment Script

```bash
#!/bin/bash
# deploy-to-minikube.sh

set -e
cd "$(dirname "$0")/.."

echo "🔨 Building images with Minikube Docker..."
eval $(minikube docker-env)

docker build -t todo-backend:latest ./backend
docker build -t todo-frontend:latest ./frontend

eval $(minikube docker-env -u)

echo "📦 Deploying with Helm..."
helm upgrade --install todo-app ./helm-charts/todo-app \
  --set backend.image.repository=todo-backend \
  --set backend.image.tag=latest \
  --set backend.image.pullPolicy=Never \
  --set frontend.image.repository=todo-frontend \
  --set frontend.image.tag=latest \
  --set frontend.image.pullPolicy=Never \
  -f ./helm-charts/todo-app/values-dev.yaml

echo "⏳ Waiting for pods..."
kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance=todo-app --timeout=120s

echo "✅ Deployment complete!"
kubectl get pods
kubectl get services
```

## Important: Image Pull Policy

When using locally built images, set `imagePullPolicy: Never` or `IfNotPresent`:

```yaml
# In Helm values or deployment manifest
image:
  pullPolicy: Never  # Don't try to pull from registry
```

## Troubleshooting

### ImagePullBackOff error
```bash
# Image not in Minikube. Load it:
minikube image load myapp:latest

# Or use Minikube's Docker:
eval $(minikube docker-env)
docker build -t myapp:latest .
```

### Pod stuck in Pending
```bash
# Check events for reason
kubectl describe pod <pod-name>

# Common causes: insufficient resources, PVC issues
kubectl get events --sort-by='.lastTimestamp'
```

### CrashLoopBackOff
```bash
# Check pod logs
kubectl logs <pod-name>
kubectl logs <pod-name> --previous  # Previous container logs
```

## Related Skills

- `k8s.start` - Start the cluster
- `k8s.status` - Check deployment status
- `k8s.logs` - View application logs
- `k8s.portforward` - Access services locally
