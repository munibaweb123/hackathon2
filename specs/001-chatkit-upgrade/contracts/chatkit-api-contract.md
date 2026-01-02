# ChatKit API Contracts

## Overview
This document defines the API contracts for the ChatKit implementation in the todo application, following OpenAPI 3.0 specification patterns.

## Base Server Interface Contract

### ChatKitServer Interface
```python
class ChatKitServer:
    async def respond(self, thread_id: str, input: str, user_id: str) -> dict:
        """
        Handle user input and generate response with widgets.

        Args:
            thread_id: Unique identifier for the conversation thread
            input: User's input message
            user_id: Unique identifier for the authenticated user

        Returns:
            dict: Response containing status and any immediate data
        """
        pass

    async def action(self, thread_id: str, action: dict, user_id: str) -> dict:
        """
        Handle user interactions with widgets (button clicks, form submissions).

        Args:
            thread_id: Unique identifier for the conversation thread
            action: Action data including type and payload
            user_id: Unique identifier for the authenticated user

        Returns:
            dict: Response containing status and any immediate data
        """
        pass
```

## REST API Endpoints

### ChatKit Respond Endpoint
```
POST /api/chatkit/respond
```

#### Request
```json
{
  "thread_id": "thread_abc123",
  "input": "Show me my tasks",
  "metadata": {
    "user_agent": "web",
    "session_id": "session_xyz789"
  }
}
```

#### Response
```json
{
  "status": "success",
  "thread_id": "thread_abc123",
  "response_id": "resp_def456"
}
```

#### Authentication
- Bearer token via Authorization header
- JWT token validated via Better Auth

#### Error Responses
- `401 Unauthorized`: Invalid or missing authentication
- `403 Forbidden`: User not authorized for this thread
- `422 Unprocessable Entity`: Invalid request format
- `500 Internal Server Error`: Server processing error

### ChatKit Action Endpoint
```
POST /api/chatkit/action
```

#### Request
```json
{
  "thread_id": "thread_abc123",
  "action": {
    "type": "button_click",
    "widget_id": "task_complete_btn_123",
    "payload": {
      "task_id": "task_456",
      "action": "complete"
    }
  }
}
```

#### Response
```json
{
  "status": "success",
  "thread_id": "thread_abc123",
  "action_id": "action_ghi789"
}
```

#### Authentication
- Bearer token via Authorization header
- JWT token validated via Better Auth

#### Error Responses
- `401 Unauthorized`: Invalid or missing authentication
- `403 Forbidden`: User not authorized for this thread
- `422 Unprocessable Entity`: Invalid action format
- `500 Internal Server Error`: Server processing error

## Widget Schema Contracts

### Base Widget Schema
```json
{
  "id": "string",
  "type": "string",
  "children": [],
  "props": {},
  "metadata": {}
}
```

### Card Widget
```json
{
  "id": "task_list_card",
  "type": "card",
  "children": [
    {
      "id": "task_list_headline",
      "type": "headline",
      "props": {
        "text": "Your Tasks"
      }
    },
    {
      "id": "task_list",
      "type": "listview",
      "children": [
        {
          "id": "task_item_1",
          "type": "row",
          "children": [
            {
              "id": "task_title_1",
              "type": "text",
              "props": {
                "text": "Buy groceries"
              }
            }
          ]
        }
      ]
    }
  ]
}
```

### Button Widget
```json
{
  "id": "complete_task_btn_1",
  "type": "button",
  "props": {
    "text": "Complete",
    "action": {
      "type": "task_complete",
      "payload": {
        "task_id": "task_1"
      }
    }
  }
}
```

## Authentication Contract

### JWT Token Format
```json
{
  "user_id": "uuid",
  "exp": 1234567890,
  "iat": 1234567890,
  "sub": "user_subject"
}
```

### Authentication Headers
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

## Error Response Format

### Standard Error Format
```json
{
  "error": {
    "type": "string",
    "message": "string",
    "code": "integer"
  }
}
```

### Common Error Types
- `AUTH_ERROR`: Authentication-related issues
- `VALIDATION_ERROR`: Request validation failures
- `PROCESSING_ERROR`: Backend processing issues
- `WIDGET_ERROR`: Widget rendering or action handling issues

## CORS Policy

### Allowed Origins
- Production: `https://yourdomain.com`
- Development: `http://localhost:3000`

### Allowed Headers
- `Content-Type`
- `Authorization`
- `X-Requested-With`

### Allowed Methods
- `GET`
- `POST`
- `PUT`
- `DELETE`
- `OPTIONS`

## Rate Limiting

### Limits
- 100 requests per minute per user
- 10 concurrent requests per user
- 1MB max request size

### Headers
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Requests remaining
- `X-RateLimit-Reset`: Time when limit resets