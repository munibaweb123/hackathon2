---
id: 0002
title: AI Chatbot Plan
stage: plan
date: 2025-12-18
surface: agent
model: claude-opus-4-5-20251101
feature: 001-ai-chatbot-mcp
branch: 001-ai-chatbot-mcp
user: user
command: /sp.plan "use this reference for chatkit \"# ChatKit Custom Backend — Python Reference\\n\\nThis document supports the `openai-chatkit-backend-python` Skill.\\nIt standardizes how you implement and reason about a **custom ChatKit backend**\\nin Python, powered by the **OpenAI Agents SDK** (and optionally Gemini via an\\nOpenAI-compatible endpoint).\\n\\nUse this as the **high-authority reference** for:\\n- Folder structure and separation of concerns\\n- Environment variables and model factory behavior\\n- Expected HTTP endpoints for ChatKit\\n- How ChatKit events are handled in the backend\\n- How to integrate Agents SDK (agents, tools, runners)\\n- Streaming, auth, security, and troubleshooting\\n\\n---\\n\\n## 1. Recommended Folder Structure\\n\\nA clean project structure keeps ChatKit transport logic separate from the\\nAgents SDK logic and business tools.\\n\\n```text\\nbackend/\\n  main.py                # FastAPI / Flask / Django entry\\n  env.py                 # env loading, settings\\n  chatkit/\\n    __init__.py\\n    router.py            # ChatKit event routing + handlers\\n    upload.py            # Upload endpoint helpers\\n    streaming.py         # SSE helpers (optional)\\n    types.py             # Typed helpers for ChatKit events (optional)\\n  agents/\\n    __init__.py\\n    factory.py           # create_model() lives here\\n    base_agent.py        # base configuration or utilities\\n    support_agent.py     # example specialized agent\\n    tools/\\n      __init__.py\\n      db_tools.py        # DB-related tools\\n      erp_tools.py       # ERP-related tools\\n```\\n\\n**Key idea:**  \\n- `chatkit/` knows about HTTP requests/responses and ChatKit event shapes.  \\n- `agents/` knows about models, tools, and reasoning.  \\n- Nothing in `agents/` should know that ChatKit exists.\\n\\n---\\n\\n## 2. Environment Variables & Model Factory Contract\\n\\nAll model selection must go through a **single factory function** in\\n`agents/factory.py`. This keeps your backend flexible and prevents\\nChatKit-specific code from hard-coding model choices.\\n\\n### 2.1 Required/Recommended Env Vars\\n\\n```text\\nLLM_PROVIDER=openai or gemini\\n\\n# OpenAI\\nOPENAI_API_KEY=sk-...\\nOPENAI_DEFAULT_MODEL=gpt-4.1-mini\\n\\n# Gemini via OpenAI-compatible endpoint\\nGEMINI_API_KEY=...\\nGEMINI_DEFAULT_MODEL=gemini-2.5-flash\\n\\n# Optional\\nLOG_LEVEL=INFO\\n```\\n\\n### 2.2 Factory Contract\\n\\n```python\\n# agents/factory.py\\n\\ndef create_model():\\n    \"\"\"Return a model object compatible with the Agents SDK.\\n\\n    - Uses LLM_PROVIDER to decide provider.\\n    - Uses provider-specific env vars for keys and defaults.\\n    - Returns a model usable in Agent(model=...).\\n    \"\"\"\\n```\\n\\nRules:\\n\\n- If `LLM_PROVIDER` is `\"gemini\"`, use an OpenAI-compatible client with:\\n  `base_url = \"https://generativelanguage.googleapis.com/v1beta/openai/\"`.\\n- If it is `\"openai\"` or unset, use OpenAI default with `OPENAI_API_KEY`.\\n- Never instantiate models directly inside ChatKit handlers; always call\\n  `create_model()`.\\n\\n---\\n\\n## 3. Required HTTP Endpoints for ChatKit\\n\\nIn **custom backend** mode, the frontend ChatKit client is configured to call\\nyour backend instead of OpenAI’s hosted workflows.\\n\\nAt minimum, the backend should provide:\\n\\n### 3.1 Main Chat Endpoint\\n\\n```http\\nPOST /chatkit/api\\n```\\n\\nResponsibilities:\\n\\n- Authenticate the incoming request (session / JWT / cookie).\\n- Parse the incoming ChatKit event (e.g., user message, action).\\n- Create or reuse an appropriate agent (using `create_model()`).\\n- Invoke the Agents SDK (Agent + Runner).\\n- Return a response in a shape compatible with ChatKit expectations\\n  (usually a JSON object / stream that represents the assistant’s reply).\\n\\n### 3.2 Upload Endpoint (Optional)\\n\\nIf the frontend config uses a **direct upload strategy**, you’ll also need:\\n\\n```http\\nPOST /chatkit/api/upload\\n```\\n\\nResponsibilities:\\n\\n- Accept file uploads (`multipart/form-data`).\\n- Store the file (local disk, S3, etc.).\\n- Return a JSON body with a URL and any metadata ChatKit expects\\n  (e.g., `{ \"url\": \"https://cdn.example.com/path/file.pdf\" }`).\\n\\nThe frontend will include this URL in messages or pass it as context.\\n\\n---\\n\\n## 4. ChatKit Event Handling (Conceptual)\\n\\nChatKit will deliver events to your backend. The exact schema is documented\\nin the official ChatKit Custom Backends docs, but conceptually you will see\\npatterns like:\\n\\n- A **user message** event with text and maybe references to files.\\n- An **action invocation** event when the user clicks a button or submits a form.\\n- System or housekeeping events that can usually be ignored or logged.\\n\\nA typical handler shape in `chatkit/router.py` might be:\\n\\n```python\\nasync def handle_event(event: dict) -> dict:\\n    event_type = event.get(\"type\")\\n\\n    if event_type == \"user_message\":\\n        return await handle_user_message(event)\\n    elif event_type == \"action_invoked\":\\n        return await handle_action(event)\\n    else:\\n        # Log and return a no-op or simple message\\n        return {\"type\": \"message\", \"content\": \"Unsupported event type.\"}\\n```\\n\\nThen inside `handle_user_message`, you’ll:\\n\\n1. Extract the user’s text.\\n2. Build or fetch context (user id, tenant id, conversation state).\\n3. Call the appropriate Agent with the user’s input.\\n4. Return the agent’s output mapped into ChatKit’s expected structure.\\n\\n---\\n\\n## 5. Agents SDK Integration Rules\\n\\nAll reasoning and tool execution should be done via the **Agents SDK**,\\nnot via direct `chat.completions` calls.\\n\\n### 5.1 Basic Agent Execution\\n\\n```python\\nfrom agents import Agent, Runner\\nfrom agents.factory import create_model\\n\\ndef run_simple_agent(user_text: str) -> str:\\n    agent = Agent(\\n        name=\"chatkit-backend-agent\",\\n        model=create_model(),\\n        instructions=(\\n            \"You are the backend agent behind a ChatKit UI. \"\\n            \"Respond concisely and be robust to noisy input.\"\\n        ),\\n    )\\n    result = Runner.run_sync(starting_agent=agent, input=user_text)\\n    return result.final_output\\n```\\n\\n### 5.2 Tools Integration\\n\\nTools should be defined in `agents/tools/` and attached to agents where needed.\\n\\n- Use the Agents SDK’s tool decorator/pattern.\\n- Keep tools focused and side-effect-aware (e.g., read-only vs write).\\n\\nAgents like `support_agent.py` may load tools such as:\\n\\n- `get_employee_record`\\n- `create_support_ticket`\\n- `fetch_invoice_status`\\n\\nChatKit itself does not know about tools; it only sees the agent’s messages.\\n\\n---\\n\\n## 6. Streaming Responses\\n\\nFor better UX, you may choose to stream responses to ChatKit using\\nServer-Sent Events (SSE) or an equivalent streaming mechanism supported\\nby your framework.\\n\\nGeneral rules:\\n\\n- The handler for `/chatkit/api` should return a streaming response.\\n- Each chunk should be formatted consistently (e.g., `data: {...}\\n\\n`).\\n- The final chunk should clearly indicate completion (e.g., `done: true`).\\n\\nYou may wrap the Agents SDK call in a generator that yields partial tokens\\nor partial messages as they are produced.\\n\\n---\\n\\n## 7. Auth, Security, and Tenant Context\\n\\n### 7.1 Auth\\n\\n- Every request to `/chatkit/api` and `/chatkit/api/upload` must be authenticated.\\n- Common patterns: bearer tokens, session cookies, signed headers.\\n- The backend must **never** return API keys or other secrets to the browser.\\n\\n### 7.2 Tenant / User Context\\n\\nOften you’ll want to include:\\n\\n- `user_id`\\n- `tenant_id` / `company_id`\\n- user’s role (e.g. `employee`, `manager`, `admin`)\\n\\ninto the agent’s instructions or tool calls. For example:\\n\\n```python\\ninstructions = f\"\"\"\\nYou are the support agent for tenant {tenant_id}.\\nYou must respect role-based access and never leak other tenants' data.\\nCurrent user: {user_id}, role: {role}.\\n\"\"\"\\n```\\n\\n### 7.3 Domain Allowlist\\n\\nIf the ChatKit widget renders blank or fails silently, verify:\\n\\n- The frontend origin domain is included in the OpenAI dashboard allowlist.\\n- The `domainKey` configured on the frontend matches the backend’s expectations.\\n\\n---\\n\\n## 8. Logging and Troubleshooting\\n\\n### 8.1 What to Log\\n\\n- Incoming ChatKit event types and minimal metadata (no secrets).\\n- Auth failures (excluding raw tokens).\\n- Agents SDK errors (model not found, invalid arguments, tool exceptions).\\n- File upload failures.\\n\\n### 8.2 Common Failure Modes\\n\\n- **Blank ChatKit UI**  \\n  → Domain not allowlisted or domainKey mismatch.\\n\\n- **“Loading…” never completes**  \\n  → Backend did not return a valid response or streaming never sends final chunk.\\n\\n- **Model / provider errors**  \\n  → Wrong `LLM_PROVIDER`, incorrect API key, or wrong base URL.\\n\\n- **Multipart upload errors**  \\n  → Upload endpoint doesn’t accept `multipart/form-data` or returns wrong JSON shape.\\n\\nHaving structured logs (JSON logs) greatly speeds up debugging.\\n\\n---\\n\\n## 9. Evolution and Versioning\\n\\nOver time, ChatKit and the Agents SDK may evolve. To keep this backend\\nmaintainable:\\n\\n- Treat the official ChatKit Custom Backends docs as the top-level source of truth.\\n- Treat `agents/factory.py` as the single place to update model/provider logic.\\n- When updating the Agents SDK:\\n  - Verify that Agent/Runner APIs have not changed.\\n  - Update tools to match any new signatures or capabilities.\\n\\nWhen templates or examples drift from the docs, prefer the **docs** and\\nupdate the local files accordingly.\\n\""
labels: ["ai", "chatbot", "mcp", "planning", "openapi"]
links:
  spec: /specs/001-ai-chatbot-mcp/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - /specs/001-ai-chatbot-mcp/plan.md
 - /specs/001-ai-chatbot-mcp/research.md
 - /specs/001-ai-chatbot-mcp/data-model.md
 - /specs/001-ai-chatbot-mcp/quickstart.md
 - /specs/001-ai-chatbot-mcp/contracts/openapi.yaml
tests:
 - constitution check passed
 - research completed
 - data model defined
 - api contracts created
---

## Prompt

use this reference for chatkit "# ChatKit Custom Backend — Python Reference

This document supports the `openai-chatkit-backend-python` Skill.
It standardizes how you implement and reason about a **custom ChatKit backend**
in Python, powered by the **OpenAI Agents SDK** (and optionally Gemini via an
OpenAI-compatible endpoint).

Use this as the **high-authority reference** for:
- Folder structure and separation of concerns
- Environment variables and model factory behavior
- Expected HTTP endpoints for ChatKit
- How ChatKit events are handled in the backend
- How to integrate Agents SDK (agents, tools, runners)
- Streaming, auth, security, and troubleshooting

---

## 1. Recommended Folder Structure

A clean project structure keeps ChatKit transport logic separate from the
Agents SDK logic and business tools.

```text
backend/
  main.py                # FastAPI / Flask / Django entry
  env.py                 # env loading, settings
  chatkit/
    __init__.py
    router.py            # ChatKit event routing + handlers
    upload.py            # Upload endpoint helpers
    streaming.py         # SSE helpers (optional)
    types.py             # Typed helpers for ChatKit events (optional)
  agents/
    __init__.py
    factory.py           # create_model() lives here
    base_agent.py        # base configuration or utilities
    support_agent.py     # example specialized agent
    tools/
      __init__.py
      db_tools.py        # DB-related tools
      erp_tools.py       # ERP-related tools
```

**Key idea:**
- `chatkit/` knows about HTTP requests/responses and ChatKit event shapes.
- `agents/` knows about models, tools, and reasoning.
- Nothing in `agents/` should know that ChatKit exists.

---

## 2. Environment Variables & Model Factory Contract

All model selection must go through a **single factory function** in
`agents/factory.py`. This keeps your backend flexible and prevents
ChatKit-specific code from hard-coding model choices.

### 2.1 Required/Recommended Env Vars

```text
LLM_PROVIDER=openai or gemini

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_DEFAULT_MODEL=gpt-4.1-mini

# Gemini via OpenAI-compatible endpoint
GEMINI_API_KEY=...
GEMINI_DEFAULT_MODEL=gemini-2.5-flash

# Optional
LOG_LEVEL=INFO
```

### 2.2 Factory Contract

```python
# agents/factory.py

def create_model():
    """Return a model object compatible with the Agents SDK.

    - Uses LLM_PROVIDER to decide provider.
    - Uses provider-specific env vars for keys and defaults.
    - Returns a model usable in Agent(model=...).
    """
```

Rules:

- If `LLM_PROVIDER` is `"gemini"`, use an OpenAI-compatible client with:
  `base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"`.
- If it is `"openai"` or unset, use OpenAI default with `OPENAI_API_KEY`.
- Never instantiate models directly inside ChatKit handlers; always call
  `create_model()`.

---

## 3. Required HTTP Endpoints for ChatKit

In **custom backend** mode, the frontend ChatKit client is configured to call
your backend instead of OpenAI's hosted workflows.

At minimum, the backend should provide:

### 3.1 Main Chat Endpoint

```http
POST /chatkit/api
```

Responsibilities:

- Authenticate the incoming request (session / JWT / cookie).
- Parse the incoming ChatKit event (e.g., user message, action).
- Create or reuse an appropriate agent (using `create_model()`).
- Invoke the Agents SDK (Agent + Runner).
- Return a response in a shape compatible with ChatKit expectations
  (usually a JSON object / stream that represents the assistant's reply).

### 3.2 Upload Endpoint (Optional)

If the frontend config uses a **direct upload strategy**, you'll also need:

```http
POST /chatkit/api/upload
```

Responsibilities:

- Accept file uploads (`multipart/form-data`).
- Store the file (local disk, S3, etc.).
- Return a JSON body with a URL and any metadata ChatKit expects
  (e.g., `{ "url": "https://cdn.example.com/path/file.pdf" }`).

The frontend will include this URL in messages or pass it as context.

---

## 4. ChatKit Event Handling (Conceptual)

ChatKit will deliver events to your backend. The exact schema is documented
in the official ChatKit Custom Backends docs, but conceptually you will see
patterns like:

- A **user message** event with text and maybe references to files.
- An **action invocation** event when the user clicks a button or submits a form.
- System or housekeeping events that can usually be ignored or logged.

A typical handler shape in `chatkit/router.py` might be:

```python
async def handle_event(event: dict) -> dict:
    event_type = event.get("type")

    if event_type == "user_message":
        return await handle_user_message(event)
    elif event_type == "action_invoked":
        return await handle_action(event)
    else:
        # Log and return a no-op or simple message
        return {"type": "message", "content": "Unsupported event type."}
```

Then inside `handle_user_message`, you'll:

1. Extract the user's text.
2. Build or fetch context (user id, tenant id, conversation state).
3. Call the appropriate Agent with the user's input.
4. Return the agent's output mapped into ChatKit's expected structure.

---

## 5. Agents SDK Integration Rules

All reasoning and tool execution should be done via the **Agents SDK**,
not via direct `chat.completions` calls.

### 5.1 Basic Agent Execution

```python
from agents import Agent, Runner
from agents.factory import create_model

def run_simple_agent(user_text: str) -> str:
    agent = Agent(
        name="chatkit-backend-agent",
        model=create_model(),
        instructions=(
            "You are the backend agent behind a ChatKit UI. "
            "Respond concisely and be robust to noisy input."
        ),
    )
    result = Runner.run_sync(starting_agent=agent, input=user_text)
    return result.final_output
```

### 5.2 Tools Integration

Tools should be defined in `agents/tools/` and attached to agents where needed.

- Use the Agents SDK's tool decorator/pattern.
- Keep tools focused and side-effect-aware (e.g., read-only vs write).

Agents like `support_agent.py` may load tools such as:

- `get_employee_record`
- `create_support_ticket`
- `fetch_invoice_status`

ChatKit itself does not know about tools; it only sees the agent's messages.

---

## 6. Streaming Responses

For better UX, you may choose to stream responses to ChatKit using
Server-Sent Events (SSE) or an equivalent streaming mechanism supported
by your framework.

General rules:

- The handler for `/chatkit/api` should return a streaming response.
- Each chunk should be formatted consistently (e.g., `data: {...}\n\n`).
- The final chunk should clearly indicate completion (e.g., `done: true`).

You may wrap the Agents SDK call in a generator that yields partial tokens
or partial messages as they are produced.

---

## 7. Auth, Security, and Tenant Context

### 7.1 Auth

- Every request to `/chatkit/api` and `/chatkit/api/upload` must be authenticated.
- Common patterns: bearer tokens, session cookies, signed headers.
- The backend must **never** return API keys or other secrets to the browser.

### 7.2 Tenant / User Context

Often you'll want to include:

- `user_id`
- `tenant_id` / `company_id`
- user's role (e.g. `employee`, `manager`, `admin`)

into the agent's instructions or tool calls. For example:

```python
instructions = f"""
You are the support agent for tenant {tenant_id}.
You must respect role-based access and never leak other tenants' data.
Current user: {user_id}, role: {role}.
"""
```

### 7.3 Domain Allowlist

If the ChatKit widget renders blank or fails silently, verify:

- The frontend origin domain is included in the OpenAI dashboard allowlist.
- The `domainKey` configured on the frontend matches the backend's expectations.

---

## 8. Logging and Troubleshooting

### 8.1 What to Log

- Incoming ChatKit event types and minimal metadata (no secrets).
- Auth failures (excluding raw tokens).
- Agents SDK errors (model not found, invalid arguments, tool exceptions).
- File upload failures.

### 8.2 Common Failure Modes

- **Blank ChatKit UI**
  → Domain not allowlisted or domainKey mismatch.

- **"Loading…" never completes**
  → Backend did not return a valid response or streaming never sends final chunk.

- **Model / provider errors**
  → Wrong `LLM_PROVIDER`, incorrect API key, or wrong base URL.

- **Multipart upload errors**
  → Upload endpoint doesn't accept `multipart/form-data` or returns wrong JSON shape.

Having structured logs (JSON logs) greatly speeds up debugging.

---

## 9. Evolution and Versioning

Over time, ChatKit and the Agents SDK may evolve. To keep this backend
maintainable:

- Treat the official ChatKit Custom Backends docs as the top-level source of truth.
- Treat `agents/factory.py` as the single place to update model/provider logic.
- When updating the Agents SDK:
  - Verify that Agent/Runner APIs have not changed.
  - Update tools to match any new signatures or capabilities.

When templates or examples drift from the docs, prefer the **docs** and
update the local files accordingly.

"

## Response snapshot

Successfully created the implementation plan for the AI Chatbot for Todo Management feature with the following artifacts:

1. **Implementation Plan** (plan.md): Comprehensive plan detailing the technical context, architecture, and project structure for the AI chatbot using MCP server architecture and OpenAI Agents SDK.

2. **Research Document** (research.md): Detailed research covering technology stack decisions, architecture patterns, integration points, performance considerations, and security aspects.

3. **Data Model** (data-model.md): Entity relationship diagram and detailed specifications for Conversation and Message entities that integrate with existing User and Task models.

4. **Quickstart Guide** (quickstart.md): Complete setup instructions for local development and Docker deployment, including environment variables, project structure, and usage examples.

5. **API Contracts** (contracts/openapi.yaml): OpenAPI specification for the chatbot API endpoints, including conversation management and message processing.

The plan follows the ChatKit reference architecture with proper separation of concerns between transport layer (chatkit/) and business logic (agents/). It incorporates MCP (Model Context Protocol) tools for stateless task operations while maintaining conversation state in the database.

Key technical decisions include:
- Using OpenAI Agents SDK with MCP tools for AI reasoning and task operations
- Implementing stateless tools with database persistence
- Integrating with existing todo management system
- Using Better Auth for user authentication

All constitution principles were verified and passed during the planning phase.

## Outcome

- ✅ Impact: Created comprehensive implementation plan with all required artifacts for AI chatbot feature
- 🧪 Tests: Constitution check passed, research completed, data model defined, API contracts created
- 📁 Files: Created plan.md, research.md, data-model.md, quickstart.md, and openapi.yaml contracts
- 🔁 Next prompts: Ready for task generation phase with `/sp.tasks`
- 🧠 Reflection: Successfully applied ChatKit reference architecture to create well-structured plan with clear separation of concerns

## Evaluation notes (flywheel)

- Failure modes observed: None - planning phase completed successfully
- Graders run and results (PASS/FAIL): PASS - all validation checks passed including constitution check
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Proceed to task generation phase with `/sp.tasks`
