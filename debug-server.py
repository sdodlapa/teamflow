"""
Enhanced debugging and event capture system for TeamFlow server startup.
"""

import asyncio
import logging
import sys
import time
import traceback
from contextlib import asynccontextmanager
from typing import Any, Dict

import uvicorn
from fastapi import FastAPI

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)8s | %(name)20s | %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("debug.log", mode="w")
    ]
)

logger = logging.getLogger("TeamFlowDebug")

class EventTracker:
    """Track all events during server startup and operation."""
    
    def __init__(self):
        self.events = []
        self.start_time = time.time()
    
    def log_event(self, event_type: str, message: str, data: Dict[str, Any] = None):
        """Log an event with timestamp."""
        event = {
            "timestamp": time.time(),
            "elapsed": time.time() - self.start_time,
            "type": event_type,
            "message": message,
            "data": data or {}
        }
        self.events.append(event)
        
        # Also log to logger
        logger.info(f"[{event_type}] {message}")
        if data:
            logger.debug(f"    Data: {data}")
        
        # Print to console with emoji
        emoji_map = {
            "STARTUP": "🚀",
            "DATABASE": "🗄️",
            "REDIS": "📡",
            "MONITORING": "📊",
            "ERROR": "❌",
            "SUCCESS": "✅",
            "WARNING": "⚠️",
            "NETWORK": "🌐",
            "IMPORT": "📦"
        }
        emoji = emoji_map.get(event_type, "📝")
        print(f"{emoji} [{event_type:>10}] {message}")
    
    def log_exception(self, event_type: str, exception: Exception):
        """Log an exception with full traceback."""
        tb = traceback.format_exc()
        self.log_event(event_type, f"Exception: {str(exception)}", {
            "exception_type": type(exception).__name__,
            "traceback": tb
        })
        logger.error(f"Exception in {event_type}: {exception}")
        logger.error(f"Traceback:\n{tb}")
    
    def get_summary(self):
        """Get a summary of all events."""
        return {
            "total_events": len(self.events),
            "total_time": time.time() - self.start_time,
            "events": self.events
        }

# Global event tracker
tracker = EventTracker()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Modern lifespan handler with comprehensive event tracking."""
    
    tracker.log_event("STARTUP", "Application lifespan started")
    
    # Initialize variables
    performance_monitor = None
    
    try:
        # Import dependencies with tracking
        tracker.log_event("IMPORT", "Importing core dependencies")
        
        try:
            from app.core.config import settings
            from app.core.database import create_tables
            from app.services.performance_service import performance_monitor
            tracker.log_event("IMPORT", "Core dependencies imported successfully")
        except ImportError as e:
            tracker.log_exception("IMPORT", e)
            tracker.log_event("WARNING", "Some dependencies not available, running in limited mode")
            # Create minimal settings
            class MockSettings:
                ENVIRONMENT = "development"
            settings = MockSettings()
        
        # Database initialization
        if hasattr(settings, 'ENVIRONMENT') and settings.ENVIRONMENT == "development":
            tracker.log_event("DATABASE", "Starting database initialization")
            
            try:
                if 'create_tables' in locals():
                    # Add timeout for database operations
                    await asyncio.wait_for(create_tables(), timeout=15.0)
                    tracker.log_event("DATABASE", "Database tables created successfully")
                else:
                    tracker.log_event("WARNING", "Database creation function not available")
            except asyncio.TimeoutError:
                tracker.log_event("ERROR", "Database initialization timed out after 15 seconds")
            except Exception as e:
                tracker.log_exception("DATABASE", e)
                tracker.log_event("WARNING", "Continuing without database")
        
        # Performance monitoring
        if performance_monitor:
            tracker.log_event("MONITORING", "Starting performance monitoring")
            try:
                await performance_monitor.start_monitoring()
                tracker.log_event("MONITORING", "Performance monitoring started successfully")
            except Exception as e:
                tracker.log_exception("MONITORING", e)
                tracker.log_event("WARNING", "Continuing without performance monitoring")
        else:
            tracker.log_event("WARNING", "Performance monitor not available")
        
        tracker.log_event("SUCCESS", f"Application startup complete in {getattr(settings, 'ENVIRONMENT', 'unknown')} mode")
        
        yield  # Application runs here
        
    except Exception as e:
        tracker.log_exception("STARTUP", e)
    finally:
        # Shutdown
        tracker.log_event("STARTUP", "Application shutdown started")
        
        if performance_monitor:
            try:
                await performance_monitor.stop_monitoring()
                tracker.log_event("MONITORING", "Performance monitoring stopped")
            except Exception as e:
                tracker.log_exception("MONITORING", e)
        
        tracker.log_event("STARTUP", "Application shutdown complete")
        
        # Print final summary
        summary = tracker.get_summary()
        print("\n" + "="*60)
        print("🎯 STARTUP SUMMARY")
        print("="*60)
        print(f"Total Events: {summary['total_events']}")
        print(f"Total Time: {summary['total_time']:.2f} seconds")
        print("="*60)


def create_debug_app() -> FastAPI:
    """Create FastAPI app with enhanced debugging."""
    
    tracker.log_event("STARTUP", "Creating FastAPI application")
    
    app = FastAPI(
        title="TeamFlow API (Debug Mode)",
        description="Enterprise task management with comprehensive debugging",
        version="1.0.0-debug",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    # Add middleware for request tracking
    @app.middleware("http")
    async def debug_middleware(request, call_next):
        start_time = time.time()
        
        tracker.log_event("NETWORK", f"Request: {request.method} {request.url.path}")
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            tracker.log_event("NETWORK", f"Response: {response.status_code} in {process_time:.3f}s")
            response.headers["X-Process-Time"] = str(process_time)
            response.headers["X-Debug-Events"] = str(len(tracker.events))
            
            return response
        except Exception as e:
            tracker.log_exception("NETWORK", e)
            raise
    
    # Debug endpoints
    @app.get("/debug/events")
    async def get_debug_events():
        """Get all tracked events."""
        return tracker.get_summary()
    
    @app.get("/debug/health")
    async def debug_health():
        """Enhanced health check with debug info."""
        from app.core.config import settings
        
        health_data = {
            "status": "healthy",
            "environment": settings.ENVIRONMENT,
            "version": "1.0.0-debug",
            "timestamp": time.time(),
            "uptime": time.time() - tracker.start_time,
            "events_count": len(tracker.events),
            "recent_events": tracker.events[-5:] if tracker.events else []
        }
        
        tracker.log_event("NETWORK", "Debug health check accessed")
        return health_data
    
    @app.get("/")
    async def root():
        """Root endpoint with debug info."""
        return {
            "message": "TeamFlow API - Debug Mode",
            "version": "1.0.0-debug",
            "uptime": time.time() - tracker.start_time,
            "debug_endpoints": ["/debug/events", "/debug/health"],
            "docs": "/docs"
        }
    
    # Import API routes with tracking
    try:
        tracker.log_event("IMPORT", "Importing API routes")
        from app.api import api_router
        app.include_router(api_router, prefix="/api/v1")
        tracker.log_event("IMPORT", "API routes imported successfully")
    except Exception as e:
        tracker.log_exception("IMPORT", e)
        tracker.log_event("WARNING", "Running without full API routes")
    
    tracker.log_event("STARTUP", "FastAPI application created successfully")
    return app


def main():
    """Main entry point with comprehensive debugging."""
    import sys
    import os
    from pathlib import Path
    
    # Setup paths properly
    project_root = Path(__file__).parent
    backend_dir = project_root / "backend"
    
    # Add backend to Python path
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))
    
    # Change to backend directory
    os.chdir(backend_dir)
    
    print("🔍 TeamFlow Debug Server")
    print("=" * 50)
    print(f"📁 Backend directory: {backend_dir}")
    print(f"🐍 Python path: {sys.path[:3]}...")
    
    tracker.log_event("STARTUP", "Debug server starting")
    
    try:
        # Create the app
        app = create_debug_app()
        
        tracker.log_event("NETWORK", "Starting Uvicorn server")
        
        # Start server with debug configuration
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=8000,
            reload=False,  # Disable reload to avoid complexity
            log_level="debug",
            access_log=True,
        )
        
    except KeyboardInterrupt:
        tracker.log_event("STARTUP", "Server stopped by user (Ctrl+C)")
        print("\n👋 Debug server stopped")
    except Exception as e:
        tracker.log_exception("STARTUP", e)
        print(f"\n❌ Debug server failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())