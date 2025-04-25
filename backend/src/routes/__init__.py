"""
Route module initialization file that exports all routers.
"""

from fastapi import APIRouter

from .auth_route import router as auth_router

# Main router that includes all sub-routers
api_router = APIRouter()

# Include all routers here
api_router.include_router(auth_router)

# Export the main router
__all__ = ["api_router"]
