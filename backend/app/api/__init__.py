"""API router initialization."""

from fastapi import APIRouter

from app.api.routes import auth, organizations, projects, tasks, users, advanced_features, websocket

# Create main API router
api_router = APIRouter()

# Include route modules
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(
    organizations.router, prefix="/organizations", tags=["organizations"]
)
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(
    advanced_features.router, prefix="/advanced", tags=["advanced-features"]
)
api_router.include_router(
    websocket.router, prefix="/realtime", tags=["realtime-collaboration"]
)
