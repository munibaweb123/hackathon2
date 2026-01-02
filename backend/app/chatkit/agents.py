"""ChatKit agents utilities for AI Chatbot feature."""

from typing import Any, Dict, List, Optional, AsyncIterator
from pydantic import BaseModel
from .types import ThreadMetadata, ThreadStreamEvent, UserMessageItem, SimpleItem
from .server_interface import ContextType


from typing import List
from pydantic import BaseModel
from datetime import datetime

class WidgetEvent(BaseModel):
    """Represents a widget event that can be streamed."""
    type: str = "widget"
    widget: Any
    timestamp: datetime = None

    def __init__(self, **data):
        timestamp = datetime.utcnow()
        super().__init__(timestamp=timestamp, **data)


class AgentContext:
    """Context for agent operations."""

    def __init__(self, thread: ThreadMetadata, store: Any, request_context: Dict[str, Any]):
        self.thread = thread
        self.store = store
        self.request_context = request_context
        # Add a queue to store widget events that are streamed
        self._widget_events: List[WidgetEvent] = []

    async def stream_widget(self, widget):
        """Stream a widget to the client."""
        # Store the widget event for later retrieval
        widget_event = WidgetEvent(widget=widget)
        self._widget_events.append(widget_event)
        print(f"Queued widget for streaming: {widget}")


class SimpleItem(BaseModel):
    """Simple representation of a chat item."""
    id: str
    role: str
    content: str


async def simple_to_agent_input(items: List[SimpleItem]) -> List[Dict[str, Any]]:
    """Convert simple items to agent input format."""
    return [
        {
            "role": item.role,
            "content": item.content
        }
        for item in items
    ]


async def stream_agent_response(
    agent_context: AgentContext,
    result: Any
) -> AsyncIterator[ThreadStreamEvent]:
    """Stream agent response as ChatKit events."""
    import asyncio
    from .types import ThreadStreamEvent

    # First, yield any queued widget events that were created during tool execution
    for widget_event in agent_context._widget_events:
        yield ThreadStreamEvent(
            type="widget",
            data={
                "widget": widget_event.widget.dict() if hasattr(widget_event.widget, 'dict') else widget_event.widget,
                "timestamp": widget_event.timestamp.isoformat() if widget_event.timestamp else None
            }
        )

    # Handle the streaming result from the agents library
    # The result from Runner.run_streamed should be an async iterator
    try:
        # Check if result is an async iterable (as expected from the agents library)
        if hasattr(result, '__aiter__'):
            async for chunk in result:
                # Process each chunk from the agent's streaming response
                # The exact structure depends on the agents library implementation
                if hasattr(chunk, 'data') and hasattr(chunk, 'type'):
                    # Handle different types of chunks
                    chunk_type = getattr(chunk, 'type', 'unknown')
                    chunk_data = getattr(chunk, 'data', {})

                    if chunk_type == 'widget':
                        # Handle widget events
                        yield ThreadStreamEvent(
                            type="widget",
                            data={
                                "widget": chunk_data.dict() if hasattr(chunk_data, 'dict') else chunk_data
                            }
                        )
                    elif chunk_type == 'text' or chunk_type == 'message':
                        # Handle text message events
                        content = str(chunk_data) if not isinstance(chunk_data, str) else chunk_data
                        yield ThreadStreamEvent(
                            type="message",
                            data={"content": content}
                        )
                    else:
                        # Handle other types of events
                        content = str(chunk_data) if not isinstance(chunk_data, str) else chunk_data
                        yield ThreadStreamEvent(
                            type="message",
                            data={"content": content}
                        )
                elif isinstance(chunk, dict):
                    # Handle dictionary responses
                    if chunk.get('type') == 'widget':
                        yield ThreadStreamEvent(
                            type="widget",
                            data=chunk
                        )
                    else:
                        content = str(chunk.get('content', chunk))
                        yield ThreadStreamEvent(
                            type="message",
                            data={"content": content}
                        )
                else:
                    # Handle other response types as text
                    content = str(chunk)
                    if content and content.strip():
                        yield ThreadStreamEvent(
                            type="message",
                            data={"content": content}
                        )
        else:
            # If result is not an async iterator, handle as a completed result
            # This might happen if the agents library returns a completed result instead of a stream
            yield ThreadStreamEvent(
                type="message",
                data={"content": "Processed your request."}
            )

    except TypeError as e:
        if "'async for' requires an object with __aiter__ method" in str(e):
            # The result object is not an async iterator, handle gracefully
            yield ThreadStreamEvent(
                type="message",
                data={"content": "Processed your request."}
            )
        else:
            # Re-raise other TypeErrors
            raise e
    except Exception as e:
        # If there's an error in streaming, return a simple message
        yield ThreadStreamEvent(
            type="message",
            data={"content": f"Error streaming response: {str(e)}"}
        )
        import traceback
        print(f"Error in stream_agent_response: {traceback.format_exc()}")

    # Yield a completion event
    yield ThreadStreamEvent(
        type="completion",
        data={"status": "complete"}
    )


class InMemoryStore:
    """Simple in-memory store for thread items."""

    def __init__(self):
        self._threads = {}
        self._items = {}

    async def load_thread_items(
        self,
        thread_id: str,
        after: Optional[str] = None,
        limit: int = 20,
        order: str = "asc",
        context: Optional[Dict[str, Any]] = None
    ):
        """Load items from a thread."""
        # Create a mock response structure
        from .types import SimpleItem
        from datetime import datetime

        # Return a mock page object with data
        class MockPage:
            def __init__(self, data):
                self.data = data

        # Create some mock items
        mock_items = [
            SimpleItem(
                id=f"item_{i}",
                role="user" if i % 2 == 0 else "assistant",
                content=f"Mock message {i}"
            ) for i in range(min(limit, 5))  # 5 mock items max
        ]

        return MockPage(data=mock_items)


async def get_tasks_for_user(user_id: str, agent_context: AgentContext):
    """
    Get tasks for a specific user.

    Args:
        user_id: The ID of the user whose tasks to retrieve
        agent_context: Agent context containing thread and store information

    Returns:
        Dictionary with tasks data
    """
    from ..services.task_service import get_tasks_by_user_id

    try:
        # Retrieve tasks for the user from the database
        tasks = get_tasks_by_user_id(user_id)

        # Stream a widget with the tasks
        from .widgets import WidgetFactory

        if tasks:
            # Create a task list widget
            task_list_widget = WidgetFactory.create_task_list_widget(tasks)
            await agent_context.stream_widget(task_list_widget)

            return {
                "status": "success",
                "task_count": len(tasks),
                "tasks": [task.model_dump() for task in tasks]
            }
        else:
            # Create an empty state widget
            empty_widget = WidgetFactory.create_empty_state_widget("No tasks found")
            await agent_context.stream_widget(empty_widget)

            return {
                "status": "success",
                "task_count": 0,
                "tasks": []
            }

    except Exception as e:
        # Log the error for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error retrieving tasks for user {user_id}: {str(e)}")

        # Return a graceful error response with helpful message
        return {
            "status": "error",
            "message": "Unable to retrieve tasks at this moment. The system may be experiencing connectivity issues.",
            "fallback_response": "I'm sorry, I couldn't retrieve your tasks right now. Please try again in a moment or use the web interface."
        }


async def create_task_for_user(title: str, description: str, user_id: str, priority: str = "medium", agent_context: AgentContext = None):
    """
    Create a new task for a user.

    Args:
        title: Title of the task
        description: Description of the task
        user_id: ID of the user creating the task
        priority: Priority level of the task (low, medium, high)
        agent_context: Agent context for widget streaming

    Returns:
        Dictionary with task creation result
    """
    from ..services.task_service import create_task
    from .widgets import WidgetFactory

    try:
        # Create the task in the database
        task = create_task(title, description, user_id, priority)

        # If context provided, stream a success widget
        if agent_context:
            success_widget = WidgetFactory.create_success_confirmation_widget(
                f"Task '{task.title}' created successfully!",
                {"title": task.title, "description": task.description, "priority": task.priority.value}
            )
            await agent_context.stream_widget(success_widget)

        return {
            "status": "success",
            "task": task.model_dump()
        }

    except Exception as e:
        # Log the error for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error creating task for user {user_id}: {str(e)}")

        # Return a graceful error response with helpful message
        return {
            "status": "error",
            "message": "Unable to create task at this moment. The system may be experiencing connectivity issues.",
            "fallback_response": "I'm sorry, I couldn't create your task right now. Please try again in a moment or use the web interface."
        }


async def complete_task_for_user(task_id: int, user_id: str, completed: bool = True, agent_context: AgentContext = None):
    """
    Mark a task as completed or incomplete for a user.

    Args:
        task_id: ID of the task to update
        user_id: ID of the user who owns the task
        completed: Whether the task is completed (default True)
        agent_context: Agent context for widget streaming

    Returns:
        Dictionary with task completion result
    """
    from ..services.task_service import complete_task
    from .widgets import WidgetFactory

    try:
        # Update the task completion status
        task = complete_task(task_id, user_id, completed)

        if not task:
            return {
                "status": "error",
                "message": "Task not found or does not belong to user"
            }

        # If context provided, stream a success widget
        if agent_context:
            status_text = "completed" if completed else "marked as incomplete"
            success_widget = WidgetFactory.create_success_confirmation_widget(
                f"Task '{task.title}' {status_text}!",
                {"title": task.title, "completed": task.completed}
            )
            await agent_context.stream_widget(success_widget)

        return {
            "status": "success",
            "task": task.model_dump()
        }

    except Exception as e:
        # Log the error for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error completing task {task_id} for user {user_id}: {str(e)}")

        # Return a graceful error response with helpful message
        return {
            "status": "error",
            "message": "Unable to update task status at this moment. The system may be experiencing connectivity issues.",
            "fallback_response": "I'm sorry, I couldn't update your task status right now. Please try again in a moment or use the web interface."
        }


async def update_task_for_user(task_id: int, user_id: str, agent_context: AgentContext = None, **updates):
    """
    Update a task for a user.

    Args:
        task_id: ID of the task to update
        user_id: ID of the user who owns the task
        agent_context: Agent context for widget streaming
        **updates: Fields to update (title, description, priority, etc.)

    Returns:
        Dictionary with task update result
    """
    from ..services.task_service import update_task
    from .widgets import WidgetFactory

    try:
        # Update the task in the database
        task = update_task(task_id, user_id, **updates)

        if not task:
            return {
                "status": "error",
                "message": "Task not found or does not belong to user"
            }

        # If context provided, stream a success widget
        if agent_context:
            success_widget = WidgetFactory.create_success_confirmation_widget(
                f"Task '{task.title}' updated successfully!",
                {"title": task.title}
            )
            await agent_context.stream_widget(success_widget)

        return {
            "status": "success",
            "task": task.model_dump()
        }

    except Exception as e:
        # Log the error for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error updating task {task_id} for user {user_id}: {str(e)}")

        # Return a graceful error response with helpful message
        return {
            "status": "error",
            "message": "Unable to update task at this moment. The system may be experiencing connectivity issues.",
            "fallback_response": "I'm sorry, I couldn't update your task right now. Please try again in a moment or use the web interface."
        }


async def delete_task_for_user(task_id: int, user_id: str, agent_context: AgentContext = None):
    """
    Delete a task for a user.

    Args:
        task_id: ID of the task to delete
        user_id: ID of the user who owns the task
        agent_context: Agent context for widget streaming

    Returns:
        Dictionary with task deletion result
    """
    from ..services.task_service import delete_task
    from .widgets import WidgetFactory

    try:
        # Delete the task from the database
        success = delete_task(task_id, user_id)

        if not success:
            return {
                "status": "error",
                "message": "Task not found or does not belong to user"
            }

        # If context provided, stream a success widget
        if agent_context:
            success_widget = WidgetFactory.create_success_confirmation_widget(
                "Task deleted successfully!",
                {}
            )
            await agent_context.stream_widget(success_widget)

        return {
            "status": "success",
            "message": "Task deleted successfully"
        }

    except Exception as e:
        # Log the error for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error deleting task {task_id} for user {user_id}: {str(e)}")

        # Return a graceful error response with helpful message
        return {
            "status": "error",
            "message": "Unable to delete task at this moment. The system may be experiencing connectivity issues.",
            "fallback_response": "I'm sorry, I couldn't delete your task right now. Please try again in a moment or use the web interface."
        }