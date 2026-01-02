# Skill: k8s.cleanup

Clean up Kubernetes resources and manage cluster lifecycle.

## Description

This skill covers cleaning up deployments, stopping the cluster, and managing resources to free up system resources.

## Prerequisites

- kubectl installed and configured
- Minikube running (for Minikube-specific commands)

## Instructions

### Application Cleanup

#### Delete Helm Release
```bash
# Uninstall a Helm release
helm uninstall todo-app

# Uninstall and purge history
helm uninstall todo-app --keep-history  # keeps history
helm uninstall todo-app                  # removes everything
```

#### Delete by kubectl
```bash
# Delete all resources from manifests
kubectl delete -f ./k8s/

# Delete specific resources
kubectl delete deployment todo-app-backend
kubectl delete service todo-app-backend
kubectl delete pod todo-app-backend-abc123

# Delete by label selector
kubectl delete all -l app=todo-app

# Delete all in namespace (careful!)
kubectl delete all --all -n my-namespace
```

#### Delete Persistent Volume Claims
```bash
# List PVCs
kubectl get pvc

# Delete specific PVC
kubectl delete pvc postgres-data

# Delete all PVCs (data will be lost!)
kubectl delete pvc --all
```

### Pod Management

#### Restart pods (trigger new deployment)
```bash
# Rollout restart
kubectl rollout restart deployment/todo-app-backend

# Delete pods to force recreation
kubectl delete pods -l app=todo-app-backend

# Scale down then up
kubectl scale deployment/todo-app-backend --replicas=0
kubectl scale deployment/todo-app-backend --replicas=3
```

#### Force delete stuck pods
```bash
# Force delete (use sparingly)
kubectl delete pod <pod-name> --force --grace-period=0
```

### Cluster Cleanup

#### Stop Minikube (preserves data)
```bash
# Stop cluster (can restart later)
minikube stop

# Check status
minikube status
```

#### Delete Minikube (full reset)
```bash
# Delete cluster and all data
minikube delete

# Delete all clusters
minikube delete --all

# Purge all minikube files
minikube delete --all --purge
```

#### Clean Docker resources
```bash
# Remove unused images
docker image prune -a

# Remove all stopped containers
docker container prune

# Remove all unused resources
docker system prune -a

# Clean Minikube's Docker images
eval $(minikube docker-env)
docker image prune -a
eval $(minikube docker-env -u)
```

### Namespace Cleanup

```bash
# Delete namespace (deletes all resources in it)
kubectl delete namespace my-namespace

# Create fresh namespace
kubectl create namespace my-namespace
```

## Comprehensive Cleanup Script

```bash
#!/bin/bash
# k8s-cleanup.sh - Clean up Kubernetes resources

set -e

echo "🧹 Kubernetes Cleanup Script"
echo "═══════════════════════════"

# Parse arguments
FULL_CLEANUP=false
KEEP_CLUSTER=true

while [[ "$#" -gt 0 ]]; do
    case $1 in
        --full) FULL_CLEANUP=true ;;
        --stop-cluster) KEEP_CLUSTER=false ;;
        -h|--help)
            echo "Usage: $0 [--full] [--stop-cluster]"
            echo "  --full         Delete PVCs and all data"
            echo "  --stop-cluster Stop minikube after cleanup"
            exit 0
            ;;
    esac
    shift
done

# Check if cluster is running
if ! kubectl cluster-info &>/dev/null; then
    echo "❌ Cluster not running. Nothing to clean."
    exit 0
fi

echo ""
echo "📦 Removing Helm releases..."
helm list --short | xargs -r helm uninstall || echo "  No Helm releases found"

echo ""
echo "🗑️  Deleting deployments..."
kubectl delete deployments --all 2>/dev/null || echo "  No deployments found"

echo ""
echo "🔌 Deleting services (except kubernetes)..."
kubectl get services --no-headers | grep -v kubernetes | awk '{print $1}' | xargs -r kubectl delete service || echo "  No services to delete"

echo ""
echo "📋 Deleting configmaps (except system)..."
kubectl get configmaps --no-headers | grep -v kube | awk '{print $1}' | xargs -r kubectl delete configmap || echo "  No configmaps to delete"

echo ""
echo "🔐 Deleting secrets (except system)..."
kubectl get secrets --no-headers | grep -v -E "^(default-token|sh.helm)" | awk '{print $1}' | xargs -r kubectl delete secret 2>/dev/null || echo "  No secrets to delete"

if [ "$FULL_CLEANUP" = true ]; then
    echo ""
    echo "💾 Deleting PVCs (DATA WILL BE LOST)..."
    kubectl delete pvc --all 2>/dev/null || echo "  No PVCs found"

    echo ""
    echo "🐳 Cleaning Docker images in Minikube..."
    if minikube status &>/dev/null; then
        eval $(minikube docker-env)
        docker image prune -af
        eval $(minikube docker-env -u)
    fi
fi

echo ""
echo "🔍 Remaining resources:"
kubectl get all

if [ "$KEEP_CLUSTER" = false ]; then
    echo ""
    echo "⏹️  Stopping Minikube..."
    minikube stop
fi

echo ""
echo "✅ Cleanup complete!"
```

## Emergency Cleanup

If things are really stuck:

```bash
#!/bin/bash
# emergency-cleanup.sh - Nuclear option

echo "⚠️  EMERGENCY CLEANUP - This will destroy everything!"
read -p "Are you sure? (type 'yes'): " confirm

if [ "$confirm" = "yes" ]; then
    echo "Deleting all minikube data..."
    minikube delete --all --purge

    echo "Cleaning Docker..."
    docker system prune -af
    docker volume prune -f

    echo "Done. Run 'minikube start' to begin fresh."
else
    echo "Cancelled."
fi
```

## Troubleshooting

### Resources stuck in Terminating
```bash
# Check for finalizers
kubectl get <resource> <name> -o jsonpath='{.metadata.finalizers}'

# Remove finalizers (use with caution)
kubectl patch <resource> <name> -p '{"metadata":{"finalizers":null}}'
```

### Namespace stuck in Terminating
```bash
# Export namespace
kubectl get namespace <name> -o json > ns.json

# Edit to remove finalizers
# Then apply:
kubectl replace --raw "/api/v1/namespaces/<name>/finalize" -f ns.json
```

### Minikube won't delete
```bash
# Force delete
minikube delete --purge

# Manual cleanup
rm -rf ~/.minikube
```

## Related Skills

- `k8s.setup` - Set up fresh environment
- `k8s.start` - Start cluster
- `k8s.deploy` - Deploy applications
