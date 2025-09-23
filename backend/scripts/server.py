#!/usr/bin/env python3
"""
TeamFlow Server Entry Point

This script properly sets up the Python path and starts the FastAPI server.
It handles the module path resolution needed to run the backend from the project root.
"""

import os
import sys
from pathlib import Path


def main():
    """Entry point for the teamflow-server command."""
    # Get the absolute path to the backend directory
    current_file = Path(__file__).resolve()
    backend_dir = current_file.parent.parent  # backend/scripts/server.py -> backend/
    project_root = backend_dir.parent  # backend/ -> teamflow/
    
    # Add backend directory to Python path so 'app' module can be found
    backend_path = str(backend_dir)
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)
    
    # Change working directory to backend for relative file paths to work
    original_cwd = os.getcwd()
    os.chdir(backend_dir)
    
    try:
        # Now we can import and run the application
        import uvicorn
        from app.main import app, settings
        
        print(f"🚀 Starting TeamFlow server from {backend_dir}")
        print(f"📁 Project root: {project_root}")
        print(f"🔧 Environment: {settings.ENVIRONMENT}")
        print(f"📡 Server will be available at: http://0.0.0.0:8000")
        print(f"📚 API docs: http://0.0.0.0:8000/docs")
        
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True if settings.ENVIRONMENT == "development" else False,
            reload_dirs=[str(backend_dir)] if settings.ENVIRONMENT == "development" else None,
        )
    
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)
    
    finally:
        # Restore original working directory
        os.chdir(original_cwd)


if __name__ == "__main__":
    main()