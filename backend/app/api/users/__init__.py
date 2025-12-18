"""
User management API endpoints for the Todo Web Application.
"""

from fastapi import APIRouter

# Create the main users router
users_router = APIRouter(prefix="/users", tags=["Users"])

# Import and include user endpoints
from . import profile

# Include the user routes
users_router.include_router(profile.router, prefix="/profile")