"""
Authentication API endpoints for the Todo Web Application.
"""

from fastapi import APIRouter

# Create the main auth router
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

# Import and include auth endpoints
from . import register, login, logout, me, refresh, forgot_password, reset_password

# Include the auth routes
auth_router.include_router(register.router)
auth_router.include_router(login.router)
auth_router.include_router(logout.router)
auth_router.include_router(me.router)
auth_router.include_router(refresh.router)
auth_router.include_router(forgot_password.router)
auth_router.include_router(reset_password.router)

# Export the router as 'router' for the main app to import
router = auth_router