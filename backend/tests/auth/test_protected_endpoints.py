"""Tests for protected API endpoints (T077-T078)."""

import pytest
from fastapi.testclient import TestClient


class TestProtectedTaskEndpoints:
    """T077: Test protected task endpoints with valid/invalid tokens."""

    def test_list_tasks_with_valid_token(self, client: TestClient, registered_user):
        """Test listing tasks with valid authentication."""
        # Login to get tokens
        login_data = {
            "email": registered_user["user_data"]["email"],
            "password": registered_user["user_data"]["password"]
        }
        login_response = client.post("/api/auth/login", json=login_data)
        tokens = login_response.json()

        # List tasks
        response = client.get(
            "/api/tasks",
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data
        assert isinstance(data["tasks"], list)

    def test_list_tasks_without_token(self, client: TestClient):
        """Test listing tasks without authentication fails."""
        response = client.get("/api/tasks")

        assert response.status_code == 401

    def test_list_tasks_with_invalid_token(self, client: TestClient):
        """Test listing tasks with invalid token fails."""
        response = client.get(
            "/api/tasks",
            headers={"Authorization": "Bearer invalid-token"}
        )

        assert response.status_code == 401

    def test_create_task_with_valid_token(self, client: TestClient, registered_user):
        """Test creating a task with valid authentication."""
        # Login to get tokens
        login_data = {
            "email": registered_user["user_data"]["email"],
            "password": registered_user["user_data"]["password"]
        }
        login_response = client.post("/api/auth/login", json=login_data)
        tokens = login_response.json()

        # Create task
        task_data = {
            "title": "Test Task",
            "description": "Test Description",
            "priority": "medium"
        }
        response = client.post(
            "/api/tasks",
            json=task_data,
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Task"

    def test_create_task_without_token(self, client: TestClient):
        """Test creating a task without authentication fails."""
        task_data = {
            "title": "Test Task",
            "description": "Test Description",
            "priority": "medium"
        }
        response = client.post("/api/tasks", json=task_data)

        assert response.status_code == 401

    def test_user_can_only_access_own_tasks(self, client: TestClient, registered_user):
        """Test that users can only access their own tasks."""
        # Login with first user
        login_data = {
            "email": registered_user["user_data"]["email"],
            "password": registered_user["user_data"]["password"]
        }
        login_response = client.post("/api/auth/login", json=login_data)
        tokens = login_response.json()

        # Create a task
        task_data = {"title": "User 1 Task", "priority": "medium"}
        create_response = client.post(
            "/api/tasks",
            json=task_data,
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )
        task_id = create_response.json()["id"]

        # Create and login as second user
        second_user = {
            "email": "second@example.com",
            "password": "SecurePass123!",
            "username": "seconduser"
        }
        client.post("/api/auth/register", json=second_user)
        second_login = client.post("/api/auth/login", json={
            "email": second_user["email"],
            "password": second_user["password"]
        })
        second_tokens = second_login.json()

        # Try to access first user's task with second user's token
        response = client.get(
            f"/api/tasks/{task_id}",
            headers={"Authorization": f"Bearer {second_tokens['access_token']}"}
        )

        # Should return 404 (not found) because the task doesn't belong to this user
        assert response.status_code == 404


class TestProtectedPreferenceEndpoints:
    """Test protected preference endpoints."""

    def test_get_preferences_with_valid_token(self, client: TestClient, registered_user):
        """Test getting preferences with valid authentication."""
        # Login to get tokens
        login_data = {
            "email": registered_user["user_data"]["email"],
            "password": registered_user["user_data"]["password"]
        }
        login_response = client.post("/api/auth/login", json=login_data)
        tokens = login_response.json()

        # Get preferences
        response = client.get(
            "/api/preferences",
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )

        assert response.status_code == 200

    def test_get_preferences_without_token(self, client: TestClient):
        """Test getting preferences without authentication fails."""
        response = client.get("/api/preferences")

        assert response.status_code == 401


class TestProtectedReminderEndpoints:
    """Test protected reminder endpoints."""

    def test_list_reminders_with_valid_token(self, client: TestClient, registered_user):
        """Test listing reminders with valid authentication."""
        # Login to get tokens
        login_data = {
            "email": registered_user["user_data"]["email"],
            "password": registered_user["user_data"]["password"]
        }
        login_response = client.post("/api/auth/login", json=login_data)
        tokens = login_response.json()

        # List reminders
        response = client.get(
            "/api/reminders",
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "reminders" in data

    def test_list_reminders_without_token(self, client: TestClient):
        """Test listing reminders without authentication fails."""
        response = client.get("/api/reminders")

        assert response.status_code == 401
