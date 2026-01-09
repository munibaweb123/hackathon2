# Tasks: Phase V - Advanced Cloud Deployment

**Input**: Design documents from `/specs/004-advanced-cloud-deploy/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/
**Tests**: Not explicitly requested - test tasks omitted (add on request)
**Organization**: Tasks grouped by user story to enable independent implementation and testing

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/app/` for main API, `backend/services/` for microservices
- **Frontend**: `frontend/src/`
- **Infrastructure**: `infra/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, dependencies, and base configuration

- [x] T001 Add advanced feature dependencies to backend/requirements.txt (python-dateutil, aiokafka, httpx, Dapr SDK)
- [x] T002 [P] Create backend/app/dapr/ directory structure per plan.md
- [x] T003 [P] Create infra/helm/ directory structure per plan.md
- [x] T004 [P] Create infra/docker/ directory structure per plan.md
- [x] T005 [P] Create backend/services/notification/ directory for notification microservice
- [x] T006 [P] Create backend/services/recurring/ directory for recurring task microservice
- [x] T007 [P] Create backend/services/audit/ directory for audit log microservice
- [x] T008 Create .github/workflows/ directory for CI/CD pipelines

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can begin

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Migrations

- [x] T009 Create Alembic migration for Task table extension (priority, due_date, reminder_at, recurrence_id, parent_task_id, search_vector) in backend/alembic/versions/
- [x] T010 Create Alembic migration for Tag and TaskTag tables in backend/alembic/versions/
- [x] T011 Create Alembic migration for RecurrencePattern table and enums in backend/alembic/versions/
- [x] T012 Create Alembic migration for AuditLog table in backend/alembic/versions/
- [x] T013 Create Alembic migration for NotificationPreference table in backend/alembic/versions/
- [x] T014 Create Alembic migration for full-text search trigger on tasks.search_vector in backend/alembic/versions/

### Extended Models

- [x] T015 [P] Create Priority and TaskStatus enums in backend/app/models/enums.py
- [x] T016 [P] Create RecurrenceFrequency and RecurrenceStatus enums in backend/app/models/enums.py
- [x] T017 Extend Task model with priority, due_date, reminder_at, recurrence_id, parent_task_id in backend/app/models/task.py
- [x] T018 [P] Create Tag model in backend/app/models/tag.py
- [x] T019 [P] Create TaskTag junction model in backend/app/models/task_tag.py
- [x] T020 [P] Create RecurrencePattern model in backend/app/models/recurrence.py
- [x] T021 [P] Create AuditLog model in backend/app/models/audit.py
- [x] T022 [P] Create NotificationPreference model in backend/app/models/notification_preference.py

### Dapr Infrastructure

- [x] T023 [P] Create Dapr pubsub component config for Kafka in infra/helm/dapr-components/pubsub.yaml
- [x] T024 [P] Create Dapr statestore component config for PostgreSQL in infra/helm/dapr-components/statestore.yaml
- [x] T025 [P] Create Dapr bindings component for cron triggers in infra/helm/dapr-components/bindings.yaml
- [x] T026 [P] Create Dapr secrets component for K8s secrets in infra/helm/dapr-components/secrets.yaml
- [x] T027 Create Dapr event publisher utility in backend/app/services/event_publisher.py

### Event Schemas

- [x] T028 [P] Create TaskEvent Pydantic schema in backend/app/events/schemas.py
- [x] T029 [P] Create ReminderEvent Pydantic schema in backend/app/events/schemas.py
- [x] T030 [P] Create TaskUpdateEvent Pydantic schema in backend/app/events/schemas.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Due Date and Reminder (Priority: P1) 🎯 MVP

**Goal**: Users can set due dates and reminders on tasks, receive notifications at specified times

**Independent Test**: Create a task with due date and reminder, verify notification is received at reminder time

### Implementation for User Story 1

- [x] T031 [US1] Add due_date and reminder_at fields to CreateTaskRequest schema in backend/app/schemas/task.py
- [x] T032 [US1] Add due_date and reminder_at fields to UpdateTaskRequest schema in backend/app/schemas/task.py
- [x] T033 [US1] Add is_overdue computed property to Task response schema in backend/app/schemas/task.py
- [x] T034 [US1] Update task creation endpoint to accept due_date and reminder_at in backend/app/api/tasks.py
- [x] T035 [US1] Update task update endpoint to accept due_date and reminder_at in backend/app/api/tasks.py
- [x] T036 [US1] Create reminder scheduling logic in backend/app/services/reminder_scheduler.py
- [x] T037 [US1] Implement reminder event publishing when tasks with reminders are created/updated in backend/app/services/task_service.py
- [x] T038 [US1] Create notification microservice main entry point in backend/services/notification/main.py
- [x] T039 [US1] Implement Dapr subscription handler for reminder events in backend/services/notification/main.py
- [x] T040 [P] [US1] Create WebSocket broadcaster for in-app notifications in backend/services/notification/websocket_broadcaster.py
- [x] T041 [P] [US1] Create email sender using Resend/SendGrid in backend/services/notification/email_sender.py
- [x] T042 [US1] Create TaskForm component with due date picker in frontend/src/components/tasks/TaskForm.tsx
- [x] T043 [US1] Create overdue visual indicator styling in frontend/src/components/tasks/TaskCard.tsx
- [x] T044 [US1] Create NotificationBadge component for in-app notifications in frontend/src/components/notifications/NotificationBadge.tsx
- [x] T045 [US1] Create use-notifications hook for WebSocket notification handling in frontend/src/hooks/use-notifications.ts

**Checkpoint**: User Story 1 complete - users can set due dates and receive reminders

---

## Phase 4: User Story 2 - Recurring Tasks (Priority: P1)

**Goal**: Users can create recurring tasks that auto-generate next occurrence on completion

**Independent Test**: Create weekly recurring task, mark complete, verify next week's task is auto-created

### Implementation for User Story 2

- [x] T046 [US2] Create recurrence pattern schemas (Create, Update, Response) in backend/app/schemas/recurrence.py
- [x] T047 [US2] Add recurrence field to CreateTaskRequest and UpdateTaskRequest in backend/app/schemas/task.py
- [x] T048 [US2] Create recurrence calculation service using python-dateutil rrule in backend/app/services/recurrence_service.py
- [x] T049 [US2] Update task creation to create RecurrencePattern when recurrence specified in backend/app/services/task_service.py
- [x] T050 [US2] Create recurring task microservice main entry point in backend/services/recurring/main.py
- [x] T051 [US2] Implement Dapr subscription for task-events (completed) in backend/services/recurring/main.py
- [x] T052 [US2] Implement task generator that creates next occurrence on completion in backend/services/recurring/task_generator.py
- [x] T053 [US2] Handle recurrence end conditions (end_date, count exhausted) in backend/services/recurring/task_generator.py
- [x] T054 [US2] Add recurrence deletion options (single/all future) to delete endpoint in backend/app/api/tasks.py
- [x] T055 [US2] Create recurrence pattern UI selector in frontend/src/components/tasks/RecurrenceSelector.tsx
- [x] T056 [US2] Integrate RecurrenceSelector into TaskForm in frontend/src/components/tasks/TaskForm.tsx
- [x] T057 [US2] Display recurrence indicator on task cards in frontend/src/components/tasks/TaskCard.tsx
- [x] T058 [US2] Add delete confirmation dialog for recurring task options in frontend/src/components/tasks/DeleteTaskDialog.tsx

**Checkpoint**: User Story 2 complete - recurring tasks auto-generate on completion

---

## Phase 5: User Story 3 - Priorities and Tags (Priority: P2)

**Goal**: Users can assign priorities and multiple tags to organize tasks

**Independent Test**: Create tasks with different priorities and tags, verify filtering works

### Implementation for User Story 3

- [x] T059 [P] [US3] Create Tag schemas (Create, Update, Response) in backend/app/schemas/tag.py
- [x] T060 [US3] Add priority field to CreateTaskRequest and UpdateTaskRequest in backend/app/schemas/task.py
- [x] T061 [US3] Add tags field to Task response schema in backend/app/schemas/task.py
- [x] T062 [US3] Create TagService for tag CRUD operations in backend/app/services/tag_service.py
- [x] T063 [US3] Create tag CRUD endpoints in backend/app/api/tags.py
- [x] T064 [US3] Create add/remove tags to task endpoints in backend/app/api/tasks.py
- [x] T065 [US3] Update task creation/update to handle priority assignment in backend/app/services/task_service.py
- [x] T066 [US3] Create PrioritySelector component in frontend/src/components/tasks/PrioritySelector.tsx
- [x] T067 [US3] Create TagSelector component with create/select functionality in frontend/src/components/tasks/TagSelector.tsx
- [x] T068 [US3] Integrate PrioritySelector and TagSelector into TaskForm in frontend/src/components/tasks/TaskForm.tsx
- [x] T069 [US3] Display priority indicator on task cards in frontend/src/components/tasks/TaskCard.tsx
- [x] T070 [US3] Display tag chips on task cards in frontend/src/components/tasks/TaskCard.tsx
- [x] T071 [US3] Create tag management page in frontend/src/app/settings/tags/page.tsx

**Checkpoint**: User Story 3 complete - tasks can be organized with priorities and tags

---

## Phase 6: User Story 4 - Search, Filter, Sort (Priority: P2)

**Goal**: Users can search, filter by multiple criteria, and sort task lists

**Independent Test**: Create 50+ tasks, verify search returns relevant results in <2s

### Implementation for User Story 4

- [ ] T072 [US4] Create SearchService using PostgreSQL tsvector/tsquery in backend/app/services/search_service.py
- [ ] T073 [US4] Create search endpoint with full-text search capability in backend/app/api/search.py
- [ ] T074 [US4] Add filter parameters (status, priority, tags, due_before, due_after) to list tasks endpoint in backend/app/api/tasks.py
- [ ] T075 [US4] Add sort parameters (due_date, priority, created_at, title) to list tasks endpoint in backend/app/api/tasks.py
- [ ] T076 [US4] Implement multi-tag filter logic in backend/app/services/task_service.py
- [ ] T077 [US4] Implement date range filter logic in backend/app/services/task_service.py
- [ ] T078 [US4] Create TaskFilters component with status/priority/tag selectors in frontend/src/components/tasks/TaskFilters.tsx
- [ ] T079 [US4] Create DateRangeFilter component in frontend/src/components/tasks/DateRangeFilter.tsx
- [ ] T080 [US4] Create SearchBar component with debounced input in frontend/src/components/tasks/SearchBar.tsx
- [ ] T081 [US4] Create SortSelector component in frontend/src/components/tasks/SortSelector.tsx
- [ ] T082 [US4] Integrate filter/sort components into task list page in frontend/src/app/tasks/page.tsx
- [ ] T083 [US4] Update use-tasks hook to support filter/sort/search parameters in frontend/src/hooks/use-tasks.ts

**Checkpoint**: User Story 4 complete - full search, filter, and sort functionality

---

## Phase 7: User Story 5 - Real-time Sync (Priority: P2)

**Goal**: Task changes sync to all connected devices within 5 seconds

**Independent Test**: Open app on two devices, modify task on one, verify update appears on other within 5s

### Implementation for User Story 5

- [ ] T084 [US5] Publish TaskUpdateEvent on task create/update/delete/complete in backend/app/services/task_service.py
- [ ] T085 [US5] Create WebSocket service main entry point for real-time sync in backend/services/notification/websocket_service.py
- [ ] T086 [US5] Implement Dapr subscription for task-updates topic in backend/services/notification/websocket_service.py
- [ ] T087 [US5] Create WebSocket connection manager with user session tracking in backend/services/notification/connection_manager.py
- [ ] T088 [US5] Create WebSocket endpoint in main backend API in backend/app/api/websocket.py
- [ ] T089 [US5] Create websocket-client service for frontend in frontend/src/services/websocket-client.ts
- [ ] T090 [US5] Create use-realtime-sync hook in frontend/src/hooks/use-realtime-sync.ts
- [ ] T091 [US5] Integrate realtime sync into task list page in frontend/src/app/tasks/page.tsx
- [ ] T092 [US5] Add connection status indicator in frontend/src/components/layout/ConnectionStatus.tsx
- [ ] T093 [US5] Implement optimistic updates with rollback on conflict in frontend/src/hooks/use-tasks.ts

**Checkpoint**: User Story 5 complete - real-time sync across devices

---

## Phase 8: User Story 6 - Cloud Deployment (Priority: P3)

**Goal**: Application deployed to managed Kubernetes with CI/CD pipeline

**Independent Test**: Run deployment pipeline, verify all services healthy within 10 minutes

### Infrastructure Setup

- [ ] T094 [P] [US6] Create backend Dockerfile in infra/docker/backend.Dockerfile
- [ ] T095 [P] [US6] Create frontend Dockerfile in infra/docker/frontend.Dockerfile
- [ ] T096 [P] [US6] Create notification service Dockerfile in infra/docker/notification.Dockerfile
- [ ] T097 [P] [US6] Create recurring service Dockerfile in infra/docker/recurring.Dockerfile
- [ ] T098 [P] [US6] Create audit service Dockerfile in infra/docker/audit.Dockerfile
- [ ] T099 [US6] Create docker-compose for local development in infra/docker/docker-compose.local.yml

### Helm Charts

- [ ] T100 [US6] Create main Helm chart structure in infra/helm/todo-app/Chart.yaml
- [ ] T101 [P] [US6] Create backend deployment template in infra/helm/todo-app/templates/backend-deployment.yaml
- [ ] T102 [P] [US6] Create frontend deployment template in infra/helm/todo-app/templates/frontend-deployment.yaml
- [ ] T103 [P] [US6] Create notification service deployment template in infra/helm/todo-app/templates/notification-deployment.yaml
- [ ] T104 [P] [US6] Create recurring service deployment template in infra/helm/todo-app/templates/recurring-deployment.yaml
- [ ] T105 [P] [US6] Create audit service deployment template in infra/helm/todo-app/templates/audit-deployment.yaml
- [ ] T106 [US6] Create service templates for all deployments in infra/helm/todo-app/templates/
- [ ] T107 [US6] Create ingress template in infra/helm/todo-app/templates/ingress.yaml
- [ ] T108 [P] [US6] Create values.yaml with defaults in infra/helm/todo-app/values.yaml
- [ ] T109 [P] [US6] Create values-minikube.yaml for local testing in infra/helm/todo-app/values-minikube.yaml
- [ ] T110 [P] [US6] Create values-production.yaml for cloud deployment in infra/helm/todo-app/values-production.yaml

### Minikube Setup

- [ ] T111 [US6] Create Minikube setup script in infra/minikube/setup.sh
- [ ] T112 [US6] Document local Minikube deployment in quickstart.md

### CI/CD Pipelines

- [ ] T113 [US6] Create CI workflow for testing and linting in .github/workflows/ci.yml
- [ ] T114 [US6] Create CD workflow for staging deployment in .github/workflows/cd-staging.yml
- [ ] T115 [US6] Create CD workflow for production deployment with approval in .github/workflows/cd-production.yml
- [ ] T116 [US6] Add environment secrets configuration documentation

**Checkpoint**: User Story 6 complete - cloud deployment operational

---

## Phase 9: User Story 7 - Observability (Priority: P3)

**Goal**: Comprehensive monitoring, logging, and alerting for production operations

**Independent Test**: Generate load, verify metrics/logs visible in dashboards

### Audit Service

- [ ] T117 [US7] Create audit service main entry point in backend/services/audit/main.py
- [ ] T118 [US7] Implement Dapr subscription for task-events in backend/services/audit/main.py
- [ ] T119 [US7] Implement audit log writer in backend/services/audit/log_writer.py
- [ ] T120 [US7] Create audit log retention job (30-day cleanup) in backend/services/audit/retention.py

### Monitoring Stack

- [ ] T121 [P] [US7] Create Prometheus Helm values for todo-app metrics in infra/helm/monitoring/prometheus-values.yaml
- [ ] T122 [P] [US7] Create Grafana dashboard JSON for application metrics in infra/helm/monitoring/dashboards/todo-app.json
- [ ] T123 [P] [US7] Create Loki Helm values for log aggregation in infra/helm/monitoring/loki-values.yaml
- [ ] T124 [US7] Create Jaeger configuration for distributed tracing in infra/helm/monitoring/jaeger-values.yaml
- [ ] T125 [US7] Configure Dapr tracing and metrics export in infra/helm/dapr-components/config.yaml

### Alerting

- [ ] T126 [US7] Create Prometheus alerting rules for critical conditions in infra/helm/monitoring/alerts.yaml
- [ ] T127 [US7] Create runbook documentation for common alerts in docs/runbooks/

### Notification Preferences API

- [ ] T128 [US7] Create notification preferences endpoints (GET/PUT) in backend/app/api/notifications.py
- [ ] T129 [US7] Create notification history endpoint in backend/app/api/notifications.py
- [ ] T130 [US7] Create test notification endpoint in backend/app/api/notifications.py
- [ ] T131 [US7] Create notification preferences page in frontend/src/app/settings/notifications/page.tsx

**Checkpoint**: User Story 7 complete - full observability operational

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements affecting multiple user stories

- [ ] T132 [P] Add API error handling middleware for consistent error responses in backend/app/middleware/error_handler.py
- [ ] T133 [P] Add request correlation ID middleware for tracing in backend/app/middleware/correlation.py
- [ ] T134 [P] Add structured logging configuration in backend/app/core/logging.py
- [ ] T135 [P] Create API documentation with OpenAPI descriptions in backend/app/main.py
- [ ] T136 Validate quickstart.md end-to-end flow
- [ ] T137 Create cloud provider setup documentation (DOKS, GKE, AKS) in infra/cloud/
- [ ] T138 Security review: validate no secrets in code, proper CORS, rate limiting
- [ ] T139 Performance validation: run k6 load tests per NFR requirements

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **User Stories (Phase 3-9)**: All depend on Foundational phase
  - US1 (Due Dates) and US2 (Recurring) are both P1 - implement in order or parallel
  - US3-5 (P2) can proceed after US1/US2 or in parallel
  - US6-7 (P3) can proceed after core features or in parallel
- **Polish (Phase 10)**: After all desired user stories complete

### User Story Dependencies

| User Story | Depends On | Can Run Parallel With |
|------------|------------|----------------------|
| US1 (Due Dates) | Foundational | US2 |
| US2 (Recurring) | Foundational | US1 |
| US3 (Priorities/Tags) | Foundational | US1, US2, US4, US5 |
| US4 (Search/Filter) | Foundational | US1, US2, US3, US5 |
| US5 (Real-time) | Foundational | US1, US2, US3, US4 |
| US6 (Deployment) | Foundational + at least US1 | US7 |
| US7 (Observability) | Foundational + US6 | None |

### Parallel Opportunities

**Phase 2 (Foundational)**: Tasks T015-T022 (models) and T023-T030 (Dapr/events) can run in parallel
**Phase 8 (Deployment)**: All Dockerfiles (T094-T098) can run in parallel, all Helm templates (T101-T105) can run in parallel

---

## Parallel Example: Foundational Phase

```bash
# Models - all can run in parallel:
T015: Create Priority and TaskStatus enums
T016: Create RecurrenceFrequency and RecurrenceStatus enums
T018: Create Tag model
T019: Create TaskTag junction model
T020: Create RecurrencePattern model
T021: Create AuditLog model
T022: Create NotificationPreference model

# Dapr components - all can run in parallel:
T023: Create Dapr pubsub component
T024: Create Dapr statestore component
T025: Create Dapr bindings component
T026: Create Dapr secrets component
```

---

## Parallel Example: User Story 6 (Deployment)

```bash
# Dockerfiles - all can run in parallel:
T094: Create backend Dockerfile
T095: Create frontend Dockerfile
T096: Create notification service Dockerfile
T097: Create recurring service Dockerfile
T098: Create audit service Dockerfile

# Helm values - all can run in parallel:
T108: Create values.yaml
T109: Create values-minikube.yaml
T110: Create values-production.yaml
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Due Dates & Reminders)
4. Complete Phase 4: User Story 2 (Recurring Tasks)
5. **STOP and VALIDATE**: Test core features independently
6. Deploy to Minikube for demo

### Incremental Delivery

1. **Foundation** (Phase 1-2): ~30 tasks → Infrastructure ready
2. **MVP** (Phase 3-4): US1 + US2 → Core time-aware features
3. **Organization** (Phase 5-6): US3 + US4 → Priority, tags, search
4. **Sync** (Phase 7): US5 → Multi-device real-time
5. **Production** (Phase 8-9): US6 + US7 → Cloud deployment + monitoring
6. **Polish** (Phase 10): Final hardening

### Task Summary

| Phase | User Story | Task Count | Parallel Tasks |
|-------|------------|------------|----------------|
| 1 | Setup | 8 | 6 |
| 2 | Foundational | 22 | 14 |
| 3 | US1 - Due Dates | 15 | 2 |
| 4 | US2 - Recurring | 13 | 0 |
| 5 | US3 - Priorities/Tags | 13 | 1 |
| 6 | US4 - Search/Filter | 12 | 0 |
| 7 | US5 - Real-time | 10 | 0 |
| 8 | US6 - Deployment | 23 | 15 |
| 9 | US7 - Observability | 15 | 3 |
| 10 | Polish | 8 | 4 |
| **Total** | | **139** | **45** |

---

## Notes

- [P] tasks = different files, no dependencies within phase
- [USn] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All file paths are relative to repository root
