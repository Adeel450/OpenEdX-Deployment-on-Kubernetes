# 🚀 OpenEdX — Production Deployment on AWS EKS

**Production-grade, highly-available OpenEdX LMS deployed on AWS EKS** using Terraform (IaC), Kubernetes manifests, and automation scripts. Designed with enterprise best practices: externalized databases, secure networking, observability, backups, and disaster recovery.

---

## Table of contents

1. [Architecture Overview](#architecture-overview)
2. [Repository Structure](#repository-structure)
3. [Prerequisites](#prerequisites)
4. [Quick Start (Bastion Host Workflow)](#quick-start-bastion-host-workflow)

   * Step 1: Connect to AWS & EKS
   * Step 2: Install & Configure Tutor
   * Step 3: Configure External Databases
   * Step 4: Deploy OpenEdX on Kubernetes
   * Step 5: Enable Monitoring
   * Step 6: Expose Ingress Controller
5. [Security & Maintenance](#security--maintenance)
6. [Backup & Restore](#backup--restore)
7. [Troubleshooting & Support](#troubleshooting--support)

---

## Architecture Overview

This platform is deployed inside a custom AWS VPC spanning **two Availability Zones** (`us-east-1a`, `us-east-1b`) for high availability and fault tolerance.

**Key components**

* **Orchestration:** AWS EKS (Kubernetes 1.30+)
* **Ingress:** Nginx Ingress Controller (ALB-backed)
* **Edge Security:** Amazon CloudFront + AWS WAF
* **Compute:** EKS worker nodes (private subnets) + Bastion Host (public subnet)
* **Data layer (externalized):** Amazon RDS (MySQL, Multi‑AZ) + Utility EC2 for MongoDB/Redis/Elasticsearch (Dockerized)
* **Storage:** Amazon EBS (gp3) via PVCs
* **Monitoring:** Prometheus & Grafana (Helm)

> All application workloads and databases are deployed in private subnets. Administrative access is provided via a hardened bastion host.

---

## Repository Structure

```text
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
```

---

## Prerequisites

Run these on the **Bastion Host** or deployment workstation with network access to the private VPC resources.

* AWS CLI v2 (configured with IAM credentials scoped to required infra)
* kubectl (compatible with EKS cluster version)
* terraform (v1.0+)
* tutor (OpenEdX Manager)
* helm
* Python 3.10+ (for Tutor virtualenv)

Security note: Prefer using temporary credentials (IAM roles) or OIDC where possible; avoid embedding long-lived secrets in repo files.

---

## Quick Start (Bastion Host Workflow)

> **Important:** Provision network, EKS cluster, and RDS using Terraform first. See `documentation/DEPLOYMENT_GUIDE.md`.

### Step 1 — Connect to AWS & EKS cluster

**Configure AWS credentials**

```bash
aws configure
# Provide Access Key ID, Secret Access Key, default region (us-east-1) and output (json)
```

**Update kubeconfig**

```bash
aws eks update-kubeconfig \
  --region us-east-1 \
  --name openedx-cluster
```

**Verify cluster access**

```bash
kubectl get nodes
# Expect worker nodes in the Ready state
```

---

### Step 2 — Install & configure Tutor

**Create and activate a virtual environment**

```bash
python3 -m venv venv
source venv/bin/activate
```

**Install Tutor (full)**

```bash
pip install "tutor[full]"
```

**Run interactive configuration**

```bash
tutor config save --interactive
```

When prompted:

* Set `production` -> **yes**
* SSL handled at the edge (ALB/CloudFront) -> set SSL to **no** inside Tutor

---

### Step 3 — Configure external databases

**Open Tutor configuration file**

```bash
nano "$(tutor config printroot)/config.yml"
```

**Append the external database configuration (example)**

```yaml
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
```

> Replace example hosts/credentials with secure values (use Secrets Manager or SOPS for secrets).

**Save config and regenerate manifests**

```bash
tutor config save
```

---

### Step 4 — Deploy OpenEdX on Kubernetes

**Run database migrations**

```bash
tutor k8s run lms ./manage.py lms migrate
tutor k8s run cms ./manage.py cms migrate
```

**Launch all OpenEdX K8s resources**

```bash
tutor k8s launch
```

**Monitor pods**

```bash
kubectl get pods -n openedx -w
```

---

### Step 5 — Enable monitoring (Prometheus & Grafana)

**Add Helm repo and update**

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
```

**Install kube-prometheus-stack**

```bash
helm install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set grafana.service.type=LoadBalancer
```

**Verify monitoring components**

```bash
kubectl get pods -n monitoring
```

Tip: Secure Grafana with an ingress auth or use AWS PrivateLink / port-forward for admin access.

---

### Step 6 — Expose Ingress controller

**Patch the ingress-nginx service to use a LoadBalancer**

```bash
kubectl patch svc ingress-nginx-controller \
  -n ingress-nginx \
  -p '{"spec":{"type":"LoadBalancer"}}'
```

**Retrieve external endpoint**

```bash
kubectl get svc -n ingress-nginx
```

Follow-up: Configure ALB Ingress annotations, TLS certs via ACM, and CloudFront/WAF as described in the documentation.

---

## Security & Maintenance

* **Network:** Private subnets for workload and data. Public subnet only for bastion host.
* **Access:** Bastion host with MFA and SSH agent forwarding for admin tasks.
* **Secrets:** Store DB credentials and sensitive values in AWS Secrets Manager or an encryption solution (SOPS, Sealed Secrets).
* **Patching:** Regularly rotate node AMIs and Kubernetes patching schedule.

---

## Backup & Restore

* Daily automated backups scheduled at **02:00 UTC** (RDS snapshot + DB dump for utility server).

**Manual backup**

```bash
./scripts/backup.sh
```

**Restore**

```bash
./scripts/restore.sh <TIMESTAMP>
```

Record backup retention policy and test restores routinely.

---

## Troubleshooting & Support

* See `documentation/TROUBLESHOOTING.md` for curated issues and recovery steps.
* Common checks:

  * `kubectl describe pod <pod> -n openedx`
  * `kubectl logs <pod> -n openedx --previous`
  * Validate network ACLs and security group egress rules for DB connectivity

---

## Contact

**Submitted by:** Muhammad Adeel Munir
**Role:** DevOps Engineer
**Email:** [adeel.zixer11@gmail.com](mailto:adeel.zixer11@gmail.com)

---

---
**📺 Architecture Overview Video**

A visual walkthrough of the OpenEdX + AWS EKS architecture design is available here:

**🔗 Architecture Video (Google Drive):**

https://drive.google.com/file/d/1nfYCW3ljfHrNblmQhkmN2aozUnroZJfK/view?usp=sharing

---



