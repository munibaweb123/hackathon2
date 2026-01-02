# Skill: k8s.portforward

Port forward Kubernetes services to localhost for local development and testing.

## Description

This skill enables accessing Kubernetes services from your local machine through port forwarding. Essential for testing applications running in the cluster.

## Prerequisites

- kubectl installed
- Kubernetes cluster running with deployed services

## Instructions

### Basic Port Forwarding

#### Forward to a Service
```bash
# Forward local port 8000 to service port 8000
kubectl port-forward service/todo-app-backend 8000:8000

# Forward to different local port
kubectl port-forward service/todo-app-backend 8080:8000

# Forward multiple ports
kubectl port-forward service/todo-app-backend 8000:8000 8001:8001
```

#### Forward to a Pod
```bash
# Get pod name
kubectl get pods

# Forward to specific pod
kubectl port-forward pod/todo-app-backend-abc123 8000:8000
```

#### Forward to a Deployment
```bash
kubectl port-forward deployment/todo-app-backend 8000:8000
```

### Advanced Options

#### Listen on all interfaces (not just localhost)
```bash
# Accessible from other machines on network
kubectl port-forward --address 0.0.0.0 service/todo-app-backend 8000:8000

# Multiple addresses
kubectl port-forward --address localhost,192.168.1.100 service/todo-app-backend 8000:8000
```

#### Run in background
```bash
# Run in background
kubectl port-forward service/todo-app-backend 8000:8000 &

# Get the process ID
PF_PID=$!

# Stop later
kill $PF_PID
```

#### With timeout
```bash
# Wait up to 2 minutes for pod to be ready
kubectl port-forward service/todo-app-backend 8000:8000 --pod-running-timeout=2m0s
```

### Multiple Services Script

```bash
#!/bin/bash
# portforward-all.sh - Forward all app services

set -e

echo "🔌 Starting port forwards..."

# Forward backend (port 8000)
kubectl port-forward service/todo-app-backend 8000:8000 &
BACKEND_PID=$!

# Forward frontend (port 3000)
kubectl port-forward service/todo-app-frontend 3000:3000 &
FRONTEND_PID=$!

# Forward database (port 5432) - be careful with this in production!
kubectl port-forward service/todo-app-postgres 5432:5432 &
DB_PID=$!

echo ""
echo "✅ Port forwards active:"
echo "   Backend:  http://localhost:8000"
echo "   Frontend: http://localhost:3000"
echo "   Postgres: localhost:5432"
echo ""
echo "Press Ctrl+C to stop all port forwards"

# Cleanup function
cleanup() {
    echo ""
    echo "🛑 Stopping port forwards..."
    kill $BACKEND_PID $FRONTEND_PID $DB_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Wait for any process to exit
wait
```

### Using Minikube Service (Alternative)

Minikube provides a simpler way to access NodePort services:

```bash
# Open service in browser
minikube service todo-app-frontend

# Get URL without opening browser
minikube service todo-app-frontend --url

# List all accessible services
minikube service list
```

## Common Use Cases

### Access API for testing
```bash
# Forward and test
kubectl port-forward service/todo-app-backend 8000:8000 &
curl http://localhost:8000/health
curl http://localhost:8000/api/tasks
```

### Connect database client
```bash
# Forward PostgreSQL
kubectl port-forward service/todo-app-postgres 5432:5432 &

# Connect with psql
psql -h localhost -p 5432 -U postgres -d tododb
```

### Access Kubernetes Dashboard
```bash
# Forward dashboard service
kubectl -n kubernetes-dashboard port-forward svc/kubernetes-dashboard-kong-proxy 8443:443

# Access at: https://localhost:8443
```

## Troubleshooting

### Port already in use
```bash
# Find what's using the port
lsof -i :8000

# Use different local port
kubectl port-forward service/todo-app-backend 8080:8000
```

### Connection refused after starting
```bash
# Check if service has endpoints
kubectl get endpoints todo-app-backend

# Check if pods are running
kubectl get pods -l app=todo-app-backend

# View pod logs for errors
kubectl logs -l app=todo-app-backend
```

### Port forward dies unexpectedly
```bash
# Add retry logic
while true; do
    kubectl port-forward service/todo-app-backend 8000:8000
    echo "Port forward died, restarting in 5s..."
    sleep 5
done
```

### Error: unable to forward port
```bash
# Check pod is ready
kubectl get pods -o wide

# Describe service
kubectl describe service todo-app-backend

# Check service selector matches pod labels
kubectl get pods --show-labels
```

## Related Skills

- `k8s.status` - Check service and pod status
- `k8s.logs` - View application logs
- `k8s.deploy` - Deploy services
