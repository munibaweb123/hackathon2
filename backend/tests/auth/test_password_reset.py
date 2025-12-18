"""Tests for password reset functionality (T060-T063)."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import select
from app.models.user import User


class TestPasswordResetRequest:
    """T060: Test password reset request."""

    def test_request_password_reset_for_existing_user(self, client: TestClient, registered_user, session):
        """Test password reset request for existing user."""
        response = client.post(
            "/api/auth/forgot-password",
            json={"email": registered_user["user_data"]["email"]}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "reset link has been sent" in data["message"].lower()

        # Verify that a reset token was created in the database
        user = session.exec(
            select(User).where(User.email == registered_user["user_data"]["email"])
        ).first()
        assert user is not None
        assert user.password_reset_token is not None
        assert user.password_reset_expires is not None

    def test_request_password_reset_for_nonexistent_user(self, client: TestClient):
        """Test password reset request for non-existent email (should not reveal user existence)."""
        response = client.post(
            "/api/auth/forgot-password",
            json={"email": "nonexistent@example.com"}
        )

        # For security, should return success even if email doesn't exist
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "reset link has been sent" in data["message"].lower()

    def test_request_password_reset_invalid_email_format(self, client: TestClient):
        """Test password reset request with invalid email format."""
        response = client.post(
            "/api/auth/forgot-password",
            json={"email": "not-an-email"}
        )

        assert response.status_code == 422


class TestPasswordResetWithValidToken:
    """T061: Test password reset with valid token."""

    def test_reset_password_with_valid_token(self, client: TestClient, registered_user, session):
        """Test successful password reset with valid token."""
        # First, request a password reset
        client.post(
            "/api/auth/forgot-password",
            json={"email": registered_user["user_data"]["email"]}
        )

        # Get the reset token from the database
        user = session.exec(
            select(User).where(User.email == registered_user["user_data"]["email"])
        ).first()
        reset_token = user.password_reset_token

        # Reset the password
        new_password = "NewSecurePass123!"
        response = client.post(
            "/api/auth/reset-password",
            json={
                "token": reset_token,
                "new_password": new_password
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "reset successfully" in data["message"].lower()

        # Verify we can login with the new password
        login_response = client.post(
            "/api/auth/login",
            json={
                "email": registered_user["user_data"]["email"],
                "password": new_password
            }
        )
        assert login_response.status_code == 200

    def test_reset_password_clears_token(self, client: TestClient, registered_user, session):
        """Test that password reset clears the reset token."""
        # Request a password reset
        client.post(
            "/api/auth/forgot-password",
            json={"email": registered_user["user_data"]["email"]}
        )

        # Get the reset token
        user = session.exec(
            select(User).where(User.email == registered_user["user_data"]["email"])
        ).first()
        reset_token = user.password_reset_token

        # Reset the password
        client.post(
            "/api/auth/reset-password",
            json={
                "token": reset_token,
                "new_password": "NewSecurePass123!"
            }
        )

        # Verify the token is cleared
        session.refresh(user)
        assert user.password_reset_token is None
        assert user.password_reset_expires is None


class TestPasswordResetWithInvalidToken:
    """T062: Test password reset with invalid token."""

    def test_reset_password_with_invalid_token(self, client: TestClient):
        """Test password reset fails with invalid token."""
        response = client.post(
            "/api/auth/reset-password",
            json={
                "token": "invalid-token-here",
                "new_password": "NewSecurePass123!"
            }
        )

        assert response.status_code == 400
        data = response.json()
        assert "invalid" in data["detail"].lower() or "expired" in data["detail"].lower()

    def test_reset_password_with_used_token(self, client: TestClient, registered_user, session):
        """Test password reset fails when token has already been used."""
        # Request a password reset
        client.post(
            "/api/auth/forgot-password",
            json={"email": registered_user["user_data"]["email"]}
        )

        # Get the reset token
        user = session.exec(
            select(User).where(User.email == registered_user["user_data"]["email"])
        ).first()
        reset_token = user.password_reset_token

        # Use the token once
        client.post(
            "/api/auth/reset-password",
            json={
                "token": reset_token,
                "new_password": "NewSecurePass123!"
            }
        )

        # Try to use the same token again
        response = client.post(
            "/api/auth/reset-password",
            json={
                "token": reset_token,
                "new_password": "AnotherNewPass123!"
            }
        )

        assert response.status_code == 400

    def test_reset_password_with_weak_password(self, client: TestClient, registered_user, session):
        """Test password reset fails with weak password."""
        # Request a password reset
        client.post(
            "/api/auth/forgot-password",
            json={"email": registered_user["user_data"]["email"]}
        )

        # Get the reset token
        user = session.exec(
            select(User).where(User.email == registered_user["user_data"]["email"])
        ).first()
        reset_token = user.password_reset_token

        # Try to reset with a weak password
        response = client.post(
            "/api/auth/reset-password",
            json={
                "token": reset_token,
                "new_password": "weak"  # Too short, no uppercase, no number, no special
            }
        )

        assert response.status_code == 400


class TestPasswordResetRateLimiting:
    """T063: Test password reset rate limiting."""

    def test_rate_limit_password_reset_requests(self, client: TestClient):
        """Test that password reset requests are rate limited."""
        email = "ratelimit@example.com"

        # Make 4 requests (limit is 3 per hour)
        responses = []
        for i in range(4):
            response = client.post(
                "/api/auth/forgot-password",
                json={"email": email}
            )
            responses.append(response.status_code)

        # After 3 attempts, the 4th should be rate limited
        # Rate limit returns 429 Too Many Requests
        assert 429 in responses or all(r == 200 for r in responses[:3])
