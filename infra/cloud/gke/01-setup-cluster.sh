#!/bin/bash
# GKE Cluster Setup Script
# This script creates a GKE Autopilot or Standard cluster for the Todo App

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
CLUSTER_TYPE="${CLUSTER_TYPE:-autopilot}"  # autopilot or standard
REGION="${GCP_REGION:-us-central1}"
ZONE="${GCP_ZONE:-us-central1-a}"

# Check required environment variables
check_env() {
    local missing=0

    if [[ -z "${GCP_PROJECT_ID:-}" ]]; then
        echo -e "${RED}Error: GCP_PROJECT_ID environment variable is required${NC}"
        missing=1
    fi

    if [[ -z "${CLUSTER_NAME:-}" ]]; then
        echo -e "${YELLOW}Warning: CLUSTER_NAME not set, using default 'todo-app-cluster'${NC}"
        CLUSTER_NAME="todo-app-cluster"
    fi

    if [[ $missing -eq 1 ]]; then
        echo ""
        echo "Usage: GCP_PROJECT_ID=your-project CLUSTER_NAME=todo-app $0"
        exit 1
    fi
}

# Check prerequisites
check_prerequisites() {
    echo -e "${YELLOW}Checking prerequisites...${NC}"

    # Check gcloud
    if ! command -v gcloud &> /dev/null; then
        echo -e "${RED}Error: gcloud CLI not found. Install from: https://cloud.google.com/sdk/docs/install${NC}"
        exit 1
    fi

    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        echo -e "${YELLOW}Installing kubectl...${NC}"
        gcloud components install kubectl -q
    fi

    # Check gke-gcloud-auth-plugin
    if ! gcloud components list 2>/dev/null | grep -q "gke-gcloud-auth-plugin.*Installed"; then
        echo -e "${YELLOW}Installing gke-gcloud-auth-plugin...${NC}"
        gcloud components install gke-gcloud-auth-plugin -q
    fi

    echo -e "${GREEN}Prerequisites OK${NC}"
}

# Enable required APIs
enable_apis() {
    echo -e "${YELLOW}Enabling required GCP APIs...${NC}"

    gcloud services enable container.googleapis.com --project="${GCP_PROJECT_ID}"
    gcloud services enable containerregistry.googleapis.com --project="${GCP_PROJECT_ID}"
    gcloud services enable artifactregistry.googleapis.com --project="${GCP_PROJECT_ID}"
    gcloud services enable sqladmin.googleapis.com --project="${GCP_PROJECT_ID}"
    gcloud services enable servicenetworking.googleapis.com --project="${GCP_PROJECT_ID}"
    gcloud services enable cloudresourcemanager.googleapis.com --project="${GCP_PROJECT_ID}"
    gcloud services enable iam.googleapis.com --project="${GCP_PROJECT_ID}"
    gcloud services enable compute.googleapis.com --project="${GCP_PROJECT_ID}"

    echo -e "${GREEN}APIs enabled${NC}"
}

# Create Autopilot cluster
create_autopilot_cluster() {
    echo -e "${YELLOW}Creating GKE Autopilot cluster: ${CLUSTER_NAME}...${NC}"

    # Check if cluster already exists
    if gcloud container clusters describe "${CLUSTER_NAME}" --region="${REGION}" --project="${GCP_PROJECT_ID}" &>/dev/null; then
        echo -e "${YELLOW}Cluster ${CLUSTER_NAME} already exists. Skipping creation.${NC}"
        return 0
    fi

    gcloud container clusters create-auto "${CLUSTER_NAME}" \
        --region="${REGION}" \
        --project="${GCP_PROJECT_ID}" \
        --release-channel=regular \
        --enable-master-authorized-networks \
        --master-authorized-networks="0.0.0.0/0" \
        --network=default \
        --subnetwork=default

    echo -e "${GREEN}Autopilot cluster created successfully${NC}"
}

# Create Standard cluster (alternative)
create_standard_cluster() {
    echo -e "${YELLOW}Creating GKE Standard cluster: ${CLUSTER_NAME}...${NC}"

    # Check if cluster already exists
    if gcloud container clusters describe "${CLUSTER_NAME}" --zone="${ZONE}" --project="${GCP_PROJECT_ID}" &>/dev/null; then
        echo -e "${YELLOW}Cluster ${CLUSTER_NAME} already exists. Skipping creation.${NC}"
        return 0
    fi

    gcloud container clusters create "${CLUSTER_NAME}" \
        --zone="${ZONE}" \
        --project="${GCP_PROJECT_ID}" \
        --num-nodes=3 \
        --machine-type=e2-medium \
        --disk-size=50GB \
        --disk-type=pd-standard \
        --enable-autoscaling \
        --min-nodes=2 \
        --max-nodes=10 \
        --enable-autorepair \
        --enable-autoupgrade \
        --release-channel=regular \
        --workload-pool="${GCP_PROJECT_ID}.svc.id.goog" \
        --enable-ip-alias \
        --enable-network-policy \
        --addons=HttpLoadBalancing,HorizontalPodAutoscaling

    echo -e "${GREEN}Standard cluster created successfully${NC}"
}

# Configure kubectl
configure_kubectl() {
    echo -e "${YELLOW}Configuring kubectl...${NC}"

    if [[ "${CLUSTER_TYPE}" == "autopilot" ]]; then
        gcloud container clusters get-credentials "${CLUSTER_NAME}" \
            --region="${REGION}" \
            --project="${GCP_PROJECT_ID}"
    else
        gcloud container clusters get-credentials "${CLUSTER_NAME}" \
            --zone="${ZONE}" \
            --project="${GCP_PROJECT_ID}"
    fi

    # Verify connection
    kubectl cluster-info

    echo -e "${GREEN}kubectl configured successfully${NC}"
}

# Create namespace
create_namespace() {
    echo -e "${YELLOW}Creating todo-app namespace...${NC}"

    kubectl create namespace todo-app --dry-run=client -o yaml | kubectl apply -f -

    echo -e "${GREEN}Namespace created${NC}"
}

# Reserve static IP for Ingress
reserve_static_ip() {
    echo -e "${YELLOW}Reserving static IP for Ingress...${NC}"

    # Check if IP already exists
    if gcloud compute addresses describe todo-app-ip --global --project="${GCP_PROJECT_ID}" &>/dev/null; then
        echo -e "${YELLOW}Static IP 'todo-app-ip' already exists${NC}"
    else
        gcloud compute addresses create todo-app-ip \
            --global \
            --project="${GCP_PROJECT_ID}"
        echo -e "${GREEN}Static IP reserved${NC}"
    fi

    # Display the IP
    IP_ADDRESS=$(gcloud compute addresses describe todo-app-ip --global --project="${GCP_PROJECT_ID}" --format="value(address)")
    echo -e "${GREEN}Static IP Address: ${IP_ADDRESS}${NC}"
    echo -e "${YELLOW}Point your domain's A record to this IP address${NC}"
}

# Create service account for Workload Identity
setup_workload_identity() {
    echo -e "${YELLOW}Setting up Workload Identity...${NC}"

    SA_NAME="todo-app-sa"
    SA_EMAIL="${SA_NAME}@${GCP_PROJECT_ID}.iam.gserviceaccount.com"

    # Create GCP service account if it doesn't exist
    if ! gcloud iam service-accounts describe "${SA_EMAIL}" --project="${GCP_PROJECT_ID}" &>/dev/null; then
        gcloud iam service-accounts create "${SA_NAME}" \
            --project="${GCP_PROJECT_ID}" \
            --description="Service account for Todo App" \
            --display-name="Todo App Service Account"
    fi

    # Grant Cloud SQL Client role
    gcloud projects add-iam-policy-binding "${GCP_PROJECT_ID}" \
        --member="serviceAccount:${SA_EMAIL}" \
        --role="roles/cloudsql.client" \
        --condition=None

    # Grant Secret Manager access (optional, for secrets)
    gcloud projects add-iam-policy-binding "${GCP_PROJECT_ID}" \
        --member="serviceAccount:${SA_EMAIL}" \
        --role="roles/secretmanager.secretAccessor" \
        --condition=None

    # Bind Kubernetes SA to GCP SA
    gcloud iam service-accounts add-iam-policy-binding "${SA_EMAIL}" \
        --project="${GCP_PROJECT_ID}" \
        --role="roles/iam.workloadIdentityUser" \
        --member="serviceAccount:${GCP_PROJECT_ID}.svc.id.goog[todo-app/todo-app-sa]"

    echo -e "${GREEN}Workload Identity configured${NC}"
}

# Print summary
print_summary() {
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}GKE Cluster Setup Complete!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "Cluster Name: ${CLUSTER_NAME}"
    echo "Project ID:   ${GCP_PROJECT_ID}"
    echo "Region:       ${REGION}"
    echo "Type:         ${CLUSTER_TYPE}"
    echo ""
    echo "Next steps:"
    echo "  1. Run 02-setup-artifact-registry.sh to create container registry"
    echo "  2. Run 03-setup-cloud-sql.sh to create PostgreSQL database"
    echo "  3. Run 04-deploy.sh to deploy the application"
    echo ""
    echo "Useful commands:"
    echo "  kubectl get nodes"
    echo "  kubectl get pods -n todo-app"
    echo "  gcloud container clusters describe ${CLUSTER_NAME} --region=${REGION}"
}

# Main execution
main() {
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}GKE Cluster Setup for Todo App${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""

    check_env
    check_prerequisites

    # Set project
    gcloud config set project "${GCP_PROJECT_ID}"

    enable_apis

    if [[ "${CLUSTER_TYPE}" == "autopilot" ]]; then
        create_autopilot_cluster
    else
        create_standard_cluster
    fi

    configure_kubectl
    create_namespace
    reserve_static_ip
    setup_workload_identity

    print_summary
}

# Run main
main "$@"
