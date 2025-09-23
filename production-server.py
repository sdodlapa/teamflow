#!/usr/bin/env python3
"""
Production TeamFlow Server - Full API with database integration
"""

import sys
import os
import time
import asyncio
import uvicorn
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Setup paths
project_root = Path(__file__).parent
backend_dir = project_root / "backend"
sys.path.insert(0, str(backend_dir))
os.chdir(backend_dir)

# Global state for server status
server_state = {"database_ready": False, "startup_time": None}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Modern lifespan event handler for FastAPI."""
    # Startup
    print("🚀 TeamFlow Production Server Starting...")
    print("=" * 50)
    server_state["startup_time"] = time.time()
    
    try:
        # Import and test database
        from app.core.database import AsyncSessionLocal, create_tables
        from sqlalchemy import text
        
        print("🔍 Testing database connection...")
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        print("✅ Database connection successful")
        
        print("📋 Creating/verifying tables...")
        await create_tables()
        print("✅ Database tables ready")
        
        server_state["database_ready"] = True
        print("✅ Full production mode active")
        
    except Exception as e:
        print(f"⚠️  Database error: {e}")
        print("🔄 Server will run in limited mode")
        server_state["database_ready"] = False
    
    yield
    
    # Shutdown
    print("👋 TeamFlow Production Server shutting down")

def create_production_app():
    """Create the production FastAPI application."""
    
    app = FastAPI(
        title="TeamFlow API - Production",
        description="Enterprise task management platform - Full Production Version",
        version="1.0.0-production",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, replace with specific origins
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
        """Production health check with full status."""
        try:
            if server_state["database_ready"]:
                from app.core.database import AsyncSessionLocal
                from sqlalchemy import text
                
                async with AsyncSessionLocal() as session:
                    await session.execute(text("SELECT 1"))
                    db_status = "✅ Connected and operational"
            else:
                db_status = "⚠️  Limited mode"
        except Exception as e:
            db_status = f"❌ Error: {str(e)[:100]}"
        
        return {
            "status": "healthy",
            "version": "1.0.0-production",
            "timestamp": time.time(),
            "uptime": time.time() - server_state["startup_time"] if server_state["startup_time"] else 0,
            "database": db_status,
            "mode": "production_full_api",
            "api_routes": 174  # Based on the project overview
        }

    # Root endpoint
    @app.get("/")
    async def root():
        """Production root endpoint."""
        return {
            "message": "TeamFlow API - Production Ready",
            "version": "1.0.0-production",
            "docs": "/docs",
            "health": "/health",
            "api_prefix": "/api/v1",
            "features": [
                "Multi-tenant Architecture",
                "Advanced Task Management", 
                "Real-time Collaboration",
                "File Management",
                "Workflow Automation",
                "Webhook Integrations",
                "Security & Compliance",
                "Audit Logging",
                "GDPR Compliance",
                "Performance Optimization"
            ],
            "endpoints_count": 174,
            "database_mode": "full" if server_state["database_ready"] else "limited"
        }

    # Include API routes if database is ready
    try:
        from app.api import api_router
        app.include_router(api_router, prefix="/api/v1")
        print("✅ API routes included")
    except Exception as e:
        print(f"⚠️  API routes error: {e}")
        
        # Add fallback API status endpoint
        @app.get("/api/v1/status")
        async def api_status():
            return {
                "status": "API routes not available",
                "error": str(e),
                "mode": "limited",
                "basic_endpoints": ["health", "docs"]
            }

    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Production global exception handler."""
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "error": str(exc),
                "type": type(exc).__name__,
                "path": str(request.url),
                "method": request.method,
                "timestamp": time.time()
            },
        )

    return app

def main():
    """Start the production server."""
    print("🏭 TeamFlow Production Server")
    print("=" * 40)
    
    try:
        app = create_production_app()
        
        print("🌐 Server: http://localhost:8000")
        print("📚 Docs: http://localhost:8000/docs")
        print("💚 Health: http://localhost:8000/health")
        print("🔗 API: http://localhost:8000/api/v1/")
        print("=" * 40)
        
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=8000,
            reload=False,
            access_log=True,
        )
        
    except KeyboardInterrupt:
        print("\n👋 Production server stopped")
    except Exception as e:
        print(f"\n❌ Production server error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())