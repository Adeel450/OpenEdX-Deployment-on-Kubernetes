# 🚀 OpenEdX Production Deployment on AWS EKS

**Technical Assessment Submission for Al Nafi DevOps Department**

This repository contains the complete Infrastructure-as-Code (IaC), Kubernetes manifests, and automation scripts required to deploy a production-grade, highly available **OpenEdX Learning Management System (LMS)** on **AWS Elastic Kubernetes Service (EKS)**.

The solution is architected to meet enterprise standards, featuring **External Databases**, **Nginx Ingress**, **AWS WAF/CloudFront integration**, and **Automated Disaster Recovery**.

---

## Architecture Overview

The platform is built on a **Custom VPC** network designed for security and high availability across two Availability Zones (`us-east-1a`, `us-east-1b`).

* **Orchestration:** AWS EKS (Kubernetes 1.30+)
* **Web Layer:** Nginx Ingress Controller (Replacing Caddy) behind AWS Application Load Balancer (ALB).
* **Edge Security:** AWS WAF + Amazon CloudFront (CDN).
* **Compute Layer:**
    * **Application:** EKS Worker Nodes (Private Subnets).
    * **Management:** Bastion Host (Public Subnet) for secure administrative access.
* **Data Layer (Externalized):**
    * **MySQL:** AWS RDS (Multi-AZ).
    * **NoSQL (Mongo, Redis, Elastic):** Dedicated Utility Server (Private EC2) managed via Docker.
* **Storage:** AWS EBS (gp3) via Persistent Volume Claims (PVC).

![Architecture Diagram](diagrams/architecture-diagram.png)

---

## Repository Structure

```text
.
├── README.md                      # Project Overview & Quick Start
├── diagrams/                      # Architecture & Network Diagrams
├── documentation/                 # Detailed Operational Guides
│   ├── DEPLOYMENT_GUIDE.md        # Step-by-Step Installation Manual
│   ├── TROUBLESHOOTING.md         # Issue Resolution Log
│   └── BACKUP_STRATEGY.md         # DR & Backup Policies
├── k8s-manifests/                 # Kubernetes YAML Configurations
│   ├── ingress/                   # Nginx Ingress & Certs
│   ├── monitoring/                # Prometheus/Grafana Stack
│   └── tutor-manifest/            # OpenEdX K8s Resources
├── scripts/                       # Automation Scripts
│   ├── backup.sh                  # Database Backup Script
│   └── restore.sh                 # Database Restoration Script
├── terraform/                     # Infrastructure as Code
│   ├── vpc/                       # Network Layer (VPC, Subnets, IGW, NAT)
│   ├── eks/                       # EKS Cluster & Node Groups
│   └── databases/                 # RDS & Utility Server
└── screenshots/                   # Proof of Implementation
 PrerequisitesTo deploy this infrastructure, ensure the following tools are installed on your deployment station (Bastion Host):AWS CLI v2 (Configured with Administrator Access)Kubectl (Compatible with EKS version)Terraform (v1.0+)Tutor (OpenEdX Manager)Helm (For Ingress/Monitoring) Quick Start Guide (Bastion Host Workflow)Follow these commands on your Bastion Host to configure the cluster and launch the platform. For infrastructure provisioning steps (VPC/RDS/EKS creation), refer to the Deployment Guide.Step 1: Connect to AWS & EKS ClusterAuthenticate your session and generate the kubeconfig file to communicate with the cluster.Bash# 1. Configure AWS Credentials
aws configure
# Enter Access Key ID, Secret Key, Region (us-east-1), Output (json)

# 2. Update Kubeconfig
aws eks update-kubeconfig --region us-east-1 --name openedx-cluster

# 3. Verify Connection
kubectl get nodes
# Expected Output: List of worker nodes in 'Ready' state
Step 2: Install & Configure TutorSet up the OpenEdX manager in a virtual environment.Bash# 1. Create & Activate Virtual Env
python3 -m venv venv
source venv/bin/activate

# 2. Install Tutor (Full Release)
pip install "tutor[full]"

# 3. Interactive Configuration
tutor config save --interactive
# Inputs:
# - Production: "y"
# - LMS Domain: "lms.adeel-openedx.com"
# - CMS Domain: "cms.adeel-openedx.com"
# - SSL: "n" (Handled by AWS ALB)
Step 3: Connect External DatabasesOverride the default Kubernetes database configuration to point to AWS RDS and the Utility Server.1. Open Configuration File:Bashnano "$(tutor config printroot)/config.yml"
2. Append the following configuration (Replace with your actual endpoints):YAML# --- External Databases Configuration ---
RUN_MYSQL: false
MYSQL_HOST: "openedx-mysql.xxxxxx.us-east-1.rds.amazonaws.com"
MYSQL_PORT: 3306
MYSQL_USERNAME: "admin"
MYSQL_PASSWORD: "YourStrongPassword!"
MYSQL_DATABASE: "openedx"

RUN_MONGODB: false
MONGODB_HOST: "10.0.5.90"  # Private IP of Utility Server
MONGODB_PORT: 27017
MONGODB_DATABASE: "openedx"

RUN_REDIS: false
REDIS_HOST: "10.0.5.90"
REDIS_PORT: 6379

RUN_ELASTICSEARCH: false
ELASTICSEARCH_HOST: "10.0.5.90"
ELASTICSEARCH_PORT: 9200
ELASTICSEARCH_SCHEME: "http"
3. Save Changes and Regenerate Manifests:Bashtutor config save
Step 4: Deploy Platform to KubernetesLaunch the application pods, services, and ingress rules.Bash# 1. Initialize Database Migrations (Run once)
tutor k8s run lms ./manage.py lms migrate
tutor k8s run cms ./manage.py cms migrate

# 2. Launch OpenEdX Platform
tutor k8s launch

# 3. Monitor Deployment Status
kubectl get pods -n openedx -w
# Wait until all pods are 'Running'

CompletedComprehensive markdown guides included

🛡️Security & Maintenance
Access Control: All worker nodes and databases reside in Private Subnets. Access is restricted to the Bastion Host via SSH Agent Forwarding.
Backups: Database backups run daily at 02:00 UTC.
Manual Trigger: ./scripts/backup.sh
Restore: ./scripts/restore.sh <TIMESTAMP>
Troubleshooting: Refer to TROUBLESHOOTING.md for common issues and fixes.

📞 Contact
Submitted by: Muhammad Adeel Munir Role: DevOps Engineer Email: adeel.zixer11@gmail.com


