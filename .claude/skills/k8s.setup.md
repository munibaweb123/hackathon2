# Skill: k8s.setup

Setup Kubernetes development environment with Docker, Minikube, and kubectl for WSL2.

## Description

This skill sets up a complete local Kubernetes development environment. It handles:
- Docker Desktop WSL2 integration verification
- kubectl installation (to ~/.local/bin for non-sudo installation)
- Minikube configuration with Docker driver
- Environment validation

## Prerequisites

- Windows with WSL2 enabled
- Docker Desktop installed on Windows
- WSL2 distribution (Ubuntu recommended)

## Instructions

### Step 1: Verify Docker Desktop WSL2 Integration

First, check if Docker is accessible from WSL2:

```bash
docker info &>/dev/null && echo "Docker OK" || echo "Docker not available"
```

If Docker is not available:
1. Open Docker Desktop on Windows
2. Go to Settings → Resources → WSL Integration
3. Enable integration with your WSL2 distro
4. Restart your WSL2 terminal

Wait for Docker to be ready:
```bash
for i in {1..30}; do docker info &>/dev/null && echo "Docker ready!" && break || sleep 2; done
```

### Step 2: Install kubectl (non-sudo method)

```bash
# Create local bin directory
mkdir -p ~/.local/bin

# Download latest kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"

# Make executable and move to local bin
chmod +x kubectl
mv kubectl ~/.local/bin/

# Add to PATH (add to ~/.bashrc for persistence)
export PATH="$HOME/.local/bin:$PATH"
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc

# Verify installation
kubectl version --client
```

### Step 3: Install Minikube (if not installed)

```bash
# Download minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64

# Install to local bin (non-sudo)
chmod +x minikube-linux-amd64
mv minikube-linux-amd64 ~/.local/bin/minikube

# Or with sudo to /usr/local/bin
sudo install minikube-linux-amd64 /usr/local/bin/minikube
```

### Step 4: Configure Minikube defaults

```bash
# Set Docker as default driver
minikube config set driver docker

# Disable update notifications (optional, good for CI)
minikube config set WantUpdateNotification false
```

### Step 5: Validate Setup

```bash
echo "=== Docker ===" && docker version --format '{{.Server.Version}}'
echo "=== kubectl ===" && kubectl version --client --short 2>/dev/null || kubectl version --client
echo "=== Minikube ===" && minikube version --short
```

## Troubleshooting

### Docker not found in WSL2
```
The command 'docker' could not be found in this WSL 2 distro.
```
**Solution:** Enable WSL integration in Docker Desktop settings.

### kubectl connection refused
```
The connection to the server was refused
```
**Solution:** Minikube is not running. Run `minikube start`.

### Minikube PROVIDER_DOCKER_VERSION_EXIT_1
```
Exiting due to PROVIDER_DOCKER_VERSION_EXIT_1
```
**Solution:** Docker Desktop is not running. Start Docker Desktop on Windows.

## Related Skills

- `k8s.start` - Start the Kubernetes cluster
- `k8s.status` - Check cluster status
- `k8s.cleanup` - Clean up resources
