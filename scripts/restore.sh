#!/bin/bash

# Usage: ./restore.sh <TIMESTAMP_FOLDER_NAME>

if [ -z "$1" ]; then
    echo "Usage: ./restore.sh <YYYYMMDD_HHMMSS>"
    exit 1
fi

TIMESTAMP="$1"
BACKUP_DIR="/home/ubuntu/openedx_backups/$TIMESTAMP"

# Database Credentials
MYSQL_HOST="openedx-mysql.xxxxxx.us-east-1.rds.amazonaws.com"
MYSQL_USER="admin"
MYSQL_PASSWORD="OpenEdXStrongPass123!"
MYSQL_DB="openedx"
MONGO_CONTAINER="mongodb"

echo "CRITICAL WARNING: This will OVERWRITE the current Database."
echo "Are you sure you want to proceed? (yes/no)"
read confirm

if [ "$confirm" != "yes" ]; then
    echo "Restore Cancelled."
    exit 1
fi

# --- 1. Restore MySQL ---
if [ -f "$BACKUP_DIR/mysql_openedx.sql.gz" ]; then
    echo "Restoring MySQL..."
    gunzip < "$BACKUP_DIR/mysql_openedx.sql.gz" | mysql -h "$MYSQL_HOST" -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DB"
    echo "MySQL Restoration Complete."
else
    echo "MySQL Backup file not found!"
fi

# --- 2. Restore MongoDB ---
if [ -f "$BACKUP_DIR/mongo_openedx.archive.gz" ]; then
    echo "Restoring MongoDB..."
    cat "$BACKUP_DIR/mongo_openedx.archive.gz" | docker exec -i "$MONGO_CONTAINER" mongorestore --archive --gzip --drop
    echo "MongoDB Restoration Complete."
else
    echo "MongoDB Backup file not found!"
fi
