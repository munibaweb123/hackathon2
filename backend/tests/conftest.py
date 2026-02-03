"""Pytest configuration and fixtures for backend tests."""

import os
import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool

from app.main import app
from app.core.database import get_session


@pytest.fixture(name="session")
def session_fixture():
    """Create a database session for testing.

    Uses PostgreSQL if DATABASE_URL is set (CI environment),
    otherwise falls back to SQLite for local testing.
    """
    database_url = os.environ.get("DATABASE_URL")

    if database_url and database_url.startswith("postgresql"):
        # Use PostgreSQL for CI/integration tests
        engine = create_engine(database_url, echo=False)
        SQLModel.metadata.create_all(engine)
        with Session(engine) as session:
            yield session
        # Clean up tables after test
        SQLModel.metadata.drop_all(engine)
    else:
        # Fall back to SQLite for quick local tests
        # Note: Some PostgreSQL features like ARRAY won't work with SQLite
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
