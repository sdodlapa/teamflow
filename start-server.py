#!/usr/bin/env python3
"""
TeamFlow Server Launcher

This script properly sets up the Python path and starts the TeamFlow backend server.
"""
import sys
import os
from pathlib import Path

# Get the project root directory (where this script is located)
project_root = Path(__file__).parent

# Add the backend directory to Python path so imports work correctly
backend_dir = project_root / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Change to backend directory so relative paths work
os.chdir(backend_dir)

def main():
    """Start the TeamFlow server."""
    try:
        import uvicorn
        
        # Set environment to skip database initialization that might hang
        os.environ["SKIP_DB_INIT"] = "true"
        
        print("🚀 Starting TeamFlow Server (Simple Mode)...")
        print(f"📁 Project root: {project_root}")
        print(f"📁 Backend directory: {backend_dir}")
        print(f"🐍 Python path includes: {backend_dir}")
        print("🌐 Server will be available at: http://localhost:8000")
        print("📖 API documentation: http://localhost:8000/docs")
        print("❤️  Health check: http://localhost:8000/health")
        print()
        
        uvicorn.run(
            "app.main:app",
            host="127.0.0.1",  # Use localhost instead of 0.0.0.0
            port=8000,
            reload=True,
        )
    except KeyboardInterrupt:
        print("\\n👋 TeamFlow Server stopped by user")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you've activated the virtual environment and installed dependencies:")
        print("   source .venv/bin/activate")
        print("   pip install -e '.[dev]'")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()