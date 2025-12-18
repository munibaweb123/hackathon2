# Hackathon Todo - Project Overview

## Description

A full-stack todo application built with a multi-phase development approach, demonstrating modern web development practices with FastAPI backend and Next.js frontend.

## Project Phases

### Phase 1: Console Application (Completed)

Basic console-based todo application with:
- In-memory task storage
- JSON file persistence
- Rich console formatting
- Basic CRUD operations

### Phase 2: Web Application (In Progress)

Full-stack web application featuring:
- RESTful API with FastAPI
- Next.js 14 frontend with App Router
- User authentication with Better Auth
- PostgreSQL/SQLite database with SQLModel
- Responsive UI with Tailwind CSS

### Phase 3: Chatbot Integration (Planned)

AI-powered task management:
- Natural language processing for task creation
- Smart reminders and scheduling
- Voice command support
- Integration with LLMs

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend                              │
│                    (Next.js 14 + TypeScript)                 │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTP/REST
┌─────────────────────────▼───────────────────────────────────┐
│                        Backend                               │
│                    (FastAPI + Python)                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Routers   │  │  Services   │  │    Auth (JWT)       │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────┬───────────────────────────────────┘
                          │ SQLModel/ORM
┌─────────────────────────▼───────────────────────────────────┐
│                       Database                               │
│              (PostgreSQL / SQLite)                          │
└─────────────────────────────────────────────────────────────┘
```

## Key Features

- **Task Management**: Create, read, update, delete tasks
- **Priority System**: Low, Medium, High, Urgent priorities
- **Status Tracking**: Pending, In Progress, Completed, Cancelled
- **Due Dates**: Optional deadline assignment
- **User Authentication**: Secure login and registration
- **Multi-user Support**: Each user has their own tasks

## Specifications Index

- **Features**: `specs/features/`
  - [Task CRUD](features/task-crud.md) - Core task operations
- **API**: `specs/api/`
  - [REST Endpoints](api/rest-endpoints.md) - API contract
- **Database**: `specs/database/`
  - [Schema](database/schema.md) - Data model
- **UI**: `specs/ui/`
  - Component specifications (coming soon)

## Development Guidelines

See individual CLAUDE.md files in:
- `/backend/CLAUDE.md` - Backend development guidelines
- `/frontend/CLAUDE.md` - Frontend development guidelines
- `/CLAUDE.md` - Root project guidelines
