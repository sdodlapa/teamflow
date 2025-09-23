from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from app.core.config import settings
from app.core.database import engine
from app.models import Base

# Import routers (will be added as we build them)
# from app.api.auth import router as auth_router
# from app.api.users import router as users_router

def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    app = FastAPI(
        title="TeamFlow API",
        description="Enterprise task management and collaboration platform",
        version="1.0.0",
        docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
        redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request timing middleware
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint for load balancers and monitoring."""
        return {
            "status": "healthy",
            "environment": settings.ENVIRONMENT,
            "version": "1.0.0",
            "timestamp": time.time()
        }

    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint with API information."""
        return {
            "message": "TeamFlow API",
            "version": "1.0.0",
            "docs": "/docs" if settings.ENVIRONMENT != "production" else "Docs disabled in production",
            "health": "/health"
        }

    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Global exception handler for unhandled errors."""
        if settings.DEBUG:
            # In development, return detailed error information
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Internal server error",
                    "error": str(exc),
                    "type": type(exc).__name__
                }
            )
        else:
            # In production, return generic error message
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"}
            )

    # Include API routers (will be uncommented as we build them)
    # app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
    # app.include_router(users_router, prefix="/api/users", tags=["Users"])

    return app

# Create the application instance
app = create_application()

# Create database tables on startup (for development)
# In production, this should be handled by Alembic migrations
@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    try:
        if settings.ENVIRONMENT == "development":
            # Create tables if they don't exist (development only)
            Base.metadata.create_all(bind=engine)
        print(f"TeamFlow API starting up in {settings.ENVIRONMENT} mode with database")
    except Exception as e:
        print(f"TeamFlow API starting up in {settings.ENVIRONMENT} mode WITHOUT database (Error: {e})")
        print("Note: Database features will be unavailable until database is connected")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    print("TeamFlow API shutting down")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.ENVIRONMENT == "development" else False
    )