# Data Model: Better Auth + FastAPI JWT Integration

## Entities

### User
- **Fields**:
  - id: string (unique identifier from Better Auth)
  - email: string (user's email address)
  - name: string (optional, user's display name)
  - created_at: datetime (when user account was created)
  - updated_at: datetime (when user account was last updated)
- **Relationships**: One-to-many with Task entities
- **Validation**: Email format validation, required fields

### JWT Token
- **Fields**:
  - token: string (the JWT token string)
  - user_id: string (embedded in token payload)
  - issuer: string (Better Auth service)
  - issued_at: datetime (when token was issued)
  - expires_at: datetime (token expiration time)
  - claims: object (user identity information)
- **State transitions**: Valid → Expired when expiration time is reached

### Task
- **Fields**:
  - id: string (unique identifier)
  - title: string (task title)
  - description: string (optional task description)
  - completed: boolean (task completion status)
  - user_id: string (foreign key to User)
  - created_at: datetime (when task was created)
  - updated_at: datetime (when task was last updated)
  - due_date: datetime (optional due date)
- **Relationships**: Many-to-one with User entities
- **Validation**: Title is required, user_id must match authenticated user
- **State transitions**: Pending → Completed when toggled

## Authentication Flow Data Requirements

### Authenticated Request
- **Fields**:
  - user_id: string (extracted from JWT token)
  - token_valid: boolean (verification status)
  - permissions: array (user permissions/roles)
  - request_timestamp: datetime (when request was made)

### Auth Error Response
- **Fields**:
  - error_code: string (e.g., "INVALID_TOKEN", "TOKEN_EXPIRED", "UNAUTHORIZED")
  - message: string (human-readable error message)
  - timestamp: datetime (when error occurred)
  - request_id: string (for debugging correlation)