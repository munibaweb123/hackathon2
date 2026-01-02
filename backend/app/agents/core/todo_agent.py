"""Main todo management agent for AI Chatbot feature."""

from openai import OpenAI
from app.agents.core.factory import create_model
from app.agents.core.base_agent import BaseAgentConfig
from app.agents.tools.add_task import add_task
from app.agents.tools.list_tasks import list_tasks
from app.agents.tools.complete_task import complete_task
from app.agents.tools.delete_task import delete_task
from app.agents.tools.update_task import update_task
from app.core.database import get_session
from sqlmodel import Session
from typing import Dict, Any, Optional, List
from uuid import UUID
import json
from app.agents.core.conversation_manager import ConversationManager
from app.models.message import MessageRole
from app.agents.services.context_service import ContextTrackingService


async def run_chatbot_agent(user_text: str, user_id: str, conversation_id: Optional[str] = None) -> str:
    """
    Run the chatbot agent to process user input and return appropriate response.

    Args:
        user_text: The user's natural language input
        user_id: The ID of the current user
        conversation_id: Optional conversation ID for context

    Returns:
        Response string for the user
    """
    # Create the model client
    client = create_model()

    # Initialize conversation manager for state management
    conv_manager = ConversationManager(user_id=user_id)

    # Initialize context tracking service
    context_service = ContextTrackingService(user_id=user_id)

    # Get or create conversation
    conversation = conv_manager.get_or_create_conversation(conversation_id)

    # Add user message to conversation history
    db_user_message = conv_manager.add_message_to_conversation(
        conversation_id=conversation.id,
        role=MessageRole.USER,
        content=user_text
    )

    # Define the tools available to the agent
    tools = [
        {
            "type": "function",
            "function": {
                "name": "add_task",
                "description": "Create a new task in the user's task list",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "The user's ID"},
                        "title": {"type": "string", "description": "The title of the task"},
                        "description": {"type": "string", "description": "Optional description of the task"},
                        "conversation_id": {"type": "string", "description": "The conversation ID for context tracking"},
                        "message_id": {"type": "string", "description": "The message ID for context tracking"}
                    },
                    "required": ["user_id", "title"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "list_tasks",
                "description": "Retrieve tasks from the user's task list",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "The user's ID"},
                        "status": {"type": "string", "description": "Filter by status: all, pending, completed"}
                    },
                    "required": ["user_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "complete_task",
                "description": "Mark a task as complete",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "The user's ID"},
                        "task_id": {"type": "integer", "description": "The ID of the task to complete"}
                    },
                    "required": ["user_id", "task_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "delete_task",
                "description": "Remove a task from the user's list",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "The user's ID"},
                        "task_id": {"type": "integer", "description": "The ID of the task to delete"}
                    },
                    "required": ["user_id", "task_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_task",
                "description": "Modify task title or description",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "The user's ID"},
                        "task_id": {"type": "integer", "description": "The ID of the task to update"},
                        "title": {"type": "string", "description": "New title for the task (optional)"},
                        "description": {"type": "string", "description": "New description for the task (optional)"}
                    },
                    "required": ["user_id", "task_id"]
                }
            }
        }
    ]

    # Prepare the system message with instructions for the agent
    system_message = {
        "role": "system",
        "content": (
            f"You are the backend agent behind a ChatKit UI for todo management. "
            f"The current user's ID is '{user_id}' - ALWAYS use this ID automatically in all function calls. "
            f"NEVER ask the user for their user_id - you already have it. "
            f"Interpret user requests and call appropriate functions to manage tasks. "
            f"Be concise and helpful. "
            f"If a user asks for tasks, call list_tasks with user_id='{user_id}'. "
            f"If they want to add a task, call add_task with user_id='{user_id}' and the title. "
            f"If they want to complete a task, call complete_task with user_id='{user_id}' and task_id. "
            f"If they want to delete or update a task, call the respective functions with user_id='{user_id}'. "
            f"If you need to disambiguate which task, ask for clarification but never ask for user_id.\n\n"

            # Add specific instructions for natural language patterns
            f"Handle these specific patterns:\n"
            f"- 'Add a task to [title]' or 'Add task [title]' -> call add_task\n"
            f"- 'Show me all my tasks' or 'List tasks' -> call list_tasks with status='all'\n"
            f"- 'What's pending?' or 'Show pending tasks' -> call list_tasks with status='pending'\n"
            f"- 'What have I completed?' or 'Show completed tasks' -> call list_tasks with status='completed'\n"
            f"- 'Mark task [id] as complete' or 'Complete task [id]' -> call complete_task\n"
            f"- 'Delete task [id]' or 'Remove task [id]' -> call delete_task\n"
            f"- 'Change task [id] to [new title]' or 'Update task [id] to [new title]' -> call update_task\n"
            f"- 'Add description [description] of task [title]' -> call update_task with description\n"
            f"- 'Add description to id:[id] [description]' -> call update_task with description\n"
            f"- 'Task [id]' -> call list_tasks to show specific task details\n"
            f"- 'I need to remember to [task]' -> call add_task\n"
            f"- 'Update task [id] with description [description]' -> call update_task\n"
            f"- 'Add note [note] to task [id]' -> call update_task with description\n"
            f"- 'Set description of task [id] to [description]' -> call update_task\n\n"

            f"When updating tasks with descriptions, preserve existing title if not specified in the update. "
            f"Always include the user_id in function calls automatically. "
            f"If a user provides just a task number without context, assume they want to see details about that task. "
            f"If you can't determine the intent, call list_tasks to provide context before other operations."
        )
    }

    # Prepare the user message
    user_message = {
        "role": "user",
        "content": user_text
    }

    # Build the conversation history for context
    conversation_history = conv_manager.get_conversation_history(conversation.id, limit=10)

    # Create the messages list with system message first, then conversation history, then current user message
    messages = [system_message]

    # Add conversation history to messages
    for hist_msg in conversation_history:
        messages.append({
            "role": hist_msg["role"],
            "content": hist_msg["content"]
        })

    # Add the current user message
    messages.append(user_message)

    try:
        # Call the OpenAI API with the tools
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Use configurable model
            messages=messages,
            tools=tools,
            tool_choice="auto",
            max_tokens=1000,
            temperature=0.7
        )

        # Get the response
        response_message = response.choices[0].message

        # Check if the model wanted to call a function
        tool_calls = response_message.tool_calls

        if tool_calls:
            # Process each tool call
            final_response = ""
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                # Add the user_id to function arguments if not present
                if "user_id" not in function_args:
                    function_args["user_id"] = user_id

                # Call the appropriate function based on the name
                if function_name == "add_task":
                    # Add conversation and message IDs for context tracking
                    function_args["conversation_id"] = str(conversation.id)
                    function_args["message_id"] = str(db_user_message.id)  # Using the user message that triggered this
                    result = add_task(**function_args)
                    final_response += f"Added task: {result['title']} (ID: {result['task_id']}). "
                elif function_name == "list_tasks":
                    result = list_tasks(**function_args)
                    if result:
                        task_list = ", ".join([f"'{t['title']}'" for t in result])
                        final_response += f"Here are your tasks: {task_list}. "
                    else:
                        final_response += "You have no tasks. "
                elif function_name == "complete_task":
                    result = complete_task(**function_args)
                    final_response += f"Completed task: {result['title']}. "
                elif function_name == "delete_task":
                    result = delete_task(**function_args)
                    final_response += f"Deleted task: {result['title']}. "
                elif function_name == "update_task":
                    result = update_task(**function_args)
                    final_response += f"Updated task: {result['title']}. "
                else:
                    final_response += f"Unknown function: {function_name}. "

            # Add assistant's response to conversation history
            assistant_message = conv_manager.add_message_to_conversation(
                conversation_id=conversation.id,
                role=MessageRole.ASSISTANT,
                content=final_response
            )

            return final_response.strip()
        else:
            # If no tool was called, return the assistant's message content
            assistant_response = response_message.content or "I processed your request."

            # Add assistant's response to conversation history
            assistant_message = conv_manager.add_message_to_conversation(
                conversation_id=conversation.id,
                role=MessageRole.ASSISTANT,
                content=assistant_response
            )

            return assistant_response
    except Exception as e:
        # Handle any errors
        error_response = f"Sorry, I encountered an error: {str(e)}"

        # Add error response to conversation history
        error_message = conv_manager.add_message_to_conversation(
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT,
            content=error_response
        )

        return error_response


class TodoAgent:
    """Class-based implementation of the todo management agent."""

    def __init__(self, user_id: str, conversation_id: Optional[str] = None):
        """
        Initialize the todo agent.

        Args:
            user_id: The ID of the current user
            conversation_id: Optional conversation ID for context
        """
        self.user_id = user_id
        self.conversation_id = conversation_id
        self.client = create_model()
        self.config = BaseAgentConfig(
            client=self.client,
            model="gpt-4o-mini",
            instructions=(
                "You are a helpful assistant for managing todos through natural language. "
                "Interpret user requests and call appropriate functions to manage tasks. "
                "Be concise and helpful. Always include the user_id in function calls."
            )
        )

    async def process_request(self, user_input: str) -> str:
        """
        Process a user request and return a response.

        Args:
            user_input: The user's natural language request

        Returns:
            Response string for the user
        """
        return await run_chatbot_agent(user_input, self.user_id, self.conversation_id)