#!/bin/bash
# Deploy Todo App to Kubernetes with Helm
# Usage: ./scripts/deploy.sh [environment] [namespace]

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-"dev"}
NAMESPACE=${2:-"default"}
RELEASE_NAME="todo-app"
CHART_PATH="./helm-charts/todo-app"
VALUES_FILE="values-${ENVIRONMENT}.yaml"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Deploying Todo App to Kubernetes${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Environment: ${ENVIRONMENT}"
echo "Namespace: ${NAMESPACE}"
echo "Release: ${RELEASE_NAME}"
echo "Chart: ${CHART_PATH}"
echo "Values: ${VALUES_FILE}"
echo ""

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}✗ kubectl not found. Please install kubectl.${NC}"
    exit 1
fi

# Check if helm is available
if ! command -v helm &> /dev/null; then
    echo -e "${RED}✗ helm not found. Please install Helm.${NC}"
    exit 1
fi

# Check if cluster is accessible
if ! kubectl cluster-info &> /dev/null; then
    echo -e "${RED}✗ Cannot connect to Kubernetes cluster${NC}"
    echo "Start Minikube with: minikube start"
    exit 1
fi

# Lint Helm chart
echo -e "${GREEN}Linting Helm chart...${NC}"
if [ -f "${CHART_PATH}/${VALUES_FILE}" ]; then
    helm lint "${CHART_PATH}" -f "${CHART_PATH}/${VALUES_FILE}"
else
    echo -e "${YELLOW}WARNING: ${VALUES_FILE} not found, using default values.yaml${NC}"
    helm lint "${CHART_PATH}"
fi

# Check if release already exists
if helm list -n "${NAMESPACE}" | grep -q "${RELEASE_NAME}"; then
    echo -e "${YELLOW}Release ${RELEASE_NAME} already exists. Upgrading...${NC}"

    if [ -f "${CHART_PATH}/${VALUES_FILE}" ]; then
        helm upgrade "${RELEASE_NAME}" "${CHART_PATH}" \
            -f "${CHART_PATH}/${VALUES_FILE}" \
            --namespace "${NAMESPACE}" \
            --wait \
            --timeout 5m
    else
        helm upgrade "${RELEASE_NAME}" "${CHART_PATH}" \
            --namespace "${NAMESPACE}" \
            --wait \
            --timeout 5m
    fi

    echo -e "${GREEN}✓ Release upgraded successfully${NC}"
else
    echo -e "${GREEN}Installing new release...${NC}"

    # Create namespace if it doesn't exist
    kubectl create namespace "${NAMESPACE}" --dry-run=client -o yaml | kubectl apply -f -

    if [ -f "${CHART_PATH}/${VALUES_FILE}" ]; then
        helm install "${RELEASE_NAME}" "${CHART_PATH}" \
            -f "${CHART_PATH}/${VALUES_FILE}" \
            --namespace "${NAMESPACE}" \
            --create-namespace \
            --wait \
            --timeout 5m
    else
        helm install "${RELEASE_NAME}" "${CHART_PATH}" \
            --namespace "${NAMESPACE}" \
            --create-namespace \
            --wait \
            --timeout 5m
    fi

    echo -e "${GREEN}✓ Release installed successfully${NC}"
fi

# Wait for pods to be ready
echo ""
echo -e "${GREEN}Waiting for pods to be ready...${NC}"
kubectl wait --for=condition=ready pod \
    -l app.kubernetes.io/name=todo-app \
    -n "${NAMESPACE}" \
    --timeout=300s || true

# Display deployment status
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Deployment Status${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

echo -e "${GREEN}Pods:${NC}"
kubectl get pods -n "${NAMESPACE}" -l app.kubernetes.io/name=todo-app

echo ""
echo -e "${GREEN}Services:${NC}"
kubectl get services -n "${NAMESPACE}" -l app.kubernetes.io/name=todo-app

echo ""
echo -e "${GREEN}Helm Release:${NC}"
helm list -n "${NAMESPACE}"

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Deployment Complete!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Access the application:"
echo "  Frontend: minikube service todo-frontend -n ${NAMESPACE}"
echo "  Or use port-forward: kubectl port-forward svc/todo-frontend 3000:3000 -n ${NAMESPACE}"
echo ""
echo "Check health:"
echo "  ./scripts/health-check.sh ${NAMESPACE}"
echo ""
echo "View logs:"
echo "  kubectl logs -l app.kubernetes.io/component=backend -n ${NAMESPACE}"
echo "  kubectl logs -l app.kubernetes.io/component=frontend -n ${NAMESPACE}"
