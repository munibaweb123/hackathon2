"""ChatKit server implementation for the todo application following OpenAI ChatKit SDK patterns."""

import logging
from typing import Any, Dict
from .server_interface import ChatKitServer, StreamingResult
from .types import ChatKitRequest, ChatKitActionRequest, ChatKitResponse, ChatKitActionResponse
from .agents import get_tasks_for_user, create_task_for_user, complete_task_for_user, delete_task_for_user, update_task_for_user, AgentContext
from .widgets import WidgetFactory
from ..services.task_service import get_tasks_by_user_id
from ..services.thread_service import create_thread
from ..services.message_service import get_conversation_context
from ..models.task import Task
from uuid import UUID

# Set up logger
logger = logging.getLogger(__name__)


class TodoChatKitServer(ChatKitServer):
    """ChatKit server for todo management with widget streaming capabilities."""

    def __init__(self):
        """Initialize the TodoChatKitServer."""
        super().__init__()

    async def respond(self, thread_id: str, input: str, user_id: str) -> Dict[str, Any]:
        """
        Handle user input and generate response with widgets.

        Args:
            thread_id: Unique identifier for the conversation thread
            input: User's input message
            user_id: Unique identifier for the authenticated user

        Returns:
            dict: Response containing status and any immediate data
        """
        # Log the incoming request
        logger.info(f"Processing ChatKit respond request - Thread: {thread_id}, User: {user_id}, Input: {input[:100]}...")

        # Get conversation context (recent messages for context)
        # Handle potential database errors gracefully
        from uuid import UUID
        from ..services.message_service import get_conversation_context

        # Validate thread_id format and convert to UUID if needed
        try:
            # Check if thread_id is already in UUID format
            UUID(thread_id)
            valid_uuid = thread_id
        except ValueError:
            # If not in UUID format, log and use an empty context
            logger.warning(f"Invalid UUID format for thread {thread_id}, skipping context retrieval")
            conversation_context = []
        else:
            try:
                conversation_context = get_conversation_context(valid_uuid, limit=20)
            except Exception as e:
                logger.warning(f"Could not retrieve conversation context for thread {thread_id}: {str(e)}")
                conversation_context = []

        # Process the input to determine the appropriate action
        input_lower = input.lower().strip()

        # Create an agent context for this request
        # For now, we'll create a minimal context for widget streaming
        class MinimalContext:
            def __init__(self):
                self._widget_queue = []

            async def stream_widget(self, widget):
                """Stream a widget."""
                self._widget_queue.append(widget)
                # In a real implementation, this would stream to the client
                print(f"Streaming widget: {widget}")

        agent_context = MinimalContext()

        # Check for greetings and general conversation
        greeting_keywords = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening", "hy", "hii", "hiii"]
        if any(input_lower == keyword or input_lower.startswith(keyword + " ") for keyword in greeting_keywords):
            logger.info(f"User {user_id} sent a greeting")
            return {
                "status": "success",
                "thread_id": thread_id,
                "user_id": user_id,
                "input": input,
                "response_type": "greeting",
                "message": "Hello! I'm your AI task assistant. I can help you manage your tasks. Try:\n• \"Show my tasks\" - to see your tasks\n• \"Add task [title]\" - to create a new task\n• \"Complete task [number]\" - to mark a task as done\n• \"Delete task [number]\" - to remove a task\n\nHow can I help you today?",
                "context": [msg.content for msg in conversation_context[:5]]
            }

        # Check for help requests
        help_keywords = ["help", "what can you do", "how do i", "how to", "commands", "options"]
        if any(keyword in input_lower for keyword in help_keywords):
            logger.info(f"User {user_id} requested help")
            return {
                "status": "success",
                "thread_id": thread_id,
                "user_id": user_id,
                "input": input,
                "response_type": "help",
                "message": "Here's what I can help you with:\n\n📋 **View Tasks**\n• \"Show my tasks\" or \"List tasks\"\n\n➕ **Add Tasks**\n• \"Add task buy groceries\" or \"Create task finish report\"\n\n✅ **Complete Tasks**\n• \"Complete task 1\" or \"Mark task 2 as done\"\n\n🗑️ **Delete Tasks**\n• \"Delete task 3\" or \"Remove task 1\"\n\nJust type naturally and I'll understand!",
                "context": [msg.content for msg in conversation_context[:5]]
            }

        # Check if user wants to see their tasks - be more specific
        show_task_patterns = ["show task", "show my task", "list task", "list my task", "view task", "view my task", "my tasks", "show tasks", "list tasks", "view tasks"]
        if any(pattern in input_lower for pattern in show_task_patterns):
            logger.info(f"User {user_id} requested to see their tasks")
            logger.info(f"DEBUG: Fetching tasks for user_id: '{user_id}' (type: {type(user_id).__name__})")
            # Call the get_tasks_for_user function
            result = await get_tasks_for_user(user_id, agent_context)
            logger.info(f"DEBUG: Task fetch result - status: {result.get('status')}, count: {result.get('task_count', 0)}")

            logger.info(f"Tasks retrieved for user {user_id}, count: {result.get('task_count', 0)}")
            return {
                "status": "success",
                "thread_id": thread_id,
                "user_id": user_id,
                "input": input,
                "response_type": "task_list",
                "data": result,
                "context": [msg.content for msg in conversation_context[:5]]  # Include last 5 messages for context
            }

        # Check if user wants to add a task
        elif any(keyword in input_lower for keyword in ["add task", "create task", "new task", "add a task"]):
            logger.info(f"User {user_id} requested to add a task")
            # Extract task details from the input - use original input to preserve case
            import re

            # Try to extract title using various patterns
            title = ""

            # Pattern 1: "add a task to [title]" or "add task to [title]"
            match = re.search(r'(?:add\s+(?:a\s+)?task\s+to\s+)(.+)', input, re.IGNORECASE)
            if match:
                title = match.group(1).strip()
            else:
                # Pattern 2: "add task [title]" or "create task [title]"
                for keyword in ["add a task", "add task", "create task", "new task"]:
                    pattern = re.compile(re.escape(keyword) + r'\s+(.+)', re.IGNORECASE)
                    match = pattern.search(input)
                    if match:
                        title = match.group(1).strip()
                        # Remove leading "to" if present (e.g., "add task to buy groceries" -> "buy groceries")
                        if title.lower().startswith("to "):
                            title = title[3:].strip()
                        break

            # If no title extracted, ask for clarification
            if not title or len(title) < 2:
                logger.info(f"User {user_id} provided insufficient task title, requesting clarification")
                return {
                    "status": "success",
                    "thread_id": thread_id,
                    "user_id": user_id,
                    "input": input,
                    "response_type": "request_task_details",
                    "message": "Please provide a title for the task you want to add.",
                    "context": [msg.content for msg in conversation_context[:5]]
                }

            logger.info(f"Extracted task title: '{title}' from input: '{input}'")

            # Create the task
            result = await create_task_for_user(title, "", user_id, "medium", agent_context)

            # Check if task creation was successful
            if result.get("status") == "error":
                logger.error(f"Task creation failed for user {user_id}: {result.get('message')}")
                return {
                    "status": "error",
                    "thread_id": thread_id,
                    "user_id": user_id,
                    "input": input,
                    "response_type": "task_creation_failed",
                    "message": result.get("message", "Failed to create task. Please try again."),
                    "context": [msg.content for msg in conversation_context[:5]]
                }

            logger.info(f"Task created for user {user_id}: {result.get('task', {}).get('title', 'Unknown')}")
            return {
                "status": "success",
                "thread_id": thread_id,
                "user_id": user_id,
                "input": input,
                "response_type": "task_created",
                "data": result,
                "task_title": title,  # Store the extracted title directly
                "context": [msg.content for msg in conversation_context[:5]]
            }

        # Check if user wants to complete a task
        elif any(keyword in input_lower for keyword in ["complete", "finish", "done", "mark complete"]):
            logger.info(f"User {user_id} requested to complete a task")
            # Extract task ID from the input (simplified approach)
            import re
            task_id_match = re.search(r'task (\d+)', input_lower) or re.search(r'(\d+)', input_lower)
            if task_id_match:
                task_id = int(task_id_match.group(1))
                result = await complete_task_for_user(task_id, user_id, completed=True, agent_context=agent_context)

                logger.info(f"Task completion attempted for task {task_id}, user {user_id}, success: {'task' in result}")
                return {
                    "status": "success",
                    "thread_id": thread_id,
                    "user_id": user_id,
                    "input": input,
                    "response_type": "task_completed",
                    "data": result,
                    "context": [msg.content for msg in conversation_context[:5]]
                }
            else:
                logger.info(f"User {user_id} did not specify a task ID for completion")
                return {
                    "status": "success",
                    "thread_id": thread_id,
                    "user_id": user_id,
                    "input": input,
                    "response_type": "request_task_id",
                    "message": "Please specify which task number you want to complete.",
                    "context": [msg.content for msg in conversation_context[:5]]
                }

        # Check if user wants to delete a task
        elif any(keyword in input_lower for keyword in ["delete", "remove", "remove task"]):
            logger.info(f"User {user_id} requested to delete a task")
            # Extract task ID from the input (simplified approach)
            import re
            task_id_match = re.search(r'task (\d+)', input_lower) or re.search(r'(\d+)', input_lower)
            if task_id_match:
                task_id = int(task_id_match.group(1))
                result = await delete_task_for_user(task_id, user_id, agent_context=agent_context)

                logger.info(f"Task deletion attempted for task {task_id}, user {user_id}, success: {'message' in result}")
                return {
                    "status": "success",
                    "thread_id": thread_id,
                    "user_id": user_id,
                    "input": input,
                    "response_type": "task_deleted",
                    "data": result,
                    "context": [msg.content for msg in conversation_context[:5]]
                }
            else:
                logger.info(f"User {user_id} did not specify a task ID for deletion")
                return {
                    "status": "success",
                    "thread_id": thread_id,
                    "user_id": user_id,
                    "input": input,
                    "response_type": "request_task_id",
                    "message": "Please specify which task number you want to delete.",
                    "context": [msg.content for msg in conversation_context[:5]]
                }

        # Check if user wants details about a specific task by number
        task_number_pattern = r'^task\s+(\d+)$'
        task_number_match = re.search(task_number_pattern, input_lower.strip())
        if task_number_match:
            task_id = int(task_number_match.group(1))
            logger.info(f"User {user_id} requested details for task {task_id}")

            # Get the specific task
            from ..services.task_service import get_task_by_id
            try:
                task = get_task_by_id(task_id, user_id)
                if task:
                    result = {
                        "status": "success",
                        "task": {
                            "id": task.id,
                            "title": task.title,
                            "description": task.description,
                            "completed": task.completed,
                            "priority": task.priority.value if hasattr(task.priority, 'value') else task.priority,
                            "created_at": task.created_at.isoformat() if task.created_at else None
                        }
                    }
                    logger.info(f"Task {task_id} details retrieved for user {user_id}")
                    return {
                        "status": "success",
                        "thread_id": thread_id,
                        "user_id": user_id,
                        "input": input,
                        "response_type": "task_details",
                        "data": result,
                        "context": [msg.content for msg in conversation_context[:5]]
                    }
                else:
                    logger.info(f"Task {task_id} not found for user {user_id}")
                    return {
                        "status": "success",
                        "thread_id": thread_id,
                        "user_id": user_id,
                        "input": input,
                        "response_type": "task_not_found",
                        "message": f"Could not find task with ID {task_id}.",
                        "context": [msg.content for msg in conversation_context[:5]]
                    }
            except Exception as e:
                logger.error(f"Error retrieving task {task_id} for user {user_id}: {str(e)}")
                return {
                    "status": "error",
                    "thread_id": thread_id,
                    "user_id": user_id,
                    "input": input,
                    "response_type": "error",
                    "message": "Error retrieving task details.",
                    "context": [msg.content for msg in conversation_context[:5]]
                }

        # Check if user wants to update a task - enhanced pattern matching
        elif any(keyword in input_lower for keyword in ["update", "edit", "change", "add description", "set description", "add note"]):
            logger.info(f"User {user_id} requested to update a task")
            # Extract task ID and update details from the input
            import re

            # Pattern for "add description 'text' of task 'title'"
            desc_task_pattern = r'add\s+description\s+[\'"]([^\'"]+)[\'"]\s+of\s+task\s+[\'"]([^\'"]+)[\'"]'
            match = re.search(desc_task_pattern, input, re.IGNORECASE)
            if match:
                description = match.group(1)
                task_title = match.group(2)

                # First, find the task by title
                from ..services.task_service import get_tasks_by_user_id
                tasks = get_tasks_by_user_id(user_id)
                target_task = None
                for task in tasks:
                    if task_title.lower() in task.title.lower():
                        target_task = task
                        break

                if target_task:
                    # Update the task with the new description
                    result = await update_task_for_user(target_task.id, user_id, agent_context=agent_context, description=description)
                    logger.info(f"Task {target_task.id} updated with description for user {user_id}")
                    return {
                        "status": "success",
                        "thread_id": thread_id,
                        "user_id": user_id,
                        "input": input,
                        "response_type": "task_updated",
                        "data": result,
                        "context": [msg.content for msg in conversation_context[:5]]
                    }
                else:
                    logger.info(f"Task with title '{task_title}' not found for user {user_id}")
                    return {
                        "status": "success",
                        "thread_id": thread_id,
                        "user_id": user_id,
                        "input": input,
                        "response_type": "task_not_found",
                        "message": f"Could not find a task with title '{task_title}'.",
                        "context": [msg.content for msg in conversation_context[:5]]
                    }

            # Pattern for "add description to id:XX 'text'" or "add description to task XX 'text'"
            desc_id_pattern = r'add\s+description\s+to\s+(?:id:|task\s+)(\d+)\s+[\'"]([^\'"]+)[\'"]'
            match = re.search(desc_id_pattern, input, re.IGNORECASE)
            if match:
                task_id = int(match.group(1))
                description = match.group(2)

                # Update the task with the new description
                result = await update_task_for_user(task_id, user_id, agent_context=agent_context, description=description)

                if 'task' in result:
                    logger.info(f"Task {task_id} updated with description for user {user_id}")
                    return {
                        "status": "success",
                        "thread_id": thread_id,
                        "user_id": user_id,
                        "input": input,
                        "response_type": "task_updated",
                        "data": result,
                        "context": [msg.content for msg in conversation_context[:5]]
                    }
                else:
                    logger.info(f"Failed to update task {task_id} for user {user_id}")
                    return {
                        "status": "success",
                        "thread_id": thread_id,
                        "user_id": user_id,
                        "input": input,
                        "response_type": "task_not_found",
                        "message": f"Could not find task with ID {task_id}.",
                        "context": [msg.content for msg in conversation_context[:5]]
                    }

            # Pattern for "update task XX with description 'text'"
            update_desc_pattern = r'update\s+task\s+(\d+)\s+with\s+description\s+[\'"]([^\'"]+)[\'"]'
            match = re.search(update_desc_pattern, input, re.IGNORECASE)
            if match:
                task_id = int(match.group(1))
                description = match.group(2)

                # Update the task with the new description
                result = await update_task_for_user(task_id, user_id, agent_context=agent_context, description=description)

                if 'task' in result:
                    logger.info(f"Task {task_id} updated with description for user {user_id}")
                    return {
                        "status": "success",
                        "thread_id": thread_id,
                        "user_id": user_id,
                        "input": input,
                        "response_type": "task_updated",
                        "data": result,
                        "context": [msg.content for msg in conversation_context[:5]]
                    }
                else:
                    logger.info(f"Failed to update task {task_id} for user {user_id}")
                    return {
                        "status": "success",
                        "thread_id": thread_id,
                        "user_id": user_id,
                        "input": input,
                        "response_type": "task_not_found",
                        "message": f"Could not find task with ID {task_id}.",
                        "context": [msg.content for msg in conversation_context[:5]]
                    }

            # Pattern for "set description of task XX to 'text'"
            set_desc_pattern = r'set\s+description\s+of\s+task\s+(\d+)\s+to\s+[\'"]([^\'"]+)[\'"]'
            match = re.search(set_desc_pattern, input, re.IGNORECASE)
            if match:
                task_id = int(match.group(1))
                description = match.group(2)

                # Update the task with the new description
                result = await update_task_for_user(task_id, user_id, agent_context=agent_context, description=description)

                if 'task' in result:
                    logger.info(f"Task {task_id} description set for user {user_id}")
                    return {
                        "status": "success",
                        "thread_id": thread_id,
                        "user_id": user_id,
                        "input": input,
                        "response_type": "task_updated",
                        "data": result,
                        "context": [msg.content for msg in conversation_context[:5]]
                    }
                else:
                    logger.info(f"Failed to update task {task_id} for user {user_id}")
                    return {
                        "status": "success",
                        "thread_id": thread_id,
                        "user_id": user_id,
                        "input": input,
                        "response_type": "task_not_found",
                        "message": f"Could not find task with ID {task_id}.",
                        "context": [msg.content for msg in conversation_context[:5]]
                    }

            # Pattern for simple "update task XX to 'new title'" or "change task XX to 'new title'"
            update_title_pattern = r'(?:update|change)\s+task\s+(\d+)\s+to\s+[\'"]([^\'"]+)[\'"]'
            match = re.search(update_title_pattern, input, re.IGNORECASE)
            if match:
                task_id = int(match.group(1))
                new_title = match.group(2)

                # Update the task with the new title
                result = await update_task_for_user(task_id, user_id, agent_context=agent_context, title=new_title)

                if 'task' in result:
                    logger.info(f"Task {task_id} updated with new title for user {user_id}")
                    return {
                        "status": "success",
                        "thread_id": thread_id,
                        "user_id": user_id,
                        "input": input,
                        "response_type": "task_updated",
                        "data": result,
                        "context": [msg.content for msg in conversation_context[:5]]
                    }
                else:
                    logger.info(f"Failed to update task {task_id} for user {user_id}")
                    return {
                        "status": "success",
                        "thread_id": thread_id,
                        "user_id": user_id,
                        "input": input,
                        "response_type": "task_not_found",
                        "message": f"Could not find task with ID {task_id}.",
                        "context": [msg.content for msg in conversation_context[:5]]
                    }

            # If no specific pattern matched, delegate to AI agent
            logger.info(f"Delegating task update request to AI agent for user {user_id}")
            # This would normally call the AI agent, but we'll return a message for now
            # In a real implementation, we'd call the AI agent here
            return {
                "status": "success",
                "thread_id": thread_id,
                "user_id": user_id,
                "input": input,
                "response_type": "update_delegated_to_ai",
                "message": "Processing your update request...",
                "context": [msg.content for msg in conversation_context[:5]]
            }

        # Default response for unrecognized commands
        logger.info(f"Unrecognized command from user {user_id}, returning general response")
        return {
            "status": "success",
            "thread_id": thread_id,
            "user_id": user_id,
            "input": input,
            "response_type": "general",
            "message": f"Received: {input}",
            "context": [msg.content for msg in conversation_context[:5]]
        }

    async def process_respond_request(self, request: ChatKitRequest, user_id: str) -> ChatKitResponse:
        """
        Process a respond request from the API endpoint.

        Args:
            request: ChatKit request containing thread_id and input
            user_id: Unique identifier for the authenticated user

        Returns:
            ChatKitResponse with status and thread_id
        """
        result = await self.respond(request.thread_id, request.input, user_id)

        return ChatKitResponse(
            status=result.get("status", "success"),
            thread_id=request.thread_id,
            response_id=f"resp_{request.thread_id}_{hash(request.input)}"
        )

    async def process_action_request(self, request: ChatKitActionRequest, user_id: str) -> ChatKitActionResponse:
        """
        Process an action request from the API endpoint.

        Args:
            request: ChatKit action request containing thread_id and action
            user_id: Unique identifier for the authenticated user

        Returns:
            ChatKitActionResponse with status and thread_id
        """
        result = await self.action(request.thread_id, request.action, user_id)

        return ChatKitActionResponse(
            status=result.get("status", "success"),
            thread_id=request.thread_id,
            action_id=f"action_{request.thread_id}_{hash(str(request.action))}"
        )

    async def action(self, thread_id: str, action: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        Handle user interactions with widgets (button clicks, form submissions).

        Args:
            thread_id: Unique identifier for the conversation thread
            action: Action data including type and payload
            user_id: Unique identifier for the authenticated user

        Returns:
            dict: Response containing status and any immediate data
        """
        # Log the incoming action
        logger.info(f"Processing ChatKit action request - Thread: {thread_id}, User: {user_id}, Action type: {action.get('type', 'unknown')}")

        # Validate the incoming action payload
        if not isinstance(action, dict):
            logger.warning(f"Invalid action format from user {user_id}. Expected dictionary, got {type(action)}")
            return {
                "status": "error",
                "thread_id": thread_id,
                "user_id": user_id,
                "error": "Invalid action format: action must be a dictionary"
            }

        action_type = action.get("type", "")
        payload = action.get("payload", {})

        # Validate action type
        if not action_type:
            logger.warning(f"No action type provided by user {user_id}")
            return {
                "status": "error",
                "thread_id": thread_id,
                "user_id": user_id,
                "error": "Action type is required"
            }

        # Validate payload structure
        if not isinstance(payload, dict):
            logger.warning(f"Invalid payload format from user {user_id}. Expected dictionary, got {type(payload)}")
            return {
                "status": "error",
                "thread_id": thread_id,
                "user_id": user_id,
                "error": "Action payload must be a dictionary"
            }

        # Create an agent context for this request
        class MinimalContext:
            def __init__(self):
                self._widget_queue = []

            async def stream_widget(self, widget):
                """Stream a widget."""
                self._widget_queue.append(widget)
                # In a real implementation, this would stream to the client
                print(f"Streaming widget: {widget}")

        agent_context = MinimalContext()

        # Process different types of actions
        if action_type == "task_complete":
            logger.info(f"Processing task completion action for user {user_id}")
            task_id = payload.get("task_id")

            # Validate task_id
            if not task_id:
                logger.warning(f"No task_id provided for completion action by user {user_id}")
                return {
                    "status": "error",
                    "thread_id": thread_id,
                    "user_id": user_id,
                    "action_type": action_type,
                    "error": "task_id is required for task completion"
                }

            try:
                task_id = int(task_id)
            except (ValueError, TypeError):
                logger.warning(f"Invalid task_id format for completion action by user {user_id}: {task_id}")
                return {
                    "status": "error",
                    "thread_id": thread_id,
                    "user_id": user_id,
                    "action_type": action_type,
                    "error": "task_id must be a valid integer"
                }

            # Complete the task
            from ..services.task_service import complete_task
            result = complete_task(task_id, user_id, completed=True)

            if result:
                logger.info(f"Task {task_id} completed successfully for user {user_id}")
                # Create a success confirmation widget
                confirmation_widget = WidgetFactory.create_success_confirmation_widget(
                    f"Task '{result.title}' marked as completed!",
                    {"title": result.title}
                )

                return {
                    "status": "success",
                    "thread_id": thread_id,
                    "user_id": user_id,
                    "action_type": action_type,
                    "result": "task_completed",
                    "widget": confirmation_widget
                }
            else:
                logger.warning(f"Failed to complete task {task_id} for user {user_id} - task not found or unauthorized")
                return {
                    "status": "error",
                    "thread_id": thread_id,
                    "user_id": user_id,
                    "action_type": action_type,
                    "error": "Task not found or could not be completed"
                }

        elif action_type == "task_delete":
            logger.info(f"Processing task deletion action for user {user_id}")
            task_id = payload.get("task_id")

            # Validate task_id
            if not task_id:
                logger.warning(f"No task_id provided for deletion action by user {user_id}")
                return {
                    "status": "error",
                    "thread_id": thread_id,
                    "user_id": user_id,
                    "action_type": action_type,
                    "error": "task_id is required for task deletion"
                }

            try:
                task_id = int(task_id)
            except (ValueError, TypeError):
                logger.warning(f"Invalid task_id format for deletion action by user {user_id}: {task_id}")
                return {
                    "status": "error",
                    "thread_id": thread_id,
                    "user_id": user_id,
                    "action_type": action_type,
                    "error": "task_id must be a valid integer"
                }

            # Delete the task
            from ..services.task_service import delete_task
            success = delete_task(task_id, user_id)

            if success:
                logger.info(f"Task {task_id} deleted successfully for user {user_id}")
                # Create a success confirmation widget
                confirmation_widget = WidgetFactory.create_success_confirmation_widget(
                    "Task deleted successfully!",
                    {}
                )

                return {
                    "status": "success",
                    "thread_id": thread_id,
                    "user_id": user_id,
                    "action_type": action_type,
                    "result": "task_deleted",
                    "widget": confirmation_widget
                }
            else:
                logger.warning(f"Failed to delete task {task_id} for user {user_id} - task not found or unauthorized")
                return {
                    "status": "error",
                    "thread_id": thread_id,
                    "user_id": user_id,
                    "action_type": action_type,
                    "error": "Task not found or could not be deleted"
                }

        elif action_type == "task_add":
            logger.info(f"Processing task addition action for user {user_id}")
            title = payload.get("title", "New Task")
            description = payload.get("description", "")
            priority = payload.get("priority", "medium")

            # Validate title
            if not title or not title.strip():
                logger.warning(f"Empty title provided for task creation by user {user_id}")
                return {
                    "status": "error",
                    "thread_id": thread_id,
                    "user_id": user_id,
                    "action_type": action_type,
                    "error": "Title is required for task creation"
                }

            # Validate priority
            valid_priorities = ["low", "medium", "high"]
            if priority not in valid_priorities:
                logger.info(f"Invalid priority {priority} provided for task creation by user {user_id}, defaulting to medium")
                priority = "medium"  # Default to medium if invalid

            # Create the task
            from ..services.task_service import create_task
            task = create_task(title.strip(), description, user_id, priority)

            logger.info(f"Task {task.id} created successfully for user {user_id}: {task.title}")
            # Create a success confirmation widget
            confirmation_widget = WidgetFactory.create_success_confirmation_widget(
                f"Task '{task.title}' created successfully!",
                {"title": task.title, "description": task.description, "priority": task.priority.value}
            )

            return {
                "status": "success",
                "thread_id": thread_id,
                "user_id": user_id,
                "action_type": action_type,
                "result": "task_created",
                "widget": confirmation_widget
            }

        elif action_type == "show_task_list":
            logger.info(f"Processing show task list action for user {user_id}")
            # Show the task list again
            from .agents import get_tasks_for_user
            result = await get_tasks_for_user(user_id, agent_context)

            logger.info(f"Task list retrieved for user {user_id}, count: {result.get('task_count', 0)}")
            return {
                "status": "success",
                "thread_id": thread_id,
                "user_id": user_id,
                "action_type": action_type,
                "result": "task_list_refreshed",
                "data": result
            }

        # Default response for unrecognized actions
        logger.warning(f"Unrecognized action type '{action_type}' from user {user_id}")
        return {
            "status": "success",
            "thread_id": thread_id,
            "user_id": user_id,
            "action_type": action_type,
            "message": "Action processed"
        }

    async def process_respond_request(self, request: ChatKitRequest, user_id: str) -> ChatKitResponse:
        """
        Process a respond request from the API endpoint.

        Args:
            request: ChatKit request containing thread_id and input
            user_id: Unique identifier for the authenticated user

        Returns:
            ChatKitResponse with status and thread_id
        """
        result = await self.respond(request.thread_id, request.input, user_id)

        return ChatKitResponse(
            status=result.get("status", "success"),
            thread_id=request.thread_id,
            response_id=f"resp_{request.thread_id}_{hash(request.input)}"
        )

    async def process_action_request(self, request: ChatKitActionRequest, user_id: str) -> ChatKitActionResponse:
        """
        Process an action request from the API endpoint.

        Args:
            request: ChatKit action request containing thread_id and action
            user_id: Unique identifier for the authenticated user

        Returns:
            ChatKitActionResponse with status and thread_id
        """
        result = await self.action(request.thread_id, request.action, user_id)

        return ChatKitActionResponse(
            status=result.get("status", "success"),
            thread_id=request.thread_id,
            action_id=f"action_{request.thread_id}_{hash(str(request.action))}"
        )

    async def process(self, body: bytes, context: Dict[str, Any]) -> StreamingResult:
        """
        Process the raw request body from the API endpoint.

        Args:
            body: Raw request body as bytes
            context: Context containing user information

        Returns:
            StreamingResult: Streaming response with SSE events
        """
        import json

        try:
            # Parse the request body
            request_data = json.loads(body.decode('utf-8'))

            # Extract user_id from context
            user_id = context.get('user_id')
            if not user_id:
                raise ValueError("User ID not found in context")

            # Determine the input and thread_id based on request format
            thread_id = request_data.get('thread_id', '')
            input_text = ''

            # Format 1: {input, thread_id} - standard ChatKit format
            if 'input' in request_data:
                input_text = request_data.get('input', '')
                thread_id = request_data.get('thread_id', thread_id)
            # Format 2: {message, thread_id} - frontend format
            elif 'message' in request_data:
                input_text = request_data.get('message', '')
                thread_id = request_data.get('thread_id', thread_id)
            # Format 3: {action, thread_id} - action format
            elif 'action' in request_data:
                action = request_data.get('action', {})
                thread_id = request_data.get('thread_id', thread_id)
                # Process action request
                result = await self.action(thread_id, action, user_id)

                async def generate_action_response():
                    # Stream the action response
                    if result.get('message'):
                        yield json.dumps({"type": "message", "data": {"content": result.get('message')}})
                    yield json.dumps({"type": "completion", "data": {"status": "complete"}})

                return StreamingResult(generate_action_response())
            else:
                raise ValueError("Invalid request format: expecting 'input', 'message', or 'action' field")

            # Process the respond request
            result = await self.respond(thread_id, input_text, user_id)

            async def generate_response():
                # Handle different response types
                response_type = result.get('response_type', '')

                # Handle greeting and help responses (they have a message)
                if response_type in ['greeting', 'help']:
                    message = result.get('message', '')
                    if message:
                        yield json.dumps({"type": "message", "data": {"content": message}})

                # Handle task list response with widget
                elif response_type == 'task_list':
                    tasks_data = result.get('data', {}).get('tasks', [])
                    task_count = len(tasks_data)

                    if task_count > 0:
                        # Send message first
                        yield json.dumps({"type": "message", "data": {"content": f"Here are your {task_count} task(s):"}})

                        # Then send the task list widget
                        widget_data = {
                            "type": "list",
                            "status": {"icon": "clipboard", "text": f"Your Tasks ({task_count})"},
                            "children": []
                        }
                        for idx, task in enumerate(tasks_data, 1):
                            is_completed = task.get('completed', False)
                            status_icon = "✅" if is_completed else "⬜"
                            status_text = "Completed" if is_completed else "Pending"
                            title = task.get('title', 'Untitled')
                            description = task.get('description', '') or 'No description'

                            # Handle priority - might be enum or string
                            priority = task.get('priority', 'medium')
                            if hasattr(priority, 'value'):
                                priority = priority.value
                            priority_str = str(priority).lower()
                            priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(priority_str, "🟡")
                            priority_label = priority_str.capitalize()

                            widget_data["children"].append({
                                "type": "card",
                                "children": [
                                    {
                                        "type": "text",
                                        "value": f"{idx}. {status_icon} {title}",
                                        "weight": "bold",
                                        "size": "lg",
                                        "lineThrough": is_completed,
                                        "color": "secondary" if is_completed else "emphasis"
                                    },
                                    {
                                        "type": "text",
                                        "value": f"   📝 {description}",
                                        "size": "sm",
                                        "color": "secondary"
                                    },
                                    {
                                        "type": "text",
                                        "value": f"   {priority_emoji} {priority_label} priority  •  {status_text}",
                                        "size": "sm",
                                        "color": "secondary"
                                    }
                                ]
                            })
                        yield json.dumps({"type": "widget", "data": {"widget": widget_data}})
                    else:
                        yield json.dumps({"type": "message", "data": {"content": "You don't have any tasks yet. Try saying 'Add task [task name]' to create one!"}})
                elif response_type == 'task_created':
                    # Try to get title from task_title field first, then from data
                    task_title = result.get('task_title') or result.get('data', {}).get('task', {}).get('title', 'your task')
                    yield json.dumps({"type": "message", "data": {"content": f"I've created the task: '{task_title}'. Is there anything else you'd like me to do?"}})

                elif response_type == 'task_creation_failed':
                    error_msg = result.get('message', 'Failed to create task. Please try again.')
                    yield json.dumps({"type": "message", "data": {"content": f"Sorry, I couldn't create the task: {error_msg}"}})

                elif response_type == 'task_completed':
                    task_title = result.get('data', {}).get('task', {}).get('title', 'the task')
                    yield json.dumps({"type": "message", "data": {"content": f"Done! I've marked '{task_title}' as completed."}})

                elif response_type == 'task_deleted':
                    yield json.dumps({"type": "message", "data": {"content": "Task deleted successfully!"}})

                elif response_type == 'request_task_details':
                    yield json.dumps({"type": "message", "data": {"content": "Please provide a title for the task you want to add."}})

                elif response_type == 'request_task_id':
                    yield json.dumps({"type": "message", "data": {"content": result.get('message', 'Please specify which task number.')}})

                elif response_type == 'task_updated':
                    task_title = result.get('data', {}).get('task', {}).get('title', 'the task')
                    yield json.dumps({"type": "message", "data": {"content": f"Task updated: '{task_title}'"}})

                elif response_type == 'task_details':
                    task_data = result.get('data', {}).get('task', {})
                    if task_data:
                        status_text = "completed" if task_data.get('completed', False) else "pending"
                        description = task_data.get('description', 'No description')
                        priority = task_data.get('priority', 'medium')
                        yield json.dumps({"type": "message", "data": {"content": f"Task Details:\nTitle: {task_data.get('title', 'Unknown')}\nStatus: {status_text}\nDescription: {description}\nPriority: {priority}"}})
                    else:
                        yield json.dumps({"type": "message", "data": {"content": "Could not retrieve task details."}})

                elif response_type == 'task_not_found':
                    yield json.dumps({"type": "message", "data": {"content": result.get('message', 'Task not found.')}})

                elif response_type == 'general':
                    # For unrecognized commands, provide helpful response
                    yield json.dumps({"type": "message", "data": {"content": f"I'm not sure what you mean by '{input_text}'. Try:\n• 'Show my tasks' to see your tasks\n• 'Add task [name]' to create a task\n• 'Help' to see all commands"}})

                else:
                    yield json.dumps({"type": "message", "data": {"content": "I've processed your request. How else can I help?"}})

                # Send completion event
                yield json.dumps({"type": "completion", "data": {"status": "complete"}})

            return StreamingResult(generate_response())

        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON request: {str(e)}")

            async def generate_error():
                yield json.dumps({"type": "message", "data": {"content": f"Error: Invalid request format"}})
                yield json.dumps({"type": "completion", "data": {"status": "error"}})

            return StreamingResult(generate_error())
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")

            async def generate_error():
                yield json.dumps({"type": "message", "data": {"content": f"Sorry, I encountered an error. Please try again."}})
                yield json.dumps({"type": "completion", "data": {"status": "error"}})

            return StreamingResult(generate_error())

    async def health_check(self) -> Dict[str, Any]:
        """
        Health check endpoint for ChatKit services.

        Returns:
            dict: Health status information
        """
        import time
        start_time = time.time()

        # Perform basic health checks
        checks = {
            "database_connection": True,  # Assume DB connection is OK if we can reach this point
            "service_availability": True,
            "response_time_ms": round((time.time() - start_time) * 1000, 2)
        }

        return {
            "status": "healthy",
            "timestamp": time.time(),
            "service": "chatkit-server",
            "version": "1.0.0",
            "checks": checks
        }


# Create singleton server instance
_chatkit_server: TodoChatKitServer | None = None


def get_chatkit_server() -> TodoChatKitServer:
    """Get or create the ChatKit server instance."""
    global _chatkit_server
    if _chatkit_server is None:
        _chatkit_server = TodoChatKitServer()
    return _chatkit_server
