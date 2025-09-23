#!/usr/bin/env python3
"""Ultra-simple server that actually shuts down properly."""

import signal
import sys
import os
from pathlib import Path

# Setup paths
project_root = Path(__file__).parent
backend_dir = project_root / "backend"
sys.path.insert(0, str(backend_dir))
os.chdir(backend_dir)

# Set environment to skip problematic parts
os.environ["SKIP_DB_INIT"] = "true"
os.environ["SKIP_PERFORMANCE_MONITORING"] = "true"

def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully."""
    print("\n🛑 Shutting down server...")
    sys.exit(0)

def main():
    """Start the server with proper signal handling."""
    # Register signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    print("🚀 Quick TeamFlow Server")
    print("🌐 http://localhost:8000")
    print("📚 http://localhost:8000/docs")
    print("💡 Press Ctrl+C to stop")
    print()
    
    try:
        import uvicorn
        
        # Start server with minimal configuration
        uvicorn.run(
            "app.main:app",
            host="127.0.0.1",
            port=8000,
            reload=False,  # Disable reload to avoid multiple processes
            access_log=False,  # Reduce noise
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()