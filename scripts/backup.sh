#!/bin/bash
# Automated backup script for TeamFlow Production

set -e

# Configuration
BACKUP_DIR="/backups"
DB_HOST="postgres"
DB_NAME="${POSTGRES_DB:-teamflow}"
DB_USER="${POSTGRES_USER:-teamflow}"
RETENTION_DAYS=30
DATE=$(date +%Y%m%d_%H%M%S)

echo "Starting TeamFlow backup process at $(date)"

# Create backup directory
mkdir -p "$BACKUP_DIR/database"
mkdir -p "$BACKUP_DIR/uploads"
mkdir -p "$BACKUP_DIR/config"

# Database backup
echo "Creating database backup..."
pg_dump \
    --host="$DB_HOST" \
    --username="$DB_USER" \
    --dbname="$DB_NAME" \
    --verbose \
    --format=custom \
    --compress=9 \
    --file="$BACKUP_DIR/database/teamflow_${DATE}.dump"

# Create SQL backup for easier restore
pg_dump \
    --host="$DB_HOST" \
    --username="$DB_USER" \
    --dbname="$DB_NAME" \
    --verbose \
    --file="$BACKUP_DIR/database/teamflow_${DATE}.sql"

echo "Database backup completed"

# Configuration backup (if running with docker-compose)
echo "Creating configuration backup..."
if [ -f "/app/docker-compose.prod.yml" ]; then
    cp /app/docker-compose.prod.yml "$BACKUP_DIR/config/docker-compose_${DATE}.yml"
fi

if [ -f "/app/.env" ]; then
    # Remove sensitive data from env backup
    grep -v -E "(PASSWORD|SECRET|KEY)" /app/.env > "$BACKUP_DIR/config/env_${DATE}.txt" || true
fi

echo "Configuration backup completed"

# File uploads backup (if volume is mounted)
if [ -d "/app/uploads" ]; then
    echo "Creating uploads backup..."
    tar -czf "$BACKUP_DIR/uploads/uploads_${DATE}.tar.gz" -C /app uploads/
    echo "Uploads backup completed"
fi

# Create backup manifest
cat > "$BACKUP_DIR/manifest_${DATE}.txt" << EOF
TeamFlow Backup Manifest
========================
Date: $(date)
Database: teamflow_${DATE}.dump, teamflow_${DATE}.sql
Uploads: uploads_${DATE}.tar.gz
Config: docker-compose_${DATE}.yml, env_${DATE}.txt

Database Size: $(du -h "$BACKUP_DIR/database/teamflow_${DATE}.dump" | cut -f1)
Total Backup Size: $(du -sh "$BACKUP_DIR" | cut -f1)
EOF

echo "Backup manifest created"

# Cleanup old backups
echo "Cleaning up old backups (older than $RETENTION_DAYS days)..."
find "$BACKUP_DIR" -name "teamflow_*.dump" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "teamflow_*.sql" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "uploads_*.tar.gz" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "docker-compose_*.yml" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "env_*.txt" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "manifest_*.txt" -mtime +$RETENTION_DAYS -delete

echo "Backup process completed successfully at $(date)"
echo "Backup location: $BACKUP_DIR"
echo "Latest backup: teamflow_${DATE}"

# Optional: Upload to cloud storage (uncomment and configure as needed)
# echo "Uploading to cloud storage..."
# aws s3 cp "$BACKUP_DIR/database/teamflow_${DATE}.dump" s3://your-backup-bucket/teamflow/database/
# aws s3 cp "$BACKUP_DIR/uploads/uploads_${DATE}.tar.gz" s3://your-backup-bucket/teamflow/uploads/