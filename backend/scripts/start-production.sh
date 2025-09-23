#!/bin/bash
# Production startup script for TeamFlow Backend

set -e

echo "Starting TeamFlow Backend in Production Mode..."

# Wait for database to be ready
echo "Waiting for database connection..."
python -c "
import asyncio
import sys
from app.core.database import test_connection

async def wait_for_db():
    max_retries = 30
    for i in range(max_retries):
        try:
            await test_connection()
            print('Database connection successful!')
            return
        except Exception as e:
            print(f'Database connection attempt {i+1}/{max_retries} failed: {e}')
            if i < max_retries - 1:
                await asyncio.sleep(2)
            else:
                print('Failed to connect to database after maximum retries')
                sys.exit(1)

asyncio.run(wait_for_db())
"

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Start the application with Gunicorn
echo "Starting application server..."
exec gunicorn \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --worker-connections 1000 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --timeout 30 \
    --keep-alive 2 \
    --preload \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    app.main:app