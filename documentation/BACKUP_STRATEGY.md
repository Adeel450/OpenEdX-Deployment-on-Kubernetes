
---

```markdown
# 🛡️ Open edX Production Backup & Disaster Recovery Strategy

**Author:** Muhammad Adeel Munir  
**Project:** Open edX Kubernetes Deployment on AWS EKS  

---

## 📑 Table of Contents
- [Overview](#overview)
- [1. Relational Data: MySQL (AWS RDS)](#1-relational-data-mysql-aws-rds)
- [2. Caching & Task Queues: Redis (AWS ElastiCache)](#2-caching--task-queues-redis-aws-elasticache)
- [3. Stateful K8s Workloads: MongoDB & Elasticsearch (Amazon EBS)](#3-stateful-k8s-workloads-mongodb--elasticsearch-amazon-ebs)
- [4. Disaster Recovery & Restoration Procedures](#4-disaster-recovery--restoration-procedures)
  - [4.1. Restoring MySQL (AWS RDS)](#41-restoring-mysql-aws-rds)
  - [4.2. Restoring Redis (AWS ElastiCache)](#42-restoring-redis-aws-elasticache)
  - [4.3. Restoring K8s StatefulSets from EBS Snapshots](#43-restoring-k8s-statefulsets-from-ebs-snapshots)

---

## 🎯 Overview
This document outlines the comprehensive **Backup and Disaster Recovery (DR) strategy** for the Open edX platform deployed on Amazon EKS. Because our architecture utilizes a hybrid approach—leveraging both AWS Managed Cloud-Native Services and Kubernetes StatefulSets—our backup strategy is divided into distinct layers to ensure **100% data durability, zero data loss, and rapid recovery times**.

---

## 1. Relational Data: MySQL (AWS RDS)
All core relational data (user accounts, course metadata, grades) is securely stored in a fully managed Amazon RDS MySQL instance.

* **Automated Backups:** Automated daily backups are enabled with a retention period of 7 days.
* **Point-in-Time Recovery (PITR):** RDS transaction logs are backed up every 5 minutes, allowing restoration to any specific second.
* **Manual Snapshots:** Pre-deployment manual snapshots are taken for permanent retention.

## 2. Caching & Task Queues: Redis (AWS ElastiCache)
* **Automated Daily Backups:** ElastiCache takes automated daily snapshots of the Redis cluster during low-traffic maintenance windows.

## 3. Stateful K8s Workloads: MongoDB & Elasticsearch (Amazon EBS)
Course content (Modulestore) and search indices are hosted inside the EKS cluster using Kubernetes `StatefulSets` attached to AWS Elastic Block Store (EBS) `gp3` volumes.

* **Storage Decoupling:** Pods and data are completely decoupled.
* **AWS Data Lifecycle Manager (DLM):** DLM automates daily **EBS Snapshots** of the volumes attached to our StatefulSets, securely storing them in Amazon S3.

---

## 4. Disaster Recovery & Restoration Procedures

Having a backup is only half the strategy; the ability to rapidly restore is equally critical. Below are the Standard Operating Procedures (SOPs) for restoring data in case of a failure.

### 4.1. Restoring MySQL (AWS RDS)
If the primary database is compromised:

1. Navigate to **AWS Console > RDS > Snapshots**.
2. Select the latest automated backup or manual snapshot.
3. Click **Actions > Restore snapshot**. This provisions a new RDS instance with the exact state of the backup.
4. **Update Application Configuration:** Once the new RDS instance is `Available`, update the Kubernetes workloads to point to the new endpoint:
   ```bash
   tutor config save --set MYSQL_HOST="<new-rds-endpoint>.amazonaws.com"
   kubectl rollout restart deployment lms cms -n openedx

```

### 4.2. Restoring Redis (AWS ElastiCache)

1. Navigate to **AWS Console > ElastiCache > Backups**.
2. Select the desired backup and click **Restore** to spin up a new cluster.
3. **Update Application Configuration:**
```bash
tutor config save --set REDIS_HOST="<new-redis-endpoint>.amazonaws.com"
kubectl rollout restart deployment lms cms cms-worker lms-worker -n openedx

```



### 4.3. Restoring K8s StatefulSets from EBS Snapshots

To restore a destroyed Persistent Volume (e.g., MongoDB data) from an AWS EBS Snapshot:

**Step 1: Create Volume from Snapshot (AWS Console)** Go to **EC2 > Snapshots**, select the target backup, and click **Create Volume from Snapshot**. Ensure it is created in the same Availability Zone as your EKS nodes. Copy the new Volume ID (e.g., `vol-0abcd123456789xyz`).

**Step 2: Create Static PV & PVC in Kubernetes** Create a manifest file (`restore-pv.yaml`) to map the new AWS EBS volume directly into Kubernetes:

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: restored-mongo-pv
spec:
  capacity:
    storage: 20Gi
  accessModes:
    - ReadWriteOnce
  awsElasticBlockStore:
    volumeID: "vol-0abcd123456789xyz" # Insert the new restored AWS volume ID here
    fsType: ext4
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mongo-data-mongodb-0 # Must match the StatefulSet's expected PVC name
  namespace: default
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi

```

**Step 3: Apply and Rebind** Apply the manifest and restart the StatefulSet pod. The K8s controller will automatically attach the restored data volume to the new pod:

```bash
kubectl apply -f restore-pv.yaml
kubectl delete pod mongodb-0 

```

```

***

```
