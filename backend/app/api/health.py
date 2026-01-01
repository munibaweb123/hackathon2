"""Health check endpoints for the API and Kubernetes probes."""

from fastapi import APIRouter, Response, status
from pydantic import BaseModel
from sqlmodel import Session, select
from ..core.config import settings
from ..core.database import engine
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


class HealthResponse(BaseModel):
    """Health check response schema."""

    status: str
    app_name: str
    version: str


class LivenessResponse(BaseModel):
    """Liveness probe response schema."""

    status: str


class ReadinessResponse(BaseModel):
    """Readiness probe response schema."""

    status: str
    checks: dict[str, str]


@router.get("/livez", response_model=LivenessResponse)
async def liveness() -> LivenessResponse:
    """
    Liveness probe endpoint for Kubernetes.

    Checks if the application process is running.
    Should NEVER check external dependencies.
    """
    return LivenessResponse(status="alive")


@router.get("/readyz", response_model=ReadinessResponse)
async def readiness(response: Response) -> ReadinessResponse:
    """
    Readiness probe endpoint for Kubernetes.

    Checks if the app can serve traffic by validating dependencies.
    """
    health_status = ReadinessResponse(
        status="ready",
        checks={}
    )

    # Check database connection
    try:
        with Session(engine) as session:
            session.exec(select(1)).first()
        health_status.checks["database"] = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status.checks["database"] = "unhealthy"
        health_status.status = "not_ready"
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return health_status

    return health_status


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    General health endpoint for monitoring/observability.

    Returns the application status, name, and version.
    """
    return HealthResponse(
        status="healthy",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
    )
