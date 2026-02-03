# GKE Deployment Guide

This guide covers deploying the Todo App to Google Kubernetes Engine (GKE).

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Detailed Setup](#detailed-setup)
4. [CI/CD Pipeline](#cicd-pipeline)
5. [Monitoring & Troubleshooting](#monitoring--troubleshooting)
6. [Cost Optimization](#cost-optimization)

---

## Prerequisites

### Required Tools

```bash
# Install Google Cloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Initialize and authenticate
gcloud init
gcloud auth login
gcloud auth application-default login

# Install required components
gcloud components install kubectl gke-gcloud-auth-plugin
```

### Required Permissions

Your GCP account needs these roles:
- `roles/container.admin` - GKE management
- `roles/artifactregistry.admin` - Container registry
- `roles/cloudsql.admin` - Cloud SQL management
- `roles/iam.serviceAccountAdmin` - Service account management
- `roles/compute.admin` - Static IP allocation

### Environment Variables

Create a `.env.gke` file (do not commit):

```bash
export GCP_PROJECT_ID="your-project-id"
export GCP_REGION="us-central1"
export CLUSTER_NAME="todo-app-cluster"
export DOMAIN="todo.yourdomain.com"
export DB_PASSWORD="your-secure-database-password"
export BETTER_AUTH_SECRET="your-auth-secret"
export OPENAI_API_KEY="your-openai-key"  # Optional
```

---

## Quick Start

### One-Command Deployment

```bash
# Load environment variables
source .env.gke

# Run all setup scripts in sequence
cd infra/cloud/gke
./01-setup-cluster.sh && \
./02-setup-artifact-registry.sh && \
./03-setup-cloud-sql.sh && \
./04-deploy.sh
```

### Estimated Time & Cost

| Resource | Setup Time | Monthly Cost (estimate) |
|----------|------------|------------------------|
| GKE Autopilot | 5-10 min | $70-150 |
| Cloud SQL (db-g1-small) | 3-5 min | $25-50 |
| Artifact Registry | 1 min | $1-5 |
| Static IP | 1 min | $3 |
| **Total** | **15-20 min** | **$100-210** |

---

## Detailed Setup

### Step 1: Create GKE Cluster

```bash
export GCP_PROJECT_ID="your-project-id"
export CLUSTER_NAME="todo-app-cluster"

# Option A: Autopilot (recommended - managed, pay-per-pod)
./infra/cloud/gke/01-setup-cluster.sh

# Option B: Standard cluster (more control)
CLUSTER_TYPE=standard ./infra/cloud/gke/01-setup-cluster.sh
```

**Autopilot vs Standard:**

| Feature | Autopilot | Standard |
|---------|-----------|----------|
| Node management | Automatic | Manual |
| Pricing | Per-pod | Per-node |
| Min nodes | 0 (scales to zero) | 1+ |
| Best for | Variable workloads | Predictable workloads |

### Step 2: Set Up Artifact Registry

```bash
# Build and push all images
./infra/cloud/gke/02-setup-artifact-registry.sh all

# Or build specific images
./infra/cloud/gke/02-setup-artifact-registry.sh backend
./infra/cloud/gke/02-setup-artifact-registry.sh frontend
```

### Step 3: Create Cloud SQL Instance

```bash
export DB_PASSWORD="secure-password-here"

# Default tier (db-g1-small, ~$25/month)
./infra/cloud/gke/03-setup-cloud-sql.sh

# Smaller tier for development (db-f1-micro, ~$10/month)
DB_TIER=db-f1-micro ./infra/cloud/gke/03-setup-cloud-sql.sh
```

### Step 4: Deploy the Application

```bash
export DOMAIN="todo.yourdomain.com"

# Deploy
./infra/cloud/gke/04-deploy.sh

# Dry run (preview changes)
./infra/cloud/gke/04-deploy.sh --dry-run
```

### Step 5: Configure DNS

After deployment, get the static IP:

```bash
gcloud compute addresses describe todo-app-ip --global --format="value(address)"
```

Add an A record in your DNS provider:
- **Type:** A
- **Name:** todo (or @ for root)
- **Value:** <static-ip>
- **TTL:** 300

SSL certificates are provisioned automatically by Google after DNS propagates (5-15 minutes).

---

## CI/CD Pipeline

### GitHub Actions Setup

1. **Create a GCP Service Account for CI/CD:**

```bash
# Create service account
gcloud iam service-accounts create github-actions \
  --display-name="GitHub Actions"

# Grant permissions
SA_EMAIL="github-actions@${GCP_PROJECT_ID}.iam.gserviceaccount.com"

gcloud projects add-iam-policy-binding ${GCP_PROJECT_ID} \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/container.developer"

gcloud projects add-iam-policy-binding ${GCP_PROJECT_ID} \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/artifactregistry.writer"
```

2. **Set up Workload Identity Federation:**

```bash
# Create workload identity pool
gcloud iam workload-identity-pools create "github" \
  --location="global" \
  --display-name="GitHub Actions Pool"

# Create provider
gcloud iam workload-identity-pools providers create-oidc "github-provider" \
  --location="global" \
  --workload-identity-pool="github" \
  --display-name="GitHub Provider" \
  --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
  --issuer-uri="https://token.actions.githubusercontent.com"

# Bind service account
gcloud iam service-accounts add-iam-policy-binding ${SA_EMAIL} \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/github/attribute.repository/YOUR_GITHUB_ORG/YOUR_REPO"
```

3. **Add GitHub Secrets:**

| Secret Name | Value |
|------------|-------|
| `GCP_PROJECT_ID` | Your GCP project ID |
| `GCP_WORKLOAD_IDENTITY_PROVIDER` | `projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github/providers/github-provider` |
| `GCP_SERVICE_ACCOUNT` | `github-actions@PROJECT_ID.iam.gserviceaccount.com` |
| `DOMAIN` | Your domain (e.g., `todo.example.com`) |

4. **Trigger Deployment:**

Go to Actions > "CD - GKE Production" > Run workflow

---

## Monitoring & Troubleshooting

### View Logs

```bash
# All pods
kubectl logs -f -l app.kubernetes.io/name=todo-app -n todo-app

# Backend specifically
kubectl logs -f deployment/todo-app-backend -n todo-app

# Frontend
kubectl logs -f deployment/todo-app-frontend -n todo-app
```

### Check Pod Status

```bash
# List all pods
kubectl get pods -n todo-app -o wide

# Describe a pod
kubectl describe pod <pod-name> -n todo-app

# Check events
kubectl get events -n todo-app --sort-by='.lastTimestamp'
```

### Database Connectivity

```bash
# Connect to Cloud SQL directly
gcloud sql connect todo-postgres --user=todo_user --database=todo_app

# Check proxy logs
kubectl logs -f deployment/todo-app-backend -c cloudsql-proxy -n todo-app
```

### Common Issues

#### 1. Pods stuck in Pending

```bash
# Check if nodes are available
kubectl get nodes
kubectl describe pod <pod-name> -n todo-app | grep -A 20 Events
```

**Solution:** For Autopilot, pods may take 1-2 minutes to start as nodes scale up.

#### 2. SSL Certificate not provisioning

```bash
# Check certificate status
kubectl describe managedcertificate todo-app-cert -n todo-app
```

**Solution:** Ensure DNS is correctly pointing to the static IP. Certificates can take 15-60 minutes.

#### 3. Database connection refused

```bash
# Verify Cloud SQL Proxy is running
kubectl get pods -n todo-app -l app=todo-app-backend -o jsonpath='{.items[*].spec.containers[*].name}'

# Check secrets exist
kubectl get secrets -n todo-app
```

**Solution:** Ensure `db-credentials` secret exists and Cloud SQL Proxy sidecar is configured.

#### 4. 502 Bad Gateway

```bash
# Check backend health
kubectl port-forward svc/todo-app-backend 8000:8000 -n todo-app
curl http://localhost:8000/health
```

**Solution:** Usually indicates the backend isn't ready. Check pod logs and health checks.

---

## Cost Optimization

### Development Environment

```yaml
# Use in values-gke-dev.yaml
replicaCount:
  backend: 1
  frontend: 1
  notification: 0
  recurring: 0
  audit: 0

resources:
  backend:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 200m
      memory: 256Mi
```

### Reduce Cloud SQL Costs

```bash
# Use smaller tier
DB_TIER=db-f1-micro ./03-setup-cloud-sql.sh

# Stop instance when not in use
gcloud sql instances patch todo-postgres --activation-policy=NEVER
gcloud sql instances patch todo-postgres --activation-policy=ALWAYS  # to restart
```

### Clean Up Resources

```bash
# Delete deployment
helm uninstall todo-app -n todo-app

# Delete cluster
gcloud container clusters delete todo-app-cluster --region=us-central1

# Delete Cloud SQL
gcloud sql instances delete todo-postgres

# Delete static IP
gcloud compute addresses delete todo-app-ip --global

# Delete Artifact Registry
gcloud artifacts repositories delete todo-app --location=us-central1
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Google Cloud                              │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    Cloud Load Balancer                     │  │
│  │                 (with managed SSL cert)                    │  │
│  └─────────────────────────┬─────────────────────────────────┘  │
│                            │                                     │
│  ┌─────────────────────────┴─────────────────────────────────┐  │
│  │                    GKE Autopilot                           │  │
│  │  ┌─────────────────┐    ┌─────────────────┐               │  │
│  │  │    Frontend     │    │    Backend      │               │  │
│  │  │   (Next.js)     │    │   (FastAPI)     │               │  │
│  │  │   Replicas: 2   │    │   Replicas: 2   │               │  │
│  │  └─────────────────┘    └────────┬────────┘               │  │
│  │                                  │                         │  │
│  │                         ┌────────┴────────┐               │  │
│  │                         │ Cloud SQL Proxy │               │  │
│  │                         │   (sidecar)     │               │  │
│  │                         └────────┬────────┘               │  │
│  └──────────────────────────────────┼────────────────────────┘  │
│                                     │                            │
│  ┌──────────────────────────────────┴────────────────────────┐  │
│  │                     Cloud SQL                              │  │
│  │                   (PostgreSQL 16)                          │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                  Artifact Registry                         │  │
│  │              (Container images storage)                    │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Files Reference

| File | Description |
|------|-------------|
| `infra/cloud/gke/01-setup-cluster.sh` | Creates GKE cluster |
| `infra/cloud/gke/02-setup-artifact-registry.sh` | Creates container registry and builds images |
| `infra/cloud/gke/03-setup-cloud-sql.sh` | Creates PostgreSQL database |
| `infra/cloud/gke/04-deploy.sh` | Deploys application with Helm |
| `infra/helm/todo-app/values-gke.yaml` | GKE-specific Helm values |
| `infra/cloud/gke/gke-ingress.yaml` | Ingress and SSL configuration |
| `.github/workflows/cd-gke.yml` | GitHub Actions CD pipeline |

---

## Support

- [GKE Documentation](https://cloud.google.com/kubernetes-engine/docs)
- [Cloud SQL Documentation](https://cloud.google.com/sql/docs)
- [Artifact Registry Documentation](https://cloud.google.com/artifact-registry/docs)
