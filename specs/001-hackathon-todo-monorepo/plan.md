# Implementation Plan: Hackathon Todo Monorepo Initialization

**Branch**: `001-hackathon-todo-monorepo` | **Date**: 2025-12-18 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-hackathon-todo-monorepo/spec.md`

## Summary

Restructure the existing hackathon-todo project into a proper monorepo structure. The project already has a working web application in `todo_web/` that needs to be migrated to the new `backend/` and `frontend/` directories. This involves moving existing code, updating configuration files, and ensuring the docker-compose orchestration works with the new structure.

## Technical Context

**Language/Version**: Python 3.13+ (backend), TypeScript/Node.js 20+ (frontend)
**Primary Dependencies**: FastAPI, SQLModel, Better Auth, Next.js 14, Tailwind CSS
**Storage**: SQLite (development), PostgreSQL (production via docker-compose)
**Testing**: pytest (backend), Jest/Vitest (frontend)
**Target Platform**: Linux server (Docker), macOS/Windows (local dev)
**Project Type**: Web application (monorepo with frontend + backend)
**Performance Goals**: Medium scale (hundreds of users, thousands of tasks per user); API pagination required
**Constraints**: Better Auth handles frontend sessions; backend validates JWT tokens
**Scale/Scope**: Full-stack todo app with auth, tasks, reminders, preferences

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Basic Task Management | ✅ PASS | Existing backend has full CRUD for tasks |
| II. Task Organization & Usability | ✅ PASS | Priority, categories, search, filter, sort implemented |
| III. Advanced Task Automation | ✅ PASS | Recurring tasks and reminders implemented |

**Gate Status**: PASSED - All constitution principles satisfied by existing implementation.

## Project Structure

### Documentation (this feature)

```text
specs/001-hackathon-todo-monorepo/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (created by /sp.tasks)
```

### Source Code (repository root)

**Current Structure (to migrate FROM):**
```text
todo_web/
├── backend/             # Existing FastAPI backend (45+ Python files)
│   ├── app/
│   │   ├── api/         # Route handlers (tasks, auth, reminders, etc.)
│   │   ├── auth/        # Authentication middleware & utils
│   │   ├── core/        # Config, database, security, JWKS
│   │   ├── models/      # SQLModel entities
│   │   ├── schemas/     # Pydantic schemas
│   │   ├── services/    # Business logic
│   │   └── utils/       # Utilities (recurrence, reminder scheduler)
│   └── tests/
└── todo_web_frontend/   # Existing Next.js frontend (55+ files)
    └── src/
        ├── app/         # App Router pages
        ├── components/  # UI components (auth, tasks, layout, etc.)
        ├── hooks/       # Custom hooks (use-auth, use-tasks)
        ├── lib/         # Utilities (auth-client, api-client)
        ├── services/    # Service layer
        └── types/       # TypeScript types
```

**Target Structure (to migrate TO):**
```text
backend/                 # Monorepo backend location
├── app/                 # Migrated from todo_web/backend/app
│   ├── api/
│   ├── auth/
│   ├── core/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   └── utils/
├── tests/
├── .env
├── requirements.txt
├── pyproject.toml
└── CLAUDE.md

frontend/                # Monorepo frontend location
├── src/                 # Migrated from todo_web/todo_web_frontend/src
│   ├── app/
│   ├── components/
│   ├── hooks/
│   ├── lib/
│   ├── services/
│   └── types/
├── public/
├── .env.local
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── CLAUDE.md

src/                     # Preserved console app (Phase 1)
└── todo_app/

.spec-kit/
└── config.yaml

specs/
├── overview.md
├── features/
├── api/
├── database/
└── ui/

docker-compose.yml
```

**Structure Decision**: Web application structure with separate backend/ and frontend/ directories. The existing todo_web/ contents will be migrated to root-level directories. Console app (src/todo_app) remains as Phase 1 artifact.

## Migration Strategy

### Phase 1: Backend Migration
1. Move `todo_web/backend/app/` → `backend/app/`
2. Move `todo_web/backend/tests/` → `backend/tests/`
3. Copy configuration files (.env, requirements.txt, pyproject.toml)
4. Update imports if necessary (should be relative, minimal changes)
5. Update docker-compose.yml to use new path

### Phase 2: Frontend Migration
1. Move `todo_web/todo_web_frontend/src/` → `frontend/src/`
2. Move `todo_web/todo_web_frontend/public/` → `frontend/public/`
3. Copy configuration files (package.json, tsconfig.json, etc.)
4. Update .env.local with correct API URL
5. Update docker-compose.yml to use new path

### Phase 3: Cleanup
1. Remove `todo_web/` directory after verification
2. Update CLAUDE.md files with accurate paths
3. Verify docker-compose up works

## Complexity Tracking

No constitution violations requiring justification.

## Dependencies

| Component | Dependency | Notes |
|-----------|------------|-------|
| Backend | SQLModel, FastAPI, python-jose | Already installed in existing backend |
| Frontend | Better Auth, Next.js 14 | Already configured in existing frontend |
| Auth Flow | Better Auth (frontend) → JWT validation (backend) | Already implemented |
| Database | SQLite (dev) / PostgreSQL (docker) | Already configured |

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Import path breakage | Medium | Use relative imports; test after move |
| .env files not copied | High | Explicit step in migration tasks |
| Docker context issues | Medium | Update build contexts in docker-compose |
| Better Auth config paths | Medium | Update BETTER_AUTH_URL in frontend .env |

## Next Steps

1. Run `/sp.tasks` to generate detailed migration tasks
2. Execute migration in order: backend → frontend → cleanup
3. Verify with `docker-compose up` and manual testing
