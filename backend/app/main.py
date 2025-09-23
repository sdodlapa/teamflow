import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import api_router
from app.core.config import settings
from app.core.database import create_tables
from app.core.security_middleware import configure_security_middleware
from app.middleware.performance import PerformanceMiddlewareConfig
from app.middleware.compression import add_compression_middleware
from app.services.performance_service import performance_monitor


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(
        title="TeamFlow API",
        description="Enterprise task management and collaboration platform with advanced security",
        version="1.0.0",
        docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
        redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    )

    # Configure security middleware (must be done before other middleware)
    app = configure_security_middleware(app)

    # Configure performance middleware
    app = PerformanceMiddlewareConfig.configure_app_middleware(app)
    
    # Add compression middleware 
    app = add_compression_middleware(app, compression_type="smart")

    # Request timing middleware (already included in security middleware, but keeping for reference)
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
            "timestamp": time.time(),
            "security": "enhanced"
        }

    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint with API information."""
        return {
            "message": "TeamFlow API - Enterprise Security Edition",
            "version": "1.0.0",
            "docs": "/docs"
            if settings.ENVIRONMENT != "production"
            else "Docs disabled in production",
            "health": "/health",
            "features": [
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


# Create database tables on startup (for development)
# In production, this should be handled by Alembic migrations
@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    try:
        if settings.ENVIRONMENT == "development":
            # Create tables if they don't exist (development only)
            await create_tables()
        
        # Start performance monitoring
        await performance_monitor.start_monitoring()
        
        print(f"TeamFlow API starting up in {settings.ENVIRONMENT} mode with database and performance monitoring")
    except Exception as e:
        print(
            f"TeamFlow API starting up in {settings.ENVIRONMENT} mode WITHOUT database (Error: {e})"
        )
        print("Note: Database features will be unavailable until database is connected")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    # Stop performance monitoring
    await performance_monitor.stop_monitoring()
    print("TeamFlow API shutting down")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.ENVIRONMENT == "development" else False,
    )
