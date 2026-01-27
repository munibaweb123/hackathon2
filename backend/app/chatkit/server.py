"""ChatKit server implementation for the todo application following OpenAI ChatKit SDK patterns."""

import logging
import re
from typing import Any, Dict
from .server_interface import ChatKitServer, StreamingResult
from .types import ChatKitRequest, ChatKitActionRequest, ChatKitResponse, ChatKitActionResponse
from .agents import (
    get_tasks_for_user, create_task_for_user, complete_task_for_user,
    delete_task_for_user, update_task_for_user, AgentContext,
    complete_task_by_title_for_user, update_task_by_title_for_user, delete_task_by_title_for_user
)
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

        # Check for greetings and general conversation (English + Urdu)
        greeting_keywords = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening", "hy", "hii", "hiii",
                            "سلام", "السلام علیکم", "ہیلو", "صبح بخیر", "شام بخیر"]
        urdu_greeting = any(kw in input for kw in ["سلام", "السلام علیکم", "ہیلو", "صبح بخیر", "شام بخیر"])
        if any(input_lower == keyword or input_lower.startswith(keyword + " ") for keyword in greeting_keywords) or urdu_greeting:
            logger.info(f"User {user_id} sent a greeting")
            message = (
                "السلام علیکم! میں آپ کا AI ٹاسک اسسٹنٹ ہوں۔ میں آپ کی مدد کر سکتا ہوں:\n"
                "• \"میرے ٹاسک دکھاؤ\" - ٹاسک دیکھنے کے لیے\n"
                "• \"ٹاسک شامل کرو [نام]\" - نیا ٹاسک بنانے کے لیے\n"
                "• \"ٹاسک مکمل کرو [نمبر]\" - ٹاسک مکمل کرنے کے لیے\n"
                "• \"ٹاسک حذف کرو [نمبر]\" - ٹاسک ہٹانے کے لیے\n\n"
                "Hello! I'm your AI task assistant. I can help you manage your tasks. Try:\n"
                "• \"Show my tasks\" - to see your tasks\n"
                "• \"Add task [title]\" - to create a new task\n"
                "• \"Complete task [number]\" - to mark a task as done\n"
                "• \"Delete task [number]\" - to remove a task"
            ) if urdu_greeting else (
                "Hello! I'm your AI task assistant. I can help you manage your tasks. Try:\n"
                "• \"Show my tasks\" - to see your tasks\n"
                "• \"Add task [title]\" - to create a new task\n"
                "• \"Complete task [number]\" - to mark a task as done\n"
                "• \"Delete task [number]\" - to remove a task\n\n"
                "How can I help you today?"
            )
            return {
                "status": "success",
                "thread_id": thread_id,
                "user_id": user_id,
                "input": input,
                "response_type": "greeting",
                "message": message,
                "context": [msg.content for msg in conversation_context[:5]]
            }

        # Check for help requests (English + Urdu)
        help_keywords = ["help", "what can you do", "how do i", "how to", "commands", "options",
                        "مدد", "کیا کر سکتے ہو", "کیسے", "احکامات"]
        urdu_help = any(kw in input for kw in ["مدد", "کیا کر سکتے ہو", "کیسے", "احکامات"])
        if any(keyword in input_lower for keyword in help_keywords) or urdu_help:
            logger.info(f"User {user_id} requested help")
            message = (
                "📋 **ٹاسک دیکھیں**\n• \"میرے ٹاسک دکھاؤ\" یا \"ٹاسک لسٹ\"\n\n"
                "➕ **ٹاسک شامل کریں**\n• \"ٹاسک شامل کرو سامان خریدنا\"\n\n"
                "✏️ **ٹاسک کا نام بدلیں**\n• \"rename task پرانا نام to نیا نام\"\n• \"update task \\\"پرانا نام\\\" with title \\\"نیا نام\\\"\"\n\n"
                "🔥 **ٹاسک کی اہمیت تبدیل کریں**\n• \"update task \\\"ٹاسک کا نام\\\" with priority high\"\n\n"
                "✅ **ٹاسک مکمل کریں**\n• \"ٹاسک مکمل کرو نام\" یا \"مکمل کرو 1\"\n\n"
                "🗑️ **ٹاسک حذف کریں**\n• \"ٹاسک حذف کرو نام\" یا \"حذف کرو 1\"\n\n"
                "---\n\n"
                "📋 **View Tasks**\n• \"Show my tasks\" or \"List tasks\"\n\n"
                "➕ **Add Tasks**\n• \"Add task buy groceries\"\n\n"
                "✏️ **Rename Tasks**\n• \"rename task old name to new name\"\n• \"update task \\\"old name\\\" with title \\\"new name\\\"\"\n\n"
                "🔥 **Update Priority**\n• \"update task \\\"task name\\\" with priority high\"\n\n"
                "✅ **Complete Tasks**\n• \"Complete task 1\" or \"complete buy groceries\"\n\n"
                "🗑️ **Delete Tasks**\n• \"Delete task 1\" or \"delete buy groceries\""
            ) if urdu_help else (
                "Here's what I can help you with:\n\n"
                "📋 **View Tasks**\n• \"Show my tasks\" or \"List tasks\"\n\n"
                "➕ **Add Tasks**\n• \"Add task buy groceries\" or \"Create task finish report\"\n\n"
                "✏️ **Rename Tasks**\n• \"rename task old title to new title\"\n• \"update task \\\"my task\\\" to \\\"new name\\\"\"\n• \"update task \\\"my task\\\" with title \\\"new title\\\"\"\n\n"
                "🔥 **Update Priority**\n• \"update task \\\"task name\\\" with priority high\"\n\n"
                "✅ **Complete Tasks**\n• \"Complete task 1\" or \"Mark buy groceries as done\"\n\n"
                "🗑️ **Delete Tasks**\n• \"Delete task 3\" or \"Remove buy groceries\"\n\n"
                "Just type naturally and I'll understand!"
            )
            return {
                "status": "success",
                "thread_id": thread_id,
                "user_id": user_id,
                "input": input,
                "response_type": "help",
                "message": message,
                "context": [msg.content for msg in conversation_context[:5]]
            }

        # Check if user wants to see their tasks - be more specific (English + Urdu)
        show_task_patterns_en = ["show task", "show my task", "list task", "list my task", "view task", "view my task", "my tasks", "show tasks", "list tasks", "view tasks"]
        show_task_patterns_ur = ["میرے ٹاسک", "ٹاسک دکھاؤ", "ٹاسک لسٹ", "میری لسٹ", "کام دکھاؤ"]
        if any(pattern in input_lower for pattern in show_task_patterns_en) or any(pattern in input for pattern in show_task_patterns_ur):
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

        # Check if user wants to add a task (English + Urdu)
        add_task_keywords_en = ["add task", "create task", "new task", "add a task"]
        add_task_keywords_ur = ["ٹاسک شامل کرو", "نیا ٹاسک", "کام شامل کرو", "ٹاسک بناؤ"]
        urdu_add = any(kw in input for kw in add_task_keywords_ur)

        if any(keyword in input_lower for keyword in add_task_keywords_en) or urdu_add:
            logger.info(f"User {user_id} requested to add a task")
            # Extract task details from the input - use original input to preserve case

            # Try to extract title using various patterns
            title = ""

            # Urdu pattern: "ٹاسک شامل کرو [title]" or "نیا ٹاسک [title]"
            if urdu_add:
                for keyword in add_task_keywords_ur:
                    if keyword in input:
                        idx = input.find(keyword) + len(keyword)
                        title = input[idx:].strip()
                        break

            # Pattern 1: "add a task to [title]" or "add task to [title]"
            if not title:
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
                message = "براہ کرم ٹاسک کا نام بتائیں۔" if urdu_add else "Please provide a title for the task you want to add."
                return {
                    "status": "success",
                    "thread_id": thread_id,
                    "user_id": user_id,
                    "input": input,
                    "response_type": "request_task_details",
                    "message": message,
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

        # Check if user wants to set/change priority
        priority_match_found = False
        priority_patterns = [
            r'(?:set|change|update)\s+priority\s+(?:to\s+)?(high|medium|low)\s+(?:for\s+)?(?:task\s+)?[\'"]?([^\'"]+)[\'"]?',
            r'(?:set|change|update)\s+(?:task\s+)?[\'"]?([^\'"]+)[\'"]?\s+(?:to\s+)?(high|medium|low)\s+priority',
            r'(?:make|set)\s+(?:task\s+)?[\'"]?([^\'"]+)[\'"]?\s+(high|medium|low)\s+priority',
            r'(?:add|set)\s+(high|medium|low)\s+priority\s+(?:to|for)\s+(?:task\s+)?[\'"]?([^\'"]+)[\'"]?',
        ]

        for pattern in priority_patterns:
            match = re.search(pattern, input, re.IGNORECASE)
            if match:
                priority_match_found = True
                groups = match.groups()
                # Different patterns have priority and title in different positions
                if pattern.startswith(r'(?:set|change|update)\s+priority'):
                    priority, task_title = groups[0], groups[1]
                elif pattern.startswith(r'(?:add|set)\s+(high'):
                    priority, task_title = groups[0], groups[1]
                else:
                    task_title, priority = groups[0], groups[1]

                priority = priority.lower().strip()
                task_title = task_title.strip().strip('"\'')

                logger.info(f"Setting priority '{priority}' for task '{task_title}' for user {user_id}")

                # Use title-based update function
                result = await update_task_by_title_for_user(task_title, user_id, agent_context=agent_context, priority=priority)

                if result.get("status") == "success":
                    updated_title = result.get("task", {}).get("title", task_title)
                    logger.info(f"Task '{updated_title}' priority updated to '{priority}' for user {user_id}")
                    return {
                        "status": "success",
                        "thread_id": thread_id,
                        "user_id": user_id,
                        "input": input,
                        "response_type": "task_updated",
                        "data": result,
                        "task_title": updated_title,
                        "priority": priority,
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
                        "message": result.get("message", f"Could not find a task with title '{task_title}'."),
                        "context": [msg.content for msg in conversation_context[:5]]
                    }

        # Check if user wants to update a task - check BEFORE complete to avoid "completed" in description triggering complete
        # Urdu keywords for update operations
        update_keywords_ur = ["ٹاسک تبدیل کرو", "نام تبدیل کرو", "ٹاسک کا نام", "عنوان تبدیل"]
        urdu_update = any(kw in input for kw in update_keywords_ur)

        if not priority_match_found and (any(input_lower.startswith(keyword) for keyword in ["update", "edit", "change", "rename", "add description", "set description", "add note"]) or urdu_update):
            logger.info(f"User {user_id} requested to update a task")
            # Extract task ID and update details from the input

            # Variables to hold extracted titles
            old_title = None
            new_title = None

            # Pattern 1: "update task 'old title' to 'new title'" or "rename task 'old' to 'new'" (with quotes)
            rename_title_pattern = r'(?:update|rename|change)\s+(?:task\s+)?[\'"]([^\'"]+)[\'"]\s+(?:to|with)\s+[\'"]([^\'"]+)[\'"]'
            match = re.search(rename_title_pattern, input, re.IGNORECASE)
            if match:
                old_title = match.group(1)
                new_title = match.group(2)

            # Pattern 2: "rename task old title to new title" (without quotes, using rsplit for robustness)
            if not old_title and ' to ' in input.lower():
                parts = input.rsplit(' to ', 1)  # Split from the right, only once
                if len(parts) == 2:
                    command_part = parts[0].strip()
                    new_title_part = parts[1].strip()

                    # Check if the command part starts with update/rename/change and possibly "task"
                    cmd_match = re.match(r'(?:update|rename|change)\s+(?:task\s+)?(.+)$', command_part, re.IGNORECASE)
                    if cmd_match:
                        old_title_raw = cmd_match.group(1).strip().strip('"\'')
                        new_title_raw = new_title_part.strip().strip('"\'')

                        if old_title_raw and new_title_raw and len(old_title_raw) > 1 and len(new_title_raw) > 0:
                            old_title = old_title_raw
                            new_title = new_title_raw
                            logger.info(f"Pattern 2 (to) matched: old='{old_title}', new='{new_title}'")

            # Pattern 2b: "rename task old title with new title" (without quotes, using rsplit for robustness)
            if not old_title and ' with ' in input.lower():
                # Don't match if it's a description/priority/note update
                if not any(kw in input.lower() for kw in ['with description', 'with priority', 'with note', 'with status']):
                    parts = input.rsplit(' with ', 1)  # Split from the right, only once
                    if len(parts) == 2:
                        command_part = parts[0].strip()
                        new_title_part = parts[1].strip()

                        # Check if the command part starts with update/rename/change and possibly "task"
                        cmd_match = re.match(r'(?:update|rename|change)\s+(?:task\s+)?(.+)$', command_part, re.IGNORECASE)
                        if cmd_match:
                            old_title_raw = cmd_match.group(1).strip().strip('"\'')
                            new_title_raw = new_title_part.strip().strip('"\'')

                            # Also handle "with title X" pattern
                            if new_title_raw.lower().startswith('title '):
                                new_title_raw = new_title_raw[6:].strip().strip('"\'')

                            if old_title_raw and new_title_raw and len(old_title_raw) > 1 and len(new_title_raw) > 0:
                                old_title = old_title_raw
                                new_title = new_title_raw
                                logger.info(f"Pattern 2b (with) matched: old='{old_title}', new='{new_title}'")

            # Pattern 3: Urdu pattern for renaming
            if not old_title and urdu_update:
                # Try to extract old and new titles from Urdu command
                urdu_rename_pattern = r'(?:ٹاسک\s+(?:کا\s+)?نام\s+)?(.+?)\s+(?:سے|to)\s+(.+?)(?:\s+کرو)?$'
                urdu_match = re.search(urdu_rename_pattern, input, re.IGNORECASE)
                if urdu_match:
                    old_title_raw = urdu_match.group(1).strip().strip('"\'')
                    new_title_raw = urdu_match.group(2).strip().strip('"\'')
                    # Remove Urdu keywords from old_title if present
                    for kw in update_keywords_ur:
                        old_title_raw = old_title_raw.replace(kw, '').strip()
                    if old_title_raw and new_title_raw:
                        old_title = old_title_raw
                        new_title = new_title_raw

            if old_title and new_title:
                logger.info(f"Renaming task '{old_title}' to '{new_title}' for user {user_id}")

                # Use title-based update function
                result = await update_task_by_title_for_user(old_title, user_id, agent_context=agent_context, new_title=new_title)

                if result.get("status") == "success":
                    updated_title = result.get("task", {}).get("title", new_title)
                    logger.info(f"Task renamed from '{old_title}' to '{updated_title}' for user {user_id}")
                    message = f"ٹاسک کا نام '{updated_title}' میں تبدیل کر دیا گیا!" if urdu_update else None
                    return {
                        "status": "success",
                        "thread_id": thread_id,
                        "user_id": user_id,
                        "input": input,
                        "response_type": "task_updated",
                        "data": result,
                        "task_title": updated_title,
                        "urdu_message": message,
                        "context": [msg.content for msg in conversation_context[:5]]
                    }
                else:
                    logger.info(f"Task with title '{old_title}' not found for user {user_id}")
                    message = f"'{old_title}' نام کا ٹاسک نہیں ملا۔" if urdu_update else result.get("message", f"Could not find a task with title '{old_title}'.")
                    return {
                        "status": "success",
                        "thread_id": thread_id,
                        "user_id": user_id,
                        "input": input,
                        "response_type": "task_not_found",
                        "message": message,
                        "context": [msg.content for msg in conversation_context[:5]]
                    }

            # NEW PATTERN: Handle "update task 'old title' with 'new title'" (for renaming, not description) - with quotes
            update_title_with_title_pattern = r'(?:update|change|rename)\s+(?:task\s+)?[\'"]([^\'"]+)[\'"]\s+with\s+[\'"]([^\'"]+)[\'"]'
            match = re.search(update_title_with_title_pattern, input, re.IGNORECASE)

            if match:
                old_title = match.group(1)
                new_title = match.group(2)
                logger.info(f"Renaming task (using 'with') from '{old_title}' to '{new_title}' for user {user_id}")

                # Use title-based update function
                result = await update_task_by_title_for_user(old_title, user_id, agent_context=agent_context, new_title=new_title)

                if result.get("status") == "success":
                    updated_title = result.get("task", {}).get("title", new_title)
                    logger.info(f"Task renamed from '{old_title}' to '{updated_title}' for user {user_id}")
                    message = f"ٹاسک کا نام '{updated_title}' میں تبدیل کر دیا گیا!" if urdu_update else None
                    return {
                        "status": "success",
                        "thread_id": thread_id,
                        "user_id": user_id,
                        "input": input,
                        "response_type": "task_updated",
                        "data": result,
                        "task_title": updated_title,
                        "urdu_message": message,
                        "context": [msg.content for msg in conversation_context[:5]]
                    }
                else:
                    logger.info(f"Task with title '{old_title}' not found for user {user_id}")
                    message = f"'{old_title}' نام کا ٹاسک نہیں ملا۔" if urdu_update else result.get("message", f"Could not find a task with title '{old_title}'.")
                    return {
                        "status": "success",
                        "thread_id": thread_id,
                        "user_id": user_id,
                        "input": input,
                        "response_type": "task_not_found",
                        "message": message,
                        "context": [msg.content for msg in conversation_context[:5]]
                    }

            # NEW PATTERN: Handle "update task old title with new title" (for renaming, not description) - without quotes
            update_title_with_title_no_quotes_pattern = r'(?:update|change|rename)\s+(?:task\s+)?(.+?)\s+with\s+(.+)$'
            match = re.search(update_title_with_title_no_quotes_pattern, input, re.IGNORECASE)

            if match:
                old_title_raw = match.group(1).strip().strip('"\'')
                new_title_raw = match.group(2).strip().strip('"\'')

                # Avoid matching commands like "update task with description" which should go to description update
                # Only match if both parts look like titles (not if second part contains "description", "note", etc.)
                second_part_lower = new_title_raw.lower()

                # Check if this is a "with title" command specifically
                if "title" in second_part_lower:
                    # Handle "update task 'old' with title 'new'" pattern
                    # Extract the new title after the word "title" and any quotes
                    title_parts = new_title_raw.split("title", 1)
                    if len(title_parts) > 1:
                        new_title = title_parts[1].strip().strip('"\'')
                        old_title = old_title_raw
                        logger.info(f"Renaming task (using 'with title') from '{old_title}' to '{new_title}' for user {user_id}")

                        # Use title-based update function
                        result = await update_task_by_title_for_user(old_title, user_id, agent_context=agent_context, new_title=new_title)

                        if result.get("status") == "success":
                            updated_title = result.get("task", {}).get("title", new_title)
                            logger.info(f"Task renamed from '{old_title}' to '{updated_title}' for user {user_id}")
                            message = f"ٹاسک کا نام '{updated_title}' میں تبدیل کر دیا گیا!" if urdu_update else None
                            return {
                                "status": "success",
                                "thread_id": thread_id,
                                "user_id": user_id,
                                "input": input,
                                "response_type": "task_updated",
                                "data": result,
                                "task_title": updated_title,
                                "urdu_message": message,
                                "context": [msg.content for msg in conversation_context[:5]]
                            }
                        else:
                            logger.info(f"Task with title '{old_title}' not found for user {user_id}")
                            message = f"'{old_title}' نام کا ٹاسک نہیں ملا۔" if urdu_update else result.get("message", f"Could not find a task with title '{old_title}'.")
                            return {
                                "status": "success",
                                "thread_id": thread_id,
                                "user_id": user_id,
                                "input": input,
                                "response_type": "task_not_found",
                                "message": message,
                                "context": [msg.content for msg in conversation_context[:5]]
                            }
                elif not any(keyword in second_part_lower for keyword in ["description", "note", "priority", "status"]):
                    # Handle regular "with" command (not with description/note/priority)
                    old_title = old_title_raw
                    new_title = new_title_raw
                    logger.info(f"Renaming task (using 'with', no quotes) from '{old_title}' to '{new_title}' for user {user_id}")

                    # Use title-based update function
                    result = await update_task_by_title_for_user(old_title, user_id, agent_context=agent_context, new_title=new_title)

                    if result.get("status") == "success":
                        updated_title = result.get("task", {}).get("title", new_title)
                        logger.info(f"Task renamed from '{old_title}' to '{updated_title}' for user {user_id}")
                        message = f"ٹاسک کا نام '{updated_title}' میں تبدیل کر دیا گیا!" if urdu_update else None
                        return {
                            "status": "success",
                            "thread_id": thread_id,
                            "user_id": user_id,
                            "input": input,
                            "response_type": "task_updated",
                            "data": result,
                            "task_title": updated_title,
                            "urdu_message": message,
                            "context": [msg.content for msg in conversation_context[:5]]
                        }
                    else:
                        logger.info(f"Task with title '{old_title}' not found for user {user_id}")
                        message = f"'{old_title}' نام کا ٹاسک نہیں ملا۔" if urdu_update else result.get("message", f"Could not find a task with title '{old_title}'.")
                        return {
                            "status": "success",
                            "thread_id": thread_id,
                            "user_id": user_id,
                            "input": input,
                            "response_type": "task_not_found",
                            "message": message,
                            "context": [msg.content for msg in conversation_context[:5]]
                        }

            # Pattern for "add description 'text' to task 'title'" or "add description 'text' of task 'title'"
            desc_task_pattern = r'add\s+description\s+[\'"]([^\'"]+)[\'"]\s+(?:to|of)\s+(?:task\s+)?[\'"]([^\'"]+)[\'"]'
            match = re.search(desc_task_pattern, input, re.IGNORECASE)
            if match:
                description = match.group(1)
                task_title = match.group(2)
                logger.info(f"Adding description to task '{task_title}' for user {user_id}")

                # Use title-based update function
                result = await update_task_by_title_for_user(task_title, user_id, agent_context=agent_context, description=description)

                if result.get("status") == "success":
                    updated_title = result.get("task", {}).get("title", task_title)
                    logger.info(f"Task '{updated_title}' updated with description for user {user_id}")
                    return {
                        "status": "success",
                        "thread_id": thread_id,
                        "user_id": user_id,
                        "input": input,
                        "response_type": "task_updated",
                        "data": result,
                        "task_title": updated_title,
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
                        "message": result.get("message", f"Could not find a task with title '{task_title}'."),
                        "context": [msg.content for msg in conversation_context[:5]]
                    }

            # Pattern for "update task 'title' with description 'text'" (with quotes)
            update_title_desc_pattern = r'update\s+(?:task\s+)?[\'"]([^\'"]+)[\'"]\s+with\s+description\s+[\'"]([^\'"]+)[\'"]'
            match = re.search(update_title_desc_pattern, input, re.IGNORECASE)

            # Also try pattern without quotes: "update task title with description: text"
            if not match:
                update_no_quotes_pattern = r'update\s+(?:task\s+)?(.+?)\s+with\s+description[:\s]+(.+)$'
                match = re.search(update_no_quotes_pattern, input, re.IGNORECASE)

            if match:
                task_title = match.group(1).strip().strip('"\'')
                description = match.group(2).strip().strip('"\'')
                logger.info(f"Updating task '{task_title}' with description for user {user_id}")

                # Use title-based update function
                result = await update_task_by_title_for_user(task_title, user_id, agent_context=agent_context, description=description)

                if result.get("status") == "success":
                    updated_title = result.get("task", {}).get("title", task_title)
                    logger.info(f"Task '{updated_title}' updated with description for user {user_id}")
                    return {
                        "status": "success",
                        "thread_id": thread_id,
                        "user_id": user_id,
                        "input": input,
                        "response_type": "task_updated",
                        "data": result,
                        "task_title": updated_title,
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
                        "message": result.get("message", f"Could not find a task with title '{task_title}'."),
                        "context": [msg.content for msg in conversation_context[:5]]
                    }

            # NEW: Pattern for "update task 'title' with priority 'high/medium/low'" (with quotes)
            update_priority_pattern = r'update\s+(?:task\s+)?[\'"]([^\'"]+)[\'"]\s+with\s+priority\s+(high|medium|low)'
            match = re.search(update_priority_pattern, input, re.IGNORECASE)

            # Also try pattern without quotes: "update task title with priority high"
            if not match:
                update_priority_no_quotes_pattern = r'update\s+(?:task\s+)?(.+?)\s+with\s+priority\s+(high|medium|low)'
                match = re.search(update_priority_no_quotes_pattern, input, re.IGNORECASE)

            if match:
                task_title = match.group(1).strip().strip('"\'')
                priority = match.group(2).strip()
                logger.info(f"Updating task '{task_title}' with priority '{priority}' for user {user_id}")

                # Use title-based update function with priority
                result = await update_task_by_title_for_user(task_title, user_id, agent_context=agent_context, priority=priority)

                if result.get("status") == "success":
                    updated_title = result.get("task", {}).get("title", task_title)
                    logger.info(f"Task '{updated_title}' updated with priority '{priority}' for user {user_id}")
                    return {
                        "status": "success",
                        "thread_id": thread_id,
                        "user_id": user_id,
                        "input": input,
                        "response_type": "task_updated",
                        "data": result,
                        "task_title": updated_title,
                        "priority": priority,
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
                        "message": result.get("message", f"Could not find a task with title '{task_title}'."),
                        "context": [msg.content for msg in conversation_context[:5]]
                    }

            # NEW: Pattern for "update task 'title' with title 'new title'" (for renaming with "with title")
            update_title_with_title_new_pattern = r'update\s+(?:task\s+)?[\'"]([^\'"]+)[\'"]\s+with\s+title\s+[\'"]([^\'"]+)[\'"]'
            match = re.search(update_title_with_title_new_pattern, input, re.IGNORECASE)

            # Also try pattern without quotes: "update task title with title new title"
            if not match:
                update_title_with_title_no_quotes_pattern = r'update\s+(?:task\s+)?(.+?)\s+with\s+title\s+(.+)$'
                match = re.search(update_title_with_title_no_quotes_pattern, input, re.IGNORECASE)

            if match:
                task_title = match.group(1).strip().strip('"\'')
                new_title = match.group(2).strip().strip('"\'')
                logger.info(f"Updating task '{task_title}' with new title '{new_title}' for user {user_id}")

                # Use title-based update function with new title
                result = await update_task_by_title_for_user(task_title, user_id, agent_context=agent_context, new_title=new_title)

                if result.get("status") == "success":
                    updated_title = result.get("task", {}).get("title", new_title)
                    logger.info(f"Task '{updated_title}' updated with new title '{new_title}' for user {user_id}")
                    return {
                        "status": "success",
                        "thread_id": thread_id,
                        "user_id": user_id,
                        "input": input,
                        "response_type": "task_updated",
                        "data": result,
                        "task_title": updated_title,
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
                        "message": result.get("message", f"Could not find a task with title '{task_title}'."),
                        "context": [msg.content for msg in conversation_context[:5]]
                    }

            # If no pattern matched, ask for clarification
            logger.info(f"Update request from user {user_id} didn't match any pattern")
            return {
                "status": "success",
                "thread_id": thread_id,
                "user_id": user_id,
                "input": input,
                "response_type": "request_task_id",
                "message": "Please specify which task to update. Examples:\n• update task \"title\" with description \"new description\"\n• edit task \"old title\" to \"new title\"\n• update task \"title\" with priority high\n• update task \"title\" with title \"new title\"",
                "context": [msg.content for msg in conversation_context[:5]]
            }

        # Check if user wants to complete a task (English + Urdu)
        complete_keywords_en = ["complete", "finish", "done", "mark complete", "mark as complete"]
        complete_keywords_ur = ["مکمل کرو", "ٹاسک مکمل", "کام مکمل", "ہو گیا"]
        urdu_complete = any(kw in input for kw in complete_keywords_ur)

        if any(input_lower.startswith(keyword) for keyword in complete_keywords_en) or urdu_complete:
            logger.info(f"User {user_id} requested to complete a task")

            # Try to extract task ID - only match "task N" or standalone number at end
            # Don't match numbers embedded in titles like "phase 2"
            task_id_match = re.search(r'\btask\s+(\d+)\b', input_lower) or re.search(r'(?:complete|finish|done|mark\s+(?:as\s+)?completed?)\s+(\d+)$', input_lower)

            # Try to extract task title in quotes: complete task "title" or complete "title"
            task_title_match = re.search(r'(?:complete|finish|done|mark\s+(?:as\s+)?completed?)\s+(?:task\s+)?[\'"]([^\'"]+)[\'"]', input, re.IGNORECASE)

            # Also try to extract title without quotes after keywords
            task_title_no_quotes = None

            # Urdu title extraction: "ٹاسک مکمل کرو ادا" -> "ادا"
            if urdu_complete and not task_title_match:
                for keyword in complete_keywords_ur:
                    if keyword in input:
                        idx = input.find(keyword) + len(keyword)
                        potential_title = input[idx:].strip()
                        if potential_title and not potential_title.isdigit():
                            task_title_no_quotes = potential_title
                            break

            if not task_title_match and not task_title_no_quotes:
                # Pattern: complete task <title> or mark as completed <title>
                no_quotes_match = re.search(r'(?:complete|finish|done|mark\s+(?:as\s+)?completed?)\s+(?:task\s+)?(.+)$', input, re.IGNORECASE)
                if no_quotes_match:
                    potential_title = no_quotes_match.group(1).strip()
                    # Make sure it's not just a number
                    if potential_title and not potential_title.isdigit():
                        task_title_no_quotes = potential_title

            # Prioritize title match over ID match when title contains numbers like "phase 2"
            if task_title_match or task_title_no_quotes:
                task_title = task_title_match.group(1) if task_title_match else task_title_no_quotes
                logger.info(f"Completing task by title: '{task_title}' for user {user_id}")

                # Use the title-based function
                result = await complete_task_by_title_for_user(task_title, user_id, completed=True, agent_context=agent_context)

                if result.get("status") == "success":
                    completed_title = result.get("task", {}).get("title", task_title)
                    logger.info(f"Task '{completed_title}' completed for user {user_id}")
                    return {
                        "status": "success",
                        "thread_id": thread_id,
                        "user_id": user_id,
                        "input": input,
                        "response_type": "task_completed",
                        "data": result,
                        "task_title": completed_title,
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
                        "message": result.get("message", f"Could not find a task with title '{task_title}'."),
                        "context": [msg.content for msg in conversation_context[:5]]
                    }
            elif task_id_match:
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
                logger.info(f"User {user_id} did not specify a task ID or title for completion")
                return {
                    "status": "success",
                    "thread_id": thread_id,
                    "user_id": user_id,
                    "input": input,
                    "response_type": "request_task_id",
                    "message": "Please specify which task you want to complete. You can use the task number or title (e.g., 'complete task 1' or 'complete buy groceries').",
                    "context": [msg.content for msg in conversation_context[:5]]
                }

        # Check if user wants to delete a task (English + Urdu)
        delete_keywords_en = ["delete", "remove", "remove task"]
        delete_keywords_ur = ["حذف کرو", "ٹاسک حذف", "ہٹاؤ", "مٹاؤ", "ٹاسک مٹاؤ"]
        urdu_delete = any(kw in input for kw in delete_keywords_ur)

        if any(keyword in input_lower for keyword in delete_keywords_en) or urdu_delete:
            logger.info(f"User {user_id} requested to delete a task")

            # Try to extract task ID - only match "task N" or standalone number at end
            task_id_match = re.search(r'\btask\s+(\d+)\b', input_lower) or re.search(r'(?:delete|remove)\s+(\d+)$', input_lower)

            # Try to extract task title in quotes: delete task "title" or delete "title"
            task_title_match = re.search(r'(?:delete|remove)\s+(?:task\s+)?[\'"]([^\'"]+)[\'"]', input, re.IGNORECASE)

            # Also try to extract title without quotes after keywords
            task_title_no_quotes = None

            # Urdu title extraction: "ٹاسک حذف کرو ادا" -> "ادا"
            if urdu_delete and not task_title_match:
                for keyword in delete_keywords_ur:
                    if keyword in input:
                        idx = input.find(keyword) + len(keyword)
                        potential_title = input[idx:].strip()
                        if potential_title and not potential_title.isdigit():
                            task_title_no_quotes = potential_title
                            break

            if not task_title_match and not task_title_no_quotes:
                # Pattern: delete task <title> or delete <title>
                no_quotes_match = re.search(r'(?:delete|remove)\s+(?:task\s+)?(.+)$', input, re.IGNORECASE)
                if no_quotes_match:
                    potential_title = no_quotes_match.group(1).strip()
                    # Make sure it's not just a number
                    if potential_title and not potential_title.isdigit():
                        task_title_no_quotes = potential_title

            # Prioritize title match over ID match when title contains numbers like "phase 2"
            if task_title_match or task_title_no_quotes:
                task_title = task_title_match.group(1) if task_title_match else task_title_no_quotes
                logger.info(f"Deleting task by title: '{task_title}' for user {user_id}")

                # Use the new title-based function
                result = await delete_task_by_title_for_user(task_title, user_id, agent_context=agent_context)

                if result.get("status") == "success":
                    deleted_title = result.get("deleted_title", task_title)
                    logger.info(f"Task '{deleted_title}' deleted for user {user_id}")
                    return {
                        "status": "success",
                        "thread_id": thread_id,
                        "user_id": user_id,
                        "input": input,
                        "response_type": "task_deleted",
                        "data": result,
                        "deleted_title": deleted_title,
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
                        "message": result.get("message", f"Could not find a task with title '{task_title}'."),
                        "context": [msg.content for msg in conversation_context[:5]]
                    }
            elif task_id_match:
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
                logger.info(f"User {user_id} did not specify a task ID or title for deletion")
                return {
                    "status": "success",
                    "thread_id": thread_id,
                    "user_id": user_id,
                    "input": input,
                    "response_type": "request_task_id",
                    "message": "Please specify which task you want to delete. You can use the task number or title (e.g., 'delete task 1' or 'delete buy groceries').",
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
            from ..services.task_service import complete_task, get_tasks_by_user_id
            result = complete_task(task_id, user_id, completed=True)

            if result:
                logger.info(f"Task {task_id} completed successfully for user {user_id}")
                # Create a success confirmation widget
                confirmation_widget = WidgetFactory.create_success_confirmation_widget(
                    f"Task '{result.title}' marked as completed!",
                    {"title": result.title}
                )

                # Get updated task list for widget refresh (T055/T059)
                updated_tasks = get_tasks_by_user_id(user_id)
                updated_task_list_widget = WidgetFactory.create_task_list_widget(updated_tasks) if updated_tasks else None

                return {
                    "status": "success",
                    "thread_id": thread_id,
                    "user_id": user_id,
                    "action_type": action_type,
                    "result": "task_completed",
                    "widget": confirmation_widget,
                    "updated_task_list": updated_task_list_widget,
                    "task_title": result.title
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

            # Get task title before deletion for confirmation message
            from ..services.task_service import delete_task, get_task_by_id, get_tasks_by_user_id
            task_to_delete = get_task_by_id(task_id, user_id)
            task_title = task_to_delete.title if task_to_delete else "Unknown"

            # Delete the task
            success = delete_task(task_id, user_id)

            if success:
                logger.info(f"Task {task_id} ('{task_title}') deleted successfully for user {user_id}")
                # Create a success confirmation widget
                confirmation_widget = WidgetFactory.create_success_confirmation_widget(
                    f"Task '{task_title}' deleted successfully!",
                    {"title": task_title}
                )

                # Get updated task list for widget refresh (T055/T059)
                updated_tasks = get_tasks_by_user_id(user_id)
                updated_task_list_widget = WidgetFactory.create_task_list_widget(updated_tasks) if updated_tasks else WidgetFactory.create_empty_state_widget("No tasks found")

                return {
                    "status": "success",
                    "thread_id": thread_id,
                    "user_id": user_id,
                    "action_type": action_type,
                    "result": "task_deleted",
                    "widget": confirmation_widget,
                    "updated_task_list": updated_task_list_widget,
                    "deleted_title": task_title
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
            from ..services.task_service import create_task, get_tasks_by_user_id
            task = create_task(title.strip(), description, user_id, priority)

            logger.info(f"Task {task.id} created successfully for user {user_id}: {task.title}")
            # Create a success confirmation widget
            confirmation_widget = WidgetFactory.create_success_confirmation_widget(
                f"Task '{task.title}' created successfully!",
                {"title": task.title, "description": task.description, "priority": task.priority.value}
            )

            # Get updated task list for widget refresh (T055/T059)
            updated_tasks = get_tasks_by_user_id(user_id)
            updated_task_list_widget = WidgetFactory.create_task_list_widget(updated_tasks) if updated_tasks else None

            return {
                "status": "success",
                "thread_id": thread_id,
                "user_id": user_id,
                "action_type": action_type,
                "result": "task_created",
                "widget": confirmation_widget,
                "updated_task_list": updated_task_list_widget,
                "task_title": task.title
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
                    # Try multiple paths to get the task title
                    task_title = (
                        result.get('data', {}).get('task', {}).get('title') or
                        result.get('data', {}).get('title') or
                        result.get('task_title') or
                        'the task'
                    )
                    yield json.dumps({"type": "message", "data": {"content": f"Done! I've marked '{task_title}' as completed."}})

                elif response_type == 'task_deleted':
                    # Try to get deleted task title from result
                    deleted_title = result.get('deleted_title') or result.get('data', {}).get('deleted_title', '')
                    if deleted_title:
                        yield json.dumps({"type": "message", "data": {"content": f"Task '{deleted_title}' has been deleted successfully!"}})
                    else:
                        yield json.dumps({"type": "message", "data": {"content": "Task deleted successfully!"}})

                elif response_type == 'request_task_details':
                    yield json.dumps({"type": "message", "data": {"content": "Please provide a title for the task you want to add."}})

                elif response_type == 'request_task_id':
                    yield json.dumps({"type": "message", "data": {"content": result.get('message', 'Please specify which task number.')}})

                elif response_type == 'task_updated':
                    # Try multiple paths to get the task title
                    task_title = (
                        result.get('data', {}).get('task', {}).get('title') or
                        result.get('data', {}).get('title') or
                        result.get('task_title') or
                        'the task'
                    )
                    yield json.dumps({"type": "message", "data": {"content": f"Task '{task_title}' has been updated successfully!"}})

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

                elif response_type == 'error':
                    yield json.dumps({"type": "message", "data": {"content": result.get('message', 'An error occurred.')}})

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
            import traceback
            error_trace = traceback.format_exc()
            logger.error(f"Error processing request: {str(e)}\n{error_trace}")

            async def generate_error():
                yield json.dumps({"type": "message", "data": {"content": f"Sorry, I encountered an error: {str(e)}"}})
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
