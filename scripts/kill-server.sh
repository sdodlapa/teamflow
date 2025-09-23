#!/bin/bash

# Emergency TeamFlow Server Kill Script

echo "🚨 Emergency server shutdown initiated..."

# Kill by port (most reliable)
if lsof -ti:8000 >/dev/null 2>&1; then
    echo "💀 Killing processes on port 8000..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
fi

# Kill by process name patterns
echo "💀 Killing TeamFlow processes..."
pkill -9 -f "teamflow-server" 2>/dev/null || true
pkill -9 -f "uvicorn.*teamflow" 2>/dev/null || true
pkill -9 -f "python.*teamflow" 2>/dev/null || true

# Wait a moment
sleep 2

# Check if anything is still running
if lsof -ti:8000 >/dev/null 2>&1; then
    echo "⚠️ Some processes may still be running on port 8000"
    lsof -i:8000
else
    echo "✅ All TeamFlow processes killed successfully"
fi

echo "🧹 Emergency shutdown complete"