#!/usr/bin/env python3
"""
Working TeamFlow Server - Bypasses problematic database initialization
"""

import sys
import os
import uvicorn
from pathlib import Path
from fastapi import FastAPI

# Setup paths
project_root = Path(__file__).parent
backend_dir = project_root / "backend"
sys.path.insert(0, str(backend_dir))
os.chdir(backend_dir)

def create_minimal_app():
    """Create a minimal working FastAPI app."""
    
    app = FastAPI(
        title="TeamFlow API - Working Mode",
        description="Minimal working server while debugging database issues",
        version="1.0.0-minimal",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    @app.get("/")
    async def root():
        return {
            "message": "TeamFlow API - Working Mode",
            "status": "operational",
            "version": "1.0.0-minimal",
            "endpoints": {
                "health": "/health",
                "docs": "/docs",
                "test": "/test"
            }
        }
    
    @app.get("/health")
    async def health():
        return {
            "status": "healthy",
            "mode": "minimal",
            "database": "bypassed",
            "timestamp": "2025-09-23"
        }
    
    @app.get("/test")
    async def test():
        """Test endpoint to verify server is working."""
        try:
            # Test basic imports
            from app.core.config import settings
            config_status = "✅ Config loaded"
        except:
            config_status = "❌ Config failed"
        
        try:
            # Test model imports without database
            from app.models.user import User
            models_status = "✅ Models loaded"
        except:
            models_status = "❌ Models failed"
        
        return {
            "server": "✅ Working",
            "config": config_status,
            "models": models_status,
            "database": "⏭️ Bypassed for testing",
            "next_steps": [
                "Fix async SQLAlchemy configuration",
                "Resolve database session handling",
                "Test with proper database initialization"
            ]
        }
    
    return app

def main():
    """Start the minimal server."""
    print("🏥 TeamFlow Emergency Server")
    print("=" * 40)
    print("🎯 This bypasses database issues to get a working server")
    print("🌐 Server: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    print("🧪 Test: http://localhost:8000/test")
    print("💚 Health: http://localhost:8000/health")
    print("=" * 40)
    
    try:
        app = create_minimal_app()
        
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=8000,
            reload=False,
            access_log=True,
        )
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())