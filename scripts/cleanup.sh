#!/bin/bash
# Cleanup script for Kubernetes resources
# Usage: ./scripts/cleanup.sh [namespace] [--delete-pvc]

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

NAMESPACE=${1:-"default"}
DELETE_PVC=false
RELEASE_NAME="todo-app"

# Parse arguments
for arg in "$@"; do
    case $arg in
        --delete-pvc)
        DELETE_PVC=true
        shift
        ;;
    esac
done

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Cleaning Up Todo App Resources${NC}"
echo -e "${YELLOW}========================================${NC}"
echo ""
echo "Namespace: ${NAMESPACE}"
echo "Release: ${RELEASE_NAME}"
echo "Delete PVCs: ${DELETE_PVC}"
echo ""

# Confirm deletion
read -p "Are you sure you want to delete the deployment? (yes/no): " -r
echo
if [[ ! $REPLY =~ ^(yes|YES)$ ]]; then
    echo "Cleanup cancelled."
    exit 0
fi

# Uninstall Helm release
echo -e "${GREEN}Uninstalling Helm release...${NC}"
if helm list -n "${NAMESPACE}" | grep -q "${RELEASE_NAME}"; then
    helm uninstall "${RELEASE_NAME}" -n "${NAMESPACE}"
    echo -e "${GREEN}✓ Helm release uninstalled${NC}"
else
    echo -e "${YELLOW}No Helm release found${NC}"
fi

# Wait for pods to terminate
echo ""
echo -e "${GREEN}Waiting for pods to terminate...${NC}"
kubectl wait --for=delete pod \
    -l app.kubernetes.io/name=todo-app \
    -n "${NAMESPACE}" \
    --timeout=60s 2>/dev/null || echo -e "${YELLOW}Pods may already be deleted${NC}"

# Delete PVCs if requested
if [ "${DELETE_PVC}" = true ]; then
    echo ""
    echo -e "${YELLOW}Deleting PersistentVolumeClaims...${NC}"
    read -p "This will DELETE ALL DATA. Are you sure? (yes/no): " -r
    echo
    if [[ $REPLY =~ ^(yes|YES)$ ]]; then
        kubectl delete pvc -l app.kubernetes.io/name=todo-app -n "${NAMESPACE}" 2>/dev/null || echo -e "${YELLOW}No PVCs found${NC}"
        echo -e "${GREEN}✓ PVCs deleted${NC}"
    else
        echo "PVC deletion cancelled. Data preserved."
    fi
fi

# Check for any remaining resources
echo ""
echo -e "${GREEN}Checking for remaining resources...${NC}"
REMAINING=$(kubectl get all -l app.kubernetes.io/name=todo-app -n "${NAMESPACE}" 2>/dev/null | tail -n +2 || echo "")
if [ -z "${REMAINING}" ]; then
    echo -e "${GREEN}✓ All resources cleaned up${NC}"
else
    echo -e "${YELLOW}Warning: Some resources may still exist:${NC}"
    kubectl get all -l app.kubernetes.io/name=todo-app -n "${NAMESPACE}"
fi

# Display PVCs if they exist
PVC_LIST=$(kubectl get pvc -l app.kubernetes.io/name=todo-app -n "${NAMESPACE}" 2>/dev/null | tail -n +2 || echo "")
if [ -n "${PVC_LIST}" ]; then
    echo ""
    echo -e "${YELLOW}PersistentVolumeClaims still exist (data preserved):${NC}"
    kubectl get pvc -l app.kubernetes.io/name=todo-app -n "${NAMESPACE}"
    echo ""
    echo "To delete PVCs and data, run:"
    echo "  kubectl delete pvc -l app.kubernetes.io/name=todo-app -n ${NAMESPACE}"
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Cleanup Complete${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "To redeploy, run: ./scripts/deploy.sh"
