# Skill: k8s.start

Start and verify the local Kubernetes cluster using Minikube.

## Description

This skill starts Minikube with optimal settings for local development and verifies the cluster is healthy.

## Prerequisites

- Docker Desktop running with WSL2 integration
- kubectl installed
- Minikube installed

## Instructions

### Step 1: Ensure Docker is Running

```bash
# Check Docker and wait if starting
if ! docker info &>/dev/null; then
    echo "Waiting for Docker..."
    for i in {1..30}; do
        docker info &>/dev/null && echo "Docker ready!" && break
        sleep 2
    done
fi

# Final check
docker info &>/dev/null || { echo "ERROR: Docker not available. Start Docker Desktop."; exit 1; }
```

### Step 2: Start Minikube

Basic start:
```bash
minikube start --driver=docker
```

With custom resources:
```bash
minikube start --driver=docker --cpus=4 --memory=8192
```

With static IP (useful for consistent networking):
```bash
minikube start --driver=docker --static-ip=192.168.200.200
```

### Step 3: Verify Cluster

```bash
# Check cluster info
kubectl cluster-info

# Verify nodes
kubectl get nodes

# Check system pods
kubectl get pods -n kube-system
```

### Step 4: Enable Useful Addons

```bash
# Enable metrics server for resource monitoring
minikube addons enable metrics-server

# Enable ingress for HTTP routing
minikube addons enable ingress

# Enable dashboard (optional)
minikube addons enable dashboard

# List all addons
minikube addons list
```

## Quick Start Script

```bash
#!/bin/bash
# k8s-start.sh - One-command cluster start

set -e

echo "🐳 Checking Docker..."
for i in {1..30}; do
    docker info &>/dev/null && break
    echo "  Waiting for Docker... ($i/30)"
    sleep 2
done
docker info &>/dev/null || { echo "❌ Docker not running"; exit 1; }

echo "🚀 Starting Minikube..."
minikube start --driver=docker

echo "✅ Verifying cluster..."
kubectl cluster-info
kubectl get nodes

echo "🎉 Cluster is ready!"
```

## Troubleshooting

### Cluster won't start after Docker restart
```bash
# Delete and recreate the cluster
minikube delete
minikube start --driver=docker
```

### Old cluster with different driver
```bash
# Switch to Docker driver
minikube delete
minikube start --driver=docker
```

### Insufficient resources
```bash
# Start with minimal resources
minikube start --driver=docker --cpus=2 --memory=2048
```

## Related Skills

- `k8s.setup` - Initial environment setup
- `k8s.status` - Check cluster status
- `k8s.deploy` - Deploy applications
