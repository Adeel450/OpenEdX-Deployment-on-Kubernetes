🚀 OpenEdX — Production Deployment on AWS EKS

Production-grade, highly-available OpenEdX LMS deployed on AWS EKS using Terraform (IaC), Kubernetes manifests, and automation scripts. Designed with enterprise best practices: externalized databases, secure networking, observability, backups, autoscaling, and disaster recovery.

Table of Contents

Architecture Overview

Repository Structure

Prerequisites

Quick Start (Bastion Host Workflow)

Security & Maintenance

Backup & Restore

HPA & Scalability Verification

Troubleshooting & Support

Architecture Overview Video

Architecture Overview

This platform is deployed inside a custom AWS VPC spanning two Availability Zones (us-east-1a, us-east-1b) to ensure high availability and fault tolerance.

Key Components

Orchestration: AWS EKS (Kubernetes 1.30+)

Ingress: Nginx Ingress Controller (ALB-backed)

Edge Security: Amazon CloudFront + AWS WAF

Compute: EKS worker nodes (private subnets) + Bastion Host (public subnet)

Data Layer (Externalized):

Amazon RDS (MySQL, Multi-AZ)

Utility EC2 (MongoDB, Redis, Elasticsearch – Dockerized)

Storage: Amazon EBS (gp3) via PVCs

Monitoring: Prometheus & Grafana (Helm)

Autoscaling: Kubernetes Horizontal Pod Autoscaler (HPA)

All workloads and databases operate in private subnets. Administrative access is provided exclusively via a hardened bastion host.

Repository Structure
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
│   ├── restore.sh
│   ├── generate_load.sh
│   └── stop_load.sh
├── terraform/
│   ├── vpc/
│   ├── eks/
│   └── databases/
└── screenshots/

Prerequisites

Run these on the Bastion Host or deployment workstation with access to private VPC resources:

AWS CLI v2

kubectl (compatible with cluster version)

Terraform v1.0+

Helm

Tutor (OpenEdX Manager)

Python 3.10+

Prefer IAM roles or OIDC over long-lived static credentials.

Quick Start (Bastion Host Workflow)

Provision VPC, EKS, and RDS using Terraform before proceeding. See documentation/DEPLOYMENT_GUIDE.md.

Step 1 — Connect to AWS & EKS
aws configure
aws eks update-kubeconfig --region us-east-1 --name openedx-cluster
kubectl get nodes

Step 2 — Install & Configure Tutor
python3 -m venv venv
source venv/bin/activate
pip install "tutor[full]"
tutor config save --interactive


Set:

Production → Yes

SSL handled externally → No inside Tutor

Step 3 — Configure External Databases

Edit Tutor config:

nano "$(tutor config printroot)/config.yml"


Add external DB configuration (example):

RUN_MYSQL: false
MYSQL_HOST: "openedx-mysql.xxxxxx.us-east-1.rds.amazonaws.com"
MYSQL_PORT: 3306
MYSQL_USERNAME: "admin"
MYSQL_PASSWORD: "YourStrongPassword!"
MYSQL_DATABASE: "openedx"

RUN_MONGODB: false
MONGODB_HOST: "10.0.5.90"
MONGODB_PORT: 27017

RUN_REDIS: false
REDIS_HOST: "10.0.5.90"
REDIS_PORT: 6379

RUN_ELASTICSEARCH: false
ELASTICSEARCH_HOST: "10.0.5.90"
ELASTICSEARCH_PORT: 9200


Then:

tutor config save

Step 4 — Deploy OpenEdX
tutor k8s run lms ./manage.py lms migrate
tutor k8s run cms ./manage.py cms migrate
tutor k8s launch
kubectl get pods -n openedx -w

Step 5 — Enable Monitoring
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set grafana.service.type=LoadBalancer

Step 6 — Expose Ingress
kubectl patch svc ingress-nginx-controller \
  -n ingress-nginx \
  -p '{"spec":{"type":"LoadBalancer"}}'

kubectl get svc -n ingress-nginx

Security & Maintenance

Private subnet isolation for workloads

Bastion host access with MFA

Secrets stored in AWS Secrets Manager or encrypted solution

Regular AMI rotation & Kubernetes patching

Backup & Restore

Daily automated backups at 02:00 UTC

Manual Backup
./scripts/backup.sh

Restore
./scripts/restore.sh <TIMESTAMP>

HPA & Scalability Verification

To validate production-grade autoscaling capability, controlled load-testing scripts are implemented under the scripts/ directory.

These scripts generate synthetic internal traffic to LMS and CMS services, validating Kubernetes Horizontal Pod Autoscaler (HPA) behavior under stress.

Objective

This validation ensures:

Correct HPA configuration

Metrics Server availability

CPU-based autoscaling threshold enforcement (e.g., 50%)

Automatic scale-out during load

Elastic scale-in after load removal

Production-grade scalability readiness

Script Location
scripts/
├── backup.sh
├── restore.sh
├── generate_load.sh
└── stop_load.sh

Step 1 — Make Scripts Executable
chmod +x scripts/generate_load.sh scripts/stop_load.sh

Step 2 — Start Load Generation
./scripts/generate_load.sh


This will:

Deploy temporary BusyBox load pods

Continuously send HTTP requests to:

http://lms.openedx.svc.cluster.local:8000
http://cms.openedx.svc.cluster.local:8000


Monitor HPA:

kubectl get hpa -n openedx -w

Step 3 — Observe Autoscaling
kubectl top pods -n openedx


Expected behavior:

CPU exceeds threshold

Replicas scale (e.g., 1 → 3)

HPA dynamically adjusts

Step 4 — Stop Load Generation
./scripts/stop_load.sh


Cleanup command:

kubectl delete pod load-lms load-cms --ignore-not-found=true


After stopping load:

CPU drops

Replicas scale back

Cluster stabilizes

Validation Outcome

Successful validation confirms:

Functional HPA

Stable Metrics Server

Elastic infrastructure behavior

Enterprise-ready autoscaling

Troubleshooting & Support

Refer to documentation/TROUBLESHOOTING.md

Common commands:

kubectl describe pod <pod> -n openedx
kubectl logs <pod> -n openedx --previous
kubectl get hpa -n openedx
kubectl get deployment metrics-server -n kube-system

Contact

Submitted by: Muhammad Adeel Munir
Role: DevOps Engineer
Email: adeel.zixer11@gmail.com

📺 Architecture Overview Video

A visual walkthrough of the OpenEdX + AWS EKS architecture:

🔗 https://drive.google.com/file/d/1nfYCW3ljfHrNblmQhkmN2aozUnroZJfK/view?usp=sharing
