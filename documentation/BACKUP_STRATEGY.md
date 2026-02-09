OpenEdX Backup & Disaster Recovery Strategy
1. Executive Summary
This document outlines the automated backup and disaster recovery (DR) strategy for the OpenEdX platform deployed on AWS EKS. The strategy ensures data durability for mission-critical components by leveraging a hybrid approach of AWS RDS Snapshots (Managed) and Custom Shell Scripts (Self-Managed).

1.1 Architecture Scope
Relational Database (MySQL): Hosted on AWS RDS. Critical for user data, course structures, and enrollments.

NoSQL Database (MongoDB): Hosted on a private EC2 Utility Node via Docker. Critical for course content and forum discussions.

File Storage: Static assets and media are stored in AWS S3 (Inherently durable).

1.2 Service Level Objectives (SLO)
Recovery Point Objective (RPO): 24 Hours (Maximum data loss tolerance: 1 day).

Recovery Time Objective (RTO): < 1 Hour (Time to restore operations using scripts).

Retention Policy:

Local: 7 Days (On EC2 Instance).

Remote (S3): 30 Days (For Disaster Recovery).

2. Prerequisites & Setup
Before automating the backups, the following dependencies must be installed on the Utility/Bastion Server.

2.1 Install Database Clients
The server requires clients to communicate with RDS and Docker.


# Update System
sudo apt update

# Install MySQL Client (to dump RDS data)
sudo apt install -y mysql-client-core-8.0

# Verify Docker (for MongoDB dump)
docker --version
2.2 Directory Structure
We organize backups by timestamps to prevent overwriting.


# Create the main backup directory
mkdir -p /home/ubuntu/openedx_backups
3. Implementation: Backup Script
We utilize a custom shell script to perform logical backups. It connects to the AWS RDS instance remotely and executes a dump command inside the local MongoDB container.

Source File Path: scripts/backup.sh

Functionality:

Creates a timestamped directory (e.g., 20260209_120000).

Dumps MySQL database from RDS (using mysqldump with single-transaction).

Dumps MongoDB from the Docker container (using mongodump).

Compresses files (.gz) to save space.

Enforces retention policy (deletes local backups older than 7 days).

Syncs data to AWS S3 (Optional).

Deployment: Copy the script to the server:


cp scripts/backup.sh /home/ubuntu/backup.sh
chmod +x /home/ubuntu/backup.sh

4. Implementation: Restore Script
This script is used to restore data from a specific backup folder in case of data corruption or disaster recovery.

Source File Path: scripts/restore.sh

Usage:


./restore.sh <TIMESTAMP_FOLDER_NAME>
# Example: ./restore.sh 20260209_120000
Functionality:

Accepts a backup timestamp folder as an argument.

Decompresses the SQL and Archive files.

Restores MySQL to RDS (Overwrites existing data).

Restores MongoDB to the Docker container (Drops existing collections before restore).

Deployment: Copy the script to the server:


cp scripts/restore.sh /home/ubuntu/restore.sh
chmod +x /home/ubuntu/restore.sh

5. Automation (Cronjob)
We utilize the Linux cron daemon to ensure backups happen automatically without human intervention.

Schedule: Daily at 02:00 AM UTC (Low traffic period).

Setup Instructions:

Open the crontab editor on the Utility Server:


crontab -e
Append the following line to schedule the script:


0 2 * * * /bin/bash /home/ubuntu/backup.sh >> /home/ubuntu/openedx_backups/cron.log 2>&1
6. Offsite Storage (AWS S3)
To protect against total server failure (EC2 termination), backups are synced to AWS S3.

Prerequisites:

Create an S3 Bucket: my-openedx-backups-bucket.

Configure AWS CLI: aws configure.

Sync Logic: The backup.sh script includes the following command to mirror local backups to S3:


aws s3 sync /home/ubuntu/openedx_backups s3://my-openedx-backups-bucket/ --delete
7. Monitoring & Verification
7.1 Log Monitoring
The backup process writes detailed logs. Administrators can monitor the status using:


# View live logs
tail -f /home/ubuntu/openedx_backups/backup_log.txt
7.2 Disaster Recovery Drill (Test)
It is recommended to perform a "Dry Run" restoration once a month.

Check Files: Ensure the folder exists in /home/ubuntu/openedx_backups/.

Verify Integrity:


# Check if gzip file is valid
gzip -t /home/ubuntu/openedx_backups/<TIMESTAMP>/mysql_openedx.sql.gz
Test Restore: Use restore.sh on a Staging/Test Environment first, never directly on Production unless necessary.
