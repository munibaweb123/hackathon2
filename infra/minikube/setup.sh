#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "=== Todo App - Minikube Setup ==="

# 1. Start Minikube
echo "[1/6] Starting Minikube..."
minikube start --cpus=4 --memory=8192 --driver=docker

# 2. Enable addons
echo "[2/6] Enabling addons..."
minikube addons enable ingress
minikube addons enable metrics-server

# 3. Install Dapr
echo "[3/6] Installing Dapr..."
dapr init -k --wait

# 4. Point Docker to Minikube
echo "[4/6] Building Docker images..."
eval $(minikube docker-env)
docker build -t todo-backend:latest -f "$REPO_ROOT/infra/docker/backend.Dockerfile" "$REPO_ROOT"
docker build -t todo-frontend:latest -f "$REPO_ROOT/infra/docker/frontend.Dockerfile" "$REPO_ROOT"
docker build -t todo-notification:latest -f "$REPO_ROOT/infra/docker/notification.Dockerfile" "$REPO_ROOT"
docker build -t todo-recurring:latest -f "$REPO_ROOT/infra/docker/recurring.Dockerfile" "$REPO_ROOT"
docker build -t todo-audit:latest -f "$REPO_ROOT/infra/docker/audit.Dockerfile" "$REPO_ROOT"

# 5. Deploy Dapr components
echo "[5/6] Deploying Dapr components..."
kubectl create namespace todo-app --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -f "$REPO_ROOT/infra/helm/dapr-components/" -n todo-app

# 6. Deploy with Helm
echo "[6/6] Deploying application..."
helm upgrade --install todo-app "$REPO_ROOT/infra/helm/todo-app" \
  --namespace todo-app \
  -f "$REPO_ROOT/infra/helm/todo-app/values-minikube.yaml" \
  --wait --timeout 300s

echo ""
echo "=== Setup Complete ==="
echo "Access the application:"
minikube service todo-app-frontend -n todo-app --url
echo ""
echo "Add to /etc/hosts:"
echo "$(minikube ip) todo.local"
