# Feature Specification: Phase V - Advanced Cloud Deployment

**Feature Branch**: `004-advanced-cloud-deploy`
**Created**: 2026-01-04
**Status**: Draft
**Input**: User description: "Phase V: Advanced Cloud Deployment - Advanced Level Functionality on DigitalOcean Kubernetes (DOKS), Google Cloud (GKE), or Azure (AKS). Implement advanced features, event-driven architecture with Kafka, Dapr distributed runtime, deploy to Minikube locally and production-grade cloud Kubernetes, CI/CD pipeline, monitoring and logging."

---

## Overview

Phase V delivers a production-ready, cloud-native Todo application with advanced task management features and enterprise-grade infrastructure. The system evolves from a monolithic application to a microservices architecture using event-driven patterns, deployed on managed Kubernetes with full observability.

### Scope

**In Scope:**
- Part A: Advanced Features (Recurring Tasks, Due Dates & Reminders, Priorities, Tags, Search, Filter, Sort)
- Part B: Local Deployment (Minikube with Dapr)
- Part C: Cloud Deployment (DOKS/GKE/AKS with Kafka on Redpanda Cloud, CI/CD, Monitoring)

**Out of Scope:**
- Mobile native applications
- Multi-tenancy architecture
- Custom Kafka cluster management (using managed Redpanda Cloud)
- Custom monitoring infrastructure (using cloud-native solutions)

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Task with Due Date and Reminder (Priority: P1)

As a user, I want to set due dates and reminders on tasks so that I never miss important deadlines.

**Why this priority**: Due dates and reminders are core features that drive user engagement and task completion. Without them, the todo app lacks time-awareness which is essential for productivity.

**Independent Test**: Can be fully tested by creating a task with a due date and reminder, then verifying the user receives a notification at the specified time.

**Acceptance Scenarios**:

1. **Given** I am creating a new task, **When** I set a due date for tomorrow at 3 PM, **Then** the task displays the due date and appears in my "upcoming" view sorted by date.
2. **Given** I have a task with a due date, **When** I set a reminder for 1 hour before, **Then** I receive a notification 1 hour before the due date.
3. **Given** I have a task with a due date that has passed, **When** I view my tasks, **Then** the overdue task is visually highlighted as overdue.
4. **Given** I have a task with a reminder, **When** the reminder time arrives, **Then** I receive a notification via the notification service (push/email based on user preferences).

---

### User Story 2 - Recurring Tasks (Priority: P1)

As a user, I want to create recurring tasks so that repetitive activities are automatically scheduled.

**Why this priority**: Recurring tasks reduce manual effort for routine activities and are essential for habit tracking and regular task management.

**Independent Test**: Can be fully tested by creating a weekly recurring task, marking it complete, and verifying a new instance is automatically created for the next week.

**Acceptance Scenarios**:

1. **Given** I am creating a task, **When** I set recurrence to "weekly on Monday", **Then** after completing the task, a new task is automatically created for the next Monday.
2. **Given** I have a daily recurring task, **When** I complete it, **Then** the next occurrence is created within 30 seconds.
3. **Given** I have a recurring task, **When** I edit the recurrence pattern, **Then** future occurrences follow the new pattern.
4. **Given** I have a recurring task, **When** I delete it, **Then** I can choose to delete only this instance or all future occurrences.

---

### User Story 3 - Task Organization with Priorities and Tags (Priority: P2)

As a user, I want to assign priorities and tags to tasks so that I can organize and find tasks quickly.

**Why this priority**: Organization features enhance usability but the app remains functional without them. They significantly improve user experience for power users.

**Independent Test**: Can be fully tested by creating tasks with different priorities and tags, then verifying they can be filtered and sorted accordingly.

**Acceptance Scenarios**:

1. **Given** I am creating a task, **When** I assign priority "High", **Then** the task displays with a high-priority indicator and appears first in priority-sorted views.
2. **Given** I have multiple tasks, **When** I add the tag "work" to selected tasks, **Then** I can filter to show only "work" tagged tasks.
3. **Given** I have tasks with various priorities, **When** I sort by priority, **Then** tasks appear in order: High, Medium, Low, None.
4. **Given** I want to find a specific task, **When** I search for keywords, **Then** matching tasks are displayed based on title and description content.

---

### User Story 4 - Search, Filter, and Sort (Priority: P2)

As a user, I want to search, filter, and sort my tasks so that I can quickly find what I need.

**Why this priority**: Essential for productivity when task lists grow, but the app remains functional with basic list views.

**Independent Test**: Can be fully tested by creating 50+ tasks with various attributes, then verifying search returns relevant results within acceptable time.

**Acceptance Scenarios**:

1. **Given** I have 100 tasks, **When** I search for "project alpha", **Then** all tasks containing "project alpha" in title or description are displayed within 2 seconds.
2. **Given** I have tasks with different due dates, **When** I filter by "due this week", **Then** only tasks due within the current week are shown.
3. **Given** I have tasks with different tags, **When** I filter by multiple tags, **Then** tasks matching any of the selected tags are displayed.
4. **Given** I have filtered results, **When** I apply sorting by due date, **Then** the filtered results are reordered by due date.

---

### User Story 5 - Real-time Sync Across Devices (Priority: P2)

As a user, I want my tasks to sync in real-time across all my devices so that I always see the latest state.

**Why this priority**: Multi-device sync is expected for modern applications but not critical for single-device usage.

**Independent Test**: Can be fully tested by modifying a task on one device and verifying the change appears on another device within seconds.

**Acceptance Scenarios**:

1. **Given** I am logged in on two devices, **When** I create a task on device A, **Then** the task appears on device B within 5 seconds without manual refresh.
2. **Given** I have the app open on multiple devices, **When** I mark a task complete on one device, **Then** the status updates on all devices in real-time.
3. **Given** I lose network connectivity, **When** I make changes offline, **Then** changes sync automatically when connectivity is restored.

---

### User Story 6 - Deployment to Production Cloud (Priority: P3)

As a DevOps engineer, I want the application deployed to a managed Kubernetes cluster so that it runs reliably at scale.

**Why this priority**: Cloud deployment is the end goal but development and testing can proceed on local Minikube.

**Independent Test**: Can be fully tested by deploying to a cloud Kubernetes cluster and verifying all services are running and accessible.

**Acceptance Scenarios**:

1. **Given** a configured cloud Kubernetes cluster (DOKS/GKE/AKS), **When** I run the deployment pipeline, **Then** all application components are deployed and healthy within 10 minutes.
2. **Given** the application is deployed, **When** I access the application URL, **Then** users can log in and manage tasks.
3. **Given** the application is running, **When** I push a code change to main, **Then** CI/CD automatically tests, builds, and deploys the update.

---

### User Story 7 - Observability and Monitoring (Priority: P3)

As a DevOps engineer, I want comprehensive monitoring and logging so that I can troubleshoot issues and track performance.

**Why this priority**: Monitoring is essential for production operations but not required for development or testing phases.

**Independent Test**: Can be fully tested by generating load on the system and verifying metrics and logs are captured and queryable.

**Acceptance Scenarios**:

1. **Given** the application is deployed, **When** I access the monitoring dashboard, **Then** I can see CPU, memory, and request latency metrics for all services.
2. **Given** an error occurs in the application, **When** I search the logs, **Then** I can find the error details with request correlation IDs.
3. **Given** a service becomes unhealthy, **When** health checks fail, **Then** I receive an alert within 5 minutes.

---

### Edge Cases

- What happens when a recurring task's recurrence pattern is invalid (e.g., "weekly on Feb 30")?
  - System validates patterns at creation time and rejects invalid configurations with clear error messages.

- How does the system handle reminder delivery when the user is offline?
  - Reminders are queued and delivered when the user comes online; if significantly past due, they are marked as "missed" with the original reminder time.

- What happens if Kafka/message broker is temporarily unavailable?
  - Events are buffered locally with retry logic; critical operations (task CRUD) remain functional with eventual consistency.

- How does the system handle conflicting edits from multiple devices?
  - Last-write-wins with conflict detection; users are notified of potential conflicts for manual resolution.

- What happens when cloud deployment quota/credit limits are reached?
  - Application implements graceful degradation; monitoring alerts trigger before limits are reached.

- What happens when a recurring task reaches its end_date?
  - System stops creating new occurrences and marks the recurring series as "completed" automatically.

---

## Requirements *(mandatory)*

### Functional Requirements

#### Part A: Advanced Features

- **FR-001**: System MUST allow users to set due dates on tasks with date and time precision.
- **FR-002**: System MUST send reminder notifications at user-specified times before task due dates via both in-app (WebSocket/browser) and email channels.
- **FR-003**: System MUST support recurring task patterns (daily, weekly, monthly, custom).
- **FR-004**: System MUST automatically create the next occurrence when a recurring task is completed.
- **FR-005**: System MUST allow users to assign priority levels (High, Medium, Low, None) to tasks.
- **FR-006**: System MUST allow users to add multiple tags to tasks.
- **FR-007**: System MUST provide full-text search across task titles and descriptions.
- **FR-008**: System MUST support filtering tasks by status, priority, tags, and date ranges.
- **FR-009**: System MUST support sorting tasks by due date, priority, creation date, and title.

#### Part B: Event-Driven Architecture

- **FR-010**: System MUST publish task events (created, updated, completed, deleted) to a message broker.
- **FR-011**: System MUST have a dedicated notification service that consumes reminder events.
- **FR-012**: System MUST have a dedicated recurring task service that consumes completion events and creates next occurrences.
- **FR-013**: System MUST maintain an audit log of all task operations for traceability; logs retained for 30 days, then deleted permanently.
- **FR-014**: System MUST broadcast task changes to connected clients for real-time synchronization.

#### Part C: Infrastructure & Deployment

- **FR-015**: System MUST be deployable to local Minikube for development and testing.
- **FR-016**: System MUST be deployable to managed Kubernetes (DOKS, GKE, or AKS).
- **FR-017**: System MUST use Dapr for service-to-service communication and pub/sub messaging.
- **FR-018**: System MUST use Dapr components for state management, bindings, and secrets.
- **FR-019**: System MUST have a CI/CD pipeline using GitHub Actions for automated testing and deployment.
- **FR-020**: System MUST include monitoring dashboards for application health and performance.
- **FR-021**: System MUST include centralized logging for troubleshooting and auditing.

### Non-Functional Requirements

- **NFR-001**: Reminder notifications MUST be delivered within 60 seconds of the scheduled time.
- **NFR-002**: Recurring task creation MUST complete within 30 seconds of the triggering event.
- **NFR-003**: Search results MUST return within 2 seconds for up to 10,000 tasks.
- **NFR-004**: Real-time sync MUST propagate changes to all clients within 5 seconds.
- **NFR-005**: System MUST handle at least 100 concurrent users without performance degradation.
- **NFR-006**: CI/CD pipeline MUST complete deployment within 15 minutes of code merge.
- **NFR-007**: System MUST achieve 99.5% uptime in production.

### Key Entities

- **Task**: Core entity representing a todo item with title, description, status, due_date, reminder_at, priority, recurrence_pattern, and tags.
- **TaskEvent**: Represents an event in the event stream (event_type, task_id, task_data, user_id, timestamp).
- **ReminderEvent**: Represents a scheduled reminder (task_id, title, due_at, remind_at, user_id).
- **RecurrencePattern**: Defines how a task repeats (frequency, interval, day_of_week, day_of_month, end_date). When end_date is reached, the series is marked "completed" and no new occurrences are created.
- **AuditLog**: Immutable record of all task operations for compliance and debugging.
- **Tag**: User-defined label for task organization.
- **NotificationPreference**: User settings for notification delivery. Supported channels: in-app (WebSocket/browser) and email. Users can enable/disable each channel independently.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

#### Feature Adoption & Usability

- **SC-001**: 80% of users with tasks set at least one due date within their first week.
- **SC-002**: Users can create a recurring task in under 1 minute from task creation screen.
- **SC-003**: Search returns relevant results for 95% of user queries (measured by user satisfaction surveys).
- **SC-004**: Task completion rate for tasks with reminders is 30% higher than tasks without reminders.

#### System Performance

- **SC-005**: Reminder notifications are delivered within 60 seconds of scheduled time for 99% of reminders.
- **SC-006**: Real-time sync completes within 5 seconds for 99% of updates.
- **SC-007**: System supports 100 concurrent users with response times under 500ms for 95th percentile.
- **SC-008**: Search queries on datasets up to 10,000 tasks complete in under 2 seconds.

#### Operational Excellence

- **SC-009**: Zero-downtime deployments for all production releases.
- **SC-010**: Mean time to detect issues is under 5 minutes (via monitoring alerts).
- **SC-011**: Mean time to recover from incidents is under 30 minutes.
- **SC-012**: 95% of CI/CD pipeline runs complete successfully without manual intervention.

#### Infrastructure

- **SC-013**: Application successfully deploys to at least one managed Kubernetes provider (DOKS, GKE, or AKS).
- **SC-014**: All Dapr building blocks (Pub/Sub, State, Bindings, Secrets, Service Invocation) are operational.
- **SC-015**: Event-driven services (Notification, Recurring Task, Audit) process events independently without blocking the main application.

---

## Assumptions

1. **Cloud Provider**: User will choose one cloud provider (DigitalOcean, Google Cloud, or Azure) for production deployment; spec is provider-agnostic.
2. **Message Broker**: Redpanda Cloud (Serverless) will be used for Kafka-compatible messaging due to free tier and ease of setup.
3. **Notification Channel**: Implementation supports in-app notifications (WebSocket/browser) and email from start; user preferences stored per-user with independent channel toggles.
4. **Authentication**: Existing Better Auth integration from previous phases remains in place.
5. **Database**: Existing Neon PostgreSQL database continues as the primary data store.
6. **Recurrence Patterns**: Standard patterns (daily, weekly, monthly) plus custom cron-like expressions supported.
7. **Offline Support**: Basic offline support with sync-on-reconnect; full offline-first capability out of scope.
8. **Time Zones**: All times stored in UTC; displayed in user's local timezone based on browser/device settings.

---

## Dependencies

- **Previous Phases**: Phases I-IV must be complete (console app, web app, chatbot, initial K8s deployment).
- **Cloud Provider Account**: User needs an account with one of DOKS/GKE/AKS with available credits.
- **Redpanda Cloud Account**: Free tier account for Kafka-compatible messaging.
- **Domain/DNS**: Optional but recommended for production deployment.
- **SSL Certificates**: Required for production HTTPS; can use Let's Encrypt or cloud provider certificates.

---

## Clarifications

### Session 2026-01-04

- Q: Audit log retention policy? → A: 30 days retention, then delete permanently
- Q: Recurring task end behavior? → A: Stop creating occurrences; mark series as "completed"
- Q: Primary notification delivery channel? → A: Both in-app (WebSocket/browser) and email from start

---

## Risks

1. **Cloud Credit Exhaustion**: Managed Kubernetes and associated services may exhaust free credits quickly.
   - *Mitigation*: Monitor usage closely; provide cost optimization guidelines; support Minikube for extended testing.

2. **Complexity Overhead**: Event-driven architecture adds significant complexity compared to monolithic approach.
   - *Mitigation*: Comprehensive documentation; incremental migration; fallback to direct calls if needed.

3. **Multi-Provider Variability**: DOKS, GKE, and AKS have different capabilities and configurations.
   - *Mitigation*: Use Helm charts and Dapr abstractions to minimize provider-specific code; document provider differences.
