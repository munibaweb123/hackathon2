#!/bin/bash
# Cloud SQL Setup Script
# Creates a Cloud SQL PostgreSQL instance for the Todo App

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Default values
REGION="${GCP_REGION:-us-central1}"
INSTANCE_NAME="${CLOUD_SQL_INSTANCE:-todo-postgres}"
DB_NAME="${DB_NAME:-todo_app}"
DB_USER="${DB_USER:-todo_user}"
DB_TIER="${DB_TIER:-db-g1-small}"  # Options: db-f1-micro, db-g1-small, db-custom-*

# Check required environment variables
check_env() {
    local missing=0

    if [[ -z "${GCP_PROJECT_ID:-}" ]]; then
        echo -e "${RED}Error: GCP_PROJECT_ID environment variable is required${NC}"
        missing=1
    fi

    if [[ -z "${DB_PASSWORD:-}" ]]; then
        echo -e "${RED}Error: DB_PASSWORD environment variable is required${NC}"
        missing=1
    fi

    if [[ $missing -eq 1 ]]; then
        echo ""
        echo "Usage: GCP_PROJECT_ID=your-project DB_PASSWORD=secure-password $0"
        exit 1
    fi
}

# Create Cloud SQL instance
create_instance() {
    echo -e "${YELLOW}Creating Cloud SQL instance: ${INSTANCE_NAME}...${NC}"

    # Check if instance exists
    if gcloud sql instances describe "${INSTANCE_NAME}" --project="${GCP_PROJECT_ID}" &>/dev/null; then
        echo -e "${YELLOW}Instance '${INSTANCE_NAME}' already exists${NC}"
        return 0
    fi

    gcloud sql instances create "${INSTANCE_NAME}" \
        --project="${GCP_PROJECT_ID}" \
        --database-version=POSTGRES_16 \
        --tier="${DB_TIER}" \
        --region="${REGION}" \
        --storage-type=SSD \
        --storage-size=10GB \
        --storage-auto-increase \
        --availability-type=zonal \
        --backup-start-time=03:00 \
        --maintenance-window-day=SUN \
        --maintenance-window-hour=04 \
        --database-flags=log_checkpoints=on,log_connections=on,log_disconnections=on \
        --insights-config-query-insights-enabled \
        --insights-config-query-string-length=1024 \
        --insights-config-record-application-tags \
        --root-password="${DB_PASSWORD}"

    echo -e "${GREEN}Cloud SQL instance created${NC}"
}

# Create database
create_database() {
    echo -e "${YELLOW}Creating database: ${DB_NAME}...${NC}"

    # Check if database exists
    if gcloud sql databases describe "${DB_NAME}" \
        --instance="${INSTANCE_NAME}" \
        --project="${GCP_PROJECT_ID}" &>/dev/null; then
        echo -e "${YELLOW}Database '${DB_NAME}' already exists${NC}"
        return 0
    fi

    gcloud sql databases create "${DB_NAME}" \
        --instance="${INSTANCE_NAME}" \
        --project="${GCP_PROJECT_ID}" \
        --charset=UTF8 \
        --collation=en_US.UTF8

    echo -e "${GREEN}Database created${NC}"
}

# Create database user
create_user() {
    echo -e "${YELLOW}Creating database user: ${DB_USER}...${NC}"

    # Delete user if exists (to reset password)
    gcloud sql users delete "${DB_USER}" \
        --instance="${INSTANCE_NAME}" \
        --project="${GCP_PROJECT_ID}" \
        --quiet 2>/dev/null || true

    gcloud sql users create "${DB_USER}" \
        --instance="${INSTANCE_NAME}" \
        --project="${GCP_PROJECT_ID}" \
        --password="${DB_PASSWORD}"

    echo -e "${GREEN}Database user created${NC}"
}

# Configure private IP (optional, for VPC access)
configure_private_ip() {
    echo -e "${YELLOW}Configuring private IP for Cloud SQL...${NC}"

    # Get or create the private services connection
    if ! gcloud compute addresses describe google-managed-services-default \
        --global \
        --project="${GCP_PROJECT_ID}" &>/dev/null; then

        gcloud compute addresses create google-managed-services-default \
            --global \
            --purpose=VPC_PEERING \
            --prefix-length=16 \
            --network=default \
            --project="${GCP_PROJECT_ID}"
    fi

    # Create the private connection if it doesn't exist
    gcloud services vpc-peerings connect \
        --service=servicenetworking.googleapis.com \
        --ranges=google-managed-services-default \
        --network=default \
        --project="${GCP_PROJECT_ID}" 2>/dev/null || true

    # Update instance with private IP
    gcloud sql instances patch "${INSTANCE_NAME}" \
        --project="${GCP_PROJECT_ID}" \
        --network=projects/${GCP_PROJECT_ID}/global/networks/default \
        --no-assign-ip 2>/dev/null || echo -e "${YELLOW}Private IP already configured or not available${NC}"

    echo -e "${GREEN}Private IP configured${NC}"
}

# Create Kubernetes secrets
create_k8s_secrets() {
    echo -e "${YELLOW}Creating Kubernetes secrets...${NC}"

    # Get instance connection name
    local connection_name
    connection_name=$(gcloud sql instances describe "${INSTANCE_NAME}" \
        --project="${GCP_PROJECT_ID}" \
        --format="value(connectionName)")

    # Get instance IP
    local instance_ip
    instance_ip=$(gcloud sql instances describe "${INSTANCE_NAME}" \
        --project="${GCP_PROJECT_ID}" \
        --format="value(ipAddresses[0].ipAddress)")

    # Connection string for direct connection (with public IP)
    local connection_string="postgresql://${DB_USER}:${DB_PASSWORD}@${instance_ip}:5432/${DB_NAME}"

    # Connection string for Cloud SQL Proxy
    local proxy_connection_string="postgresql://${DB_USER}:${DB_PASSWORD}@127.0.0.1:5432/${DB_NAME}"

    # Create secret in Kubernetes
    kubectl create secret generic db-credentials \
        --namespace=todo-app \
        --from-literal=connection-string="${proxy_connection_string}" \
        --from-literal=host="127.0.0.1" \
        --from-literal=port="5432" \
        --from-literal=database="${DB_NAME}" \
        --from-literal=username="${DB_USER}" \
        --from-literal=password="${DB_PASSWORD}" \
        --from-literal=instance-connection-name="${connection_name}" \
        --dry-run=client -o yaml | kubectl apply -f -

    echo -e "${GREEN}Kubernetes secrets created${NC}"

    echo ""
    echo -e "${YELLOW}Connection Details:${NC}"
    echo "  Instance Name:     ${INSTANCE_NAME}"
    echo "  Connection Name:   ${connection_name}"
    echo "  Public IP:         ${instance_ip}"
    echo "  Database:          ${DB_NAME}"
    echo "  User:              ${DB_USER}"
    echo ""
    echo "  Direct URL:        ${connection_string}"
    echo "  Proxy URL:         ${proxy_connection_string}"
}

# Setup Cloud SQL Proxy service account
setup_sql_proxy_sa() {
    echo -e "${YELLOW}Setting up Cloud SQL Proxy service account...${NC}"

    local sa_name="cloudsql-proxy"
    local sa_email="${sa_name}@${GCP_PROJECT_ID}.iam.gserviceaccount.com"

    # Create service account if it doesn't exist
    if ! gcloud iam service-accounts describe "${sa_email}" --project="${GCP_PROJECT_ID}" &>/dev/null; then
        gcloud iam service-accounts create "${sa_name}" \
            --project="${GCP_PROJECT_ID}" \
            --description="Cloud SQL Proxy service account" \
            --display-name="Cloud SQL Proxy"
    fi

    # Grant Cloud SQL Client role
    gcloud projects add-iam-policy-binding "${GCP_PROJECT_ID}" \
        --member="serviceAccount:${sa_email}" \
        --role="roles/cloudsql.client" \
        --condition=None

    # Create key for the service account
    local key_file="/tmp/cloudsql-proxy-key.json"
    gcloud iam service-accounts keys create "${key_file}" \
        --iam-account="${sa_email}" \
        --project="${GCP_PROJECT_ID}"

    # Create Kubernetes secret with the key
    kubectl create secret generic cloudsql-proxy-credentials \
        --namespace=todo-app \
        --from-file=credentials.json="${key_file}" \
        --dry-run=client -o yaml | kubectl apply -f -

    # Clean up key file
    rm -f "${key_file}"

    echo -e "${GREEN}Cloud SQL Proxy service account configured${NC}"
}

# Print summary
print_summary() {
    local connection_name
    connection_name=$(gcloud sql instances describe "${INSTANCE_NAME}" \
        --project="${GCP_PROJECT_ID}" \
        --format="value(connectionName)" 2>/dev/null || echo "N/A")

    local instance_ip
    instance_ip=$(gcloud sql instances describe "${INSTANCE_NAME}" \
        --project="${GCP_PROJECT_ID}" \
        --format="value(ipAddresses[0].ipAddress)" 2>/dev/null || echo "N/A")

    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Cloud SQL Setup Complete!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "Instance Details:"
    echo "  Name:            ${INSTANCE_NAME}"
    echo "  Connection Name: ${connection_name}"
    echo "  Public IP:       ${instance_ip}"
    echo "  Database:        ${DB_NAME}"
    echo "  User:            ${DB_USER}"
    echo "  Tier:            ${DB_TIER}"
    echo ""
    echo "Kubernetes Secrets Created:"
    echo "  - db-credentials (connection string)"
    echo "  - cloudsql-proxy-credentials (service account key)"
    echo ""
    echo "Next steps:"
    echo "  1. Update values-gke.yaml with your Cloud SQL connection name:"
    echo "     cloudSqlProxy.instanceConnectionName: ${connection_name}"
    echo "  2. Run 04-deploy.sh to deploy the application"
    echo ""
    echo "To connect manually:"
    echo "  gcloud sql connect ${INSTANCE_NAME} --user=${DB_USER} --database=${DB_NAME}"
}

# Show usage
usage() {
    echo "Usage: GCP_PROJECT_ID=your-project DB_PASSWORD=secure-pass $0 [options]"
    echo ""
    echo "Options:"
    echo "  --skip-private-ip    Skip private IP configuration"
    echo "  --tier TIER          Database tier (default: db-g1-small)"
    echo ""
    echo "Environment variables:"
    echo "  GCP_PROJECT_ID       (required) GCP project ID"
    echo "  DB_PASSWORD          (required) Database password"
    echo "  GCP_REGION           (optional) Region, default: us-central1"
    echo "  CLOUD_SQL_INSTANCE   (optional) Instance name, default: todo-postgres"
    echo "  DB_NAME              (optional) Database name, default: todo_app"
    echo "  DB_USER              (optional) Database user, default: todo_user"
    echo "  DB_TIER              (optional) Instance tier, default: db-g1-small"
}

# Main execution
main() {
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Cloud SQL Setup for Todo App${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""

    local skip_private_ip=false

    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                usage
                exit 0
                ;;
            --skip-private-ip)
                skip_private_ip=true
                shift
                ;;
            --tier)
                DB_TIER="$2"
                shift 2
                ;;
            *)
                echo -e "${RED}Unknown option: $1${NC}"
                usage
                exit 1
                ;;
        esac
    done

    check_env

    create_instance
    create_database
    create_user

    if [[ "${skip_private_ip}" != "true" ]]; then
        configure_private_ip || true
    fi

    create_k8s_secrets
    setup_sql_proxy_sa

    print_summary
}

# Run main
main "$@"
