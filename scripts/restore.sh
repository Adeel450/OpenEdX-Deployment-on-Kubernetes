#!/bin/bash

# ==========================================
# OpenEdX Restore Script
# Usage: ./restore.sh <TIMESTAMP_FOLDER_NAME>
# ==========================================

if [ -z "$1" ]; then
    echo "Usage: ./restore.sh <YYYYMMDD_HHMMSS>"
    echo "Example: ./restore.sh 20260207_120000"
    exit 1
fi

TIMESTAMP="$1"
BACKUP_DIR="/home/ubuntu/openedx_backups/$TIMESTAMP"

# MySQL RDS Details
MYSQL_HOST="database-1.cluster-xxxx.us-east-1.rds.amazonaws.com"
MYSQL_USER="admin"
MYSQL_PASSWORD="your_password"
MYSQL_DB="openedx"

# MongoDB Docker Details
MONGO_CONTAINER_NAME="mongo"

echo "WARNING: This will OVERWRITE current data. Are you sure? (y/n)"
read confirm
if [ "$confirm" != "y" ]; then
    exit 1
fi

# ------------------------------------------
# 1. Restore MySQL
# ------------------------------------------
if [ -f "$BACKUP_DIR/mysql_openedx.sql" ]; then
    echo "Restoring MySQL to RDS..."
    mysql -h "$MYSQL_HOST" -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DB" < "$BACKUP_DIR/mysql_openedx.sql"
    echo "MySQL Restore Complete"
else
    echo "MySQL backup file not found in $BACKUP_DIR"
fi

# ------------------------------------------
# 2. Restore MongoDB
# ------------------------------------------
if [ -f "$BACKUP_DIR/mongo_openedx.archive.gz" ]; then
    echo "Restoring MongoDB to Docker Container..."
    cat "$BACKUP_DIR/mongo_openedx.archive.gz" | docker exec -i "$MONGO_CONTAINER_NAME" mongorestore --archive --gzip --drop
    echo "MongoDB Restore Complete"
else
    echo "⚠️ MongoDB backup file not found in $BACKUP_DIR"
fi
