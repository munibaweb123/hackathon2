"""Health check endpoint for the API."""

from fastapi import APIRouter
from pydantic import BaseModel
from ..core.config import settings

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response schema."""

    status: str
    app_name: str
    version: str


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.

    Returns the application status, name, and version.
    """
    return HealthResponse(
        status="healthy",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
    )
