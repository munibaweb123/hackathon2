#!/bin/bash
# Check prerequisites for Kubernetes deployment
# Usage: ./scripts/check-prerequisites.sh

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Checking Kubernetes Prerequisites${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

ERRORS=0
WARNINGS=0

# Check Docker
echo -n "Checking Docker... "
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version | cut -d ' ' -f3 | cut -d ',' -f1)
    echo -e "${GREEN}✓ Found Docker $DOCKER_VERSION${NC}"
else
    echo -e "${RED}✗ Docker not found${NC}"
    echo "  Install from: https://www.docker.com/products/docker-desktop/"
    ((ERRORS++))
fi

# Check Minikube
echo -n "Checking Minikube... "
if command -v minikube &> /dev/null; then
    MINIKUBE_VERSION=$(minikube version --short 2>/dev/null || echo "unknown")
    echo -e "${GREEN}✓ Found Minikube $MINIKUBE_VERSION${NC}"
else
    echo -e "${RED}✗ Minikube not found${NC}"
    echo "  Install from: https://minikube.sigs.k8s.io/docs/start/"
    ((ERRORS++))
fi

# Check kubectl
echo -n "Checking kubectl... "
if command -v kubectl &> /dev/null; then
    KUBECTL_VERSION=$(kubectl version --client --short 2>/dev/null | cut -d ' ' -f3 || echo "unknown")
    echo -e "${GREEN}✓ Found kubectl $KUBECTL_VERSION${NC}"
else
    echo -e "${RED}✗ kubectl not found${NC}"
    echo "  Install from: https://kubernetes.io/docs/tasks/tools/"
    ((ERRORS++))
fi

# Check Helm
echo -n "Checking Helm... "
if command -v helm &> /dev/null; then
    HELM_VERSION=$(helm version --short 2>/dev/null | cut -d '+' -f1 || echo "unknown")
    echo -e "${GREEN}✓ Found Helm $HELM_VERSION${NC}"
else
    echo -e "${RED}✗ Helm not found${NC}"
    echo "  Install from: https://helm.sh/docs/intro/install/"
    ((ERRORS++))
fi

# Check Minikube status (if installed)
if command -v minikube &> /dev/null; then
    echo ""
    echo -n "Checking Minikube status... "
    if minikube status &> /dev/null; then
        echo -e "${GREEN}✓ Minikube is running${NC}"

        # Check Minikube resources
        echo ""
        echo "Minikube cluster info:"
        minikube profile list 2>/dev/null | grep -v "Profile" || echo "  No active profiles"

    else
        echo -e "${YELLOW}⚠ Minikube is not running${NC}"
        echo "  Start with: minikube start --cpus=2 --memory=4096"
        ((WARNINGS++))
    fi
fi

# Check Docker daemon (if Minikube is running)
if command -v minikube &> /dev/null && minikube status &> /dev/null; then
    echo ""
    echo -n "Checking Docker daemon configuration... "
    if docker info 2>/dev/null | grep -q "minikube"; then
        echo -e "${GREEN}✓ Using Minikube Docker daemon${NC}"
    else
        echo -e "${YELLOW}⚠ Not using Minikube Docker daemon${NC}"
        echo "  Run: eval \$(minikube docker-env)"
        ((WARNINGS++))
    fi
fi

# Check system resources
echo ""
echo -e "${BLUE}System Resources:${NC}"

# Memory
if command -v free &> /dev/null; then
    TOTAL_MEM=$(free -m | awk '/^Mem:/{print $2}')
    echo "  Total Memory: ${TOTAL_MEM}MB"
    if [ "$TOTAL_MEM" -lt 8192 ]; then
        echo -e "  ${YELLOW}⚠ Recommended: 8GB+ RAM${NC}"
        ((WARNINGS++))
    fi
fi

# Disk space
if command -v df &> /dev/null; then
    AVAILABLE_DISK=$(df -h . | awk 'NR==2 {print $4}')
    echo "  Available Disk: $AVAILABLE_DISK"
fi

# Summary
echo ""
echo -e "${BLUE}========================================${NC}"
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✓ All prerequisites met!${NC}"
    echo ""
    echo "You're ready to deploy. Next steps:"
    echo "  1. Start Minikube: minikube start --cpus=2 --memory=4096"
    echo "  2. Configure Docker: eval \$(minikube docker-env)"
    echo "  3. Build images: ./scripts/build-images.sh v1.0.0"
    echo "  4. Deploy: ./scripts/deploy.sh dev"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ Prerequisites met with $WARNINGS warning(s)${NC}"
    echo ""
    echo "You can proceed, but consider addressing warnings above."
    exit 0
else
    echo -e "${RED}✗ Missing $ERRORS required tool(s)${NC}"
    echo ""
    echo "Please install missing tools before deploying."
    exit 1
fi
