# API Specification: REST Endpoints

**Version**: 1.0.0
**Base URL**: `http://localhost:8000`
**Created**: 2025-12-18

## Overview

RESTful API contract for the hackathon-todo application backend.

## Authentication

All task endpoints require authentication via JWT Bearer token.

```
Authorization: Bearer <access_token>
```

## Endpoints

### Health Check

```
GET /health
```

**Response**: `200 OK`
```json
{
  "status": "healthy"
}
```

---

### Tasks

#### List Tasks

```
GET /api/tasks
```

**Query Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| status | string | No | Filter by status |
| priority | string | No | Filter by priority |
| limit | int | No | Max results (default: 50) |
| offset | int | No | Pagination offset |

**Response**: `200 OK`
```json
{
  "items": [
    {
      "id": 1,
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "status": "pending",
      "priority": "medium",
      "due_date": "2025-12-20T00:00:00Z",
      "owner_id": 1,
      "created_at": "2025-12-18T10:00:00Z",
      "updated_at": "2025-12-18T10:00:00Z",
      "completed_at": null
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

---

#### Get Task

```
GET /api/tasks/{id}
```

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| id | int | Task ID |

**Response**: `200 OK`
```json
{
  "id": 1,
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "status": "pending",
  "priority": "medium",
  "due_date": "2025-12-20T00:00:00Z",
  "owner_id": 1,
  "created_at": "2025-12-18T10:00:00Z",
  "updated_at": "2025-12-18T10:00:00Z",
  "completed_at": null
}
```

**Errors**:
- `404 Not Found`: Task does not exist

---

#### Create Task

```
POST /api/tasks
```

**Request Body**:
```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "priority": "medium",
  "due_date": "2025-12-20T00:00:00Z"
}
```

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| title | string | Yes | 1-200 chars |
| description | string | No | Max 2000 chars |
| status | string | No | pending, in_progress, completed, cancelled |
| priority | string | No | low, medium, high, urgent (default: medium) |
| due_date | string | No | ISO 8601 datetime |

**Response**: `201 Created`
```json
{
  "id": 1,
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "status": "pending",
  "priority": "medium",
  "due_date": "2025-12-20T00:00:00Z",
  "owner_id": 1,
  "created_at": "2025-12-18T10:00:00Z",
  "updated_at": "2025-12-18T10:00:00Z",
  "completed_at": null
}
```

**Errors**:
- `400 Bad Request`: Validation error
- `422 Unprocessable Entity`: Invalid field values

---

#### Update Task

```
PATCH /api/tasks/{id}
```

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| id | int | Task ID |

**Request Body** (all fields optional):
```json
{
  "title": "Buy groceries and supplies",
  "status": "in_progress",
  "priority": "high"
}
```

**Response**: `200 OK`
```json
{
  "id": 1,
  "title": "Buy groceries and supplies",
  "description": "Milk, eggs, bread",
  "status": "in_progress",
  "priority": "high",
  "due_date": "2025-12-20T00:00:00Z",
  "owner_id": 1,
  "created_at": "2025-12-18T10:00:00Z",
  "updated_at": "2025-12-18T11:00:00Z",
  "completed_at": null
}
```

**Errors**:
- `404 Not Found`: Task does not exist
- `403 Forbidden`: Not task owner

---

#### Delete Task

```
DELETE /api/tasks/{id}
```

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| id | int | Task ID |

**Response**: `204 No Content`

**Errors**:
- `404 Not Found`: Task does not exist
- `403 Forbidden`: Not task owner

---

### Authentication

#### Register

```
POST /api/auth/register
```

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "name": "John Doe"
}
```

**Response**: `201 Created`
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2025-12-18T10:00:00Z"
}
```

---

#### Login

```
POST /api/auth/login
```

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response**: `200 OK`
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

---

#### Logout

```
POST /api/auth/logout
```

**Response**: `200 OK`
```json
{
  "message": "Successfully logged out"
}
```

---

## Error Response Format

All errors follow this format:

```json
{
  "detail": "Error message describing what went wrong",
  "code": "ERROR_CODE"
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| VALIDATION_ERROR | 400 | Request validation failed |
| UNAUTHORIZED | 401 | Missing or invalid authentication |
| FORBIDDEN | 403 | Insufficient permissions |
| NOT_FOUND | 404 | Resource not found |
| CONFLICT | 409 | Resource already exists |
| INTERNAL_ERROR | 500 | Server error |
