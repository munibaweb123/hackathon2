# Kubernetes Deployment Testing Guide

**Feature**: 001-k8s-deployment
**Date**: 2025-12-30
**Purpose**: Validate the minimal MVP Kubernetes deployment

---

## Prerequisites Checklist

Before starting, verify you have all required tools installed:

```bash
# Check Docker
docker --version
# Expected: Docker version 24.0.0 or higher

# Check Minikube
minikube version
# Expected: minikube version: v1.32.0 or higher

# Check kubectl
kubectl version --client
# Expected: Client Version: v1.29.0 or higher

# Check Helm
helm version
# Expected: version.BuildInfo{Version:"v3.14.0" ...}
```

**If any tool is missing, install it before proceeding:**
- Docker Desktop: https://www.docker.com/products/docker-desktop/
- Minikube: https://minikube.sigs.k8s.io/docs/start/
- kubectl: https://kubernetes.io/docs/tasks/tools/
- Helm: https://helm.sh/docs/intro/install/

---

## Step 1: Start Minikube Cluster

### 1.1 Start Minikube with Recommended Resources

```bash
# Start Minikube with adequate resources
minikube start \
  --cpus=2 \
  --memory=4096 \
  --disk-size=20g \
  --driver=docker

# Expected output:
# 😄  minikube v1.32.0 on ...
# ✨  Using the docker driver based on user configuration
# 👍  Starting control plane node minikube in cluster minikube
# ...
# 🏄  Done! kubectl is now configured to use "minikube" cluster
```

### 1.2 Verify Cluster Status

```bash
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

### 1.3 Enable Required Addons

```bash
# Enable metrics server (for resource monitoring)
minikube addons enable metrics-server

# Verify addon
minikube addons list | grep metrics-server
# Expected: | metrics-server | minikube | enabled ✅ |
```

**✅ Checkpoint 1**: Minikube cluster is running and healthy

---

## Step 2: Build Docker Images

### 2.1 Configure Docker to Use Minikube

```bash
# IMPORTANT: This configures your shell to use Minikube's Docker daemon
# Run this in every new terminal session where you build images
eval $(minikube docker-env)

# Verify configuration
docker ps | grep k8s
# Should show Minikube containers
```

### 2.2 Build Images Using Script

```bash
# Navigate to project root
cd "C:\Users\YOusuf Traders\Documents\quarter-4\hackathon_2"

# Build all images with version tag
./scripts/build-images.sh v1.0.0
```

**Expected Output:**
```
========================================
Building Docker Images for Minikube
========================================

Version: v1.0.0
Project Root: /path/to/hackathon_2

Building backend image...
✓ Backend image built successfully

Building frontend image...
✓ Frontend image built successfully

========================================
Build Complete!
========================================

Images built:
  - todo-backend:v1.0.0
  - todo-frontend:v1.0.0
```

### 2.3 Verify Images

```bash
docker images | grep -E "todo-(backend|frontend)" | grep "v1.0.0"
```

**Expected Output:**
```
todo-frontend    v1.0.0    abc123def456   2 minutes ago   524MB
todo-backend     v1.0.0    def456ghi789   5 minutes ago   412MB
```

**✅ Checkpoint 2**: Docker images built successfully

---

## Step 3: Validate Helm Chart

### 3.1 Lint the Helm Chart

```bash
helm lint helm-charts/todo-app
```

**Expected Output:**
```
==> Linting helm-charts/todo-app
[INFO] Chart.yaml: icon is recommended

1 chart(s) linted, 0 chart(s) failed
```

### 3.2 Dry Run Installation

```bash
helm install todo-app ./helm-charts/todo-app \
  --dry-run \
  --debug \
  --namespace default
```

This will output all Kubernetes manifests that will be created. Look for:
- ✅ No template errors
- ✅ Valid YAML syntax
- ✅ Proper resource naming
- ✅ Correct image references

### 3.3 Validate Specific Templates

```bash
# Check backend deployment
helm template todo-app ./helm-charts/todo-app \
  --show-only templates/deployment-backend.yaml

# Check frontend deployment
helm template todo-app ./helm-charts/todo-app \
  --show-only templates/deployment-frontend.yaml
```

**✅ Checkpoint 3**: Helm chart validates successfully

---

## Step 4: Deploy Application

### 4.1 Deploy with Helm

```bash
# Deploy using the automated script
./scripts/deploy.sh dev

# Or manually with Helm
helm install todo-app ./helm-charts/todo-app \
  -f ./helm-charts/todo-app/values-dev.yaml \
  --namespace default \
  --wait \
  --timeout 5m
```

**Expected Output:**
```
========================================
Deploying Todo App to Kubernetes
========================================

Environment: dev
Namespace: default
Release: todo-app

Linting Helm chart...
==> Linting helm-charts/todo-app
1 chart(s) linted, 0 chart(s) failed

Installing new release...
NAME: todo-app
...
STATUS: deployed
```

### 4.2 Monitor Pod Creation

```bash
# Watch pods being created
kubectl get pods -w -l app.kubernetes.io/name=todo-app

# Press Ctrl+C to stop watching
```

**Expected Pod States:**
```
NAME                              READY   STATUS              RESTARTS   AGE
todo-app-backend-xxx              0/1     ContainerCreating   0          10s
todo-app-frontend-xxx             0/1     ContainerCreating   0          10s
todo-app-postgres-xxx             0/1     ContainerCreating   0          10s

# After 30-60 seconds:
NAME                              READY   STATUS    RESTARTS   AGE
todo-app-backend-xxx              1/1     Running   0          45s
todo-app-frontend-xxx             1/1     Running   0          45s
todo-app-postgres-xxx             1/1     Running   0          45s
```

**✅ Checkpoint 4**: All pods reach Running status

---

## Step 5: Verify Deployment Health

### 5.1 Check All Resources

```bash
# Check all resources
kubectl get all -l app.kubernetes.io/name=todo-app

# Expected output:
# - 3 pods (backend, frontend, postgres)
# - 3 services
# - 3 deployments
# - 3 replicasets
```

### 5.2 Run Health Check Script

```bash
./scripts/health-check.sh default
```

**Expected Output:**
```
========================================
Todo App Health Check
========================================

Checking backend health...
Backend pod: todo-app-backend-xxx
✓ Liveness check passed
✓ Readiness check passed

Checking frontend health...
Frontend pod: todo-app-frontend-xxx
✓ Frontend health check passed

Checking database...
Database pod: todo-app-postgres-xxx
✓ Database is ready

Resource usage:
NAME                        CPU(cores)   MEMORY(bytes)
todo-app-backend-xxx        50m          128Mi
todo-app-frontend-xxx       30m          96Mi
todo-app-postgres-xxx       10m          64Mi

========================================
Health Check Complete
========================================
```

### 5.3 Manual Health Endpoint Verification

```bash
# Port forward backend
kubectl port-forward svc/todo-app-backend 8000:8000 &

# Test backend health endpoints
curl http://localhost:8000/livez
# Expected: {"status":"alive"}

curl http://localhost:8000/readyz
# Expected: {"status":"ready","checks":{"database":"healthy"}}

curl http://localhost:8000/health
# Expected: {"status":"healthy","app_name":"...","version":"..."}

# Kill port forward
pkill -f "port-forward svc/todo-app-backend"

# Port forward frontend
kubectl port-forward svc/todo-app-frontend 3000:3000 &

# Test frontend health endpoints
curl http://localhost:3000/api/health/live
# Expected: {"status":"alive"}

curl http://localhost:3000/api/health/ready
# Expected: {"status":"ready","checks":{"backend":"healthy"}}

# Kill port forward
pkill -f "port-forward svc/todo-app-frontend"
```

**✅ Checkpoint 5**: All health checks pass

---

## Step 6: Access Application

### 6.1 Get Frontend URL

```bash
# Method 1: Using Minikube service (opens browser)
minikube service todo-app-frontend

# Method 2: Get URL manually
export NODE_PORT=$(kubectl get -o jsonpath="{.spec.ports[0].nodePort}" services todo-app-frontend)
export NODE_IP=$(minikube ip)
echo "Frontend URL: http://$NODE_IP:$NODE_PORT"
```

### 6.2 Test Frontend Access

```bash
# Using curl
curl -I http://$(minikube ip):30000

# Expected: HTTP/1.1 200 OK
```

### 6.3 Access in Browser

Open the URL from step 6.1 in your browser:
- URL should be: `http://<minikube-ip>:30000`
- Expected: Todo application UI loads
- Expected: No console errors
- Expected: Can interact with the application

**✅ Checkpoint 6**: Application accessible via browser

---

## Step 7: Functional Testing

### 7.1 Test Phase III Features

Open the frontend in your browser and test:

**Basic Task Management:**
- [ ] Create a new task
- [ ] View task list
- [ ] Update task status
- [ ] Delete task

**Advanced Features (Phase III):**
- [ ] Create recurring task
- [ ] Set task reminder
- [ ] Use AI chatbot for task management
- [ ] Test task categories/tags
- [ ] Test search functionality

### 7.2 Test Data Persistence

```bash
# Create a test task via the UI or API

# Delete the backend pod to trigger restart
kubectl delete pod -l app.kubernetes.io/component=backend

# Wait for new pod to be ready
kubectl wait --for=condition=ready pod \
  -l app.kubernetes.io/component=backend \
  --timeout=60s

# Verify task still exists in the UI
# Expected: Tasks persist after pod restart (PostgreSQL PVC working)
```

### 7.3 Test Backend API Directly

```bash
# Port forward backend
kubectl port-forward svc/todo-app-backend 8000:8000 &

# Test API endpoints (adjust based on your actual API)
curl http://localhost:8000/docs
# Expected: Swagger UI documentation loads

# Kill port forward
pkill -f "port-forward svc/todo-app-backend"
```

**✅ Checkpoint 7**: Application functions correctly

---

## Step 8: Resource Monitoring

### 8.1 Check Resource Usage

```bash
# Pod resource usage
kubectl top pods -l app.kubernetes.io/name=todo-app

# Node resource usage
kubectl top nodes
```

### 8.2 Check Logs

```bash
# Backend logs
kubectl logs -l app.kubernetes.io/component=backend --tail=50

# Frontend logs
kubectl logs -l app.kubernetes.io/component=frontend --tail=50

# Database logs
kubectl logs -l app.kubernetes.io/component=postgres --tail=50
```

### 8.3 Check Events

```bash
# Check for any warnings or errors
kubectl get events --sort-by='.lastTimestamp' | tail -20
```

**✅ Checkpoint 8**: No resource issues or errors

---

## Step 9: Scaling Test

### 9.1 Scale Backend

```bash
# Scale backend to 3 replicas
kubectl scale deployment/todo-app-backend --replicas=3

# Wait for pods
kubectl wait --for=condition=ready pod \
  -l app.kubernetes.io/component=backend \
  --timeout=60s

# Verify all 3 pods are running
kubectl get pods -l app.kubernetes.io/component=backend
```

**Expected**: All 3 backend pods reach Running status

### 9.2 Scale Down

```bash
# Scale back to 1 replica
kubectl scale deployment/todo-app-backend --replicas=1
```

**✅ Checkpoint 9**: Scaling works without downtime

---

## Step 10: Helm Operations Test

### 10.1 Test Helm Upgrade

```bash
# Update log level
helm upgrade todo-app ./helm-charts/todo-app \
  --set backend.logLevel=DEBUG \
  --reuse-values \
  --wait

# Verify upgrade
helm list
kubectl get pods -l app.kubernetes.io/component=backend
```

### 10.2 Test Helm Rollback

```bash
# View revision history
helm history todo-app

# Rollback to previous version
helm rollback todo-app 1

# Verify rollback
helm list
kubectl get pods
```

**✅ Checkpoint 10**: Helm upgrade and rollback work

---

## Final Validation Checklist

Mark each item as you verify:

### Infrastructure
- [ ] Minikube cluster running
- [ ] Docker images built (backend, frontend)
- [ ] Helm chart validates without errors

### Deployment
- [ ] All 3 pods reach Running status
- [ ] No CrashLoopBackOff or Error states
- [ ] All pods pass health checks

### Networking
- [ ] Backend service accessible internally
- [ ] Frontend service accessible via NodePort
- [ ] PostgreSQL service accessible to backend
- [ ] Frontend can communicate with backend

### Health & Monitoring
- [ ] Backend /livez endpoint returns 200
- [ ] Backend /readyz endpoint returns 200
- [ ] Frontend /api/health/live returns 200
- [ ] Frontend /api/health/ready returns 200
- [ ] Resource usage within limits

### Functionality
- [ ] Frontend UI loads in browser
- [ ] Can create tasks
- [ ] Can view tasks
- [ ] Can update tasks
- [ ] Can delete tasks
- [ ] Phase III features work
- [ ] Data persists after pod restart

### Operations
- [ ] Pods can be scaled up/down
- [ ] Helm upgrade works
- [ ] Helm rollback works
- [ ] Logs accessible via kubectl

---

## Success Criteria (From spec.md)

Verify these success criteria are met:

- [ ] **SC-001**: Docker images build in under 5 minutes ✅
- [ ] **SC-002**: Application deploys to Minikube within 3 minutes ✅
- [ ] **SC-003**: All Phase III Todo features work correctly ✅
- [ ] **SC-004**: Pod restarts don't cause data loss or >5s interruption ✅
- [ ] **SC-007**: Full deployment cycle completes in <15 minutes ✅
- [ ] **SC-008**: Application scales 1→3→1 without service interruption ✅
- [ ] **SC-010**: API response times remain sub-second ✅

---

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl get pods -l app.kubernetes.io/name=todo-app

# Describe pod for events
kubectl describe pod <pod-name>

# Check logs
kubectl logs <pod-name>
```

**Common Issues:**
- **ImagePullBackOff**: Run `eval $(minikube docker-env)` before building
- **CrashLoopBackOff**: Check logs for application errors
- **Pending**: Check resource availability with `kubectl describe nodes`

### Service Not Accessible

```bash
# Check service endpoints
kubectl get endpoints

# Check service configuration
kubectl describe service/todo-app-frontend

# Test internal DNS
kubectl run -it --rm debug --image=busybox --restart=Never -- nslookup todo-app-backend
```

### Health Checks Failing

```bash
# Check probe configuration
kubectl describe pod <pod-name> | grep -A 5 "Liveness\|Readiness"

# Test endpoint manually from within pod
kubectl exec -it <pod-name> -- curl http://localhost:8000/livez
```

### Database Connection Issues

```bash
# Check database pod
kubectl get pods -l app.kubernetes.io/component=postgres

# Check database logs
kubectl logs -l app.kubernetes.io/component=postgres

# Verify DATABASE_URL environment variable
kubectl exec deployment/todo-app-backend -- env | grep DATABASE_URL
```

---

## Cleanup

When done testing:

```bash
# Uninstall application
./scripts/cleanup.sh default

# Or manually
helm uninstall todo-app
kubectl delete pvc -l app.kubernetes.io/name=todo-app

# Stop Minikube
minikube stop

# (Optional) Delete Minikube cluster
minikube delete
```

---

## Next Steps After Successful Testing

Once all checkpoints pass:

1. **Document Results**: Note any issues encountered
2. **Performance Baseline**: Record resource usage and response times
3. **Iteration 2**: Add advanced features (ConfigMaps, Secrets, HPA)
4. **User Story 2**: Implement AI-assisted DevOps tools
5. **Production Prep**: External database, secret management, monitoring

---

## Test Results Template

```markdown
# Deployment Test Results

**Date**: YYYY-MM-DD
**Tester**: [Your Name]
**Environment**: Minikube v1.32.0, Kubernetes v1.27.0

## Results Summary

- Build Time: ___ minutes
- Deploy Time: ___ minutes
- Total Setup Time: ___ minutes

## Checkpoints

1. Minikube Cluster: ✅/❌
2. Docker Images: ✅/❌
3. Helm Validation: ✅/❌
4. Deployment: ✅/❌
5. Health Checks: ✅/❌
6. Application Access: ✅/❌
7. Functional Tests: ✅/❌
8. Resource Monitoring: ✅/❌
9. Scaling: ✅/❌
10. Helm Operations: ✅/❌

## Issues Encountered

[List any issues and how they were resolved]

## Performance Metrics

- Backend Pod CPU: ___m
- Backend Pod Memory: ___Mi
- Frontend Pod CPU: ___m
- Frontend Pod Memory: ___Mi
- API Response Time: ___ms

## Recommendations

[Any improvements or observations]
```

---

**Good luck with your deployment! 🚀**
