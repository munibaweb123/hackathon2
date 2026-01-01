#!/bin/bash
# Build Docker images for Minikube deployment
# Usage: ./scripts/build-images.sh [version]

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
VERSION=${1:-"v1.0.0"}
REGISTRY=${DOCKER_REGISTRY:-""}
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Building Docker Images for Minikube${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Version: ${VERSION}"
echo "Project Root: ${PROJECT_ROOT}"
echo ""

# Check if using Minikube Docker daemon
if ! docker info 2>/dev/null | grep -q "minikube"; then
    echo -e "${YELLOW}WARNING: Not using Minikube Docker daemon${NC}"
    echo "Run: eval \$(minikube docker-env)"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Build backend image
echo -e "${GREEN}Building backend image...${NC}"
cd "${PROJECT_ROOT}"
docker build \
    -t "${REGISTRY}todo-backend:${VERSION}" \
    -t "${REGISTRY}todo-backend:latest" \
    -f backend/Dockerfile \
    --build-arg PYTHON_VERSION=3.13 \
    ./backend

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Backend image built successfully${NC}"
else
    echo -e "${RED}✗ Backend image build failed${NC}"
    exit 1
fi

# Build frontend image
echo -e "${GREEN}Building frontend image...${NC}"
docker build \
    -t "${REGISTRY}todo-frontend:${VERSION}" \
    -t "${REGISTRY}todo-frontend:latest" \
    -f frontend/Dockerfile \
    --build-arg NEXT_PUBLIC_API_URL=http://todo-backend:8000 \
    --build-arg NEXT_PUBLIC_APP_VERSION=${VERSION} \
    ./frontend

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Frontend image built successfully${NC}"
else
    echo -e "${RED}✗ Frontend image build failed${NC}"
    exit 1
fi

# Verify images
echo ""
echo -e "${GREEN}Verifying images...${NC}"
docker images | grep -E "todo-(backend|frontend)" | grep "${VERSION}"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Build Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Images built:"
echo "  - ${REGISTRY}todo-backend:${VERSION}"
echo "  - ${REGISTRY}todo-frontend:${VERSION}"
echo ""
echo "Next steps:"
echo "  1. Deploy with Helm: ./scripts/deploy.sh"
echo "  2. Or run manually: helm install todo-app ./helm-charts/todo-app"
