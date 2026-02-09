🚀 OpenEdX Production Deployment on AWS EKS

This repository provides a production-grade, highly available OpenEdX LMS deployment on AWS EKS, built using Infrastructure as Code (Terraform) and Kubernetes-native tooling.

The solution follows enterprise best practices, including externalized databases, secure networking, monitoring, backups, and disaster recovery.

🏗️ Architecture Overview

The platform is deployed inside a custom AWS VPC spanning two Availability Zones (us-east-1a, us-east-1b) for high availability.

Key Components

Container Orchestration: AWS EKS (Kubernetes 1.30+)

Ingress Layer: Nginx Ingress Controller (ALB-backed)

Edge Security: AWS CloudFront + AWS WAF

Compute:

EKS Worker Nodes (Private Subnets)

Bastion Host (Public Subnet)

Data Layer (Externalized):

MySQL: Amazon RDS (Multi-AZ)

MongoDB, Redis, Elasticsearch: Utility EC2 (Dockerized)

Storage: Amazon EBS (gp3) via PVCs

Monitoring: Prometheus & Grafana

📌 All application workloads and databases run in private subnets.

📂 Repository Structure
.
├── README.md
├── diagrams/
├── documentation/
│   ├── DEPLOYMENT_GUIDE.md
│   ├── TROUBLESHOOTING.md
│   └── BACKUP_STRATEGY.md
├── k8s-manifests/
│   ├── ingress/
│   ├── monitoring/
│   └── tutor-manifest/
├── scripts/
│   ├── backup.sh
│   └── restore.sh
├── terraform/
│   ├── vpc/
│   ├── eks/
│   └── databases/
└── screenshots/

🛠️ Prerequisites

Ensure the following tools are installed on the Bastion Host:

AWS CLI v2 (configured with admin access)

kubectl (EKS compatible)

Terraform v1.0+

Tutor (OpenEdX Manager)

Helm

🚀 Quick Start (Bastion Host Workflow)

⚠️ Infrastructure provisioning (VPC, EKS, RDS) must be completed first using Terraform.
Refer to documentation/DEPLOYMENT_GUIDE.md.

Step 1: Connect to AWS & EKS Cluster
Configure AWS Credentials
aws configure

Update kubeconfig
aws eks update-kubeconfig \
  --region us-east-1 \
  --name openedx-cluster

Verify Cluster Access
kubectl get nodes


✅ Expected: Worker nodes in Ready state

Step 2: Install & Configure Tutor
Create and Activate Virtual Environment
python3 -m venv venv
source venv/bin/activate

Install Tutor
pip install "tutor[full]"

Run Interactive Configuration
tutor config save --interactive


📌 Select:

Production: yes

SSL: no (Handled by ALB / CloudFront)

Step 3: Configure External Databases
Edit Tutor Configuration
nano "$(tutor config printroot)/config.yml"

Append External Database Configuration
# --- External Databases Configuration ---

RUN_MYSQL: false
MYSQL_HOST: "openedx-mysql.xxxxxx.us-east-1.rds.amazonaws.com"
MYSQL_PORT: 3306
MYSQL_USERNAME: "admin"
MYSQL_PASSWORD: "YourStrongPassword!"
MYSQL_DATABASE: "openedx"

RUN_MONGODB: false
MONGODB_HOST: "10.0.5.90"
MONGODB_PORT: 27017
MONGODB_DATABASE: "openedx"

RUN_REDIS: false
REDIS_HOST: "10.0.5.90"
REDIS_PORT: 6379

RUN_ELASTICSEARCH: false
ELASTICSEARCH_HOST: "10.0.5.90"
ELASTICSEARCH_PORT: 9200
ELASTICSEARCH_SCHEME: "http"

Save & Regenerate Manifests
tutor config save

Step 4: Deploy OpenEdX on Kubernetes
Run Initial Database Migrations
tutor k8s run lms ./manage.py lms migrate
tutor k8s run cms ./manage.py cms migrate

Launch Platform
tutor k8s launch

Monitor Pods
kubectl get pods -n openedx -w

Step 5: Enable Monitoring (Prometheus & Grafana)
Add Helm Repository
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

Install Monitoring Stack
helm install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set grafana.service.type=LoadBalancer

Verify Deployment
kubectl get pods -n monitoring

Step 6: Expose Ingress Controller
Patch Ingress Service
kubectl patch svc ingress-nginx-controller \
  -n ingress-nginx \
  -p '{"spec":{"type":"LoadBalancer"}}'

Get External Endpoint
kubectl get svc -n ingress-nginx

🛡️ Security & Maintenance

Network Isolation: All workloads run in private subnets

Access Control: Bastion Host with SSH agent forwarding

Backups: Daily automated backups at 02:00 UTC

Manual Backup
./scripts/backup.sh

Restore
./scripts/restore.sh <TIMESTAMP>


📘 See documentation/TROUBLESHOOTING.md for known issues.

📞 Contact

Submitted by: Muhammad Adeel Munir
Role: DevOps Engineer
Email: adeel.zixer11@gmail.com
