#!/bin/bash
# Restore script for TeamFlow backups

set -e

# Configuration
BACKUP_DIR="/backups"
DB_HOST="postgres"
DB_NAME="${POSTGRES_DB:-teamflow}"
DB_USER="${POSTGRES_USER:-teamflow}"

if [ $# -eq 0 ]; then
    echo "Usage: $0 <backup_date>"
    echo "Example: $0 20250923_143000"
    echo ""
    echo "Available backups:"
    ls -la "$BACKUP_DIR/database/" | grep "teamflow_" | awk '{print $9}' | sed 's/teamflow_/  /' | sed 's/\.dump//'
    exit 1
fi

BACKUP_DATE=$1
DUMP_FILE="$BACKUP_DIR/database/teamflow_${BACKUP_DATE}.dump"
SQL_FILE="$BACKUP_DIR/database/teamflow_${BACKUP_DATE}.sql"
UPLOADS_FILE="$BACKUP_DIR/uploads/uploads_${BACKUP_DATE}.tar.gz"

echo "Starting TeamFlow restore process for backup: $BACKUP_DATE"

# Verify backup files exist
if [ ! -f "$DUMP_FILE" ] && [ ! -f "$SQL_FILE" ]; then
    echo "Error: Backup files not found for date $BACKUP_DATE"
    exit 1
fi

# Confirmation prompt
read -p "This will overwrite the current database and uploads. Are you sure? (yes/no): " -r
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "Restore cancelled"
    exit 0
fi

# Stop application (if using docker-compose)
echo "Stopping application..."
docker-compose down || true

# Database restore
echo "Restoring database..."
if [ -f "$DUMP_FILE" ]; then
    # Restore from custom format
    pg_restore \
        --host="$DB_HOST" \
        --username="$DB_USER" \
        --dbname="$DB_NAME" \
        --clean \
        --if-exists \
        --verbose \
        "$DUMP_FILE"
elif [ -f "$SQL_FILE" ]; then
    # Restore from SQL file
    psql \
        --host="$DB_HOST" \
        --username="$DB_USER" \
        --dbname="$DB_NAME" \
        --file="$SQL_FILE"
fi

echo "Database restore completed"

# Uploads restore
if [ -f "$UPLOADS_FILE" ]; then
    echo "Restoring uploads..."
    rm -rf /app/uploads/*
    tar -xzf "$UPLOADS_FILE" -C /app/
    echo "Uploads restore completed"
fi

# Start application
echo "Starting application..."
docker-compose up -d

echo "Restore process completed successfully"
echo "Application should be available shortly"