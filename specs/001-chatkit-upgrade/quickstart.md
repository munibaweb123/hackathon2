# Quickstart Guide: ChatKit Implementation

## Overview
This guide provides a quick introduction to the ChatKit implementation in the todo application. It covers the key components, how they work together, and how to get started with development.

## Architecture Overview

### Backend Components
The ChatKit backend consists of several key components:

1. **ChatKitServer** (`backend/app/chatkit/server.py`): Implements the main ChatKit server interface with `respond()` and `action()` methods
2. **Server Interface** (`backend/app/chatkit/server_interface.py`): Defines the interface contracts for ChatKit server
3. **Agents** (`backend/app/chatkit/agents.py`): Contains agent implementations with widget streaming capabilities
4. **Widgets** (`backend/app/chatkit/widgets.py`): Provides widget components and factories for different UI elements
5. **Types** (`backend/app/chatkit/types.py`): Defines ChatKit-specific type definitions and schemas

### Frontend Components
The ChatKit frontend includes:

1. **Chat Page** (`frontend/src/app/(dashboard)/chat/page.tsx`): Main chat interface with ChatKit integration
2. **ChatKit Service** (`frontend/src/services/chat/chatkit.ts`): Handles ChatKit client integration and communication
3. **Frontend Types** (`frontend/src/services/chat/types.ts`): TypeScript definitions for ChatKit frontend
4. **UI Components** (`frontend/src/components/`): Reusable components for chat interface

## Getting Started

### Prerequisites
- Python 3.13+ for backend
- Node.js 20+ and npm for frontend
- PostgreSQL (production) or SQLite (development)
- Better Auth configured for authentication
- OpenAI API key for agent functionality

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   # Copy the example environment file
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Run the backend server:
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Set up environment variables:
   ```bash
   # Copy the example environment file
   cp .env.example .env.local
   # Edit .env.local with your configuration
   ```

4. Run the frontend development server:
   ```bash
   npm run dev
   ```

## Key Implementation Details

### ChatKit Server Implementation
The `ChatKitServer` class implements the required interface with two main methods:

1. **`respond()`**: Handles incoming user messages and generates responses with widgets
2. **`action()`**: Handles user interactions with widgets (button clicks, form submissions, etc.)

Example implementation:
```python
from app.chatkit.server import ChatKitServer

class TodoChatKitServer(ChatKitServer):
    async def respond(self, thread_id: str, input: str, user_id: str):
        # Process user input and return widgets
        # Use ctx.context.stream_widget() to stream widgets progressively
        pass

    async def action(self, thread_id: str, action: dict, user_id: str):
        # Handle widget actions
        # Process the action and return updated widgets
        pass
```

### Widget Streaming
Widgets are streamed using the `ctx.context.stream_widget()` pattern:

```python
# In your agent tools
from app.chatkit.widgets import create_task_list_widget

def get_tasks_widget(user_id: str):
    tasks = get_user_tasks(user_id)
    widget = create_task_list_widget(tasks)
    ctx.context.stream_widget(widget)
    return {"status": "success"}
```

### Authentication Integration
The system uses Better Auth JWT tokens for authentication:

```python
from app.auth.dependencies import get_current_user

@chatkit_router.post("/respond")
async def chatkit_respond(
    request: ChatKitRequest,
    current_user: User = Depends(get_current_user)
):
    # Process request with authenticated user context
    pass
```

### Frontend Integration
The frontend loads the ChatKit CDN and integrates with the backend:

```typescript
// In chat page
import { loadChatKit } from '@/services/chat/chatkit';

useEffect(() => {
  loadChatKit({
    serverUrl: process.env.NEXT_PUBLIC_CHATKIT_SERVER_URL,
    authToken: getAuthToken(),
  });
}, []);
```

## Development Workflow

### Adding New Widgets
1. Create a new widget factory in `backend/app/chatkit/widgets.py`
2. Define the widget structure following ChatKit JSON schema
3. Implement the widget rendering logic
4. Test the widget in the chat interface

### Handling New Actions
1. Define the action type and payload structure
2. Implement the action handler in your `ChatKitServer` implementation
3. Add validation for the action payload
4. Test the action handling end-to-end

### Extending Agent Capabilities
1. Create new agent tools in `backend/app/chatkit/agents.py`
2. Implement the tool logic with proper error handling
3. Register the tool with the agent
4. Test the new capabilities through the chat interface

## Testing

### Backend Tests
Run backend tests to ensure ChatKit functionality:
```bash
cd backend
pytest tests/test_chatkit/
```

### Frontend Tests
Run frontend tests to ensure UI components work correctly:
```bash
cd frontend
npm run test
```

### Integration Tests
Test the complete ChatKit flow:
```bash
# Run both backend and frontend
# Test conversation flow with widgets
# Verify action handling works end-to-end
```

## Troubleshooting

### Common Issues
1. **Widget not rendering**: Check that widget IDs are unique and schema is correct
2. **Authentication failures**: Verify JWT tokens are properly configured
3. **Action handling not working**: Ensure action handlers are properly registered
4. **CDN loading failures**: Check network connectivity and CDN URL

### Debugging Tips
1. Enable detailed logging in both backend and frontend
2. Check browser console for frontend errors
3. Review backend logs for processing errors
4. Verify database connections for thread/message persistence

## Next Steps

1. Review the API contracts in `/specs/001-chatkit-upgrade/contracts/`
2. Explore the data model in `/specs/001-chatkit-upgrade/data-model.md`
3. Check the detailed implementation tasks in `/specs/001-chatkit-upgrade/tasks.md`
4. Run the full test suite to ensure all functionality works