#!/bin/bash

# ==========================================
# OpenEdX Backup Script (RDS + Docker)
# ==========================================

# 1. Configuration (Yahan apni details dalein)
# ------------------------------------------
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="/home/ubuntu/openedx_backups/$TIMESTAMP"
LOG_FILE="/home/ubuntu/openedx_backups/backup_log.txt"

# MySQL RDS Details
MYSQL_HOST="database-1.cluster-xxxx.us-east-1.rds.amazonaws.com" # Apna RDS Endpoint dalein
MYSQL_USER="admin"
MYSQL_PASSWORD="your_password" # Apna Password dalein
MYSQL_DB="openedx"

# MongoDB Docker Details
MONGO_CONTAINER_NAME="mongo" # Aapke docker ps mein naam 'mongo' ya kuch aur ho sakta hai (Check ID: 5bf275c502f5)

# Create Backup Directory
mkdir -p "$BACKUP_DIR"
echo "Starting Backup at $TIMESTAMP" >> "$LOG_FILE"

# ------------------------------------------
# 2. Backup MySQL (From AWS RDS)
# ------------------------------------------
echo "Backing up MySQL from RDS..."
mysqldump -h "$MYSQL_HOST" -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" --single-transaction --quick --lock-tables=false "$MYSQL_DB" > "$BACKUP_DIR/mysql_openedx.sql"

if [ $? -eq 0 ]; then
  echo "MySQL Backup Successful" >> "$LOG_FILE"
else
  echo "MySQL Backup Failed" >> "$LOG_FILE"
fi

# ------------------------------------------
# 3. Backup MongoDB (From Docker Container)
# ------------------------------------------
echo "Backing up MongoDB from Docker Container..."
# Hum docker exec use kar ke container ke andar se dump stream karein gy bahar
docker exec "$MONGO_CONTAINER_NAME" mongodump --archive --gzip > "$BACKUP_DIR/mongo_openedx.archive.gz"

if [ $? -eq 0 ]; then
  echo "MongoDB Backup Successful" >> "$LOG_FILE"
else
  echo "MongoDB Backup Failed" >> "$LOG_FILE"
fi

# ------------------------------------------
# 4. Optional: Upload to S3 (Production Step)
# ------------------------------------------
# Agar AWS CLI configured hai to ye uncomment karein:
# aws s3 cp "$BACKUP_DIR" s3://your-backup-bucket-name/$TIMESTAMP --recursive

echo "Backup Completed! Files saved in $BACKUP_DIR"
echo "---------------------------------------------" >> "$LOG_FILE"
