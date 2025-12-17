"""Application configuration using Pydantic Settings."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "Todo Web API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Database - Neon Serverless PostgreSQL
    DATABASE_URL: str = "postgresql://user:password@host/dbname"

    # Authentication - Better Auth
    BETTER_AUTH_URL: str = "http://localhost:3000"  # Next.js frontend URL where Better Auth runs
    BETTER_AUTH_SECRET: str = "your-secret-key-here"  # Kept for potential JWT fallback

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # API
    API_PREFIX: str = "/api"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
