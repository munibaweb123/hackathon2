"""Tests for session management (T046-T052)."""

import pytest
from fastapi.testclient import TestClient


class TestLogoutFunctionality:
    """T046: Test logout functionality."""

    def test_logout_with_valid_token(self, client: TestClient, registered_user):
        """Test successful logout with valid token."""
        # First login to get tokens
        login_data = {
            "email": registered_user["user_data"]["email"],
            "password": registered_user["user_data"]["password"]
        }
        login_response = client.post("/api/auth/login", json=login_data)
        tokens = login_response.json()

        # Then logout
        response = client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "logged out" in data["message"].lower()

    def test_logout_without_token(self, client: TestClient):
        """Test logout fails without token."""
        response = client.post("/api/auth/logout")

        assert response.status_code == 401


class TestGetCurrentUser:
    """T047-T048: Test get current user endpoint."""

    def test_get_current_user_with_valid_token(self, client: TestClient, registered_user):
        """T047: Test get current user with valid token."""
        # First login to get tokens
        login_data = {
            "email": registered_user["user_data"]["email"],
            "password": registered_user["user_data"]["password"]
        }
        login_response = client.post("/api/auth/login", json=login_data)
        tokens = login_response.json()

        # Get current user
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        assert data["user"]["email"] == registered_user["user_data"]["email"]

    def test_get_current_user_with_invalid_token(self, client: TestClient):
        """T048: Test get current user with invalid token."""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid-token-here"}
        )

        assert response.status_code == 401

    def test_get_current_user_without_token(self, client: TestClient):
        """Test get current user without token."""
        response = client.get("/api/auth/me")

        assert response.status_code == 401

    def test_get_current_user_with_expired_token(self, client: TestClient):
        """Test get current user with expired token."""
        # This would require creating an expired token
        # For now, we test with a malformed token
        expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMTIzIiwiZXhwIjoxfQ.invalid"
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"}
        )

        assert response.status_code == 401


class TestTokenRefresh:
    """T049: Test token refresh."""

    def test_refresh_token_with_valid_refresh_token(self, client: TestClient, registered_user):
        """Test token refresh with valid refresh token."""
        # First login to get tokens
        login_data = {
            "email": registered_user["user_data"]["email"],
            "password": registered_user["user_data"]["password"]
        }
        login_response = client.post("/api/auth/login", json=login_data)
        tokens = login_response.json()

        # Refresh token
        response = client.post(
            "/api/auth/refresh",
            json={"refresh_token": tokens["refresh_token"]}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        # New tokens should be different from old ones
        assert data["access_token"] != tokens["access_token"]

    def test_refresh_token_with_invalid_refresh_token(self, client: TestClient):
        """Test token refresh fails with invalid refresh token."""
        response = client.post(
            "/api/auth/refresh",
            json={"refresh_token": "invalid-refresh-token"}
        )

        assert response.status_code == 401

    def test_refresh_token_without_token(self, client: TestClient):
        """Test token refresh fails without token."""
        response = client.post("/api/auth/refresh", json={})

        assert response.status_code in [400, 422]

    def test_refresh_token_with_access_token(self, client: TestClient, registered_user):
        """Test that access token cannot be used as refresh token."""
        # First login to get tokens
        login_data = {
            "email": registered_user["user_data"]["email"],
            "password": registered_user["user_data"]["password"]
        }
        login_response = client.post("/api/auth/login", json=login_data)
        tokens = login_response.json()

        # Try to use access token as refresh token
        response = client.post(
            "/api/auth/refresh",
            json={"refresh_token": tokens["access_token"]}
        )

        # Should fail because access tokens don't have the refresh type
        assert response.status_code == 401


class TestProtectedRouteAccess:
    """Test access to protected routes."""

    def test_protected_route_with_valid_token(self, client: TestClient, registered_user):
        """Test accessing protected route with valid token."""
        # First login to get tokens
        login_data = {
            "email": registered_user["user_data"]["email"],
            "password": registered_user["user_data"]["password"]
        }
        login_response = client.post("/api/auth/login", json=login_data)
        tokens = login_response.json()
        user_id = tokens["user"]["id"]

        # Try to access user's tasks (protected route)
        response = client.get(
            f"/api/{user_id}/tasks",
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )

        # Should succeed (200 for existing tasks, or empty list)
        assert response.status_code == 200

    def test_protected_route_without_token(self, client: TestClient):
        """Test accessing protected route without token."""
        response = client.get("/api/some-user-id/tasks")

        assert response.status_code == 401
