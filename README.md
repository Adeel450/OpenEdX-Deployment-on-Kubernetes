🚀 OpenEdX — Production Deployment on AWS EKS

Production-grade, highly-available OpenEdX LMS deployed on AWS EKS using Terraform (IaC), Kubernetes manifests, and automation scripts. Designed with enterprise best practices: externalized databases, secure networking, observability, backups, disaster recovery, and autoscaling validation.

Table of contents

Architecture Overview

Repository Structure

Prerequisites

Quick Start (Bastion Host Workflow)

Security & Maintenance

Backup & Restore

HPA & Scalability Verification

Troubleshooting & Support

Architecture Overview

This platform is deployed inside a custom AWS VPC spanning two Availability Zones (us-east-1a, us-east-1b) for high availability and fault tolerance.

Key components

Orchestration: AWS EKS (Kubernetes 1.30+)

Ingress: Nginx Ingress Controller (ALB-backed)

Edge Security: Amazon CloudFront + AWS WAF

Compute: EKS worker nodes (private subnets) + Bastion Host (public subnet)

Data layer (externalized): Amazon RDS (MySQL, Multi-AZ) + Utility EC2 for MongoDB/Redis/Elasticsearch (Dockerized)

Storage: Amazon EBS (gp3) via PVCs

Monitoring: Prometheus & Grafana (Helm)

Autoscaling: Kubernetes HPA (CPU-based scaling)

All workloads and databases operate in private subnets. Administrative access is controlled via a hardened bastion host.

Repository Structure
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

Prerequisites

AWS CLI v2

kubectl

terraform (v1.0+)

helm

tutor (OpenEdX Manager)

Python 3.10+

Quick Start (Bastion Host Workflow)

(Your original deployment steps remain unchanged here — omitted for brevity in this preview, but keep them exactly as they are in your current README.)

Security & Maintenance

Private subnets for workloads

IAM-based access control

Secrets Manager / encrypted secrets

Regular patching & AMI rotation

MFA enforced on Bastion access

Backup & Restore

Daily automated backups scheduled at 02:00 UTC.

Manual Backup

./scripts/backup.sh


Restore

./scripts/restore.sh <TIMESTAMP>

📈 HPA & Scalability Verification

To validate the autoscaling behavior of the OpenEdX LMS and CMS services, dedicated load-generation scripts have been implemented within the scripts/ directory.

These scripts simulate high internal cluster traffic using lightweight Kubernetes pods and validate Horizontal Pod Autoscaler (HPA) responsiveness under controlled stress conditions.

Objective

The load testing workflow verifies:

Proper configuration of Kubernetes HPA

Metrics Server functionality

CPU-based autoscaling thresholds (e.g., 50%)

Automatic replica scaling under load

Elastic recovery once load subsides

Production-grade scalability readiness

Script Location
scripts/
├── generate_load.sh   # Initiates high-frequency internal traffic
└── stop_load.sh       # Gracefully terminates load generation

Execution Procedure
1️⃣ Make Scripts Executable (First Time Only)
chmod +x scripts/generate_load.sh scripts/stop_load.sh

2️⃣ Start Load Generation
./scripts/generate_load.sh


This script performs the following:

Deploys ephemeral BusyBox pods inside the cluster

Generates high-frequency HTTP requests to:

http://lms.openedx.svc.cluster.local:8000
http://cms.openedx.svc.cluster.local:8000


Continuously monitors HPA status:

kubectl get hpa -n openedx -w

3️⃣ Observe Autoscaling Behavior

During load execution, you should observe:

CPU utilization crossing defined threshold

LMS and CMS replicas scaling (e.g., 1 → 3)

HPA reacting dynamically based on metrics

Monitor resource usage with:

kubectl top pods -n openedx

4️⃣ Stop Load Generation
./scripts/stop_load.sh


This command safely removes load-generator pods:

kubectl delete pod load-lms load-cms --ignore-not-found=true


After stopping load:

CPU utilization decreases

HPA scales deployments back to minimum replicas

Cluster returns to steady operational state

Validation Outcome

Successful execution confirms:

Functional HPA configuration

Stable Metrics Server integration

Elastic infrastructure design

Production-ready autoscaling capability

This testing methodology demonstrates operational discipline, scalability assurance, and adherence to enterprise Kubernetes best practices.

Troubleshooting & Support

kubectl describe pod <pod> -n openedx

kubectl logs <pod> -n openedx

kubectl get hpa -n openedx

Verify Metrics Server health

📺 Architecture Overview Video

🔗 Architecture Walkthrough:
https://drive.google.com/file/d/1nfYCW3ljfHrNblmQhkmN2aozUnroZJfK/view?usp=sharing

Contact

Muhammad Adeel Munir
DevOps Engineer
adeel.zixer11@gmail.com
