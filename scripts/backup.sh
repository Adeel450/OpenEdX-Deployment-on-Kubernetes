#!/bin/bash

# =========================================================
# OpenEdX Automated Backup Script
# Components: MySQL (RDS) + MongoDB (Docker)
# =========================================================

# --- 1. Configuration ---
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="/home/ubuntu/openedx_backups/$TIMESTAMP"
LOG_FILE="/home/ubuntu/openedx_backups/backup_log.txt"

# MySQL Details (RDS)
MYSQL_HOST="openedx-mysql.xxxxxx.us-east-1.rds.amazonaws.com"
MYSQL_USER="admin"
MYSQL_PASSWORD="OpenEdXStrongPass123!"
MYSQL_DB="openedx"

# MongoDB Details (Docker)
MONGO_CONTAINER="mongodb"  # Name of the docker container

# Create Directory for this session
mkdir -p "$BACKUP_DIR"

echo "[$(date)] Starting Backup Session: $TIMESTAMP" >> "$LOG_FILE"

# --- 2. Backup MySQL (RDS) ---
echo "Backing up MySQL..."
# Uses single-transaction to ensure data consistency without locking tables
mysqldump -h "$MYSQL_HOST" -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" \
  --single-transaction --quick --lock-tables=false "$MYSQL_DB" \
  | gzip > "$BACKUP_DIR/mysql_openedx.sql.gz"

if [ $? -eq 0 ]; then
  echo "[$(date)] MySQL Backup Successful" >> "$LOG_FILE"
else
  echo "[$(date)]  MySQL Backup Failed!" >> "$LOG_FILE"
  # Optional: Add Email Alert Logic Here
fi

# --- 3. Backup MongoDB (Docker) ---
echo "Backing up MongoDB..."
# Execs into container and streams archive to host
docker exec "$MONGO_CONTAINER" mongodump --archive --gzip > "$BACKUP_DIR/mongo_openedx.archive.gz"

if [ $? -eq 0 ]; then
  echo "[$(date)]  MongoDB Backup Successful" >> "$LOG_FILE"
else
  echo "[$(date)]  MongoDB Backup Failed!" >> "$LOG_FILE"
fi

# --- 4. Cleanup (Retention Policy) ---
# Delete backups older than 7 days to save space
find /home/ubuntu/openedx_backups/* -type d -mtime +7 -exec rm -rf {} +
echo "[$(date)] Cleanup of old backups completed." >> "$LOG_FILE"

echo "[$(date)] 🏁 Backup Session Completed." >> "$LOG_FILE"
echo "---------------------------------------------------" >> "$LOG_FILE"
