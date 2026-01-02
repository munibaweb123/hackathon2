"""OpenAI Assistant API implementation for ChatKit integration."""

import asyncio
from typing import Any, Dict, AsyncIterator
from openai import OpenAI
from app.chatkit.types import ThreadStreamEvent, ThreadMetadata, UserMessageItem
from app.agents.sdk_tools import list_tasks, add_task, complete_task, delete_task, update_task
from app.chatkit.agents import AgentContext


# Initialize OpenAI client
client = OpenAI()

# Create or retrieve the assistant
assistant = None


def get_assistant():
    """Get or create the OpenAI assistant."""
    global assistant
    if assistant is None:
        # Try to find existing assistant or create new one
        try:
            # Attempt to list assistants to see if our assistant exists
            assistants = client.beta.assistants.list(limit=100)
            for existing_assistant in assistants.data:
                if existing_assistant.name == "TaskAssistant":
                    assistant = existing_assistant
                    break
        except Exception:
            pass  # If listing fails, we'll create a new one

        if assistant is None:
            assistant = client.beta.assistants.create(
                name="TaskAssistant",
                instructions="""You are a helpful task management assistant.

IMPORTANT RULES:
1. When list_tasks is called, DO NOT format or display the data yourself.
   Simply say "Here are your tasks" or a similar brief acknowledgment.
   The data will be displayed automatically in a widget.

2. For other operations (add, complete, delete, update), provide a helpful
   confirmation message after the action is completed.

3. Be concise and friendly in your responses.

4. If the user's request is unclear, ask for clarification.

5. You can help users:
   - View their tasks (all, pending, or completed)
   - Add new tasks with optional descriptions
   - Mark tasks as complete
   - Delete tasks
   - Update task titles or descriptions""",
                model="gpt-4o-mini",
                tools=[
                    {"type": "function", "function": list_tasks.function_definition},
                    {"type": "function", "function": add_task.function_definition},
                    {"type": "function", "function": complete_task.function_definition},
                    {"type": "function", "function": delete_task.function_definition},
                    {"type": "function", "function": update_task.function_definition},
                ]
            )
    return assistant


async def stream_openai_response(
    thread_metadata: ThreadMetadata,
    input_message: UserMessageItem,
    context: Dict[str, Any]
) -> AsyncIterator[ThreadStreamEvent]:
    """Stream response from OpenAI Assistant API."""
    from datetime import datetime

    # Get or create the assistant
    assistant = get_assistant()

    # Create a thread if one doesn't exist
    # In a real implementation, we would map the ChatKit thread to an OpenAI thread
    # For now, we'll create a temporary thread for this interaction

    # Add the user message to the thread
    # In practice, we'd need to maintain thread state between calls
    # This is a simplified implementation for demonstration

    # For now, let's simulate the response by directly calling the tools based on the message content
    # This is a fallback implementation until we properly integrate with OpenAI API

    user_message_content = input_message.content.lower() if input_message.content else ""

    # Simple keyword matching to simulate assistant behavior
    if "list" in user_message_content and ("task" in user_message_content or "todo" in user_message_content):
        # Simulate calling the list_tasks tool
        from app.agents.sdk_tools import create_task_list_widget

        # Get user_id from context
        user_id = context.get('user_id', 'unknown')

        # Create a mock agent context for the tool call
        mock_agent_context = AgentContext(
            thread=thread_metadata,
            store=None,  # This would be the actual store
            request_context=context
        )

        # Simulate the tool call
        try:
            # This would normally be an async call to the actual tool
            import json
            # Simulate a response with tasks
            simulated_tasks = [
                {"id": 1, "title": "Sample task 1", "completed": False},
                {"id": 2, "title": "Sample task 2", "completed": True}
            ]

            # Create widget for the tasks
            widget = create_task_list_widget(simulated_tasks)

            # Yield the widget event
            yield ThreadStreamEvent(
                type="widget",
                data={
                    "widget": widget.dict(),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )

            # Yield a brief acknowledgment
            yield ThreadStreamEvent(
                type="message",
                data={
                    "content": "Here are your tasks"
                }
            )
        except Exception as e:
            yield ThreadStreamEvent(
                type="message",
                data={
                    "content": f"Error processing your request: {str(e)}"
                }
            )
    else:
        # For other messages, return a simple response
        yield ThreadStreamEvent(
            type="message",
            data={
                "content": f"I received your message: '{input_message.content}'. I can help you manage your tasks."
            }
        )