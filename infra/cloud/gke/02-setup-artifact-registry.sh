#!/bin/bash
# Artifact Registry Setup Script
# Creates Google Artifact Registry and builds/pushes container images

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Default values
REGION="${GCP_REGION:-us-central1}"
REPO_NAME="${REPO_NAME:-todo-app}"

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"

# Check required environment variables
check_env() {
    if [[ -z "${GCP_PROJECT_ID:-}" ]]; then
        echo -e "${RED}Error: GCP_PROJECT_ID environment variable is required${NC}"
        echo "Usage: GCP_PROJECT_ID=your-project $0"
        exit 1
    fi
}

# Create Artifact Registry repository
create_registry() {
    echo -e "${YELLOW}Creating Artifact Registry repository...${NC}"

    # Check if repository exists
    if gcloud artifacts repositories describe "${REPO_NAME}" \
        --location="${REGION}" \
        --project="${GCP_PROJECT_ID}" &>/dev/null; then
        echo -e "${YELLOW}Repository '${REPO_NAME}' already exists${NC}"
        return 0
    fi

    gcloud artifacts repositories create "${REPO_NAME}" \
        --repository-format=docker \
        --location="${REGION}" \
        --project="${GCP_PROJECT_ID}" \
        --description="Todo App container images"

    echo -e "${GREEN}Repository created successfully${NC}"
}

# Configure Docker authentication
configure_docker_auth() {
    echo -e "${YELLOW}Configuring Docker authentication...${NC}"

    gcloud auth configure-docker "${REGION}-docker.pkg.dev" --quiet

    echo -e "${GREEN}Docker authentication configured${NC}"
}

# Build and push backend image
build_backend() {
    echo -e "${YELLOW}Building backend image...${NC}"

    local image_name="${REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/${REPO_NAME}/backend"
    local tag="${IMAGE_TAG:-latest}"

    docker build \
        -t "${image_name}:${tag}" \
        -f "${PROJECT_ROOT}/backend/Dockerfile" \
        "${PROJECT_ROOT}/backend"

    echo -e "${YELLOW}Pushing backend image...${NC}"
    docker push "${image_name}:${tag}"

    echo -e "${GREEN}Backend image pushed: ${image_name}:${tag}${NC}"
}

# Build and push frontend image
build_frontend() {
    echo -e "${YELLOW}Building frontend image...${NC}"

    local image_name="${REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/${REPO_NAME}/frontend"
    local tag="${IMAGE_TAG:-latest}"

    docker build \
        -t "${image_name}:${tag}" \
        -f "${PROJECT_ROOT}/frontend/Dockerfile" \
        "${PROJECT_ROOT}/frontend"

    echo -e "${YELLOW}Pushing frontend image...${NC}"
    docker push "${image_name}:${tag}"

    echo -e "${GREEN}Frontend image pushed: ${image_name}:${tag}${NC}"
}

# Build and push notification service
build_notification() {
    echo -e "${YELLOW}Building notification service image...${NC}"

    local image_name="${REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/${REPO_NAME}/notification"
    local tag="${IMAGE_TAG:-latest}"

    # Check if Dockerfile exists
    if [[ -f "${PROJECT_ROOT}/infra/docker/notification.Dockerfile" ]]; then
        docker build \
            -t "${image_name}:${tag}" \
            -f "${PROJECT_ROOT}/infra/docker/notification.Dockerfile" \
            "${PROJECT_ROOT}/backend"

        docker push "${image_name}:${tag}"
        echo -e "${GREEN}Notification image pushed: ${image_name}:${tag}${NC}"
    else
        echo -e "${YELLOW}Notification Dockerfile not found, skipping...${NC}"
    fi
}

# Build and push recurring service
build_recurring() {
    echo -e "${YELLOW}Building recurring service image...${NC}"

    local image_name="${REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/${REPO_NAME}/recurring"
    local tag="${IMAGE_TAG:-latest}"

    if [[ -f "${PROJECT_ROOT}/infra/docker/recurring.Dockerfile" ]]; then
        docker build \
            -t "${image_name}:${tag}" \
            -f "${PROJECT_ROOT}/infra/docker/recurring.Dockerfile" \
            "${PROJECT_ROOT}/backend"

        docker push "${image_name}:${tag}"
        echo -e "${GREEN}Recurring image pushed: ${image_name}:${tag}${NC}"
    else
        echo -e "${YELLOW}Recurring Dockerfile not found, skipping...${NC}"
    fi
}

# Build and push audit service
build_audit() {
    echo -e "${YELLOW}Building audit service image...${NC}"

    local image_name="${REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/${REPO_NAME}/audit"
    local tag="${IMAGE_TAG:-latest}"

    if [[ -f "${PROJECT_ROOT}/infra/docker/audit.Dockerfile" ]]; then
        docker build \
            -t "${image_name}:${tag}" \
            -f "${PROJECT_ROOT}/infra/docker/audit.Dockerfile" \
            "${PROJECT_ROOT}/backend"

        docker push "${image_name}:${tag}"
        echo -e "${GREEN}Audit image pushed: ${image_name}:${tag}${NC}"
    else
        echo -e "${YELLOW}Audit Dockerfile not found, skipping...${NC}"
    fi
}

# Build all images
build_all() {
    build_backend
    build_frontend
    build_notification
    build_recurring
    build_audit
}

# Print summary
print_summary() {
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Artifact Registry Setup Complete!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "Repository: ${REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/${REPO_NAME}"
    echo ""
    echo "Images pushed:"
    echo "  - backend:${IMAGE_TAG:-latest}"
    echo "  - frontend:${IMAGE_TAG:-latest}"
    echo "  - notification:${IMAGE_TAG:-latest} (if Dockerfile exists)"
    echo "  - recurring:${IMAGE_TAG:-latest} (if Dockerfile exists)"
    echo "  - audit:${IMAGE_TAG:-latest} (if Dockerfile exists)"
    echo ""
    echo "Next steps:"
    echo "  1. Run 03-setup-cloud-sql.sh to create the database"
    echo "  2. Run 04-deploy.sh to deploy to GKE"
}

# Show usage
usage() {
    echo "Usage: GCP_PROJECT_ID=your-project $0 [command]"
    echo ""
    echo "Commands:"
    echo "  all         Build and push all images (default)"
    echo "  backend     Build and push backend only"
    echo "  frontend    Build and push frontend only"
    echo "  registry    Create registry only (no builds)"
    echo ""
    echo "Environment variables:"
    echo "  GCP_PROJECT_ID  (required) GCP project ID"
    echo "  GCP_REGION      (optional) Region, default: us-central1"
    echo "  IMAGE_TAG       (optional) Image tag, default: latest"
    echo "  REPO_NAME       (optional) Repository name, default: todo-app"
}

# Main execution
main() {
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Artifact Registry Setup for Todo App${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""

    local command="${1:-all}"

    case "${command}" in
        -h|--help|help)
            usage
            exit 0
            ;;
        *)
            check_env
            ;;
    esac

    create_registry
    configure_docker_auth

    case "${command}" in
        all)
            build_all
            ;;
        backend)
            build_backend
            ;;
        frontend)
            build_frontend
            ;;
        notification)
            build_notification
            ;;
        recurring)
            build_recurring
            ;;
        audit)
            build_audit
            ;;
        registry)
            echo -e "${GREEN}Registry created, no images built${NC}"
            ;;
        *)
            echo -e "${RED}Unknown command: ${command}${NC}"
            usage
            exit 1
            ;;
    esac

    print_summary
}

# Run main
main "$@"
