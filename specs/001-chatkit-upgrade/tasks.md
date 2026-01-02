# Implementation Tasks: ChatKit Upgrade to Production Best Practices

**Feature**: ChatKit Upgrade to Production Best Practices
**Branch**: `001-chatkit-upgrade`
**Generated**: 2026-01-02
**Input**: `/specs/001-chatkit-upgrade/spec.md`, `/specs/001-chatkit-upgrade/plan.md`, `/specs/001-chatkit-upgrade/data-model.md`, `/specs/001-chatkit-upgrade/contracts/chatkit-api-contract.md`

## Overview

This document contains the implementation tasks for upgrading the chatbot with proper ChatKit backend, frontend, and widget implementations following production best practices. The implementation will follow OpenAI ChatKit SDK patterns with proper streaming widgets, action handlers, and authentication via Better Auth.

## Dependencies

User stories completion order:
- US1 (P1) - View Tasks with Rich Widget Display - No dependencies
- US2 (P1) - Manage Tasks via Conversational Actions - No dependencies
- US3 (P2) - Interactive Widget Actions - Depends on US1, US2
- US4 (P2) - Proper Frontend ChatKit Integration - No dependencies
- US5 (P3) - Session Persistence and Conversation History - Depends on US1, US2

## Parallel Execution Examples

Per user story parallelization opportunities:
- US1: [P] Create Thread model, [P] Create Message model, [P] Create Widget model
- US2: [P] Create Task CRUD service, [P] Create ChatKitServer implementation
- US3: [P] Create Action model, [P] Implement action handlers
- US4: [P] Create frontend components, [P] Update chat page with ChatKit integration
- US5: [P] Update User model, [P] Create conversation history service

## Implementation Strategy

MVP scope includes User Story 1 (view tasks with rich widgets) and User Story 2 (manage tasks via conversational actions). These represent the core functionality of the ChatKit upgrade. Subsequent stories add advanced features like interactive widgets, proper frontend styling, and conversation persistence.

---

## Phase 1: Setup

Setup tasks for project initialization and environment configuration.

- [X] T001 Create chatkit package directory structure in backend/app/chatkit/
- [X] T002 [P] Create backend/app/chatkit/__init__.py
- [X] T003 [P] Create backend/app/chatkit/server.py
- [X] T004 [P] Create backend/app/chatkit/server_interface.py
- [X] T005 [P] Create backend/app/chatkit/agents.py
- [X] T006 [P] Create backend/app/chatkit/widgets.py
- [X] T007 [P] Create backend/app/chatkit/types.py
- [X] T008 Create frontend/src/services/chat/ directory
- [X] T009 [P] Create frontend/src/services/chat/chatkit.ts (using existing chatkit-client.ts)
- [X] T010 [P] Create frontend/src/services/chat/types.ts
- [X] T011 Install OpenAI Agents SDK and ChatKit dependencies in backend (already in requirements.txt)
- [X] T012 Install ChatKit frontend dependencies in frontend (using CDN script integration)

## Phase 2: Foundational Components

Foundational tasks that block all user stories - database models, authentication integration, and core infrastructure.

- [X] T013 [P] Create Thread model in backend/app/models/thread.py with id, user_id, title, timestamps, metadata
- [X] T014 [P] Create Message model in backend/app/models/chatkit_message.py with id, thread_id, role, content, timestamps, metadata
- [X] T015 [P] Create Widget model in backend/app/models/widget.py with id, message_id, type, payload, timestamps, action_handler
- [X] T016 [P] Create Action model in backend/app/models/action.py with id, widget_id, thread_id, type, payload, timestamps, result
- [X] T017 [P] Extend User model with chat_preferences and last_chat_thread_id in backend/app/models/user.py
- [X] T018 Create database migration for new ChatKit entities in backend/alembic/versions/
- [X] T019 [P] Create Thread schema in backend/app/schemas/thread.py
- [X] T020 [P] Create Message schema in backend/app/schemas/chatkit_message.py
- [X] T021 [P] Create Widget schema in backend/app/schemas/widget.py
- [X] T022 [P] Create Action schema in backend/app/schemas/action.py
- [X] T023 [P] Create ChatKit-specific types in backend/app/chatkit/types.py
- [X] T024 Implement authentication middleware for ChatKit endpoints using Better Auth in backend/app/auth/
- [X] T025 Configure CORS settings for ChatKit streaming in backend/app/main.py (already configured)
- [X] T026 Create base ChatKit server interface in backend/app/chatkit/server_interface.py

## Phase 3: User Story 1 - View Tasks with Rich Widget Display (Priority: P1)

As a user, I want to see my tasks displayed in an interactive, visually rich widget format when I ask the chatbot to show my tasks, so that I can quickly understand my task status at a glance.

**Independent Test**: Can be fully tested by asking "Show me my tasks" and verifying a styled, interactive task list widget appears with proper icons, colors, and layout that renders correctly in the ChatKit UI.

- [X] T027 [US1] Create Task list widget factory in backend/app/chatkit/widgets.py
- [X] T028 [US1] Create Task display widget components (card, listview, row, text) in backend/app/chatkit/widgets.py
- [X] T029 [US1] Create get_tasks_for_user tool in backend/app/chatkit/agents.py
- [X] T030 [US1] Implement task retrieval service in backend/app/services/task_service.py
- [X] T031 [US1] Create task list widget with proper styling and status indicators
- [X] T032 [US1] Implement thread creation for new conversations in backend/app/services/thread_service.py
- [X] T033 [US1] Create ChatKitServer.respond() method that handles "show tasks" requests
- [X] T034 [US1] Implement widget streaming using ctx.stream_widget() for task display
- [X] T035 [US1] Create empty state widget for when user has no tasks
- [X] T036 [US1] Implement proper widget ID naming following {purpose}_{type} convention
- [X] T037 [US1] Add performance optimization to render widgets within 2 seconds
- [ ] T038 [US1] Create acceptance test for task list widget display

## Phase 4: User Story 2 - Manage Tasks via Conversational Actions (Priority: P1)

As a user, I want to add, complete, update, and delete tasks through natural language conversation, receiving immediate visual confirmation through widgets, so that task management feels intuitive and responsive.

**Independent Test**: Can be tested by performing each CRUD operation (add, complete, update, delete) and verifying appropriate confirmation widget appears.

- [X] T039 [US2] Create task creation tool in backend/app/chatkit/agents.py
- [X] T040 [US2] Create task completion tool in backend/app/chatkit/agents.py
- [X] T041 [US2] Create task update tool in backend/app/chatkit/agents.py
- [X] T042 [US2] Create task deletion tool in backend/app/chatkit/agents.py
- [X] T043 [US2] Create success confirmation widget factory in backend/app/chatkit/widgets.py
- [X] T044 [US2] Create task confirmation widgets with task details
- [X] T045 [US2] Implement task CRUD operations in backend/app/services/task_service.py
- [X] T046 [US2] Update ChatKitServer.respond() to handle task management commands
- [X] T047 [US2] Implement natural language processing for task commands
- [X] T048 [US2] Add task validation to ensure proper creation and updates
- [ ] T049 [US2] Create acceptance test for task CRUD operations via conversation
- [X] T050 [US2] Implement proper error handling for task operations

## Phase 5: User Story 3 - Interactive Widget Actions (Priority: P2)

As a user, I want to interact with task widgets directly (click to complete, edit, or delete), so that I can manage tasks without typing additional commands.

**Independent Test**: Can be tested by clicking action buttons within task widgets and verifying the corresponding backend action executes.

- [X] T051 [US3] Update ChatKitServer.action() method to handle widget actions
- [X] T052 [US3] Create action handler for task completion button clicks
- [X] T053 [US3] Create action handler for task deletion button clicks
- [X] T054 [US3] Create confirmation dialog widget for delete actions
- [ ] T055 [US3] Implement widget update after action processing
- [X] T056 [US3] Create button widget factory with proper action payloads
- [X] T057 [US3] Add validation for incoming action payloads
- [X] T058 [US3] Implement action processing with result tracking
- [ ] T059 [US3] Update task list widget after interactive actions
- [ ] T060 [US3] Create acceptance test for interactive widget actions
- [X] T061 [US3] Add proper action ID generation and tracking

## Phase 6: User Story 4 - Proper Frontend ChatKit Integration (Priority: P2)

As a user, I want the chat interface to have proper styling, loading states, and error handling that matches production-quality ChatKit applications, so that the experience feels polished and reliable.

**Independent Test**: Can be tested by loading the chat page and verifying ChatKit CDN styles are applied, loading animations work, and error states display gracefully.

- [X] T062 [US4] Update frontend/src/app/(dashboard)/chat/page.tsx with ChatKit CDN integration
- [X] T063 [US4] Create ChatKit service in frontend/src/services/chat/chatkit.ts (using existing chatkit-client.ts)
- [ ] T064 [US4] Add ChatKit CDN script loading with fallback handling
- [X] T065 [US4] Create loading state components for chat interface
- [X] T066 [US4] Create error state components for chat interface
- [X] T067 [US4] Implement proper ChatKit styling and theming
- [ ] T068 [US4] Add accessibility features (keyboard navigation, ARIA labels)
- [X] T069 [US4] Create frontend types for ChatKit integration in frontend/src/services/chat/types.ts
- [ ] T070 [US4] Implement graceful degradation when CDN fails
- [ ] T071 [US4] Add retry mechanism for failed requests
- [ ] T072 [US4] Create acceptance test for frontend ChatKit integration

## Phase 7: User Story 5 - Session Persistence and Conversation History (Priority: P3)

As a user, I want my conversation history to persist across page refreshes and sessions, so that I can continue where I left off.

**Independent Test**: Can be tested by having a conversation, refreshing the page, and verifying previous messages and context are restored.

- [X] T073 [US5] Implement conversation history retrieval in backend/app/services/thread_service.py
- [X] T074 [US5] Create message history service in backend/app/services/message_service.py
- [X] T075 [US5] Update ChatKitServer to include conversation history in responses
- [X] T076 [US5] Implement pagination for long conversation histories
- [X] T077 [US5] Add conversation context to agent processing (last 20 messages)
- [ ] T078 [US5] Create frontend service to restore conversation history on page load
- [X] T079 [US5] Implement session persistence using backend storage
- [X] T080 [US5] Add thread association to user session
- [ ] T081 [US5] Create acceptance test for conversation history persistence
- [ ] T082 [US5] Implement data retention policies for old conversations

## Phase 8: Polish & Cross-Cutting Concerns

Final implementation tasks that cut across all user stories to ensure production readiness.

- [X] T083 Implement rate limiting for ChatKit endpoints (100 requests/min per user)
- [X] T084 Add comprehensive logging for ChatKit interactions
- [X] T085 Implement proper error handling and user-friendly error messages
- [ ] T086 Add performance monitoring for widget rendering times
- [ ] T087 Create comprehensive test suite covering all user stories
- [X] T088 Implement widget data sanitization for security
- [X] T089 Add proper validation for all incoming action payloads
- [X] T090 Create documentation for ChatKit API endpoints (in contracts/chatkit-api-contract.md)
- [X] T091 Implement proper cleanup for unused threads and messages
- [X] T092 Add caching for frequently accessed widgets to improve performance
- [X] T093 Create health check endpoints for ChatKit services
- [X] T094 Perform security review of ChatKit implementation
- [X] T095 Update README with ChatKit setup and usage instructions