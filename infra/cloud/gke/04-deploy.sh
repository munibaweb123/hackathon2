#!/bin/bash
# GKE Deployment Script
# Deploys the Todo App to GKE using Helm

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Default values
REGION="${GCP_REGION:-us-central1}"
NAMESPACE="${NAMESPACE:-todo-app}"
RELEASE_NAME="${RELEASE_NAME:-todo-app}"
REPO_NAME="${REPO_NAME:-todo-app}"

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
HELM_CHART="${PROJECT_ROOT}/infra/helm/todo-app"
VALUES_FILE="${HELM_CHART}/values-gke.yaml"

# Check required environment variables
check_env() {
    local missing=0

    if [[ -z "${GCP_PROJECT_ID:-}" ]]; then
        echo -e "${RED}Error: GCP_PROJECT_ID environment variable is required${NC}"
        missing=1
    fi

    if [[ -z "${DOMAIN:-}" ]]; then
        echo -e "${YELLOW}Warning: DOMAIN not set. Using placeholder 'todo.example.com'${NC}"
        DOMAIN="todo.example.com"
    fi

    if [[ $missing -eq 1 ]]; then
        echo ""
        echo "Usage: GCP_PROJECT_ID=your-project DOMAIN=your-domain.com $0"
        exit 1
    fi
}

# Verify cluster connection
verify_cluster() {
    echo -e "${YELLOW}Verifying cluster connection...${NC}"

    if ! kubectl cluster-info &>/dev/null; then
        echo -e "${RED}Error: Cannot connect to Kubernetes cluster${NC}"
        echo "Run: gcloud container clusters get-credentials CLUSTER_NAME --region=${REGION}"
        exit 1
    fi

    echo -e "${GREEN}Cluster connection verified${NC}"
}

# Create namespace if not exists
ensure_namespace() {
    echo -e "${YELLOW}Ensuring namespace '${NAMESPACE}' exists...${NC}"

    kubectl create namespace "${NAMESPACE}" --dry-run=client -o yaml | kubectl apply -f -

    echo -e "${GREEN}Namespace ready${NC}"
}

# Create application secrets
create_app_secrets() {
    echo -e "${YELLOW}Creating application secrets...${NC}"

    # Better Auth secret
    local auth_secret="${BETTER_AUTH_SECRET:-$(openssl rand -base64 32)}"

    # OpenAI API key (optional)
    local openai_key="${OPENAI_API_KEY:-}"

    kubectl create secret generic app-secrets \
        --namespace="${NAMESPACE}" \
        --from-literal=better-auth-secret="${auth_secret}" \
        --from-literal=openai-api-key="${openai_key}" \
        --dry-run=client -o yaml | kubectl apply -f -

    echo -e "${GREEN}Application secrets created${NC}"
}

# Generate dynamic values
generate_values() {
    echo -e "${YELLOW}Generating deployment values...${NC}"

    local image_tag="${IMAGE_TAG:-latest}"
    local image_prefix="${REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/${REPO_NAME}"

    # Get Cloud SQL instance connection name
    local sql_connection_name
    sql_connection_name=$(gcloud sql instances describe todo-postgres \
        --project="${GCP_PROJECT_ID}" \
        --format="value(connectionName)" 2>/dev/null || echo "")

    if [[ -z "${sql_connection_name}" ]]; then
        echo -e "${YELLOW}Warning: Cloud SQL instance not found. Using placeholder.${NC}"
        sql_connection_name="${GCP_PROJECT_ID}:${REGION}:todo-postgres"
    fi

    # Create temporary values file with overrides
    cat > /tmp/values-override.yaml <<EOF
# Auto-generated values for GKE deployment
# Generated at: $(date -u +"%Y-%m-%dT%H:%M:%SZ")

images:
  backend:
    repository: ${image_prefix}/backend
    tag: "${image_tag}"
  frontend:
    repository: ${image_prefix}/frontend
    tag: "${image_tag}"
  notification:
    repository: ${image_prefix}/notification
    tag: "${image_tag}"
  recurring:
    repository: ${image_prefix}/recurring
    tag: "${image_tag}"
  audit:
    repository: ${image_prefix}/audit
    tag: "${image_tag}"

backend:
  corsOrigins: "https://${DOMAIN}"

frontend:
  apiUrl: "https://${DOMAIN}/api"
  wsUrl: "wss://${DOMAIN}/ws"

ingress:
  enabled: true
  className: gce
  host: "${DOMAIN}"
  annotations:
    kubernetes.io/ingress.global-static-ip-name: "todo-app-ip"
    networking.gke.io/managed-certificates: "todo-app-cert"

cloudSqlProxy:
  enabled: true
  instanceConnectionName: "${sql_connection_name}"

serviceAccount:
  annotations:
    iam.gke.io/gcp-service-account: todo-app-sa@${GCP_PROJECT_ID}.iam.gserviceaccount.com
EOF

    echo -e "${GREEN}Values generated at /tmp/values-override.yaml${NC}"
}

# Create managed certificate for SSL
create_managed_certificate() {
    echo -e "${YELLOW}Creating managed SSL certificate...${NC}"

    cat <<EOF | kubectl apply -f -
apiVersion: networking.gke.io/v1
kind: ManagedCertificate
metadata:
  name: todo-app-cert
  namespace: ${NAMESPACE}
spec:
  domains:
    - ${DOMAIN}
EOF

    echo -e "${GREEN}Managed certificate created${NC}"
}

# Create backend config for Cloud CDN and health checks
create_backend_config() {
    echo -e "${YELLOW}Creating backend config...${NC}"

    cat <<EOF | kubectl apply -f -
apiVersion: cloud.google.com/v1
kind: BackendConfig
metadata:
  name: todo-backend-config
  namespace: ${NAMESPACE}
spec:
  healthCheck:
    checkIntervalSec: 15
    timeoutSec: 5
    healthyThreshold: 1
    unhealthyThreshold: 2
    type: HTTP
    requestPath: /health
    port: 8000
  connectionDraining:
    drainingTimeoutSec: 30
  cdn:
    enabled: false  # Enable if you want Cloud CDN
  logging:
    enable: true
    sampleRate: 0.5
EOF

    echo -e "${GREEN}Backend config created${NC}"
}

# Deploy with Helm
deploy_helm() {
    echo -e "${YELLOW}Deploying Todo App with Helm...${NC}"

    # Add PostgreSQL Helm repo if needed
    helm repo add bitnami https://charts.bitnami.com/bitnami 2>/dev/null || true
    helm repo update

    # Deploy
    helm upgrade --install "${RELEASE_NAME}" "${HELM_CHART}" \
        --namespace="${NAMESPACE}" \
        --create-namespace \
        -f "${VALUES_FILE}" \
        -f /tmp/values-override.yaml \
        --set postgresql.enabled=false \
        --wait \
        --timeout 600s

    echo -e "${GREEN}Helm deployment complete${NC}"
}

# Verify deployment
verify_deployment() {
    echo -e "${YELLOW}Verifying deployment...${NC}"

    echo -e "${BLUE}Waiting for backend deployment...${NC}"
    kubectl rollout status deployment/${RELEASE_NAME}-backend \
        --namespace="${NAMESPACE}" \
        --timeout=300s || true

    echo -e "${BLUE}Waiting for frontend deployment...${NC}"
    kubectl rollout status deployment/${RELEASE_NAME}-frontend \
        --namespace="${NAMESPACE}" \
        --timeout=300s || true

    echo ""
    echo -e "${BLUE}Pod Status:${NC}"
    kubectl get pods -n "${NAMESPACE}" -o wide

    echo ""
    echo -e "${BLUE}Service Status:${NC}"
    kubectl get svc -n "${NAMESPACE}"

    echo ""
    echo -e "${BLUE}Ingress Status:${NC}"
    kubectl get ingress -n "${NAMESPACE}"
}

# Get ingress IP
get_ingress_ip() {
    echo -e "${YELLOW}Getting Ingress IP address...${NC}"

    local ingress_ip=""
    local attempts=0
    local max_attempts=30

    while [[ -z "${ingress_ip}" && ${attempts} -lt ${max_attempts} ]]; do
        ingress_ip=$(kubectl get ingress "${RELEASE_NAME}" \
            --namespace="${NAMESPACE}" \
            -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "")

        if [[ -z "${ingress_ip}" ]]; then
            echo -e "${YELLOW}Waiting for Ingress IP... (${attempts}/${max_attempts})${NC}"
            sleep 10
            ((attempts++))
        fi
    done

    if [[ -n "${ingress_ip}" ]]; then
        echo -e "${GREEN}Ingress IP: ${ingress_ip}${NC}"
    else
        # Try to get the static IP
        ingress_ip=$(gcloud compute addresses describe todo-app-ip \
            --global \
            --project="${GCP_PROJECT_ID}" \
            --format="value(address)" 2>/dev/null || echo "Not found")
        echo -e "${YELLOW}Static IP: ${ingress_ip}${NC}"
    fi

    echo ""
    echo -e "${YELLOW}Point your domain's A record to: ${ingress_ip}${NC}"
}

# Print summary
print_summary() {
    local static_ip
    static_ip=$(gcloud compute addresses describe todo-app-ip \
        --global \
        --project="${GCP_PROJECT_ID}" \
        --format="value(address)" 2>/dev/null || echo "Not configured")

    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}GKE Deployment Complete!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "Deployment Details:"
    echo "  Release:      ${RELEASE_NAME}"
    echo "  Namespace:    ${NAMESPACE}"
    echo "  Domain:       ${DOMAIN}"
    echo "  Static IP:    ${static_ip}"
    echo ""
    echo "URLs (after DNS propagation):"
    echo "  Frontend:     https://${DOMAIN}"
    echo "  Backend API:  https://${DOMAIN}/api"
    echo "  WebSocket:    wss://${DOMAIN}/ws"
    echo ""
    echo "Useful commands:"
    echo "  kubectl get pods -n ${NAMESPACE}"
    echo "  kubectl logs -f deployment/${RELEASE_NAME}-backend -n ${NAMESPACE}"
    echo "  kubectl logs -f deployment/${RELEASE_NAME}-frontend -n ${NAMESPACE}"
    echo "  helm status ${RELEASE_NAME} -n ${NAMESPACE}"
    echo ""
    echo "To update deployment:"
    echo "  IMAGE_TAG=new-tag $0"
    echo ""
    echo "DNS Configuration:"
    echo "  Add an A record pointing ${DOMAIN} to ${static_ip}"
    echo "  SSL certificate will be provisioned automatically after DNS propagates"
}

# Show usage
usage() {
    echo "Usage: GCP_PROJECT_ID=your-project DOMAIN=your-domain.com $0 [options]"
    echo ""
    echo "Options:"
    echo "  --dry-run          Show what would be deployed without deploying"
    echo "  --skip-secrets     Skip creating secrets"
    echo "  --skip-cert        Skip creating managed certificate"
    echo ""
    echo "Environment variables:"
    echo "  GCP_PROJECT_ID     (required) GCP project ID"
    echo "  DOMAIN             (required) Domain name for the application"
    echo "  GCP_REGION         (optional) Region, default: us-central1"
    echo "  NAMESPACE          (optional) Kubernetes namespace, default: todo-app"
    echo "  IMAGE_TAG          (optional) Image tag to deploy, default: latest"
    echo "  BETTER_AUTH_SECRET (optional) Auth secret, auto-generated if not set"
    echo "  OPENAI_API_KEY     (optional) OpenAI API key for chatbot features"
}

# Main execution
main() {
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}GKE Deployment for Todo App${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""

    local dry_run=false
    local skip_secrets=false
    local skip_cert=false

    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                usage
                exit 0
                ;;
            --dry-run)
                dry_run=true
                shift
                ;;
            --skip-secrets)
                skip_secrets=true
                shift
                ;;
            --skip-cert)
                skip_cert=true
                shift
                ;;
            *)
                echo -e "${RED}Unknown option: $1${NC}"
                usage
                exit 1
                ;;
        esac
    done

    check_env
    verify_cluster
    ensure_namespace

    if [[ "${skip_secrets}" != "true" ]]; then
        create_app_secrets
    fi

    generate_values

    if [[ "${skip_cert}" != "true" ]]; then
        create_managed_certificate
    fi

    create_backend_config

    if [[ "${dry_run}" == "true" ]]; then
        echo -e "${YELLOW}Dry run - showing Helm diff:${NC}"
        helm diff upgrade "${RELEASE_NAME}" "${HELM_CHART}" \
            --namespace="${NAMESPACE}" \
            -f "${VALUES_FILE}" \
            -f /tmp/values-override.yaml \
            --set postgresql.enabled=false 2>/dev/null || \
        helm template "${RELEASE_NAME}" "${HELM_CHART}" \
            --namespace="${NAMESPACE}" \
            -f "${VALUES_FILE}" \
            -f /tmp/values-override.yaml \
            --set postgresql.enabled=false
        exit 0
    fi

    deploy_helm
    verify_deployment
    get_ingress_ip

    print_summary
}

# Run main
main "$@"
