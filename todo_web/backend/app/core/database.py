"""Database connection and session management for Neon PostgreSQL."""

from sqlmodel import SQLModel, Session, create_engine
from typing import Generator
from .config import settings

# Import models to ensure they're registered with SQLModel metadata
from ..models import task, reminder, preference  # noqa: F401

# Create engine with Neon PostgreSQL connection
# Using connection pooling for serverless environment
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,  # Verify connections before use
    pool_size=5,
    max_overflow=10,
)


def create_db_and_tables() -> None:
    """Create all database tables."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Dependency to get database session."""
    with Session(engine) as session:
        yield session


# Async support for future use
async def init_db() -> None:
    """Initialize database - create tables if they don't exist."""
    create_db_and_tables()
