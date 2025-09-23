"""
TeamFlow main.py with improved database handling - no hanging
"""
import asyncio
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import api_router
from app.core.config import settings
from app.core.database import ensure_database_ready, close_database


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(
        title="TeamFlow API",
        description="Enterprise task management and collaboration platform with improved architecture",
        version="2.0.0",
        docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
        redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.ENVIRONMENT == "development" else [],
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
            "version": "2.0.0",
            "timestamp": time.time(),
            "architecture": "improved"
        }

    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint with API information."""
        return {
            "message": "TeamFlow API v2.0 - Improved Architecture (No Hanging)",
            "version": "2.0.0",
            "docs": "/docs"
            if settings.ENVIRONMENT != "production"
            else "Docs disabled in production",
            "health": "/health",
            "database": "lazy-loaded",
            "features": [
                "No Startup Hanging",
                "Lazy Database Loading",
                "Improved Session Management",
                "Better Error Handling",
                "Multi-tenant Architecture",
                "Advanced Task Management", 
                "Real-time Collaboration",
                "File Management",
                "Workflow Automation",
                "Webhook Integrations",
                "Security & Compliance",
                "Audit Logging",
                "GDPR Compliance"
            ]
        }

    # Test database endpoint
    @app.get("/test-db")
    async def test_database():
        """Test database connectivity without hanging."""
        try:
            from app.core.database import check_database_exists
            db_ready = check_database_exists()
            
            return {
                "database_exists": db_ready,
                "message": "Database ready" if db_ready else "Database not initialized - run: python setup_database.py",
                "timestamp": time.time(),
                "status": "success"
            }
        except Exception as e:
            return {
                "database_exists": False,
                "error": str(e),
                "message": "Database check failed",
                "timestamp": time.time(),
                "status": "error"
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
                    "type": type(exc).__name__,
                },
            )
        else:
            # In production, return generic error message
            return JSONResponse(
                status_code=500, content={"detail": "Internal server error"}
            )

    # Include API routers
    app.include_router(api_router, prefix="/api/v1")

    return app


# Create the application instance
app = create_application()


@app.on_event("startup")
async def startup_event():
    """Application startup event - no hanging database operations."""
    try:
        print("🚀 TeamFlow API v2.0 starting up...")
        print(f"✅ Environment: {settings.ENVIRONMENT}")
        print("📋 Database: Lazy-loaded (use /test-db to check or run setup_database.py)")
        print("🎯 No hanging - server ready instantly!")
        print(f"✅ TeamFlow API startup complete in {settings.ENVIRONMENT} mode")
    except Exception as e:
        print(f"TeamFlow API starting up in {settings.ENVIRONMENT} mode with startup warning: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    print("👋 TeamFlow API shutting down...")
    try:
        await close_database()
        print("✅ Database connections closed cleanly")
    except Exception as e:
        print(f"⚠️ Error during shutdown: {e}")
    print("✅ TeamFlow API shutdown complete")