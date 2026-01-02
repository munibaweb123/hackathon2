# Skill: k8s.status

Check the status of the Kubernetes cluster and deployed applications.

## Description

This skill provides comprehensive status checking for your local Kubernetes environment, including cluster health, pod status, and resource utilization.

## Prerequisites

- kubectl installed and configured
- Minikube or Kubernetes cluster running

## Instructions

### Quick Status Check

```bash
# One-liner for quick overview
kubectl cluster-info && kubectl get nodes && kubectl get pods --all-namespaces
```

### Detailed Status Commands

#### Cluster Health
```bash
# Cluster info
kubectl cluster-info

# Node status
kubectl get nodes -o wide

# Cluster component status
kubectl get componentstatuses 2>/dev/null || kubectl get --raw='/readyz?verbose'
```

#### Pod Status
```bash
# All pods in current namespace
kubectl get pods

# All pods in all namespaces
kubectl get pods --all-namespaces

# Pods with more details
kubectl get pods -o wide

# Watch pods in real-time
kubectl get pods -w
```

#### Service Status
```bash
# List services
kubectl get services

# List endpoints
kubectl get endpoints
```

#### Deployment Status
```bash
# List deployments
kubectl get deployments

# Rollout status
kubectl rollout status deployment/<deployment-name>
```

#### Resource Usage
```bash
# Node resource usage (requires metrics-server)
kubectl top nodes

# Pod resource usage
kubectl top pods

# Enable metrics-server if not installed
minikube addons enable metrics-server
```

### Minikube-Specific Status

```bash
# Minikube status
minikube status

# Minikube IP
minikube ip

# List minikube services
minikube service list

# Dashboard (opens in browser)
minikube dashboard
```

## Comprehensive Status Script

```bash
#!/bin/bash
# k8s-status.sh - Full cluster status

echo "╔══════════════════════════════════════╗"
echo "║     KUBERNETES CLUSTER STATUS        ║"
echo "╚══════════════════════════════════════╝"

echo ""
echo "🔧 MINIKUBE STATUS"
echo "─────────────────"
minikube status 2>/dev/null || echo "Minikube not running or not installed"

echo ""
echo "🌐 CLUSTER INFO"
echo "───────────────"
kubectl cluster-info 2>/dev/null || { echo "❌ Cluster not accessible"; exit 1; }

echo ""
echo "🖥️  NODES"
echo "────────"
kubectl get nodes -o wide

echo ""
echo "📦 PODS (All Namespaces)"
echo "────────────────────────"
kubectl get pods --all-namespaces --field-selector=status.phase!=Running 2>/dev/null | head -20
echo ""
kubectl get pods --all-namespaces -o custom-columns=\
'NAMESPACE:.metadata.namespace,NAME:.metadata.name,STATUS:.status.phase,RESTARTS:.status.containerStatuses[0].restartCount,AGE:.metadata.creationTimestamp'

echo ""
echo "🔌 SERVICES"
echo "───────────"
kubectl get services --all-namespaces

echo ""
echo "📊 RESOURCE USAGE"
echo "─────────────────"
kubectl top nodes 2>/dev/null || echo "(metrics-server not enabled)"
echo ""
kubectl top pods 2>/dev/null || echo "(enable with: minikube addons enable metrics-server)"

echo ""
echo "⚠️  RECENT EVENTS"
echo "─────────────────"
kubectl get events --sort-by='.lastTimestamp' --field-selector type!=Normal 2>/dev/null | tail -10 || echo "No warning events"
```

## Troubleshooting Status Issues

### Connection refused
```bash
# Check if cluster is running
minikube status

# Start if not running
minikube start
```

### Pods not ready
```bash
# Get detailed pod info
kubectl describe pod <pod-name>

# Check events
kubectl get events --field-selector involvedObject.name=<pod-name>
```

### Service not accessible
```bash
# Check endpoints
kubectl get endpoints <service-name>

# Check service selector matches pod labels
kubectl get pods --show-labels
kubectl describe service <service-name>
```

## Related Skills

- `k8s.start` - Start the cluster
- `k8s.logs` - View application logs
- `k8s.portforward` - Access services locally
