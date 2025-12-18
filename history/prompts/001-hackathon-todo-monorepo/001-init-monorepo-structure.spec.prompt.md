---
id: 001
title: Initialize hackathon-todo monorepo structure
stage: spec
date: 2025-12-18
surface: agent
model: claude-opus-4-5-20251101
feature: 001-hackathon-todo-monorepo
branch: 001-hackathon-todo-monorepo
user: user
command: /sp.specify
labels: ["monorepo", "initialization", "full-stack", "spec-kit"]
links:
  spec: specs/001-hackathon-todo-monorepo/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - .spec-kit/config.yaml
  - CLAUDE.md
  - backend/CLAUDE.md
  - backend/main.py
  - backend/models.py
  - backend/db.py
  - backend/Dockerfile
  - backend/requirements.txt
  - frontend/CLAUDE.md
  - frontend/app/layout.tsx
  - frontend/app/page.tsx
  - frontend/app/globals.css
  - frontend/lib/api.ts
  - frontend/package.json
  - frontend/tsconfig.json
  - frontend/tailwind.config.ts
  - frontend/Dockerfile
  - specs/overview.md
  - specs/features/task-crud.md
  - specs/api/rest-endpoints.md
  - specs/database/schema.md
  - specs/001-hackathon-todo-monorepo/spec.md
  - specs/001-hackathon-todo-monorepo/checklists/requirements.md
  - docker-compose.yml
tests:
  - None (infrastructure setup - manual verification)
---

## Prompt

Initialize a full-stack monorepo structure for a project named 'hackathon-todo' based on the Spec-Kit and Claude Code integration guide.

Please perform the following steps:
1. Create the root directory structure including:
   - /.spec-kit/ (with config.yaml)
   - /specs/ (with subfolders: features, api, database, ui)
   - /frontend/ (Next.js placeholder)
   - /backend/ (FastAPI placeholder)

2. Create the Root CLAUDE.md: Include sections for Project Overview, Spec-Kit Structure, How to Use Specs (@specs/ reference rules), and Development Workflow (Backend first, then Frontend).

3. Create the Backend:
   - Generate /backend/CLAUDE.md with FastAPI, SQLModel, and project structure guidelines.
   - Create a basic FastAPI boilerplate (main.py, models.py, db.py).

4. Create the Frontend:
   - Generate /frontend/CLAUDE.md with Next.js 14 (App Router), TypeScript, and Tailwind patterns.
   - Create a basic Next.js file structure placeholder.

5. Initialize the Specs:
   - Create /specs/overview.md, /specs/features/task-crud.md, /specs/api/rest-endpoints.md, and /specs/database/schema.md using the provided Spec-Kit conventions.

6. Add a root docker-compose.yml to orchestrate the frontend and backend.

Refer to the Spec-Kit configuration where phases are defined (phase1-console, phase2-web, phase3-chatbot). implement this in my project

## Response snapshot

Created complete hackathon-todo monorepo structure with:

1. **Root Configuration**:
   - `.spec-kit/config.yaml` with phase1-console, phase2-web, phase3-chatbot definitions
   - Updated `CLAUDE.md` with Project Overview, Spec-Kit Structure, spec reference rules, and Backend-first workflow

2. **Backend (FastAPI)**:
   - `backend/CLAUDE.md` - Development guidelines
   - `backend/main.py` - FastAPI app with CORS, health endpoint
   - `backend/models.py` - SQLModel Task/User entities with enums
   - `backend/db.py` - Database session management
   - `backend/Dockerfile` and `requirements.txt`

3. **Frontend (Next.js 14)**:
   - `frontend/CLAUDE.md` - Development guidelines
   - `frontend/app/` - App Router structure (layout.tsx, page.tsx, globals.css)
   - `frontend/lib/api.ts` - Typed API client
   - Configuration files (package.json, tsconfig.json, tailwind.config.ts, Dockerfile)

4. **Specifications**:
   - `specs/overview.md` - Project overview with architecture diagram
   - `specs/features/task-crud.md` - Task CRUD feature spec
   - `specs/api/rest-endpoints.md` - Complete REST API contract
   - `specs/database/schema.md` - Database schema with ERD

5. **Infrastructure**:
   - `docker-compose.yml` - Backend, frontend, PostgreSQL, optional pgAdmin

6. **Feature Spec**:
   - `specs/001-hackathon-todo-monorepo/spec.md` - Full specification for this initialization
   - `specs/001-hackathon-todo-monorepo/checklists/requirements.md` - Quality validation passed

## Outcome

- ✅ Impact: Complete monorepo structure created with 23 files across backend, frontend, specs, and infrastructure
- 🧪 Tests: Manual verification required - run `uvicorn` for backend, `npm run dev` for frontend
- 📁 Files: 23 files created/modified (see files list above)
- 🔁 Next prompts: `/sp.plan` to create implementation plan, or `/sp.clarify` if refinements needed
- 🧠 Reflection: Comprehensive initialization completed; all checklist items pass; ready for development

## Evaluation notes (flywheel)

- Failure modes observed: None - all tasks completed successfully
- Graders run and results (PASS/FAIL): Manual checklist validation - PASS
- Prompt variant (if applicable): Standard /sp.specify flow
- Next experiment (smallest change to try): N/A - specification complete
