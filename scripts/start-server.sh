#!/bin/bash

# TeamFlow Server Startup Script with Error Handling and Timeouts

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${GREEN}🚀 TeamFlow Server Startup Script${NC}"
echo -e "${GREEN}📁 Project root: $PROJECT_ROOT${NC}"

# Function to kill existing processes
kill_existing_server() {
    echo -e "${YELLOW}🔄 Checking for existing TeamFlow processes...${NC}"
    
    # Kill by port
    if lsof -ti:8000 >/dev/null 2>&1; then
        echo -e "${YELLOW}💀 Killing processes on port 8000...${NC}"
        lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    fi
    
    # Kill by process name
    pkill -9 -f "teamflow-server" 2>/dev/null || true
    pkill -9 -f "uvicorn.*teamflow" 2>/dev/null || true
    
    sleep 2
    echo -e "${GREEN}✅ Cleaned up existing processes${NC}"
}

# Function to activate virtual environment
activate_venv() {
    echo -e "${YELLOW}🔧 Activating virtual environment...${NC}"
    
    if [ ! -d ".venv" ]; then
        echo -e "${RED}❌ Virtual environment not found at .venv${NC}"
        exit 1
    fi
    
    source .venv/bin/activate
    echo -e "${GREEN}✅ Virtual environment activated${NC}"
}

# Function to check database
check_database() {
    echo -e "${YELLOW}🗄️ Checking database...${NC}"
    
    # Remove potentially corrupted database files
    rm -f backend/teamflow_dev.db-shm backend/teamflow_dev.db-wal
    
    echo -e "${GREEN}✅ Database ready${NC}"
}

# Function to start server with timeout
start_server() {
    echo -e "${YELLOW}🌟 Starting TeamFlow server...${NC}"
    
    # Start server in background
    teamflow-server &
    SERVER_PID=$!
    
    # Wait for server to be ready
    echo -e "${YELLOW}⏳ Waiting for server to start (max 30 seconds)...${NC}"
    
    for i in {1..30}; do
        if curl -s http://localhost:8000/health >/dev/null 2>&1; then
            echo -e "${GREEN}✅ Server is ready!${NC}"
            echo -e "${GREEN}🌐 Server: http://localhost:8000${NC}"
            echo -e "${GREEN}📚 API Docs: http://localhost:8000/docs${NC}"
            echo -e "${GREEN}💚 Health Check: http://localhost:8000/health${NC}"
            echo ""
            echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
            
            # Wait for the server process or user interrupt
            wait $SERVER_PID
            return 0
        fi
        
        # Check if process is still running
        if ! kill -0 $SERVER_PID 2>/dev/null; then
            echo -e "${RED}❌ Server process died unexpectedly${NC}"
            echo -e "${YELLOW}📋 Last few lines of server output:${NC}"
            # Try to show any error output
            return 1
        fi
        
        sleep 1
    done
    
    echo -e "${RED}❌ Server failed to start within 30 seconds${NC}"
    kill -9 $SERVER_PID 2>/dev/null || true
    return 1
}

# Cleanup function for script exit
cleanup() {
    echo -e "\n${YELLOW}🧹 Cleaning up...${NC}"
    kill_existing_server
    echo -e "${GREEN}✅ Cleanup complete${NC}"
}

# Set trap for cleanup on script exit
trap cleanup EXIT INT TERM

# Main execution
main() {
    kill_existing_server
    activate_venv
    check_database
    start_server
}

# Run main function
main "$@"