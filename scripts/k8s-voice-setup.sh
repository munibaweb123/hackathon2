#!/bin/bash
# =============================================================================
# Kubernetes Voice Input Setup Script
# =============================================================================
# This script sets up the Todo app in Minikube with voice input support.
# Voice input requires HTTPS or localhost access.
#
# Options:
#   --port-forward   : Use port-forwarding (simplest, recommended for dev)
#   --ingress        : Use Ingress with HTTPS (production-like)
#   --chrome-flag    : Show Chrome launch command for insecure origins
# =============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
HELM_CHART="$PROJECT_ROOT/helm-charts/todo-app"

print_header() {
    echo -e "\n${BLUE}=== $1 ===${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"

    local missing=0

    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl not found"
        missing=1
    else
        print_success "kubectl found"
    fi

    if ! command -v minikube &> /dev/null; then
        print_error "minikube not found"
        missing=1
    else
        print_success "minikube found"
    fi

    if ! command -v helm &> /dev/null; then
        print_error "helm not found"
        missing=1
    else
        print_success "helm found"
    fi

    if ! command -v docker &> /dev/null; then
        print_error "docker not found"
        missing=1
    else
        print_success "docker found"
    fi

    if [ $missing -eq 1 ]; then
        print_error "Please install missing prerequisites"
        exit 1
    fi
}

# Start Minikube if not running
start_minikube() {
    print_header "Starting Minikube"

    if minikube status | grep -q "Running"; then
        print_success "Minikube already running"
    else
        echo "Starting Minikube..."
        minikube start --driver=docker --memory=4096 --cpus=2
        print_success "Minikube started"
    fi

    # Point Docker to Minikube's daemon
    echo "Configuring Docker environment..."
    eval $(minikube docker-env)
    print_success "Docker configured for Minikube"
}

# Build Docker images
build_images() {
    local mode="${1:-portforward}"
    print_header "Building Docker Images (mode: $mode)"

    echo "Building backend image..."
    docker build -t todo-backend:v1.0.0 "$PROJECT_ROOT/backend" --quiet
    print_success "Backend image built"

    # Determine API URL based on mode
    local api_url
    if [ "$mode" = "ingress" ]; then
        # For ingress mode, use relative path (same origin)
        api_url=""
    else
        # For port-forward mode, use localhost
        api_url="http://localhost:8000"
    fi

    echo "Building frontend image with API_URL=$api_url..."
    docker build -t todo-frontend:v1.0.0 "$PROJECT_ROOT/frontend" \
        --build-arg NEXT_PUBLIC_API_URL="$api_url" \
        --quiet
    print_success "Frontend image built"
}

# Deploy with Helm
deploy_helm() {
    print_header "Deploying with Helm"

    local extra_args=""

    if [ "$1" = "ingress" ]; then
        extra_args="--set ingress.enabled=true --set ingress.host=todo.local"
    fi

    helm upgrade --install todo-app "$HELM_CHART" \
        --set backend.image.pullPolicy=Never \
        --set frontend.image.pullPolicy=Never \
        $extra_args \
        --wait --timeout 5m

    print_success "Helm deployment complete"
}

# Enable ingress addon and setup HTTPS
setup_ingress() {
    print_header "Setting up Ingress with HTTPS"

    # Enable ingress addon
    echo "Enabling Minikube ingress addon..."
    minikube addons enable ingress
    print_success "Ingress addon enabled"

    # Generate self-signed certificate
    echo "Generating self-signed TLS certificate..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout /tmp/tls.key -out /tmp/tls.crt \
        -subj "/CN=todo.local/O=TodoApp" \
        -addext "subjectAltName=DNS:todo.local" 2>/dev/null

    # Create TLS secret
    kubectl delete secret todo-app-tls --ignore-not-found
    kubectl create secret tls todo-app-tls \
        --cert=/tmp/tls.crt --key=/tmp/tls.key
    print_success "TLS certificate created"

    # Get Minikube IP
    MINIKUBE_IP=$(minikube ip)

    # Add to /etc/hosts
    print_warning "Add this to your /etc/hosts file:"
    echo -e "${YELLOW}  $MINIKUBE_IP todo.local${NC}"

    echo ""
    print_success "Ingress setup complete!"
    echo ""
    echo -e "Access your app at: ${GREEN}https://todo.local${NC}"
    echo -e "${YELLOW}Note: Your browser will show a security warning for self-signed cert.${NC}"
    echo -e "${YELLOW}Click 'Advanced' -> 'Proceed' to continue.${NC}"
}

# Setup port-forwarding
setup_port_forward() {
    print_header "Setting up Port Forwarding"

    echo "Waiting for pods to be ready..."
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/component=frontend --timeout=120s
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/component=backend --timeout=120s
    print_success "Pods are ready"

    # Kill any existing port-forwards
    pkill -f "kubectl port-forward" 2>/dev/null || true

    echo ""
    echo "Starting port-forwarding in background..."

    # Port-forward frontend
    kubectl port-forward svc/todo-app-frontend 3000:3000 &
    FRONTEND_PID=$!

    # Port-forward backend
    kubectl port-forward svc/todo-app-backend 8000:8000 &
    BACKEND_PID=$!

    sleep 2

    print_success "Port forwarding active!"
    echo ""
    echo -e "Frontend: ${GREEN}http://localhost:3000${NC} (Voice input works here!)"
    echo -e "Backend:  ${GREEN}http://localhost:8000${NC}"
    echo -e "API Docs: ${GREEN}http://localhost:8000/docs${NC}"
    echo ""
    echo -e "${YELLOW}Press Ctrl+C to stop port-forwarding${NC}"
    echo ""

    # Wait for user to stop
    trap "kill $FRONTEND_PID $BACKEND_PID 2>/dev/null; exit 0" INT TERM
    wait
}

# Show Chrome flag command
show_chrome_flag() {
    print_header "Chrome Insecure Origin Flag"

    MINIKUBE_IP=$(minikube ip 2>/dev/null || echo "192.168.49.2")

    echo "For development, you can launch Chrome with a flag to allow"
    echo "insecure origins for Speech API:"
    echo ""
    echo -e "${YELLOW}Linux:${NC}"
    echo "  google-chrome --unsafely-treat-insecure-origin-as-secure=\"http://$MINIKUBE_IP:30000\" --user-data-dir=/tmp/chrome-dev"
    echo ""
    echo -e "${YELLOW}macOS:${NC}"
    echo "  /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --unsafely-treat-insecure-origin-as-secure=\"http://$MINIKUBE_IP:30000\" --user-data-dir=/tmp/chrome-dev"
    echo ""
    echo -e "${YELLOW}Windows (PowerShell):${NC}"
    echo "  & 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe' --unsafely-treat-insecure-origin-as-secure=\"http://$MINIKUBE_IP:30000\" --user-data-dir=\$env:TEMP\\chrome-dev"
    echo ""
    echo -e "${RED}⚠ WARNING: This flag reduces security. Only use for development!${NC}"
}

# Show status
show_status() {
    print_header "Deployment Status"

    echo "Pods:"
    kubectl get pods -l app.kubernetes.io/name=todo-app
    echo ""
    echo "Services:"
    kubectl get svc -l app.kubernetes.io/name=todo-app
    echo ""

    if kubectl get ingress todo-app &>/dev/null; then
        echo "Ingress:"
        kubectl get ingress todo-app
    fi
}

# Main
main() {
    echo -e "${BLUE}"
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║         Todo App - Kubernetes Voice Input Setup               ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"

    case "${1:-}" in
        --port-forward|-p)
            check_prerequisites
            start_minikube
            build_images "portforward"
            deploy_helm
            show_status
            setup_port_forward
            ;;
        --ingress|-i)
            check_prerequisites
            start_minikube
            build_images "ingress"
            setup_ingress
            deploy_helm "ingress"
            show_status
            ;;
        --chrome-flag|-c)
            show_chrome_flag
            ;;
        --status|-s)
            show_status
            ;;
        --help|-h|*)
            echo "Usage: $0 [option]"
            echo ""
            echo "Options:"
            echo "  --port-forward, -p   Deploy and use port-forwarding (RECOMMENDED)"
            echo "                       Access via http://localhost:3000"
            echo "                       Voice input works on localhost!"
            echo ""
            echo "  --ingress, -i        Deploy with Ingress + HTTPS"
            echo "                       Access via https://todo.local"
            echo "                       Requires /etc/hosts modification"
            echo ""
            echo "  --chrome-flag, -c    Show Chrome flag for insecure origins"
            echo "                       Allows Speech API on http://<minikube-ip>"
            echo ""
            echo "  --status, -s         Show deployment status"
            echo ""
            echo "  --help, -h           Show this help message"
            echo ""
            echo "For voice input to work, you need ONE of:"
            echo "  1. Access via localhost (--port-forward)"
            echo "  2. Access via HTTPS (--ingress)"
            echo "  3. Chrome with insecure origin flag (--chrome-flag)"
            ;;
    esac
}

main "$@"
