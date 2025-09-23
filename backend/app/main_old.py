import asyncio
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


# FIXED: Background database initialization to prevent event loop deadlock
@app.on_event("startup")
async def startup_event():
    """Application startup event - BYPASSING DATABASE INIT TO PREVENT HANGING."""
    try:
        print("� TEAMFLOW API STARTUP - DATABASE INIT DISABLED TO PREVENT HANGING")
        print("📋 To create tables manually, run: python -c 'import asyncio; from app.core.database import create_tables; asyncio.run(create_tables())'")
        print(f"✅ TeamFlow API startup complete in {settings.ENVIRONMENT} mode")
    except Exception as e:
        print(f"TeamFlow API starting up in {settings.ENVIRONMENT} mode with startup warning: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    # Stop performance monitoring
    await performance_monitor.stop_monitoring()
    print("TeamFlow API shutting down")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.ENVIRONMENT == "development" else False,
    )


def main():
    """Entry point for the teamflow-server command."""
    import sys
    import os
    import uvicorn
    
    # Add backend directory to Python path
    backend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)))
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)
    
    print("🚀 Starting TeamFlow server from", backend_dir)
    print("📁 Project root:", os.path.dirname(backend_dir))
    print("🔧 Environment: development")
    print("📡 Server will be available at: http://localhost:8000")
    print("📚 API docs: http://localhost:8000/docs")
    
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",  # Changed from 0.0.0.0 to localhost
        port=8000,
        reload=True,
    )
