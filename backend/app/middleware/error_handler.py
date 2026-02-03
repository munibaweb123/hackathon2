"""Global error handling middleware for consistent API error responses."""

import logging
import traceback

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            correlation_id = request.state.correlation_id if hasattr(request.state, "correlation_id") else None
            logger.error(
                "Unhandled exception",
                extra={
                    "correlation_id": correlation_id,
                    "path": request.url.path,
                    "method": request.method,
                    "error": str(exc),
                    "traceback": traceback.format_exc(),
                },
            )
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Internal server error",
                    "code": "INTERNAL_ERROR",
                    "correlation_id": correlation_id,
                },
            )
