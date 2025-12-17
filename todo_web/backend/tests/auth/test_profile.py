"""Tests for user profile management (T070-T071)."""

import pytest
from fastapi.testclient import TestClient


class TestUpdateUserProfile:
    """T070: Test update user profile functionality."""

    def test_update_profile_with_valid_data(self, client: TestClient, registered_user):
        """Test successful profile update."""
        # First login to get tokens
        login_data = {
            "email": registered_user["user_data"]["email"],
            "password": registered_user["user_data"]["password"]
        }
        login_response = client.post("/api/auth/login", json=login_data)
        tokens = login_response.json()

        # Update profile
        profile_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "username": "updateduser"
        }
        response = client.put(
            "/api/users/profile",
            json=profile_data,
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Updated"
        assert data["last_name"] == "Name"
        assert data["username"] == "updateduser"

    def test_update_profile_partial_data(self, client: TestClient, registered_user):
        """Test partial profile update (only some fields)."""
        # First login to get tokens
        login_data = {
            "email": registered_user["user_data"]["email"],
            "password": registered_user["user_data"]["password"]
        }
        login_response = client.post("/api/auth/login", json=login_data)
        tokens = login_response.json()

        # Update only first name
        profile_data = {
            "first_name": "OnlyFirst"
        }
        response = client.put(
            "/api/users/profile",
            json=profile_data,
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "OnlyFirst"

    def test_update_profile_without_token(self, client: TestClient):
        """Test profile update fails without authentication."""
        profile_data = {
            "first_name": "Test"
        }
        response = client.put("/api/users/profile", json=profile_data)

        assert response.status_code == 401

    def test_update_profile_duplicate_username(self, client: TestClient, registered_user):
        """Test profile update fails with duplicate username."""
        # First login to get tokens
        login_data = {
            "email": registered_user["user_data"]["email"],
            "password": registered_user["user_data"]["password"]
        }
        login_response = client.post("/api/auth/login", json=login_data)
        tokens = login_response.json()

        # Create another user with a specific username
        other_user = {
            "email": "other@example.com",
            "password": "SecurePass123!",
            "username": "takenusername"
        }
        client.post("/api/auth/register", json=other_user)

        # Try to update our profile with the taken username
        profile_data = {
            "username": "takenusername"
        }
        response = client.put(
            "/api/users/profile",
            json=profile_data,
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )

        assert response.status_code == 409
        data = response.json()
        assert "already taken" in data["detail"].lower()

    def test_update_profile_with_invalid_token(self, client: TestClient):
        """Test profile update fails with invalid token."""
        profile_data = {
            "first_name": "Test"
        }
        response = client.put(
            "/api/users/profile",
            json=profile_data,
            headers={"Authorization": "Bearer invalid-token"}
        )

        assert response.status_code == 401
