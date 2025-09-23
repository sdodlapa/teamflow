#!/usr/bin/env python3
"""
Debug server to identify exact hanging point
"""

import sys
import os
import time
import asyncio
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Setup paths
project_root = Path(__file__).parent
backend_dir = project_root / "backend"
sys.path.insert(0, str(backend_dir))
os.chdir(backend_dir)

@asynccontextmanager
async def debug_lifespan(app: FastAPI):
    """Debug lifespan with detailed logging."""
    print("🔧 [LIFESPAN] Starting...")
    
    try:
        print("🔧 [LIFESPAN] Step 1: Import models...")
        start_time = time.time()
        from app.models.user import User
        from app.models.organization import Organization
        print(f"🔧 [LIFESPAN] Models imported in {time.time() - start_time:.3f}s")
        
        print("🔧 [LIFESPAN] Step 2: Create tables...")
        db_start = time.time()
        from app.core.database import create_tables
        await create_tables()
        print(f"🔧 [LIFESPAN] Tables created in {time.time() - db_start:.3f}s")
        
        print("🔧 [LIFESPAN] Step 3: Performance monitor...")
        try:
            from app.services.performance_service import performance_monitor
            await performance_monitor.start_monitoring()
            print("🔧 [LIFESPAN] Performance monitor started")
        except Exception as e:
            print(f"🔧 [LIFESPAN] Performance monitor failed: {e}")
        
        print("✅ [LIFESPAN] Startup complete")
        
    except Exception as e:
        print(f"❌ [LIFESPAN] Error: {e}")
        import traceback
        traceback.print_exc()
    
    yield
    
    try:
        print("🔧 [LIFESPAN] Shutdown starting...")
        from app.services.performance_service import performance_monitor
        await performance_monitor.stop_monitoring()
        print("👋 [LIFESPAN] Shutdown complete")
    except:
        print("👋 [LIFESPAN] Shutdown (no cleanup needed)")

def create_debug_app():
    """Create debug app with detailed logging."""
    print("🔧 [APP] Creating FastAPI app...")
    
    app = FastAPI(
        title="TeamFlow Debug Server",
        description="Debug server to identify hanging issues",
        version="debug",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=debug_lifespan
    )
    print("✅ [APP] FastAPI app created")
    
    print("🔧 [APP] Adding CORS middleware...")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    print("✅ [APP] CORS middleware added")
    
    @app.get("/")
    async def root():
        return {"message": "Debug server working", "time": time.time()}
    
    @app.get("/health")  
    async def health():
        return {"status": "healthy", "time": time.time()}
    
    print("🔧 [APP] Adding API routes...")
    try:
        from app.api import api_router
        app.include_router(api_router, prefix="/api/v1")
        print("✅ [APP] API routes added")
    except Exception as e:
        print(f"⚠️ [APP] API routes failed: {e}")
    
    return app

def main():
    """Main debug function."""
    print("🐛 TeamFlow Debug Server")
    print("=" * 40)
    
    print("🔧 [MAIN] Creating app...")
    app = create_debug_app()
    print("✅ [MAIN] App created")
    
    print("🔧 [MAIN] Starting uvicorn...")
    print("📍 Expected hang point: After 'Application startup complete.'")
    print("=" * 40)
    
    import uvicorn
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        reload=False,
        access_log=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()