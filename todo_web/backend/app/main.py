"""FastAPI Todo Web Application - Main Entry Point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
import logging

from .core.config import settings
from .core.database import create_db_and_tables
from .core.jwks import fetch_jwks, _cached_jwks
from .api import tasks, reminders, preferences, health, auth, auth_public, notifications
from .utils.reminder_scheduler import start_scheduler

# Initialize rate limiter for the entire application
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler - runs on startup and shutdown."""
    # Startup: Create database tables
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    create_db_and_tables()
    print("Database tables created/verified")

    # Fetch JWKS from Better Auth for JWT verification
    logging.info("Fetching JWKS from Better Auth...")
    jwks_result = await fetch_jwks()
    if jwks_result:
        logging.info(f"Successfully fetched JWKS with {len(jwks_result.get('keys', []))} keys")
    else:
        logging.warning("Failed to fetch JWKS - JWT verification may not work until JWKS is available")

    # Start the reminder scheduler
    logging.info("Starting reminder scheduler...")
    start_scheduler(interval=60)  # Check every 60 seconds

    yield

    # Shutdown: Cleanup if needed
    print("Shutting down...")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Todo Web Application API with Better Auth cookie-based authentication",
    lifespan=lifespan,
)

# Register the rate limit handler
app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(tasks.router, prefix=settings.API_PREFIX, tags=["Tasks"])
app.include_router(reminders.router, prefix=settings.API_PREFIX, tags=["Reminders"])
app.include_router(preferences.router, prefix=settings.API_PREFIX, tags=["Preferences"])
app.include_router(auth_public.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(notifications.router, tags=["Notifications"])

# Include user profile router
from .api.users import profile
app.include_router(profile.router, prefix=f"{settings.API_PREFIX}/users", tags=["User Profile"])


@app.get("/")
async def root():
    """Root endpoint - API information."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/debug/jwks-status")
async def jwks_status():
    """Debug endpoint to check JWKS cache status."""
    return {
        "jwks_cached": _cached_jwks is not None,
        "jwks_count": len(_cached_jwks.get('keys', [])) if _cached_jwks else 0,
        "jwks_keys": [key.get('kid') for key in _cached_jwks.get('keys', [])] if _cached_jwks else []
    }
