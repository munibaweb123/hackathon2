"""Pytest configuration and fixtures for backend tests."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool

from app.main import app
from app.core.database import get_session


@pytest.fixture(name="session")
def session_fixture():
    """Create an in-memory SQLite database session for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create a test client with dependency overrides."""

    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def valid_user_data():
    """Valid user registration data."""
    return {
        "email": "test@example.com",
        "password": "SecurePass123!",
        "username": "testuser",
        "first_name": "Test",
        "last_name": "User"
    }


@pytest.fixture
def registered_user(client, valid_user_data):
    """Create a registered user and return the user data with tokens."""
    response = client.post("/api/auth/register", json=valid_user_data)
    assert response.status_code == 200 or response.status_code == 201
    return {
        "user_data": valid_user_data,
        "response": response.json()
    }
