---
id: 0006
title: Create Better Auth Skills
stage: misc
date: 2025-12-10
surface: agent
model: claude-opus-4-5-20251101
feature: 003-advanced-todo-features
branch: 003-advanced-todo-features
user: user
command: direct-request
labels: ["skills", "authentication", "better-auth", "api", "slash-commands"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/commands/auth.signup.md
  - .claude/commands/auth.signin.md
  - .claude/commands/auth.validateToken.md
  - .claude/commands/auth.config.md
tests:
  - N/A (documentation/skill files only)
---

## Prompt

create skill for {
  "name": "better_auth_skill",
  "description": "Skill for handling user authentication using Better Auth API.",
  "type": "api",
  "config": {
    "baseUrl": "https://your-better-auth-url.com",
    "endpoints": {
      "signup": {
        "method": "POST",
        "path": "/auth/signup"
      },
      "signin": {
        "method": "POST",
        "path": "/auth/signin"
      },
      "validateToken": {
        "method": "POST",
        "path": "/auth/validate"
      }
    }
  }
}

## Response snapshot

Created 4 Claude Code slash command skills for Better Auth API authentication:

1. `/auth.signup` - Register new user (POST /auth/signup)
2. `/auth.signin` - Authenticate user (POST /auth/signin)
3. `/auth.validateToken` - Validate session token (POST /auth/validate)
4. `/auth.config` - Configure base URL and manage tokens

Each skill includes:
- Endpoint details and method
- Request/response schemas
- curl command templates
- Error handling guidance
- Security best practices
- Usage examples

Integration with FastAPI backend documented in auth.config.

## Outcome

- ✅ Impact: Added 4 new slash commands for Better Auth API interaction
- 🧪 Tests: N/A - documentation/template files
- 📁 Files: 4 files created in .claude/commands/
- 🔁 Next prompts: Configure actual baseUrl, integrate with FastAPI skills
- 🧠 Reflection: Auth skills complement FastAPI skills for full authenticated workflow

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Add token refresh endpoint skill
