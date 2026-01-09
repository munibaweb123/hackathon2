"""FastAPI Todo Web Application - Main Entry Point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
import logging

from .core.config import settings
from .core.database import create_db_and_tables
from .core import jwks as jwks_module
from .api import tasks, reminders, preferences, health, auth, auth_public, auth_routes, auth_bridge, notifications, chat
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

    # Fetch JWKS from Better Auth for JWT verification (with retries)
    print("Fetching JWKS from Better Auth...")
    max_retries = 5
    retry_delay = 2  # seconds
    jwks_result = None

    for attempt in range(max_retries):
        jwks_result = await jwks_module.fetch_jwks()
        if jwks_result:
            print(f"Successfully fetched JWKS with {len(jwks_result.get('keys', []))} keys")
            break
        else:
            if attempt < max_retries - 1:
                print(f"JWKS fetch attempt {attempt + 1} failed, retrying in {retry_delay}s...")
                import asyncio
                await asyncio.sleep(retry_delay)
            else:
                print("WARNING: Failed to fetch JWKS after all retries - JWT verification may not work")

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


@app.on_event("startup")
async def startup_event():
    """Additional startup tasks"""
    print("Startup complete - JWKS should be loaded")
    # Verify JWKS was loaded
    cached = jwks_module._cached_jwks
    if cached:
        print(f"✓ JWKS loaded with {len(cached.get('keys', []))} keys")
        for key in cached.get('keys', []):
            print(f"  - Key: kid={key.get('kid')}, alg={key.get('alg')}, kty={key.get('kty')}")
    else:
        print("✗ JWKS not loaded - authentication may fail")

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
app.include_router(auth_routes.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(auth_bridge.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(notifications.router, tags=["Notifications"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])

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
    cached = jwks_module._cached_jwks
    return {
        "jwks_cached": cached is not None,
        "jwks_count": len(cached.get('keys', [])) if cached else 0,
        "jwks_keys": [key.get('kid') for key in cached.get('keys', [])] if cached else [],
        "better_auth_url": settings.BETTER_AUTH_URL
    }


@app.post("/debug/jwks-refresh")
async def jwks_refresh():
    """Debug endpoint to manually refresh JWKS cache."""
    result = await jwks_module.fetch_jwks()
    return {
        "success": result is not None,
        "jwks_count": len(result.get('keys', [])) if result else 0,
        "jwks_keys": [key.get('kid') for key in result.get('keys', [])] if result else [],
        "better_auth_url": settings.BETTER_AUTH_URL
    }
