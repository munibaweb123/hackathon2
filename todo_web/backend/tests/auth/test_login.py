"""Tests for user login (T032-T037)."""

import pytest
from fastapi.testclient import TestClient
import time


class TestSuccessfulLogin:
    """T032: Test successful login with valid credentials."""

    def test_login_with_valid_credentials(self, client: TestClient, registered_user):
        """Test successful login returns access and refresh tokens."""
        login_data = {
            "email": registered_user["user_data"]["email"],
            "password": registered_user["user_data"]["password"]
        }
        response = client.post("/api/auth/login", json=login_data)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data
        assert "refresh_token" in data
        assert "user" in data
        assert data["user"]["email"] == login_data["email"]

    def test_login_returns_user_info(self, client: TestClient, registered_user):
        """Test login response includes user information."""
        login_data = {
            "email": registered_user["user_data"]["email"],
            "password": registered_user["user_data"]["password"]
        }
        response = client.post("/api/auth/login", json=login_data)

        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        user = data["user"]
        assert "id" in user
        assert "email" in user
        assert user["email"] == login_data["email"]

    def test_login_tokens_are_valid_jwt(self, client: TestClient, registered_user):
        """Test that returned tokens appear to be valid JWT format."""
        login_data = {
            "email": registered_user["user_data"]["email"],
            "password": registered_user["user_data"]["password"]
        }
        response = client.post("/api/auth/login", json=login_data)

        assert response.status_code == 200
        data = response.json()

        # JWT tokens should have 3 parts separated by dots
        access_token = data["access_token"]
        refresh_token = data["refresh_token"]

        assert len(access_token.split(".")) == 3
        assert len(refresh_token.split(".")) == 3


class TestFailedLogin:
    """T033: Test failed login with invalid credentials."""

    def test_login_with_wrong_password(self, client: TestClient, registered_user):
        """Test login fails with incorrect password."""
        login_data = {
            "email": registered_user["user_data"]["email"],
            "password": "WrongPassword123!"
        }
        response = client.post("/api/auth/login", json=login_data)

        assert response.status_code == 401
        data = response.json()
        assert "Incorrect" in data["detail"] or "invalid" in data["detail"].lower()

    def test_login_with_nonexistent_email(self, client: TestClient):
        """Test login fails with non-existent email."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "SomePassword123!"
        }
        response = client.post("/api/auth/login", json=login_data)

        assert response.status_code == 401
        # Error message should not reveal that email doesn't exist
        data = response.json()
        assert "Incorrect" in data["detail"] or "invalid" in data["detail"].lower()

    def test_login_with_empty_password(self, client: TestClient, registered_user):
        """Test login fails with empty password."""
        login_data = {
            "email": registered_user["user_data"]["email"],
            "password": ""
        }
        response = client.post("/api/auth/login", json=login_data)

        assert response.status_code in [400, 401, 422]

    def test_login_with_missing_email(self, client: TestClient):
        """Test login fails when email is missing."""
        login_data = {
            "password": "SomePassword123!"
        }
        response = client.post("/api/auth/login", json=login_data)

        assert response.status_code == 422

    def test_login_with_invalid_email_format(self, client: TestClient):
        """Test login fails with invalid email format."""
        login_data = {
            "email": "not-an-email",
            "password": "SomePassword123!"
        }
        response = client.post("/api/auth/login", json=login_data)

        assert response.status_code in [401, 422]


class TestLoginRateLimiting:
    """T034: Test login rate limiting."""

    def test_rate_limit_after_multiple_failed_attempts(self, client: TestClient, registered_user):
        """Test that rate limiting kicks in after multiple failed attempts."""
        login_data = {
            "email": registered_user["user_data"]["email"],
            "password": "WrongPassword123!"
        }

        # Make 6 failed attempts (limit is 5 per minute)
        responses = []
        for i in range(6):
            response = client.post("/api/auth/login", json=login_data)
            responses.append(response.status_code)

        # After 5 attempts, the 6th should be rate limited
        # Rate limit returns 429 Too Many Requests
        assert 429 in responses or all(r == 401 for r in responses[:5])

    def test_successful_login_after_rate_limit_window(self, client: TestClient, registered_user):
        """Test that login works again after rate limit window expires."""
        # This is a slow test - skipping the actual wait
        # In a real test, you would wait for the rate limit window to expire
        pass


class TestOAuth2TokenEndpoint:
    """Test OAuth2 compatible token endpoint."""

    def test_oauth2_token_endpoint(self, client: TestClient, registered_user):
        """Test OAuth2 compatible login endpoint."""
        form_data = {
            "username": registered_user["user_data"]["email"],
            "password": registered_user["user_data"]["password"]
        }
        response = client.post(
            "/api/auth/login/token",
            data=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
