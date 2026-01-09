# Quickstart: Phase V - Advanced Cloud Deployment

**Feature**: 004-advanced-cloud-deploy
**Date**: 2026-01-04

## Prerequisites

- Docker Desktop 4.53+
- Minikube v1.32+
- kubectl v1.28+
- Helm 3.x
- Dapr CLI v1.12+
- Node.js 20+
- Python 3.13+
- Git

## Quick Setup (Local Development)

### 1. Clone and Install Dependencies

```bash
# Clone repository
git clone <repository-url>
cd hackathon_2

# Backend dependencies
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend dependencies
cd ../frontend
npm install
```

### 2. Start Minikube with Dapr

```bash
# Start Minikube
minikube start --cpus=4 --memory=8192

# Install Dapr
dapr init -k

# Verify Dapr installation
dapr status -k
```

### 3. Deploy Redpanda (Local Kafka)

```bash
# Add Redpanda Helm repo
helm repo add redpanda https://charts.redpanda.com
helm repo update

# Install Redpanda (single node for dev)
helm install redpanda redpanda/redpanda \
  --namespace redpanda --create-namespace \
  --set statefulset.replicas=1 \
  --set resources.cpu.cores=1 \
  --set resources.memory.container.max=1.5Gi

# Wait for Redpanda to be ready
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=redpanda -n redpanda --timeout=300s
```

### 4. Apply Dapr Components

```bash
# Create namespace
kubectl create namespace todo-app

# Apply Dapr components
kubectl apply -f infra/helm/dapr-components/ -n todo-app
```

### 5. Run Database Migrations

```bash
cd backend

# Set environment variables
export DATABASE_URL="postgresql://user:password@neon-host/todo"

# Run migrations
alembic upgrade head
```

### 6. Start Services Locally

```bash
# Terminal 1: Backend API with Dapr
cd backend
dapr run --app-id backend --app-port 8000 --dapr-http-port 3500 -- uvicorn app.main:app --reload

# Terminal 2: Notification Service with Dapr
cd backend/services/notification
dapr run --app-id notification --app-port 8001 --dapr-http-port 3501 -- python main.py

# Terminal 3: Recurring Service with Dapr
cd backend/services/recurring
dapr run --app-id recurring --app-port 8002 --dapr-http-port 3502 -- python main.py

# Terminal 4: Audit Service with Dapr
cd backend/services/audit
dapr run --app-id audit --app-port 8003 --dapr-http-port 3503 -- python main.py

# Terminal 5: Frontend
cd frontend
npm run dev
```

### 7. Verify Setup

```bash
# Check Dapr services
dapr list

# Test backend health
curl http://localhost:8000/health

# Test Dapr pub/sub
curl -X POST http://localhost:3500/v1.0/publish/kafka-pubsub/task-events \
  -H "Content-Type: application/json" \
  -d '{"event_type": "test", "task_id": "123"}'

# Access frontend
open http://localhost:3000
```

## Kubernetes Deployment (Minikube)

### 1. Build and Push Images

```bash
# Point docker to Minikube's daemon
eval $(minikube docker-env)

# Build images
docker build -t todo-backend:latest -f infra/docker/backend.Dockerfile .
docker build -t todo-frontend:latest -f infra/docker/frontend.Dockerfile .
docker build -t todo-notification:latest -f infra/docker/notification.Dockerfile .
docker build -t todo-recurring:latest -f infra/docker/recurring.Dockerfile .
docker build -t todo-audit:latest -f infra/docker/audit.Dockerfile .
```

### 2. Deploy with Helm

```bash
# Install the Helm chart
helm install todo-app infra/helm/todo-app \
  --namespace todo-app \
  --create-namespace \
  -f infra/helm/todo-app/values-minikube.yaml

# Wait for pods
kubectl wait --for=condition=ready pod -l app=todo-app -n todo-app --timeout=300s
```

### 3. Access the Application

```bash
# Get Minikube IP
minikube service todo-app-frontend -n todo-app --url
```

## Cloud Deployment (DOKS/GKE/AKS)

### DigitalOcean (DOKS)

```bash
# Install doctl CLI
brew install doctl  # macOS

# Authenticate
doctl auth init

# Create cluster
doctl kubernetes cluster create todo-cluster \
  --region nyc1 \
  --node-pool "name=default;size=s-2vcpu-4gb;count=3"

# Get credentials
doctl kubernetes cluster kubeconfig save todo-cluster
```

### Google Cloud (GKE)

```bash
# Install gcloud CLI
# See: https://cloud.google.com/sdk/docs/install

# Authenticate
gcloud auth login

# Create cluster
gcloud container clusters create todo-cluster \
  --zone us-central1-a \
  --num-nodes 3 \
  --machine-type e2-standard-2

# Get credentials
gcloud container clusters get-credentials todo-cluster --zone us-central1-a
```

### Azure (AKS)

```bash
# Install Azure CLI
brew install azure-cli  # macOS

# Authenticate
az login

# Create resource group
az group create --name todo-rg --location eastus

# Create cluster
az aks create \
  --resource-group todo-rg \
  --name todo-cluster \
  --node-count 3 \
  --node-vm-size Standard_B2s \
  --generate-ssh-keys

# Get credentials
az aks get-credentials --resource-group todo-rg --name todo-cluster
```

### Deploy to Cloud

```bash
# Install Dapr on cloud cluster
dapr init -k --runtime-version 1.12.0

# Apply Dapr components (with Redpanda Cloud)
kubectl apply -f infra/helm/dapr-components/cloud/ -n todo-app

# Deploy application
helm install todo-app infra/helm/todo-app \
  --namespace todo-app \
  --create-namespace \
  -f infra/helm/todo-app/values-production.yaml

# Verify deployment
kubectl get pods -n todo-app
kubectl get svc -n todo-app
```

## Environment Variables

### Backend (.env)

```bash
# Database
DATABASE_URL=postgresql://user:password@neon-host/todo

# Auth
BETTER_AUTH_SECRET=your-secret-key

# Dapr
DAPR_HTTP_PORT=3500
PUBSUB_NAME=kafka-pubsub

# Email (Resend)
RESEND_API_KEY=re_xxxxx

# Redpanda Cloud (for non-Dapr direct access)
KAFKA_BOOTSTRAP_SERVERS=your-cluster.cloud.redpanda.com:9092
KAFKA_SASL_USERNAME=your-username
KAFKA_SASL_PASSWORD=your-password
```

### Frontend (.env.local)

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

## Testing

```bash
# Backend unit tests
cd backend
pytest tests/unit -v

# Backend integration tests
pytest tests/integration -v

# Frontend tests
cd frontend
npm test

# E2E tests
npm run test:e2e

# Load testing (k6)
k6 run tests/load/tasks-api.js
```

## Monitoring Setup

```bash
# Install Prometheus + Grafana
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace

# Access Grafana
kubectl port-forward svc/prometheus-grafana 3001:80 -n monitoring
# Default: admin / prom-operator

# Install Loki for logs
helm repo add grafana https://grafana.github.io/helm-charts
helm install loki grafana/loki-stack \
  --namespace monitoring
```

## Troubleshooting

### Dapr not publishing events

```bash
# Check Dapr sidecar logs
kubectl logs <pod-name> -c daprd -n todo-app

# Verify component connection
dapr components -k -n todo-app
```

### Kafka/Redpanda connection issues

```bash
# Check Redpanda logs
kubectl logs -l app.kubernetes.io/name=redpanda -n redpanda

# Test connectivity
kubectl run kafka-client --rm -it --image=bitnami/kafka -- \
  kafka-topics.sh --bootstrap-server redpanda.redpanda:9092 --list
```

### Database connection issues

```bash
# Check Neon connection
psql $DATABASE_URL -c "SELECT 1"

# View backend logs
kubectl logs -l app=backend -n todo-app
```

## Next Steps

1. Run `/sp.tasks` to generate implementation tasks
2. Set up CI/CD pipeline in GitHub Actions
3. Configure production secrets in Kubernetes
4. Set up monitoring dashboards in Grafana
