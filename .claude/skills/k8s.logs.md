# Skill: k8s.logs

View and stream logs from Kubernetes pods and containers.

## Description

This skill covers viewing logs from pods, containers, and deployments in Kubernetes, including real-time streaming and filtering.

## Prerequisites

- kubectl installed and configured
- Pods running in the cluster

## Instructions

### Basic Log Commands

#### View pod logs
```bash
# Logs from a pod
kubectl logs <pod-name>

# Logs from a specific container in a multi-container pod
kubectl logs <pod-name> -c <container-name>

# Logs from all containers in a pod
kubectl logs <pod-name> --all-containers=true
```

#### View logs by label selector
```bash
# Logs from all pods matching a label
kubectl logs -l app=todo-app-backend

# Logs from all pods in a deployment
kubectl logs deployment/todo-app-backend
```

### Streaming and Following

```bash
# Stream logs in real-time (like tail -f)
kubectl logs -f <pod-name>

# Stream logs from all pods with a label
kubectl logs -f -l app=todo-app-backend

# Stream with timestamps
kubectl logs -f --timestamps <pod-name>
```

### Historical Logs

```bash
# Last 100 lines
kubectl logs --tail=100 <pod-name>

# Logs from last hour
kubectl logs --since=1h <pod-name>

# Logs from last 30 minutes
kubectl logs --since=30m <pod-name>

# Logs since specific time
kubectl logs --since-time="2024-01-15T10:00:00Z" <pod-name>
```

### Previous Container Logs

```bash
# Logs from previous (crashed) container instance
kubectl logs <pod-name> --previous

# Useful for debugging CrashLoopBackOff
kubectl logs <pod-name> -p
```

### Multi-Pod Log Viewing

Using stern (recommended for multiple pods):
```bash
# Install stern
brew install stern  # macOS
# or download from https://github.com/stern/stern

# View logs from all pods matching pattern
stern todo-app

# With regex
stern "todo-app-.*"

# Specific namespace
stern todo-app -n production
```

## Log Viewing Script

```bash
#!/bin/bash
# k8s-logs.sh - Smart log viewer

SELECTOR=${1:-"app.kubernetes.io/instance=todo-app"}
NAMESPACE=${2:-default}
LINES=${3:-100}

echo "📋 Viewing logs for: $SELECTOR"
echo "   Namespace: $NAMESPACE"
echo "   Lines: $LINES"
echo "─────────────────────────────"

# Get all pods matching selector
PODS=$(kubectl get pods -n $NAMESPACE -l "$SELECTOR" -o jsonpath='{.items[*].metadata.name}')

if [ -z "$PODS" ]; then
    echo "❌ No pods found matching selector: $SELECTOR"
    exit 1
fi

echo "Found pods: $PODS"
echo ""

for POD in $PODS; do
    echo "═══════════════════════════════════════"
    echo "📦 POD: $POD"
    echo "═══════════════════════════════════════"

    # Get containers in pod
    CONTAINERS=$(kubectl get pod $POD -n $NAMESPACE -o jsonpath='{.spec.containers[*].name}')

    for CONTAINER in $CONTAINERS; do
        echo ""
        echo "🔹 Container: $CONTAINER"
        echo "───────────────────────────────────────"
        kubectl logs $POD -n $NAMESPACE -c $CONTAINER --tail=$LINES 2>/dev/null || \
            echo "  (no logs or container not ready)"
    done
done
```

## Common Debugging Patterns

### Debug CrashLoopBackOff
```bash
# Get pod name
POD=$(kubectl get pods -l app=todo-app-backend -o jsonpath='{.items[0].metadata.name}')

# Check current logs
kubectl logs $POD

# Check previous container logs (before crash)
kubectl logs $POD --previous

# Describe pod for events
kubectl describe pod $POD
```

### Debug startup issues
```bash
# Watch pod events
kubectl get events --field-selector involvedObject.name=$POD --watch

# Check init container logs (if any)
kubectl logs $POD -c init-container-name
```

### Search logs for errors
```bash
# Grep for errors
kubectl logs $POD | grep -i error

# Grep for specific pattern
kubectl logs $POD | grep -E "(ERROR|WARN|Exception)"

# Count errors
kubectl logs $POD | grep -c -i error
```

### Export logs to file
```bash
# Save to file
kubectl logs $POD > pod-logs.txt

# Save with timestamp
kubectl logs $POD --timestamps > pod-logs-$(date +%Y%m%d-%H%M%S).txt

# Save all app logs
for pod in $(kubectl get pods -l app=todo-app -o name); do
    kubectl logs $pod > "logs-${pod#pod/}.txt"
done
```

## Troubleshooting

### No logs available
```bash
# Check if pod is running
kubectl get pod $POD

# Check container status
kubectl describe pod $POD | grep -A5 "Container ID"

# Container might not have started yet
kubectl get pod $POD -o jsonpath='{.status.containerStatuses[*].ready}'
```

### Logs rotated/missing
```bash
# Check last restart time
kubectl get pod $POD -o jsonpath='{.status.containerStatuses[*].lastState.terminated.finishedAt}'

# Logs are lost on container restart - use centralized logging for persistence
```

### Too many logs to search
```bash
# Use time filters
kubectl logs $POD --since=5m

# Or line limits
kubectl logs $POD --tail=50
```

## Related Skills

- `k8s.status` - Check pod status
- `k8s.portforward` - Access services for testing
- `k8s.cleanup` - Restart pods for fresh logs
