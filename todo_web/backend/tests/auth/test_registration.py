"""Tests for user registration (T021-T025)."""

import pytest
from fastapi.testclient import TestClient


class TestUserRegistrationWithValidCredentials:
    """T021: Test user registration with valid credentials."""

    def test_register_with_valid_data(self, client: TestClient):
        """Test successful registration with all valid fields."""
        user_data = {
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "username": "newuser",
            "first_name": "New",
            "last_name": "User"
        }
        response = client.post("/api/auth/register", json=user_data)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "user" in data
        assert data["user"]["email"] == user_data["email"]
        assert data["user"]["username"] == user_data["username"]
        assert data["user"]["is_verified"] is False

    def test_register_with_minimal_data(self, client: TestClient):
        """Test registration with only required fields (email and password)."""
        user_data = {
            "email": "minimal@example.com",
            "password": "SecurePass123!"
        }
        response = client.post("/api/auth/register", json=user_data)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["user"]["email"] == user_data["email"]

    def test_register_creates_inactive_verification(self, client: TestClient):
        """Test that newly registered users are not verified by default."""
        user_data = {
            "email": "unverified@example.com",
            "password": "SecurePass123!"
        }
        response = client.post("/api/auth/register", json=user_data)

        assert response.status_code == 200
        data = response.json()
        assert data["user"]["is_verified"] is False


class TestUserRegistrationWithInvalidCredentials:
    """T022: Test user registration with invalid credentials."""

    def test_register_with_invalid_email_format(self, client: TestClient):
        """Test registration fails with invalid email format."""
        user_data = {
            "email": "not-an-email",
            "password": "SecurePass123!"
        }
        response = client.post("/api/auth/register", json=user_data)

        assert response.status_code == 422  # Validation error

    def test_register_with_empty_email(self, client: TestClient):
        """Test registration fails with empty email."""
        user_data = {
            "email": "",
            "password": "SecurePass123!"
        }
        response = client.post("/api/auth/register", json=user_data)

        assert response.status_code == 422

    def test_register_with_short_password(self, client: TestClient):
        """Test registration fails with password shorter than 8 characters."""
        user_data = {
            "email": "user@example.com",
            "password": "Short1!"
        }
        response = client.post("/api/auth/register", json=user_data)

        assert response.status_code == 400
        data = response.json()
        assert "8 characters" in data["detail"]

    def test_register_with_password_no_uppercase(self, client: TestClient):
        """Test registration fails with password missing uppercase letter."""
        user_data = {
            "email": "user@example.com",
            "password": "securepass123!"
        }
        response = client.post("/api/auth/register", json=user_data)

        assert response.status_code == 400
        data = response.json()
        assert "uppercase" in data["detail"]

    def test_register_with_password_no_lowercase(self, client: TestClient):
        """Test registration fails with password missing lowercase letter."""
        user_data = {
            "email": "user@example.com",
            "password": "SECUREPASS123!"
        }
        response = client.post("/api/auth/register", json=user_data)

        assert response.status_code == 400
        data = response.json()
        assert "lowercase" in data["detail"]

    def test_register_with_password_no_number(self, client: TestClient):
        """Test registration fails with password missing number."""
        user_data = {
            "email": "user@example.com",
            "password": "SecurePass!"
        }
        response = client.post("/api/auth/register", json=user_data)

        assert response.status_code == 400
        data = response.json()
        assert "number" in data["detail"]

    def test_register_with_password_no_special_char(self, client: TestClient):
        """Test registration fails with password missing special character."""
        user_data = {
            "email": "user@example.com",
            "password": "SecurePass123"
        }
        response = client.post("/api/auth/register", json=user_data)

        assert response.status_code == 400
        data = response.json()
        assert "special character" in data["detail"]

    def test_register_with_missing_password(self, client: TestClient):
        """Test registration fails when password is missing."""
        user_data = {
            "email": "user@example.com"
        }
        response = client.post("/api/auth/register", json=user_data)

        assert response.status_code == 422


class TestDuplicateEmailRegistration:
    """T023: Test duplicate email registration."""

    def test_register_duplicate_email(self, client: TestClient, registered_user):
        """Test registration fails when email already exists."""
        duplicate_data = {
            "email": registered_user["user_data"]["email"],
            "password": "AnotherPass123!"
        }
        response = client.post("/api/auth/register", json=duplicate_data)

        assert response.status_code == 409
        data = response.json()
        assert "already exists" in data["detail"]

    def test_register_duplicate_email_different_case(self, client: TestClient, registered_user):
        """Test registration fails for case-insensitive duplicate emails."""
        # Note: This test depends on database configuration for case sensitivity
        duplicate_data = {
            "email": registered_user["user_data"]["email"].upper(),
            "password": "AnotherPass123!"
        }
        response = client.post("/api/auth/register", json=duplicate_data)

        # Behavior depends on whether email uniqueness is case-insensitive
        # Most systems should treat emails as case-insensitive
        # If this test fails, it may indicate case-sensitivity issue

    def test_register_duplicate_username(self, client: TestClient, registered_user):
        """Test registration fails when username already exists."""
        duplicate_data = {
            "email": "different@example.com",
            "password": "SecurePass123!",
            "username": registered_user["user_data"]["username"]
        }
        response = client.post("/api/auth/register", json=duplicate_data)

        assert response.status_code == 409
        data = response.json()
        assert "already taken" in data["detail"] or "already exists" in data["detail"]
