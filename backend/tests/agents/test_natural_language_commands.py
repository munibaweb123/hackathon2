"""Test natural language commands for AI Chatbot feature."""

import pytest
from unittest.mock import AsyncMock, patch
from app.agents.todo_agent import run_chatbot_agent


@pytest.mark.asyncio
async def test_add_task_command():
    """Test natural language command: 'Add a task to buy groceries'."""
    user_text = "Add a task to buy groceries"
    user_id = "test_user_123"

    # Mock the OpenAI client response
    with patch('app.agents.factory.create_model') as mock_client:
        mock_response = AsyncMock()
        mock_response.choices = [AsyncMock()]
        mock_response.choices[0].message = AsyncMock()
        mock_response.choices[0].message.tool_calls = None
        mock_response.choices[0].message.content = "I've added the task 'buy groceries' to your list."

        mock_client.return_value.chat.completions.create.return_value = mock_response

        # Run the agent
        response = await run_chatbot_agent(user_text, user_id)

        # Verify the response
        assert "buy groceries" in response.lower()
        assert "add" in response.lower()


@pytest.mark.asyncio
async def test_show_all_tasks_command():
    """Test natural language command: 'Show me all my tasks'."""
    user_text = "Show me all my tasks"
    user_id = "test_user_123"

    # Mock the OpenAI client response
    with patch('app.agents.factory.create_model') as mock_client:
        mock_response = AsyncMock()
        mock_response.choices = [AsyncMock()]
        mock_response.choices[0].message = AsyncMock()
        mock_response.choices[0].message.tool_calls = None
        mock_response.choices[0].message.content = "Here are all your tasks: Buy groceries, Call mom, Pay bills."

        mock_client.return_value.chat.completions.create.return_value = mock_response

        # Run the agent
        response = await run_chatbot_agent(user_text, user_id)

        # Verify the response
        assert "tasks" in response.lower()


@pytest.mark.asyncio
async def test_pending_tasks_command():
    """Test natural language command: 'What's pending?'."""
    user_text = "What's pending?"
    user_id = "test_user_123"

    # Mock the OpenAI client response
    with patch('app.agents.factory.create_model') as mock_client:
        mock_response = AsyncMock()
        mock_response.choices = [AsyncMock()]
        mock_response.choices[0].message = AsyncMock()
        mock_response.choices[0].message.tool_calls = None
        mock_response.choices[0].message.content = "Here are your pending tasks: Buy groceries, Call mom."

        mock_client.return_value.chat.completions.create.return_value = mock_response

        # Run the agent
        response = await run_chatbot_agent(user_text, user_id)

        # Verify the response
        assert "pending" in response.lower()


@pytest.mark.asyncio
async def test_complete_task_command():
    """Test natural language command: 'Mark task 3 as complete'."""
    user_text = "Mark task 3 as complete"
    user_id = "test_user_123"

    # Mock the OpenAI client response
    with patch('app.agents.factory.create_model') as mock_client:
        mock_response = AsyncMock()
        mock_response.choices = [AsyncMock()]
        mock_response.choices[0].message = AsyncMock()
        mock_response.choices[0].message.tool_calls = None
        mock_response.choices[0].message.content = "I've marked task 3 as complete."

        mock_client.return_value.chat.completions.create.return_value = mock_response

        # Run the agent
        response = await run_chatbot_agent(user_text, user_id)

        # Verify the response
        assert "complete" in response.lower()
        assert "3" in response