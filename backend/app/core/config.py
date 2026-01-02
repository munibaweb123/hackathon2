"""Application configuration using Pydantic Settings."""

import json
from pydantic_settings import BaseSettings
from pydantic import field_validator
from functools import lru_cache
from typing import List, Any


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

    # CORS - accepts comma-separated string or list
    CORS_ORIGINS: Any = ["http://localhost:3000", "http://127.0.0.1:3000"]

    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        # Handle the case where the value is an empty string that can't be parsed as JSON
        if v == "" or (isinstance(v, str) and v.strip() == ""):
            return ["http://localhost:3000", "http://127.0.0.1:3000"]
        elif isinstance(v, str):
            # Check if it's a JSON-formatted string
            try:
                parsed_json = json.loads(v)
                # If it's valid JSON and a list, return it
                if isinstance(parsed_json, list):
                    return parsed_json
                else:
                    # If it's valid JSON but not a list, treat as comma-separated string
                    return [origin.strip() for origin in v.split(',') if origin.strip()]
            except (json.JSONDecodeError, TypeError):
                # If it's not valid JSON, treat as comma-separated string
                return [origin.strip() for origin in v.split(',') if origin.strip()]
        elif v is None:
            # Handle None case
            return ["http://localhost:3000", "http://127.0.0.1:3000"]
        return v

    # Property to get the actual list of CORS origins
    @property
    def cors_origins_list(self) -> List[str]:
        """Get the list of CORS origins."""
        if isinstance(self.CORS_ORIGINS, list):
            return self.CORS_ORIGINS
        # Otherwise, treat as comma-separated string
        return [origin.strip() for origin in str(self.CORS_ORIGINS).split(',') if origin.strip()]

    # API
    API_PREFIX: str = "/api"

    # OpenAI API Configuration
    OPENAI_API_KEY: str = "your-openai-api-key-here"
    LLM_PROVIDER: str = "openai"
    OPENAI_DEFAULT_MODEL: str = "gpt-4o-mini"
    VERBOSE_AI_LOGGING: bool = False

    # ChatKit Configuration
    CHATKIT_DOMAIN_KEY: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
