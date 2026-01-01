# Kubernetes Deployment Quickstart Guide
**Feature**: 001-k8s-deployment
**Created**: 2025-12-30

## Overview

This guide provides step-by-step instructions for deploying the Todo Chatbot application to a local Kubernetes cluster using Minikube and Helm. You'll learn how to build Docker images, configure Helm charts, deploy the application, and verify functionality.

**Estimated Time**: 30-45 minutes (first-time setup)

---

## Prerequisites

### Required Software

| Tool | Minimum Version | Installation | Verification |
|------|----------------|--------------|--------------|
| **Docker Desktop** | 4.53+ | [Download](https://www.docker.com/products/docker-desktop/) | `docker --version` |
| **Minikube** | 1.32+ | [Install Guide](https://minikube.sigs.k8s.io/docs/start/) | `minikube version` |
| **kubectl** | 1.27+ | [Install Guide](https://kubernetes.io/docs/tasks/tools/) | `kubectl version --client` |
| **Helm** | 3.14+ | [Install Guide](https://helm.sh/docs/intro/install/) | `helm version` |
| **kubectl-ai** (optional) | Latest | [GitHub](https://github.com/sozercan/kubectl-ai) | `kubectl-ai version` |
| **Kagent** (optional) | Latest | Installation varies by platform | `kagent --version` |

### System Requirements

- **RAM**: Minimum 8GB (4GB allocated to Minikube)
- **CPU**: 4+ cores (2 cores allocated to Minikube)
- **Disk**: 20GB free space
- **OS**: Windows 10/11, macOS 11+, or Linux

### Verify Installation

```bash
# Check all required tools
docker --version
# Expected: Docker version 24.0.0 or higher

minikube version
# Expected: minikube version: v1.32.0 or higher

kubectl version --client
# Expected: Client Version: v1.29.0 or higher

helm version
# Expected: version.BuildInfo{Version:"v3.14.0" ...}
```

---

## Step 1: Start Minikube Cluster

### 1.1 Start Minikube with Resource Allocation

```bash
# Start Minikube with adequate resources
minikube start \
  --cpus=2 \
  --memory=4096 \
  --disk-size=20g \
  --driver=docker

# Verify cluster status
minikube status
```

**Expected Output:**
```
minikube
type: Control Plane
host: Running
kubelet: Running
apiserver: Running
kubeconfig: Configured
```

### 1.2 Enable Required Addons

```bash
# Enable ingress controller (for external access)
minikube addons enable ingress

# Enable metrics server (for autoscaling)
minikube addons enable metrics-server

# Verify addons
minikube addons list | grep enabled
```

### 1.3 Configure Docker Environment

```bash
# Configure shell to use Minikube's Docker daemon
# This allows building images directly in Minikube (no need to push to registry)
eval $(minikube docker-env)

# Verify Docker is pointing to Minikube
docker ps
# Should show Minikube containers
```

**Important**: Run `eval $(minikube docker-env)` in each new terminal session where you build images.

---

## Step 2: Build Docker Images

### 2.1 Navigate to Project Root

```bash
cd /path/to/hackathon_2
```

### 2.2 Build Backend Image

```bash
# Build FastAPI backend
docker build \
  -t todo-backend:v1.0.0 \
  -f backend/Dockerfile \
  ./backend

# Verify image
docker images | grep todo-backend
```

**Build Arguments (Optional):**
```bash
docker build \
  --build-arg PYTHON_VERSION=3.13 \
  -t todo-backend:v1.0.0 \
  ./backend
```

### 2.3 Build Frontend Image

```bash
# Build Next.js frontend
docker build \
  --build-arg NEXT_PUBLIC_API_URL=http://todo-backend:8000 \
  --build-arg NEXT_PUBLIC_APP_VERSION=v1.0.0 \
  -t todo-frontend:v1.0.0 \
  -f frontend/Dockerfile \
  ./frontend

# Verify image
docker images | grep todo-frontend
```

### 2.4 Pull PostgreSQL Image

```bash
# Pull official PostgreSQL image
docker pull postgres:15-alpine

# Verify image
docker images | grep postgres
```

### 2.5 Verify All Images

```bash
docker images | grep -E "todo-|postgres"
```

**Expected Output:**
```
todo-frontend    v1.0.0    abc123def456   2 minutes ago   524MB
todo-backend     v1.0.0    def456ghi789   5 minutes ago   412MB
postgres         15-alpine xyz789abc123   1 hour ago      231MB
```

---

## Step 3: Create Helm Chart

### 3.1 Create Chart Directory Structure

```bash
# Create Helm chart directory
mkdir -p helm-charts/todo-app

# Create subdirectories
cd helm-charts/todo-app
mkdir -p templates tests ci
```

### 3.2 Create Chart.yaml

```bash
cat > Chart.yaml <<'EOF'
apiVersion: v2
name: todo-app
version: 1.0.0
appVersion: v1.0.0
description: Todo Chatbot application with FastAPI backend and Next.js frontend
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
EOF
```

### 3.3 Create values.yaml

```bash
cat > values.yaml <<'EOF'
global:
  environment: development

backend:
  replicaCount: 1
  image:
    repository: todo-backend
    tag: v1.0.0
    pullPolicy: IfNotPresent
  service:
    type: ClusterIP
    port: 8000
  resources:
    limits:
      cpu: 500m
      memory: 512Mi
    requests:
      cpu: 100m
      memory: 128Mi
  autoscaling:
    enabled: false
  logLevel: INFO

frontend:
  replicaCount: 1
  image:
    repository: todo-frontend
    tag: v1.0.0
    pullPolicy: IfNotPresent
  service:
    type: NodePort
    port: 3000
    nodePort: 30000
  resources:
    limits:
      cpu: 500m
      memory: 512Mi
    requests:
      cpu: 100m
      memory: 128Mi
  autoscaling:
    enabled: false

database:
  external:
    enabled: false
  internal:
    enabled: true
    image: postgres:15-alpine
    persistence:
      enabled: true
      size: 1Gi
      storageClass: standard
    resources:
      limits:
        cpu: 500m
        memory: 512Mi
      requests:
        cpu: 100m
        memory: 256Mi

ingress:
  enabled: false

networkPolicy:
  enabled: false

serviceAccount:
  create: true
  name: ""

migration:
  enabled: false

config:
  corsOrigins: "*"
  jwtExpiration: 3600

secrets:
  databaseUrl: "postgresql://todo_user:todo_password@todo-postgres:5432/todo_db"
  databaseUsername: "todo_user"
  databasePassword: "todo_password"
  jwtSecret: "dev-jwt-secret-must-be-32-chars-long-min"
  betterAuthSecret: "dev-better-auth-secret-32-chars-min"
EOF
```

### 3.4 Copy Kubernetes Templates

Copy the Kubernetes resource templates from `specs/001-k8s-deployment/contracts/kubernetes-resources.yaml` to `templates/` directory, or use the Helm chart templates provided in the research documentation.

**Quick Template Setup:**

```bash
# Create minimal templates for quickstart
# (Full templates available in contracts/kubernetes-resources.yaml)

# Backend Deployment
cat > templates/deployment-backend.yaml <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "todo-app.fullname" . }}-backend
  labels:
    {{- include "todo-app.labels" . | nindent 4 }}
    app.kubernetes.io/component: backend
spec:
  replicas: {{ .Values.backend.replicaCount }}
  selector:
    matchLabels:
      {{- include "todo-app.selectorLabels" . | nindent 6 }}
      app.kubernetes.io/component: backend
  template:
    metadata:
      labels:
        {{- include "todo-app.selectorLabels" . | nindent 8 }}
        app.kubernetes.io/component: backend
    spec:
      containers:
        - name: fastapi
          image: "{{ .Values.backend.image.repository }}:{{ .Values.backend.image.tag }}"
          imagePullPolicy: {{ .Values.backend.image.pullPolicy }}
          ports:
            - name: http
              containerPort: 8000
          env:
            - name: DATABASE_URL
              value: {{ .Values.secrets.databaseUrl | quote }}
            - name: JWT_SECRET
              value: {{ .Values.secrets.jwtSecret | quote }}
            - name: LOG_LEVEL
              value: {{ .Values.backend.logLevel | quote }}
          livenessProbe:
            httpGet:
              path: /livez
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /readyz
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 5
          resources:
            {{- toYaml .Values.backend.resources | nindent 12 }}
EOF

# Create other templates similarly...
# See contracts/kubernetes-resources.yaml for complete templates
```

### 3.5 Create Helper Templates

```bash
cat > templates/_helpers.tpl <<'EOF'
{{- define "todo-app.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "todo-app.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}

{{- define "todo-app.labels" -}}
helm.sh/chart: {{ include "todo-app.chart" . }}
{{ include "todo-app.selectorLabels" . }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- define "todo-app.selectorLabels" -}}
app.kubernetes.io/name: {{ include "todo-app.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{- define "todo-app.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}
EOF
```

---

## Step 4: Deploy with Helm

### 4.1 Validate Helm Chart

```bash
# Lint Helm chart
helm lint helm-charts/todo-app

# Dry-run to see generated manifests
helm install todo-app helm-charts/todo-app --dry-run --debug
```

### 4.2 Install Application

```bash
# Install Helm release
helm install todo-app ./helm-charts/todo-app \
  --namespace default \
  --create-namespace

# Watch pod creation
kubectl get pods -w
```

**Expected Output:**
```
NAME                            READY   STATUS    RESTARTS   AGE
todo-backend-xxxxxxxxx-xxxxx    1/1     Running   0          30s
todo-frontend-xxxxxxxxx-xxxxx   1/1     Running   0          30s
todo-postgres-xxxxxxxxx-xxxxx   1/1     Running   0          30s
```

### 4.3 Verify Deployment

```bash
# Check all resources
helm list
kubectl get all

# Check deployments
kubectl get deployments

# Check services
kubectl get services

# Check pods in detail
kubectl get pods -o wide
```

---

## Step 5: Access the Application

### 5.1 Get Minikube IP

```bash
# Get Minikube cluster IP
minikube ip
# Example output: 192.168.49.2
```

### 5.2 Access Frontend

```bash
# Method 1: Using NodePort
# Frontend is accessible at http://<minikube-ip>:30000
curl http://$(minikube ip):30000/api/health

# Method 2: Using minikube service
minikube service todo-frontend --url
# Opens browser or shows URL

# Method 3: Port forwarding
kubectl port-forward service/todo-frontend 3000:3000
# Access at http://localhost:3000
```

### 5.3 Access Backend API

```bash
# Port forward backend service
kubectl port-forward service/todo-backend 8000:8000

# Test health endpoint
curl http://localhost:8000/health

# Test liveness
curl http://localhost:8000/livez

# Test readiness
curl http://localhost:8000/readyz
```

### 5.4 Open Application in Browser

```bash
# Open frontend in default browser
minikube service todo-frontend

# Or manually navigate to:
# http://<minikube-ip>:30000
```

---

## Step 6: Verify Deployment Health

### 6.1 Check Pod Health

```bash
# Get pod status
kubectl get pods

# Check pod logs
kubectl logs deployment/todo-backend
kubectl logs deployment/todo-frontend
kubectl logs deployment/todo-postgres

# Follow logs in real-time
kubectl logs -f deployment/todo-backend
```

### 6.2 Verify Health Checks

```bash
# Port forward backend
kubectl port-forward service/todo-backend 8000:8000

# Test endpoints (in another terminal)
curl http://localhost:8000/livez    # Should return {"status": "alive"}
curl http://localhost:8000/readyz   # Should return {"status": "ready", "checks": {...}}
curl http://localhost:8000/health   # Should return version info

# Port forward frontend
kubectl port-forward service/todo-frontend 3000:3000

# Test frontend health
curl http://localhost:3000/api/health/live
curl http://localhost:3000/api/health/ready
```

### 6.3 Verify Database Connectivity

```bash
# Connect to PostgreSQL pod
kubectl exec -it deployment/todo-postgres -- psql -U todo_user -d todo_db

# Run SQL query
SELECT version();

# List tables
\dt

# Exit
\q
```

### 6.4 Check Resource Usage

```bash
# View pod resource usage
kubectl top pods

# View node resource usage
kubectl top nodes
```

---

## Step 7: Common Operations

### 7.1 Scale Application

```bash
# Scale backend to 3 replicas
kubectl scale deployment/todo-backend --replicas=3

# Verify scaling
kubectl get pods -l app.kubernetes.io/component=backend

# Scale using Helm (recommended)
helm upgrade todo-app ./helm-charts/todo-app \
  --set backend.replicaCount=3 \
  --reuse-values
```

### 7.2 Update Application

```bash
# Build new image version
eval $(minikube docker-env)
docker build -t todo-backend:v1.0.1 ./backend

# Update Helm release
helm upgrade todo-app ./helm-charts/todo-app \
  --set backend.image.tag=v1.0.1 \
  --reuse-values

# Watch rollout
kubectl rollout status deployment/todo-backend
```

### 7.3 Rollback Deployment

```bash
# View revision history
helm history todo-app

# Rollback to previous version
helm rollback todo-app

# Rollback to specific revision
helm rollback todo-app 2

# Verify rollback
kubectl get pods
```

### 7.4 View Application Logs

```bash
# Stream backend logs
kubectl logs -f deployment/todo-backend

# Stream frontend logs
kubectl logs -f deployment/todo-frontend

# View last 100 lines
kubectl logs deployment/todo-backend --tail=100

# View logs from all backend pods
kubectl logs -l app.kubernetes.io/component=backend --all-containers
```

---

## Step 8: Using AI Tools (Optional)

### 8.1 kubectl-ai Setup

```bash
# Install kubectl-ai
# See: https://github.com/sozercan/kubectl-ai

# Set OpenAI API key
export OPENAI_API_KEY=sk-...

# Deploy using natural language
kubectl-ai "deploy the todo frontend with 2 replicas"

# Check cluster health
kubectl-ai "check why the pods are failing"

# Scale application
kubectl-ai "scale the backend to handle more load"
```

### 8.2 Kagent Usage

```bash
# Analyze cluster health
kagent "analyze the cluster health"

# Optimize resource allocation
kagent "optimize resource allocation"

# Debug issues
kagent "why is my pod in CrashLoopBackOff?"
```

### 8.3 Docker AI Agent (Gordon)

```bash
# Enable in Docker Desktop settings
# Docker Desktop > Settings > Features in development > Enable Docker AI Agent

# Ask Gordon for help
# "What can you do?"
# "Help me build a Docker image for my FastAPI app"
```

---

## Step 9: Troubleshooting

### 9.1 Pod Not Starting

```bash
# Check pod status
kubectl get pods

# Describe pod for events
kubectl describe pod <pod-name>

# Check logs
kubectl logs <pod-name>

# Common issues:
# - Image pull errors: Check image name and tag
# - CrashLoopBackOff: Check application logs
# - Pending: Check resource availability (kubectl describe nodes)
```

### 9.2 Service Not Accessible

```bash
# Check service endpoints
kubectl get endpoints

# Check service configuration
kubectl describe service/todo-frontend

# Test internal DNS
kubectl run -it --rm debug --image=busybox --restart=Never -- nslookup todo-backend

# Check NetworkPolicy (if enabled)
kubectl get networkpolicies
```

### 9.3 Health Checks Failing

```bash
# Check probe configuration
kubectl describe pod <pod-name> | grep -A 5 "Liveness\|Readiness"

# Test health endpoint manually
kubectl exec -it <pod-name> -- curl http://localhost:8000/livez

# Increase initialDelaySeconds if startup is slow
```

### 9.4 Database Connection Issues

```bash
# Check database pod
kubectl get pods -l app.kubernetes.io/component=postgres

# Check database logs
kubectl logs deployment/todo-postgres

# Test connection from backend pod
kubectl exec -it deployment/todo-backend -- \
  curl -v telnet://todo-postgres:5432

# Verify DATABASE_URL environment variable
kubectl exec deployment/todo-backend -- env | grep DATABASE_URL
```

### 9.5 Resource Constraints

```bash
# Check node capacity
kubectl describe nodes | grep -A 5 "Allocated resources"

# Check resource requests vs limits
kubectl describe pod <pod-name> | grep -A 10 "Requests\|Limits"

# Increase Minikube resources
minikube stop
minikube start --cpus=4 --memory=8192
```

---

## Step 10: Cleanup

### 10.1 Uninstall Application

```bash
# Uninstall Helm release
helm uninstall todo-app

# Verify removal
kubectl get pods
```

### 10.2 Delete Persistent Volumes

```bash
# List PVCs
kubectl get pvc

# Delete PVC (deletes data)
kubectl delete pvc postgres-data

# List PVs
kubectl get pv

# Delete PV if needed
kubectl delete pv <pv-name>
```

### 10.3 Stop Minikube

```bash
# Stop Minikube (preserves cluster state)
minikube stop

# Delete Minikube cluster (removes all data)
minikube delete

# Delete all Minikube clusters
minikube delete --all
```

### 10.4 Clean Docker Images

```bash
# Remove built images
docker rmi todo-backend:v1.0.0
docker rmi todo-frontend:v1.0.0

# Clean up unused images
docker image prune -a
```

---

## Step 11: Next Steps

### 11.1 Enable Ingress

```yaml
# Update values.yaml
ingress:
  enabled: true
  className: nginx
  host: todo.local
  tls: []

# Update /etc/hosts
echo "$(minikube ip) todo.local" | sudo tee -a /etc/hosts

# Upgrade deployment
helm upgrade todo-app ./helm-charts/todo-app -f values.yaml

# Access at http://todo.local
```

### 11.2 Enable Autoscaling

```yaml
# Update values.yaml
backend:
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 10
    targetCPUUtilizationPercentage: 70

# Upgrade deployment
helm upgrade todo-app ./helm-charts/todo-app -f values.yaml

# Generate load to test
kubectl run -it --rm load-generator --image=busybox --restart=Never -- \
  /bin/sh -c "while true; do wget -q -O- http://todo-backend:8000/health; done"

# Watch autoscaling
kubectl get hpa -w
```

### 11.3 Add Monitoring

```bash
# Install Prometheus and Grafana
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack

# Access Grafana
kubectl port-forward svc/prometheus-grafana 3001:80
# Default credentials: admin / prom-operator
```

### 11.4 Deploy to Production

- Use external managed database (AWS RDS, Google Cloud SQL)
- Enable External Secrets Operator for secret management
- Configure production ingress with TLS certificates
- Enable NetworkPolicy for security
- Set up CI/CD pipeline for automated deployments
- Configure monitoring and alerting
- Implement backup and disaster recovery

---

## Quick Reference

### Essential Commands

```bash
# Cluster Management
minikube start --cpus=2 --memory=4096
minikube status
minikube stop
minikube delete

# Docker
eval $(minikube docker-env)
docker build -t <image>:<tag> <path>
docker images

# Helm
helm lint <chart>
helm install <release> <chart>
helm upgrade <release> <chart>
helm rollback <release>
helm uninstall <release>
helm list

# Kubectl
kubectl get pods
kubectl get services
kubectl logs <pod>
kubectl describe <resource> <name>
kubectl exec -it <pod> -- <command>
kubectl port-forward service/<service> <local-port>:<service-port>

# Health Checks
curl http://localhost:8000/livez
curl http://localhost:8000/readyz
curl http://localhost:8000/health
```

### Useful Aliases

```bash
# Add to ~/.bashrc or ~/.zshrc
alias k=kubectl
alias kg='kubectl get'
alias kd='kubectl describe'
alias kl='kubectl logs'
alias kgp='kubectl get pods'
alias kgs='kubectl get services'
alias kgd='kubectl get deployments'
alias mk=minikube
alias h=helm
```

---

## Support and Resources

### Documentation
- [Kubernetes Docs](https://kubernetes.io/docs/)
- [Helm Docs](https://helm.sh/docs/)
- [Minikube Docs](https://minikube.sigs.k8s.io/docs/)
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)

### Community
- [Kubernetes Slack](https://kubernetes.slack.com/)
- [Stack Overflow - Kubernetes](https://stackoverflow.com/questions/tagged/kubernetes)
- [CNCF Slack](https://cloud-native.slack.com/)

### AI Tools
- [kubectl-ai](https://github.com/sozercan/kubectl-ai)
- [Kagent](https://github.com/kagent-ai/kagent)
- [Docker AI Agent](https://docs.docker.com/desktop/features/ai-agent/)

---

## Congratulations!

You have successfully deployed the Todo Chatbot application to Kubernetes using Minikube and Helm. You now have a production-ready deployment running locally with proper health checks, resource management, and scalability.

**What you accomplished:**
- Set up a local Kubernetes cluster with Minikube
- Built Docker images for all application components
- Created and deployed a Helm chart
- Configured health checks and resource limits
- Verified application functionality
- Learned common Kubernetes operations

**Next challenges:**
- Deploy to a cloud Kubernetes service (GKE, EKS, AKS)
- Implement CI/CD pipelines
- Add monitoring and observability
- Configure production secrets management
- Set up automated backups

Happy deploying!
