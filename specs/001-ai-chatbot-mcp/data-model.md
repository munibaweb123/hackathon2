# Data Model: AI Chatbot for Todo Management

**Date**: 2025-12-18
**Feature**: 001-ai-chatbot-mcp
**Source**: Feature specification and existing todo management system

## Entity Relationship Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                           User                                   │
│  (Better Auth managed - read-only in backend)                    │
├──────────────────────────────────────────────────────────────────┤
│  id: str (PK, Better Auth format)                                │
│  email: str (UNIQUE)                                             │
│  name: str?                                                      │
│  email_verified: datetime?                                       │
│  image: str? (avatar URL)                                        │
│  created_at: datetime                                            │
│  updated_at: datetime                                            │
└───────────────────────┬───────────────────┬─────────────────────┘
                        │ 1:N               │ 1:1
         ┌──────────────▼──────────┐   ┌────▼────────────────────┐
         │        Task             │   │    UserPreference       │
         ├─────────────────────────┤   ├─────────────────────────┤
         │ id: int (PK)            │   │ id: str (PK, UUID)      │
         │ title: str              │   │ user_id: str (FK→User)  │
         │ description: str?       │   │ theme: enum             │
         │ completed: bool         │   │ language: str           │
         │ priority: enum          │   │ notifications: enum     │
         │ due_date: datetime?     │   │ default_view: str       │
         │ user_id: str (FK→User)  │   │ show_completed: bool    │
         │ is_recurring: bool      │   │ work_hours: str         │
         │ recurrence_pattern: enum│   │ custom_settings: JSON   │
         │ recurrence_interval: int│   └─────────────────────────┘
         │ recurrence_end_date: dt │
         │ parent_task_id: int?    │
         │ created_at: datetime    │
         │ updated_at: datetime    │
         └───────────────┬─────────┘
                         │ 1:N
              ┌──────────▼──────────┐
              │      Reminder       │
              ├─────────────────────┤
              │ id: str (PK, UUID)  │
              │ task_id: int (FK)   │
              │ user_id: str (FK)   │
              │ reminder_time: dt   │
              │ reminder_type: enum │
              │ status: enum        │
              │ message: str?       │
              │ created_at: datetime│
              │ updated_at: datetime│
              └─────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                      Conversation                                │
├──────────────────────────────────────────────────────────────────┤
│  id: str (PK, UUID)                                             │
│  user_id: str (FK→User)                                         │
│  created_at: datetime                                           │
│  updated_at: datetime                                           │
└───────────────────────┬─────────────────────────────────────────┘
                        │ 1:N
         ┌──────────────▼──────────┐
         │        Message          │
         ├─────────────────────────┤
         │ id: str (PK, UUID)      │
         │ conversation_id: str (FK)│
         │ user_id: str (FK→User)  │
         │ role: enum (user/assistant/system) │
         │ content: str            │
         │ created_at: datetime    │
         │ tool_calls: JSON?       │
         │ tool_responses: JSON?   │
         └─────────────────────────┘
```

## Entities

### Conversation

Represents a chat session between user and AI assistant for todo management.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | str | PK, UUID | Unique conversation identifier |
| user_id | str | FK→User, NOT NULL | Owner of the conversation |
| created_at | datetime | NOT NULL | Conversation creation time |
| updated_at | datetime | NOT NULL | Last interaction time |

**Indexes**: user_id

### Message

Represents individual exchanges in a conversation with the AI assistant.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | str | PK, UUID | Unique message identifier |
| conversation_id | str | FK→Conversation, NOT NULL | Associated conversation |
| user_id | str | FK→User, NOT NULL | Message author |
| role | Role | NOT NULL | user/assistant/system |
| content | str | NOT NULL, max 10000 chars | Message text content |
| created_at | datetime | NOT NULL | Message creation time |
| tool_calls | JSON | nullable | List of tools called by AI |
| tool_responses | JSON | nullable | Results from tool calls |

**Indexes**: conversation_id, user_id, created_at

## Relationships

| From | To | Type | Description |
|------|-----|------|-------------|
| User | Conversation | 1:N | User owns multiple conversations |
| Conversation | Message | 1:N | Conversation contains multiple messages |
| User | Message | 1:N | User creates multiple messages |

## Enumerations

### Role
- `user` - Messages from the user
- `assistant` - Messages from the AI assistant
- `system` - System-generated messages

## Validation Rules

1. **Message content**: Required, max 10,000 characters
2. **Conversation ownership**: User can only access their own conversations
3. **Message role**: Must be one of the defined enum values
4. **User association**: All conversations and messages must be associated with a valid user
5. **Tool call format**: When present, must be valid JSON array of tool calls
6. **Tool response format**: When present, must be valid JSON array of tool results

## Integration with Existing Models

The new Conversation and Message entities integrate with the existing User and Task models to provide chatbot functionality while maintaining the existing todo management system's integrity. The AI agent will use MCP tools to interact with Task entities through the existing service layer.