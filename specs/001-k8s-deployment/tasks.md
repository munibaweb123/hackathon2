# Tasks: Local Kubernetes Deployment

**Input**: Design documents from `/specs/001-k8s-deployment/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Tests are NOT included in this implementation as they were not explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Web app monorepo**: `backend/`, `frontend/`, `helm-charts/`, `scripts/`, `k8s/`
- Docker-related files in service directories (`backend/Dockerfile`, `frontend/Dockerfile`)
- Kubernetes manifests in `helm-charts/todo-app/templates/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and deployment structure

- [ ] T001 Create deployment directory structure (helm-charts/todo-app/, k8s/, scripts/)
- [ ] T002 [P] Create backend/.dockerignore with exclusions (node_modules, .git, *.md, tests)
- [ ] T003 [P] Create frontend/.dockerignore with exclusions (node_modules, .git, .next, *.md)
- [ ] T004 [P] Create .env.example template with required environment variables
- [ ] T005 [P] Create helm-charts/todo-app/Chart.yaml with metadata (name, version, appVersion)
- [ ] T006 [P] Create helm-charts/todo-app/.helmignore with exclusions
- [ ] T007 [P] Create scripts/ directory for automation (build-images.sh, deploy.sh, health-check.sh, cleanup.sh)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T008 Create multi-stage Dockerfile for backend in backend/Dockerfile (builder + runner stages)
- [ ] T009 Create multi-stage Dockerfile for frontend in frontend/Dockerfile (builder + runner stages)
- [ ] T010 [P] Implement backend health endpoints in backend/app/api/health.py (/livez, /readyz, /health)
- [ ] T011 [P] Implement frontend health endpoints in frontend/src/app/api/health/live/route.ts
- [ ] T012 [P] Implement frontend health endpoints in frontend/src/app/api/health/ready/route.ts
- [ ] T013 [P] Implement frontend health endpoints in frontend/src/app/api/health/route.ts
- [ ] T014 [P] Create Helm helper templates in helm-charts/todo-app/templates/_helpers.tpl
- [ ] T015 [P] Create Helm values.yaml with default configuration for development
- [ ] T016 [P] Create Helm values-dev.yaml with development-specific overrides
- [ ] T017 [P] Create Helm values-prod.yaml with production-specific overrides

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Deploy Todo Application Locally (Priority: P1) 🎯 MVP

**Goal**: Containerize and deploy the complete Todo Chatbot application (frontend and backend) to Minikube with all Phase III functionality working

**Independent Test**: Build Docker images, deploy with Helm to Minikube, access frontend via browser at NodePort service, create/update/delete tasks, verify persistence across pod restarts

### Docker Images for User Story 1

- [ ] T018 [P] [US1] Configure backend Dockerfile with Python 3.13 base image and dependencies
- [ ] T019 [P] [US1] Configure frontend Dockerfile with Node.js 20 base image and Next.js build
- [ ] T020 [P] [US1] Add health check configuration to backend Dockerfile (HEALTHCHECK instruction)
- [ ] T021 [P] [US1] Add build arguments to frontend Dockerfile (NEXT_PUBLIC_API_URL, NEXT_PUBLIC_APP_VERSION)

### Kubernetes Deployments for User Story 1

- [ ] T022 [P] [US1] Create backend deployment template in helm-charts/todo-app/templates/deployment-backend.yaml
- [ ] T023 [P] [US1] Create frontend deployment template in helm-charts/todo-app/templates/deployment-frontend.yaml
- [ ] T024 [P] [US1] Create PostgreSQL deployment template in helm-charts/todo-app/templates/deployment-postgres.yaml
- [ ] T025 [US1] Configure backend deployment with health probes (startup, liveness, readiness) in templates/deployment-backend.yaml
- [ ] T026 [US1] Configure frontend deployment with health probes (startup, liveness, readiness) in templates/deployment-frontend.yaml
- [ ] T027 [US1] Configure backend deployment with resource requests and limits in templates/deployment-backend.yaml
- [ ] T028 [US1] Configure frontend deployment with resource requests and limits in templates/deployment-frontend.yaml
- [ ] T029 [US1] Configure PostgreSQL deployment with resource requests and limits in templates/deployment-postgres.yaml

### Kubernetes Services for User Story 1

- [ ] T030 [P] [US1] Create backend service template (ClusterIP) in helm-charts/todo-app/templates/service-backend.yaml
- [ ] T031 [P] [US1] Create frontend service template (NodePort) in helm-charts/todo-app/templates/service-frontend.yaml
- [ ] T032 [P] [US1] Create PostgreSQL service template (ClusterIP) in helm-charts/todo-app/templates/service-postgres.yaml

### Configuration for User Story 1

- [ ] T033 [P] [US1] Create ConfigMap template in helm-charts/todo-app/templates/configmap.yaml (environment, CORS, service URLs)
- [ ] T034 [P] [US1] Create Secret template in helm-charts/todo-app/templates/secret.yaml (database credentials, JWT secret, Better Auth secret)
- [ ] T035 [US1] Create PersistentVolumeClaim template for PostgreSQL in helm-charts/todo-app/templates/pvc-postgres.yaml

### Automation Scripts for User Story 1

- [ ] T036 [P] [US1] Create scripts/build-images.sh to build Docker images for Minikube
- [ ] T037 [P] [US1] Create scripts/deploy.sh to deploy application with Helm
- [ ] T038 [P] [US1] Create scripts/health-check.sh to verify deployment health
- [ ] T039 [P] [US1] Create scripts/cleanup.sh to clean up Kubernetes resources
- [ ] T040 [US1] Make all scripts executable (chmod +x scripts/*.sh)

### Integration and Verification for User Story 1

- [ ] T041 [US1] Update backend environment variables to use Kubernetes service DNS (todo-postgres:5432)
- [ ] T042 [US1] Update frontend environment variables to use backend service DNS (todo-backend:8000)
- [ ] T043 [US1] Configure backend to accept connections from frontend pods (CORS configuration)
- [ ] T044 [US1] Add deployment annotations with ConfigMap/Secret checksums for auto-reload
- [ ] T045 [US1] Test Docker image builds locally (docker build for backend and frontend)
- [ ] T046 [US1] Test Helm chart validation (helm lint helm-charts/todo-app)
- [ ] T047 [US1] Perform dry-run deployment (helm install --dry-run --debug)
- [ ] T048 [US1] Deploy to Minikube and verify all pods reach Running status
- [ ] T049 [US1] Verify backend health endpoints (/livez, /readyz, /health) return 200 OK
- [ ] T050 [US1] Verify frontend health endpoints return 200 OK
- [ ] T051 [US1] Verify frontend can communicate with backend API
- [ ] T052 [US1] Test task CRUD operations (create, read, update, delete) via UI
- [ ] T053 [US1] Verify data persists after backend pod restart (kubectl delete pod)
- [ ] T054 [US1] Verify Phase III chatbot features work (AI task management, reminders, recurring tasks)

**Checkpoint**: At this point, User Story 1 should be fully functional - complete Todo Chatbot deployed to Kubernetes with all Phase III features working

---

## Phase 4: User Story 2 - Use AI-Assisted DevOps Tools (Priority: P2)

**Goal**: Enable AI-powered tools (Docker AI Agent Gordon, kubectl-ai, Kagent) for intelligent Kubernetes and Docker operations

**Independent Test**: Execute common operations through kubectl-ai ("deploy frontend with 2 replicas", "check cluster health"), verify AI tools generate correct commands, use Kagent to analyze cluster health

### Documentation for User Story 2

- [ ] T055 [P] [US2] Create docs/AI_TOOLS_SETUP.md with installation instructions for kubectl-ai
- [ ] T056 [P] [US2] Create docs/AI_TOOLS_SETUP.md section for Kagent installation
- [ ] T057 [P] [US2] Create docs/AI_TOOLS_SETUP.md section for Docker AI Agent (Gordon) setup
- [ ] T058 [US2] Document kubectl-ai usage examples in docs/AI_TOOLS_USAGE.md (deploy, scale, debug)
- [ ] T059 [US2] Document Kagent usage examples in docs/AI_TOOLS_USAGE.md (analyze, optimize)
- [ ] T060 [US2] Document Docker AI Agent usage examples in docs/AI_TOOLS_USAGE.md

### Configuration for User Story 2

- [ ] T061 [P] [US2] Create .kubectl-ai-config.yaml with OpenAI API configuration
- [ ] T062 [P] [US2] Create scripts/setup-ai-tools.sh for automated tool installation
- [ ] T063 [US2] Add environment variable template for OPENAI_API_KEY in .env.example

### Testing and Validation for User Story 2

- [ ] T064 [US2] Test kubectl-ai deployment command: "deploy the todo frontend with 2 replicas"
- [ ] T065 [US2] Test kubectl-ai debugging command: "check why the pods are failing"
- [ ] T066 [US2] Test kubectl-ai scaling command: "scale the backend to handle more load"
- [ ] T067 [US2] Test Kagent cluster analysis: "analyze the cluster health"
- [ ] T068 [US2] Test Kagent optimization: "optimize resource allocation"
- [ ] T069 [US2] Test Docker AI Agent in Docker Desktop (ask "What can you do?")
- [ ] T070 [US2] Create troubleshooting guide for AI tool failures in docs/AI_TOOLS_TROUBLESHOOTING.md

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - application deployed AND AI tools operational

---

## Phase 5: User Story 3 - Manage Deployment with Helm Charts (Priority: P2)

**Goal**: Use Helm charts for consistent deployment management across environments with install/upgrade/rollback capabilities

**Independent Test**: Install Helm chart, modify values, perform upgrade without downtime, rollback to previous version, deploy with different environment values files

### Advanced Helm Templates for User Story 3

- [ ] T071 [P] [US3] Create ServiceAccount template in helm-charts/todo-app/templates/serviceaccount.yaml
- [ ] T072 [P] [US3] Create HorizontalPodAutoscaler template for backend in templates/hpa-backend.yaml
- [ ] T073 [P] [US3] Create HorizontalPodAutoscaler template for frontend in templates/hpa-frontend.yaml
- [ ] T074 [P] [US3] Create Ingress template (optional) in templates/ingress.yaml
- [ ] T075 [P] [US3] Create NetworkPolicy template for backend in templates/networkpolicy-backend.yaml
- [ ] T076 [P] [US3] Create NetworkPolicy template for frontend in templates/networkpolicy-frontend.yaml
- [ ] T077 [P] [US3] Create PodDisruptionBudget template for backend in templates/pdb-backend.yaml
- [ ] T078 [P] [US3] Create database migration Job template in templates/job-migration.yaml
- [ ] T079 [P] [US3] Create Helm test hook in templates/tests/test-connection.yaml

### Helm Chart Validation for User Story 3

- [ ] T080 [P] [US3] Create JSON schema for values validation in helm-charts/todo-app/values.schema.json
- [ ] T081 [P] [US3] Create chart-testing configuration in helm-charts/todo-app/ci/ct-config.yaml
- [ ] T082 [US3] Add Helm chart dependencies (optional PostgreSQL chart) in Chart.yaml
- [ ] T083 [US3] Configure rolling update strategy in deployment templates (maxUnavailable, maxSurge)

### Environment-Specific Configuration for User Story 3

- [ ] T084 [P] [US3] Create values-staging.yaml with staging-specific configuration
- [ ] T085 [US3] Configure production-grade resource limits in values-prod.yaml (CPU, memory)
- [ ] T086 [US3] Configure development minimal resources in values-dev.yaml
- [ ] T087 [US3] Configure autoscaling parameters for production in values-prod.yaml (minReplicas: 3, maxReplicas: 20)
- [ ] T088 [US3] Disable autoscaling for development in values-dev.yaml

### Testing Helm Operations for User Story 3

- [ ] T089 [US3] Test Helm install with default values.yaml
- [ ] T090 [US3] Test Helm upgrade with modified configuration (change replica count)
- [ ] T091 [US3] Verify zero-downtime rolling update (no failed requests during update)
- [ ] T092 [US3] Test Helm rollback to previous revision
- [ ] T093 [US3] Test deployment with values-dev.yaml (minimal resources)
- [ ] T094 [US3] Test deployment with values-prod.yaml (production resources)
- [ ] T095 [US3] Run helm lint on all values files (values.yaml, values-dev.yaml, values-prod.yaml)
- [ ] T096 [US3] Run Helm tests with `helm test todo-app` command
- [ ] T097 [US3] Verify ConfigMap changes trigger pod restart (via checksum annotation)

**Checkpoint**: All three user stories should now work - deployed app, AI tools, AND Helm management operational

---

## Phase 6: User Story 4 - Monitor and Troubleshoot Deployments (Priority: P3)

**Goal**: Monitor Kubernetes deployments and troubleshoot issues using AI-assisted tools for quick problem resolution

**Independent Test**: Create intentional failures (resource limits, configuration errors), use kubectl-ai/Kagent to diagnose, verify accurate root cause analysis and remediation steps

### Monitoring Setup for User Story 4

- [ ] T098 [P] [US4] Add Prometheus annotations to backend deployment template (prometheus.io/scrape, prometheus.io/port)
- [ ] T099 [P] [US4] Add Prometheus annotations to frontend deployment template
- [ ] T100 [P] [US4] Create ServiceMonitor CRD in templates/servicemonitor.yaml (if Prometheus Operator available)
- [ ] T101 [US4] Configure resource metrics in HPA templates (CPU, memory utilization)

### Logging and Observability for User Story 4

- [ ] T102 [P] [US4] Configure structured JSON logging in backend (LOG_FORMAT=json)
- [ ] T103 [P] [US4] Add log level configuration via ConfigMap (DEBUG, INFO, WARNING, ERROR)
- [ ] T104 [US4] Add request tracing headers to backend API responses
- [ ] T105 [US4] Configure log aggregation labels (app, component, version)

### Troubleshooting Documentation for User Story 4

- [ ] T106 [P] [US4] Create docs/TROUBLESHOOTING.md with common issues (pod not starting, service not accessible)
- [ ] T107 [P] [US4] Document health check debugging steps in docs/TROUBLESHOOTING.md
- [ ] T108 [P] [US4] Document database connection troubleshooting in docs/TROUBLESHOOTING.md
- [ ] T109 [P] [US4] Document resource constraint troubleshooting in docs/TROUBLESHOOTING.md
- [ ] T110 [US4] Create kubectl command reference in docs/KUBECTL_REFERENCE.md

### AI-Assisted Debugging for User Story 4

- [ ] T111 [US4] Test kubectl-ai for CrashLoopBackOff diagnosis: "check why the pods are failing"
- [ ] T112 [US4] Test Kagent for resource optimization: "optimize resource allocation"
- [ ] T113 [US4] Test Kagent for cluster health analysis: "analyze the cluster health"
- [ ] T114 [US4] Create intentional failure (set invalid DATABASE_URL) and debug with AI tools
- [ ] T115 [US4] Create resource pressure scenario (insufficient memory) and diagnose with AI tools
- [ ] T116 [US4] Test log retrieval with kubectl-ai: "show me backend logs from last 10 minutes"

### Monitoring Validation for User Story 4

- [ ] T117 [US4] Verify pod resource usage with `kubectl top pods`
- [ ] T118 [US4] Verify node resource usage with `kubectl top nodes`
- [ ] T119 [US4] Test pod describe for event troubleshooting (`kubectl describe pod`)
- [ ] T120 [US4] Verify liveness probe failures trigger pod restart
- [ ] T121 [US4] Verify readiness probe failures remove pod from service endpoints
- [ ] T122 [US4] Create runbook for common operational tasks in docs/RUNBOOK.md

**Checkpoint**: All user stories should now be independently functional with full monitoring and troubleshooting capabilities

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final validation

- [ ] T123 [P] Update main README.md with Kubernetes deployment overview and prerequisites
- [ ] T124 [P] Create comprehensive deployment guide in docs/DEPLOYMENT_GUIDE.md
- [ ] T125 [P] Create security hardening checklist in docs/SECURITY.md (non-root, read-only filesystem, drop capabilities)
- [ ] T126 [P] Add Minikube setup instructions to quickstart.md
- [ ] T127 [P] Create CI/CD pipeline template in .github/workflows/k8s-deploy.yml (optional)
- [ ] T128 [P] Document backup and restore procedures in docs/BACKUP_RESTORE.md
- [ ] T129 Code cleanup: Remove hardcoded values from templates (use values.yaml)
- [ ] T130 Validate all resource names follow Kubernetes naming conventions (lowercase, hyphens)
- [ ] T131 Verify all templates use Helm helper functions for consistency
- [ ] T132 Security audit: Ensure no secrets hardcoded in values.yaml or templates
- [ ] T133 Performance test: Verify API response time <1 second under 50 concurrent requests
- [ ] T134 Load test autoscaling: Generate load and verify HPA scales pods correctly
- [ ] T135 Test full deployment cycle (build, deploy, test, update, rollback) under 15 minutes
- [ ] T136 Validate quickstart.md by following all steps from scratch
- [ ] T137 Create video walkthrough or screenshots for deployment process (optional)
- [ ] T138 Final integration test: Deploy all user stories, verify end-to-end functionality
- [ ] T139 Create release notes documenting all features and known limitations

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P2 → P3)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories - **MVP READY**
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Requires US1 deployment to be working for testing
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Requires US1 Helm chart to exist for management operations
- **User Story 4 (P3)**: Can start after Foundational (Phase 2) - Requires US1 deployment for monitoring, benefits from US2 AI tools

### Within Each User Story

**User Story 1 (Deploy Application):**
- Dockerfiles before Kubernetes templates
- Health endpoints before deployment health probes
- Deployments before services (services reference deployments via selectors)
- ConfigMap/Secret before deployments (deployments mount configuration)
- PVC before PostgreSQL deployment (deployment mounts volume)
- Individual templates can be created in parallel (marked [P])
- Automation scripts can be created in parallel
- Integration/verification tasks must run after all templates are complete

**User Story 2 (AI Tools):**
- Documentation can be created in parallel (marked [P])
- Configuration can be created in parallel
- Testing requires US1 deployment to be operational

**User Story 3 (Helm Management):**
- Advanced Helm templates can be created in parallel (marked [P])
- Environment-specific values files can be created in parallel (marked [P])
- Testing requires templates to be complete

**User Story 4 (Monitoring/Troubleshooting):**
- Monitoring templates can be created in parallel (marked [P])
- Documentation can be created in parallel (marked [P])
- Testing requires US1 deployment and benefits from US2 AI tools

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T002, T003, T004, T005, T006, T007)
- All Foundational tasks marked [P] can run in parallel (T010-T017)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Within each user story, tasks marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all health endpoint implementations together:
Task: "Implement backend health endpoints in backend/app/api/health.py"
Task: "Implement frontend health live endpoint in frontend/src/app/api/health/live/route.ts"
Task: "Implement frontend health ready endpoint in frontend/src/app/api/health/ready/route.ts"
Task: "Implement frontend health endpoint in frontend/src/app/api/health/route.ts"

# Launch all Docker image tasks together:
Task: "Configure backend Dockerfile with Python 3.13 base image"
Task: "Configure frontend Dockerfile with Node.js 20 base image"
Task: "Add health check to backend Dockerfile"
Task: "Add build arguments to frontend Dockerfile"

# Launch all Kubernetes deployment templates together:
Task: "Create backend deployment template in templates/deployment-backend.yaml"
Task: "Create frontend deployment template in templates/deployment-frontend.yaml"
Task: "Create PostgreSQL deployment template in templates/deployment-postgres.yaml"

# Launch all service templates together:
Task: "Create backend service template in templates/service-backend.yaml"
Task: "Create frontend service template in templates/service-frontend.yaml"
Task: "Create PostgreSQL service template in templates/service-postgres.yaml"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T007)
2. Complete Phase 2: Foundational (T008-T017) - **CRITICAL - blocks all stories**
3. Complete Phase 3: User Story 1 (T018-T054)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy to Minikube and verify all Phase III features work
6. Demo the deployed application

**Estimated Time**: 6-8 hours for MVP (first-time Kubernetes deployment)

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP! - Working Kubernetes deployment)
3. Add User Story 2 → Test independently → Deploy/Demo (MVP + AI tools)
4. Add User Story 3 → Test independently → Deploy/Demo (MVP + AI tools + Helm management)
5. Add User Story 4 → Test independently → Deploy/Demo (Full featured with monitoring)
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T017)
2. Once Foundational is done:
   - **Developer A**: User Story 1 - Deploy Application (T018-T054)
   - **Developer B**: User Story 2 - AI Tools (T055-T070) + User Story 3 - Helm (T071-T097)
   - **Developer C**: User Story 4 - Monitoring (T098-T122)
3. Stories complete and integrate independently
4. Team reconvenes for Phase 7: Polish (T123-T139)

---

## Success Criteria Validation

After completing all tasks, verify these success criteria from spec.md:

- **SC-001**: ✅ Docker images build in under 5 minutes on standard hardware
- **SC-002**: ✅ Application deploys to Minikube within 3 minutes of `helm install`
- **SC-003**: ✅ All Phase III Todo Chatbot features work correctly
- **SC-004**: ✅ Pod restarts don't cause data loss or >5 second interruption
- **SC-005**: ✅ kubectl-ai executes 90%+ of common commands without errors
- **SC-006**: ✅ Kagent provides insights in under 30 seconds
- **SC-007**: ✅ Full deployment cycle (build, deploy, test, update, rollback) completes in <15 minutes
- **SC-008**: ✅ Application scales 1→3→1 replicas without service interruption
- **SC-009**: ✅ Helm charts deploy to different environments with only values file changes
- **SC-010**: ✅ API response times remain sub-second under 50 concurrent requests

---

## Notes

- **[P] tasks** = different files, no dependencies, can run in parallel
- **[Story] label** maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Tests are NOT included as they were not requested in the specification
- Commit after each task or logical group of related tasks
- Stop at any checkpoint to validate story independently
- **Minikube resource requirements**: 4GB RAM, 2 CPUs minimum
- Use `eval $(minikube docker-env)` before building images to avoid registry push
- All secrets in values.yaml are development defaults - replace for production
- AI tools (kubectl-ai, Kagent, Gordon) are optional enhancements
- **MVP = User Story 1** - delivers core deployment functionality
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

---

## Total Task Count

- **Phase 1 (Setup)**: 7 tasks
- **Phase 2 (Foundational)**: 10 tasks (BLOCKS all user stories)
- **Phase 3 (User Story 1 - Deploy Application)**: 37 tasks - **MVP READY**
- **Phase 4 (User Story 2 - AI Tools)**: 16 tasks
- **Phase 5 (User Story 3 - Helm Management)**: 27 tasks
- **Phase 6 (User Story 4 - Monitoring)**: 25 tasks
- **Phase 7 (Polish)**: 17 tasks

**Total**: 139 tasks

**Parallel Opportunities**: 62 tasks marked [P] can run in parallel within their phase

**MVP Scope (Recommended)**: Phases 1 + 2 + 3 = 54 tasks for fully functional Kubernetes deployment
