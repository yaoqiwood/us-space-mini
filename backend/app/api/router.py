from fastapi import APIRouter

from app.api.routes import auth, entry, health, notifications


api_router = APIRouter(prefix="/v1")
api_router.include_router(health.router, tags=["health"])
api_router.include_router(entry.router, tags=["entry"])
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(notifications.router, tags=["notifications"])
