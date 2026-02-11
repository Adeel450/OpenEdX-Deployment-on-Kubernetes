🚀 OpenEdX — Production Deployment on AWS EKS

Production-grade, highly available OpenEdX LMS deployed on AWS EKS using Terraform (Infrastructure as Code), Kubernetes manifests, and automation scripts.

The platform follows enterprise best practices including:

Externalized databases

Secure VPC architecture

Observability & monitoring

Backup & disaster recovery

Horizontal Pod Autoscaling validation

📑 Table of Contents

Architecture Overview

Repository Structure

Prerequisites

Quick Start (Bastion Host Workflow)

Security & Maintenance

Backup & Restore

HPA & Scalability Verification

Troubleshooting & Support

Architecture Overview Video

Contact

🏗 Architecture Overview

The infrastructure is deployed inside a custom AWS VPC spanning:

us-east-1a

us-east-1b

This ensures high availability and fault tolerance.

🔹 Core Components
Layer	Technology
Orchestration	AWS EKS (Kubernetes 1.30+)
Ingress	Nginx Ingress Controller (ALB-backed)
Edge Security	Amazon CloudFront + AWS WAF
Compute	Private EKS worker nodes + Bastion Host
Database	Amazon RDS (MySQL Multi-AZ)
Utility Services	MongoDB, Redis, Elasticsearch (Dockerized EC2)
Storage	Amazon EBS (gp3)
Monitoring	Prometheus & Grafana
Autoscaling	Kubernetes HPA (CPU-based)

All workloads and databases operate in private subnets.
Administrative access is strictly controlled via a hardened bastion host.

📂 Repository Structure
.
├── README.md
├── diagrams/
├── documentation/
│   ├── DEPLOYMENT_GUIDE.md
│   ├── TROUBLESHOOTING.md
│   └── BACKUP_STRATEGY.md
├── k8s-manifests/
├── scripts/
│   ├── backup.sh
│   ├── restore.sh
│   ├── generate_load.sh
│   └── stop_load.sh
├── terraform/
└── screenshots/

⚙️ Prerequisites

Install the following tools on the Bastion Host or deployment machine:

AWS CLI v2

kubectl

Terraform (v1.0+)

Helm

Tutor (OpenEdX Manager)

Python 3.10+

🚀 Quick Start (Bastion Host Workflow)

Refer to documentation/DEPLOYMENT_GUIDE.md for complete deployment instructions.

🔐 Security & Maintenance

Private subnets for workloads and databases

IAM-based role access

AWS Secrets Manager for sensitive credentials

Regular node patching & AMI rotation

MFA enforced for bastion access

💾 Backup & Restore

Daily automated backups are scheduled at:

02:00 UTC

🔹 Manual Backup
./scripts/backup.sh

🔹 Restore from Backup
./scripts/restore.sh <TIMESTAMP>


Example:

./scripts/restore.sh 2026-02-10_02-00-00

📈 HPA & Scalability Verification

To validate production-grade autoscaling behavior, controlled load testing scripts have been implemented.

These scripts generate synthetic internal traffic to both LMS and CMS services and verify Kubernetes Horizontal Pod Autoscaler (HPA) responsiveness.

🎯 Objective

The load testing workflow validates:

HPA configuration accuracy

Metrics Server availability

CPU-based scaling thresholds (50%)

Automatic replica scaling

Elastic recovery after load removal

Enterprise-grade scalability readiness

📂 Script Location
scripts/
├── generate_load.sh   # Starts load generation
└── stop_load.sh       # Stops load generation

▶️ Execution Steps
1️⃣ Make Scripts Executable (First Time Only)
chmod +x scripts/generate_load.sh scripts/stop_load.sh

2️⃣ Start Load Generation
./scripts/generate_load.sh

🔍 What This Script Does

Deploys temporary BusyBox pods inside the cluster

Continuously sends requests to:

http://lms.openedx.svc.cluster.local:8000
http://cms.openedx.svc.cluster.local:8000


Watches HPA in real-time:

kubectl get hpa -n openedx -w

3️⃣ Monitor Resource Usage
kubectl top pods -n openedx


Expected behavior:

CPU crosses defined threshold

Replicas scale (e.g., 1 → 3)

HPA reacts dynamically

4️⃣ Stop Load Generation
./scripts/stop_load.sh


This removes the load pods safely:

kubectl delete pod load-lms load-cms --ignore-not-found=true


After stopping load:

CPU usage drops

Replicas scale back to minimum

Cluster stabilizes

✅ Validation Outcome

Successful execution confirms:

Functional HPA

Stable Metrics Server integration

Elastic infrastructure design

Production-ready autoscaling capability

This demonstrates operational discipline and adherence to Kubernetes best practices.

🛠 Troubleshooting & Support

Check pod status:

kubectl describe pod <pod-name> -n openedx


View logs:

kubectl logs <pod-name> -n openedx


Check HPA:

kubectl get hpa -n openedx


Verify Metrics Server:

kubectl get deployment metrics-server -n kube-system

📺 Architecture Overview Video

🔗 https://drive.google.com/file/d/1nfYCW3ljfHrNblmQhkmN2aozUnroZJfK/view?usp=sharing

👤 Contact

Muhammad Adeel Munir
DevOps Engineer
adeel.zixer11@gmail.com
