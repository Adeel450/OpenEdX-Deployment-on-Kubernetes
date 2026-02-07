OpenEdX Backup & Disaster Recovery Strategy
1. Executive Summary
This document outlines the automated backup and disaster recovery strategy for the OpenEdX platform deployed on AWS EKS. The strategy ensures data durability for mission-critical components (MySQL & MongoDB) by leveraging a hybrid approach of AWS RDS snapshots and custom shell scripts for self-managed containers.

Key Components:
Database Layer:

MySQL: Running on AWS RDS (Managed Service).

MongoDB: Running in Docker Containers (Self-Managed on EC2).

Backup Frequency: Automated daily backups via Cronjob at 02:00 UTC.

Retention Policy: Backups are stored locally on the Bastion Host/EC2 instance for 7 days (configurable) and synced to S3 for long-term retention.

Recovery Point Objective (RPO): 24 Hours (Daily Backups).

Recovery Time Objective (RTO): < 1 Hour (Script-based restoration).

2. Backup Automation (Cronjob)
We utilize the Linux cron daemon to automate the backup process.

Cron Schedule
The backup script is scheduled to run daily at 2:00 AM Server Time.

Command to Setup:

# Open crontab editor
crontab -e

# Add the following line at the end of the file:
0 2 * * * /home/ubuntu/backup.sh >> /home/ubuntu/openedx_backups/cron.log 2>&1
3. Backup Script (backup.sh)
This script performs a logical backup of the MySQL database from AWS RDS and the MongoDB database from the local Docker container.

Path: /home/ubuntu/backup.sh

# --- 1. Backup MySQL (From AWS RDS) ---

4. Restore Script (restore.sh)
This script is used to restore data from a specific backup timestamp in case of data corruption or disaster recovery.

Path: /home/ubuntu/restore.sh Usage: ./restore.sh <TIMESTAMP_FOLDER> (e.g., ./restore.sh 20260207_120000)

5. Monitoring & Alerting
Log File: The backup status is logged to /home/ubuntu/openedx_backups/backup_log.txt.

Verification: Administrators can verify the success of the backup by checking the log file:

tail -f /home/ubuntu/openedx_backups/backup_log.txt
Alerting: (Future Enhancement) AWS CloudWatch Alarms can be configured to monitor the log file and send SNS notifications on "Failed" keywords.
