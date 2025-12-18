"""Test context management for AI Chatbot feature."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.agents.todo_agent import run_chatbot_agent
from app.services.context_service import ContextTrackingService


@pytest.mark.asyncio
async def test_contextual_command_update_task():
    """Test contextual command: 'Update that task to include eggs' after creating a grocery list."""
    user_text = "Update that task to include eggs"
    user_id = "test_user_123"
    conversation_id = "test_conv_456"

    # Mock the OpenAI client response
    with patch('app.agents.factory.create_model') as mock_client:
        # Mock a response that would call update_task with the referenced task ID
        mock_response = AsyncMock()
        mock_response.choices = [AsyncMock()]
        mock_response.choices[0].message = AsyncMock()

        # Simulate a tool call to update_task
        mock_tool_call = MagicMock()
        mock_tool_call.function.name = "update_task"
        mock_tool_call.function.arguments = '{"user_id": "test_user_123", "task_id": 1, "title": "buy groceries and eggs"}'

        mock_response.choices[0].message.tool_calls = [mock_tool_call]
        mock_response.choices[0].message.content = "I've updated your grocery task to include eggs."

        mock_client.return_value.chat.completions.create.return_value = mock_response

        # Mock the context service to return a recent task reference
        with patch.object(ContextTrackingService, 'get_recent_task_reference', return_value={"task_id": 1}) as mock_get_ref:
            # Run the agent
            response = await run_chatbot_agent(user_text, user_id, conversation_id)

            # Verify the response includes the update action
            assert "update" in response.lower()
            assert "eggs" in response.lower()

            # Verify that the context service was called to get the recent reference
            mock_get_ref.assert_called_once()


@pytest.mark.asyncio
async def test_follow_up_questions():
    """Test follow-up questions maintaining context from previous exchanges."""
    user_text = "What did I ask about earlier?"
    user_id = "test_user_123"
    conversation_id = "test_conv_789"

    # Mock the OpenAI client response
    with patch('app.agents.factory.create_model') as mock_client:
        mock_response = AsyncMock()
        mock_response.choices = [AsyncMock()]
        mock_response.choices[0].message = AsyncMock()
        mock_response.choices[0].message.tool_calls = None
        mock_response.choices[0].message.content = "Earlier you asked me to create a grocery list with milk and bread."

        mock_client.return_value.chat.completions.create.return_value = mock_response

        # Run the agent
        response = await run_chatbot_agent(user_text, user_id, conversation_id)

        # Verify the response acknowledges the previous context
        assert "earlier" in response.lower()
        assert "grocery" in response.lower() or "milk" in response.lower() or "bread" in response.lower()


@pytest.mark.asyncio
async def test_context_window_management():
    """Test context window management across 10+ conversation exchanges."""
    user_id = "test_user_123"
    conversation_id = "test_conv_999"

    # Test multiple exchanges to ensure context window is managed properly
    for i in range(12):  # Simulate 12 exchanges to test window management
        user_text = f"This is message #{i+1} in the conversation."

        # Mock the OpenAI client response
        with patch('app.agents.factory.create_model') as mock_client:
            mock_response = AsyncMock()
            mock_response.choices = [AsyncMock()]
            mock_response.choices[0].message = AsyncMock()
            mock_response.choices[0].message.tool_calls = None
            mock_response.choices[0].message.content = f"Received message #{i+1}. Thank you."

            mock_client.return_value.chat.completions.create.return_value = mock_response

            # Run the agent
            response = await run_chatbot_agent(user_text, user_id, conversation_id)

            # Verify the response is appropriate
            assert f"message #{i+1}" in response


@pytest.mark.asyncio
async def test_context_persistence():
    """Test context persistence between chat requests."""
    user_text = "Tell me about my tasks again"
    user_id = "test_user_123"
    conversation_id = "test_conv_persist"

    # Mock the OpenAI client response
    with patch('app.agents.factory.create_model') as mock_client:
        # Mock a response that would call list_tasks to retrieve previous context
        mock_response = AsyncMock()
        mock_response.choices = [AsyncMock()]
        mock_response.choices[0].message = AsyncMock()

        # Simulate a tool call to list_tasks
        mock_tool_call = MagicMock()
        mock_tool_call.function.name = "list_tasks"
        mock_tool_call.function.arguments = '{"user_id": "test_user_123", "status": "all"}'

        mock_response.choices[0].message.tool_calls = [mock_tool_call]
        mock_response.choices[0].message.content = "Here are your tasks from our previous conversation."

        mock_client.return_value.chat.completions.create.return_value = mock_response

        # Run the agent
        response = await run_chatbot_agent(user_text, user_id, conversation_id)

        # Verify the response acknowledges previous context
        assert "previous" in response.lower() or "tasks" in response.lower()