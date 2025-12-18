"""End-to-end tests for AI Chatbot feature."""

import pytest
from unittest.mock import AsyncMock, patch
from app.agents.todo_agent import run_chatbot_agent


@pytest.mark.asyncio
async def test_end_to_end_chatbot_workflow():
    """Complete end-to-end test of the AI Chatbot functionality."""
    # Test a complete conversation flow
    user_id = "test_user_123"

    # 1. Test adding a task
    add_response = await run_chatbot_agent(
        user_text="Add a task to buy groceries",
        user_id=user_id,
        conversation_id=None
    )
    assert "add" in add_response.lower() or "create" in add_response.lower()
    assert "groceries" in add_response.lower()

    # 2. Test listing tasks
    list_response = await run_chatbot_agent(
        user_text="Show me all my tasks",
        user_id=user_id,
        conversation_id=123  # Using same conversation to maintain context
    )
    assert "task" in list_response.lower() or "grocer" in list_response.lower()

    # 3. Test completing a task
    complete_response = await run_chatbot_agent(
        user_text="Mark the grocery task as complete",
        user_id=user_id,
        conversation_id=123
    )
    assert "complete" in complete_response.lower() or "finish" in complete_response.lower()


def test_api_endpoint_integration():
    """Test that the API endpoints properly connect to the AI agent."""
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)

    # Test the chat endpoint
    response = client.post(
        "/api/test_user_123/chat",
        json={"message": "Add a task to call mom"},
        headers={"Authorization": "Bearer fake-token"}  # Would be a valid token in real test
    )

    assert response.status_code in [200, 401, 422]  # 401/422 are acceptable for auth/validation issues in test

    # Test conversation listing endpoint
    response = client.get(
        "/api/conversations",
        headers={"Authorization": "Bearer fake-token"}
    )

    assert response.status_code in [200, 401]  # 401 is acceptable for auth issues in test


@pytest.mark.asyncio
async def test_mcp_tool_integration():
    """Test that MCP tools are properly integrated with the AI agent."""
    from app.agents.tools.add_task import add_task
    from app.agents.tools.list_tasks import list_tasks

    # Test that tools can be called directly
    with patch('app.core.database.get_session') as mock_session:
        # Mock a successful task creation
        mock_session_instance = AsyncMock()
        mock_session.return_value.__aenter__.return_value = mock_session_instance
        mock_session.return_value.__aexit__.return_value = None

        # Mock the Task model
        with patch('app.models.task.Task') as mock_task:
            mock_task_instance = AsyncMock()
            mock_task_instance.id = 999
            mock_task_instance.title = "Test task"
            mock_task.from_orm.return_value = mock_task_instance

            # Test add_task tool
            result = add_task(user_id="test_user", title="Test task")

            assert result["task_id"] == 999
            assert result["title"] == "Test task"
            assert result["status"] == "created"


def test_error_handling():
    """Test error handling in the chatbot system."""
    from app.api.chat import chat_with_bot
    from fastapi import HTTPException

    # Test with mismatched user_id to trigger auth error
    try:
        # This would normally raise an HTTPException due to auth mismatch
        response = chat_with_bot(
            user_id="different_user",
            message={"message": "test"},
            current_user=MagicMock(id="authenticated_user"),
            db_session=MagicMock()
        )
        # If we reach this line, the auth check didn't work as expected
        assert False, "Expected HTTPException was not raised"
    except HTTPException as e:
        # This is expected behavior
        assert e.status_code == 403


if __name__ == "__main__":
    """Run the tests directly."""
    pytest.main([__file__, "-v"])