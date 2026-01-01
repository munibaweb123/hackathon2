#!/bin/bash
# Health check script for Kubernetes deployment
# Usage: ./scripts/health-check.sh [namespace]

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

NAMESPACE=${1:-"default"}

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Todo App Health Check${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check backend health
echo -e "${GREEN}Checking backend health...${NC}"
BACKEND_POD=$(kubectl get pods -n "${NAMESPACE}" -l app.kubernetes.io/component=backend -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")

if [ -z "${BACKEND_POD}" ]; then
    echo -e "${RED}✗ No backend pod found${NC}"
    exit 1
fi

echo "Backend pod: ${BACKEND_POD}"

# Check liveness
kubectl exec -n "${NAMESPACE}" "${BACKEND_POD}" -- curl -s http://localhost:8000/livez > /dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Liveness check passed${NC}"
else
    echo -e "${RED}✗ Liveness check failed${NC}"
fi

# Check readiness
kubectl exec -n "${NAMESPACE}" "${BACKEND_POD}" -- curl -s http://localhost:8000/readyz > /dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Readiness check passed${NC}"
else
    echo -e "${RED}✗ Readiness check failed${NC}"
fi

# Check frontend health
echo ""
echo -e "${GREEN}Checking frontend health...${NC}"
FRONTEND_POD=$(kubectl get pods -n "${NAMESPACE}" -l app.kubernetes.io/component=frontend -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")

if [ -z "${FRONTEND_POD}" ]; then
    echo -e "${RED}✗ No frontend pod found${NC}"
    exit 1
fi

echo "Frontend pod: ${FRONTEND_POD}"

kubectl exec -n "${NAMESPACE}" "${FRONTEND_POD}" -- curl -s http://localhost:3000/api/health/live > /dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Frontend health check passed${NC}"
else
    echo -e "${RED}✗ Frontend health check failed${NC}"
fi

# Check database
echo ""
echo -e "${GREEN}Checking database...${NC}"
DB_POD=$(kubectl get pods -n "${NAMESPACE}" -l app.kubernetes.io/component=postgres -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")

if [ -z "${DB_POD}" ]; then
    echo -e "${RED}✗ No database pod found${NC}"
    exit 1
fi

echo "Database pod: ${DB_POD}"
kubectl exec -n "${NAMESPACE}" "${DB_POD}" -- pg_isready -U todo_user > /dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Database is ready${NC}"
else
    echo -e "${RED}✗ Database is not ready${NC}"
fi

# Resource usage
echo ""
echo -e "${GREEN}Resource usage:${NC}"
kubectl top pods -n "${NAMESPACE}" -l app.kubernetes.io/name=todo-app 2>/dev/null || echo -e "${YELLOW}Metrics not available (metrics-server may not be installed)${NC}"

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Health Check Complete${NC}"
echo -e "${BLUE}========================================${NC}"
