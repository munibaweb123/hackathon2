# Kubernetes Deployment - Quick Reference

**Quick access to common commands for deploying and managing the Todo App on Kubernetes.**

---

## 🚀 Quick Start (First Time)

```bash
# 1. Check prerequisites
./scripts/check-prerequisites.sh

# 2. Start Minikube
minikube start --cpus=2 --memory=4096

# 3. Configure Docker
eval $(minikube docker-env)

# 4. Build images
./scripts/build-images.sh v1.0.0

# 5. Deploy
./scripts/deploy.sh dev

# 6. Access application
minikube service todo-app-frontend
```

---

## 📋 Common Commands

### Minikube

```bash
# Start cluster
minikube start --cpus=2 --memory=4096

# Check status
minikube status

# Get IP
minikube ip

# Open service in browser
minikube service todo-app-frontend

# SSH into cluster
minikube ssh

# Stop cluster (preserves data)
minikube stop

# Delete cluster (removes all data)
minikube delete

# Dashboard
minikube dashboard
```

### Docker

```bash
# Use Minikube Docker daemon
eval $(minikube docker-env)

# Undo (use local Docker)
eval $(minikube docker-env -u)

# Build images
./scripts/build-images.sh v1.0.0

# List images in Minikube
docker images | grep todo

# Remove old images
docker rmi todo-backend:old-tag
```

### Helm

```bash
# Lint chart
helm lint helm-charts/todo-app

# Install
helm install todo-app ./helm-charts/todo-app

# Install with values file
helm install todo-app ./helm-charts/todo-app -f ./helm-charts/todo-app/values-dev.yaml

# Upgrade
helm upgrade todo-app ./helm-charts/todo-app --reuse-values

# Rollback
helm rollback todo-app

# List releases
helm list

# Get release info
helm get all todo-app

# Uninstall
helm uninstall todo-app
```

### Kubectl - Pods

```bash
# List all pods
kubectl get pods

# List todo app pods
kubectl get pods -l app.kubernetes.io/name=todo-app

# Watch pods
kubectl get pods -w

# Describe pod
kubectl describe pod <pod-name>

# Get pod logs
kubectl logs <pod-name>

# Follow logs
kubectl logs -f <pod-name>

# Get logs from all backend pods
kubectl logs -l app.kubernetes.io/component=backend --all-containers

# Execute command in pod
kubectl exec -it <pod-name> -- /bin/bash

# Delete pod (will be recreated)
kubectl delete pod <pod-name>
```

### Kubectl - Services

```bash
# List services
kubectl get services

# List todo app services
kubectl get svc -l app.kubernetes.io/name=todo-app

# Describe service
kubectl describe svc todo-app-frontend

# Port forward service
kubectl port-forward svc/todo-app-backend 8000:8000

# Get service endpoints
kubectl get endpoints
```

### Kubectl - Deployments

```bash
# List deployments
kubectl get deployments

# Describe deployment
kubectl describe deployment todo-app-backend

# Scale deployment
kubectl scale deployment/todo-app-backend --replicas=3

# Restart deployment (rolling restart)
kubectl rollout restart deployment/todo-app-backend

# Check rollout status
kubectl rollout status deployment/todo-app-backend

# View rollout history
kubectl rollout history deployment/todo-app-backend
```

### Kubectl - Other Resources

```bash
# List all resources
kubectl get all

# List all todo app resources
kubectl get all -l app.kubernetes.io/name=todo-app

# Get PVCs
kubectl get pvc

# Get events
kubectl get events --sort-by='.lastTimestamp'

# Get resource usage
kubectl top nodes
kubectl top pods
```

---

## 🔍 Debugging

### Check Pod Status

```bash
# Quick status
kubectl get pods -l app.kubernetes.io/name=todo-app

# Detailed status
kubectl describe pod <pod-name>

# Check events
kubectl get events --field-selector involvedObject.name=<pod-name>

# Check logs
kubectl logs <pod-name> --previous  # Previous container logs
```

### Test Connectivity

```bash
# Test DNS
kubectl run -it --rm debug --image=busybox --restart=Never -- nslookup todo-app-backend

# Test HTTP
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
  curl http://todo-app-backend:8000/health

# Test from backend to database
kubectl exec -it deployment/todo-app-backend -- \
  curl -v telnet://todo-app-postgres:5432
```

### Health Checks

```bash
# Backend health
kubectl port-forward svc/todo-app-backend 8000:8000 &
curl http://localhost:8000/livez
curl http://localhost:8000/readyz
curl http://localhost:8000/health
pkill -f "port-forward svc/todo-app-backend"

# Frontend health
kubectl port-forward svc/todo-app-frontend 3000:3000 &
curl http://localhost:3000/api/health/live
curl http://localhost:3000/api/health/ready
pkill -f "port-forward svc/todo-app-frontend"

# Or use script
./scripts/health-check.sh
```

---

## 📊 Monitoring

### Resource Usage

```bash
# Enable metrics-server
minikube addons enable metrics-server

# Node metrics
kubectl top nodes

# Pod metrics
kubectl top pods -l app.kubernetes.io/name=todo-app

# Watch resource usage
watch kubectl top pods
```

### Logs

```bash
# Backend logs (last 50 lines)
kubectl logs -l app.kubernetes.io/component=backend --tail=50

# Frontend logs (follow)
kubectl logs -l app.kubernetes.io/component=frontend -f

# Database logs
kubectl logs -l app.kubernetes.io/component=postgres --tail=100

# All logs from a deployment
kubectl logs deployment/todo-app-backend --all-containers=true
```

---

## 🔧 Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl get pods

# Common issues:
# - ImagePullBackOff: eval $(minikube docker-env)
# - CrashLoopBackOff: kubectl logs <pod-name>
# - Pending: kubectl describe nodes
```

### Service Not Accessible

```bash
# Check service
kubectl describe svc todo-app-frontend

# Check endpoints
kubectl get endpoints todo-app-frontend

# Test internal connectivity
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
  curl http://todo-app-backend:8000/health
```

### Database Issues

```bash
# Check database pod
kubectl get pods -l app.kubernetes.io/component=postgres

# Check database logs
kubectl logs -l app.kubernetes.io/component=postgres

# Connect to database
kubectl exec -it deployment/todo-app-postgres -- \
  psql -U todo_user -d todo_db

# Check DATABASE_URL in backend
kubectl exec deployment/todo-app-backend -- env | grep DATABASE_URL
```

---

## 🛠️ Automation Scripts

All scripts are in `./scripts/` directory:

```bash
# Check prerequisites
./scripts/check-prerequisites.sh

# Build Docker images
./scripts/build-images.sh [version]

# Deploy application
./scripts/deploy.sh [environment] [namespace]

# Run health checks
./scripts/health-check.sh [namespace]

# Cleanup resources
./scripts/cleanup.sh [namespace] [--delete-pvc]
```

---

## 📝 Useful Aliases

Add to `~/.bashrc` or `~/.zshrc`:

```bash
# Kubectl
alias k=kubectl
alias kgp='kubectl get pods'
alias kgs='kubectl get svc'
alias kgd='kubectl get deployments'
alias kl='kubectl logs'
alias kd='kubectl describe'
alias kdel='kubectl delete'

# Minikube
alias mk=minikube
alias mks='minikube status'
alias mki='minikube ip'

# Helm
alias h=helm
alias hl='helm list'
alias hi='helm install'
alias hu='helm upgrade'
alias hdel='helm uninstall'

# Combined
alias kwa='kubectl get all'
alias kwat='kubectl get all -l app.kubernetes.io/name=todo-app'
```

---

## 🎯 Common Workflows

### Update Application Version

```bash
# 1. Build new images
eval $(minikube docker-env)
./scripts/build-images.sh v1.0.1

# 2. Upgrade deployment
helm upgrade todo-app ./helm-charts/todo-app \
  --set backend.image.tag=v1.0.1 \
  --set frontend.image.tag=v1.0.1 \
  --reuse-values

# 3. Verify
kubectl rollout status deployment/todo-app-backend
kubectl rollout status deployment/todo-app-frontend
```

### Rollback Deployment

```bash
# 1. Check history
helm history todo-app

# 2. Rollback
helm rollback todo-app

# 3. Verify
kubectl get pods -l app.kubernetes.io/name=todo-app
```

### Scale Application

```bash
# Scale up
kubectl scale deployment/todo-app-backend --replicas=3

# Scale down
kubectl scale deployment/todo-app-backend --replicas=1

# Or via Helm
helm upgrade todo-app ./helm-charts/todo-app \
  --set backend.replicaCount=3 \
  --reuse-values
```

### Clean Restart

```bash
# 1. Delete everything
./scripts/cleanup.sh default --delete-pvc

# 2. Rebuild images
eval $(minikube docker-env)
./scripts/build-images.sh v1.0.0

# 3. Redeploy
./scripts/deploy.sh dev
```

---

## 📚 Documentation

- **Full Deployment Guide**: `DEPLOYMENT_TEST.md`
- **Helm Chart README**: `helm-charts/todo-app/README.md`
- **Project README**: `README.md`
- **Quickstart Guide**: `specs/001-k8s-deployment/quickstart.md`

---

## 🆘 Getting Help

```bash
# Kubectl help
kubectl --help
kubectl get --help
kubectl describe --help

# Helm help
helm --help
helm install --help

# Minikube help
minikube --help
```

---

**Happy Deploying! 🚀**
