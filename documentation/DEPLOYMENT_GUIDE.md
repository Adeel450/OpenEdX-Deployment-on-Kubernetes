
---

# 🚀 Open edX Deployment Guide on AWS EKS

This guide provides a **production-grade, step-by-step walkthrough** for deploying the Open edX platform on **Amazon Elastic Kubernetes Service**.

The architecture is designed for:

✅ High Availability
✅ Security & Network Isolation
✅ Scalablity & Performance
✅ Production Reliability

It uses a **custom VPC**, private subnets for applications and data, and public subnets for load balancing.

---

## 📑 Table of Contents

* [Architecture Overview](#architecture-overview)
* [1. Network Infrastructure (VPC)](#1-network-infrastructure-vpc)
* [2. Relatonal Database Layer (RDS MySQL)](#2-relational-database-layer-rds-mysql)
* [3. Caching & Queue Layer (Redis)](#3-caching--queue-layer-redis)
* [4. NoSQL Databases (StatefulSets)](#4-nosql-databases-statefulsets)
* [5. Kubernetes Cluster Setup (EKS)](#5-kubernetes-cluster-setup-eks)
* [6. Application Deployment (Tutor)](#6-application-deployment-tutor)
* [7. Monitoring & Ingress](#7-monitoring--ingress)
* [8. Autoscaling Verification](#8-autoscaling-verification)

---

## 🏗 Architecture Overview

### Network Design

* **VPC CIDR:** `10.0.0.0/16`
* **Availability Zones:** `us-east-1a`, `us-east-1b`
* **Subnet Layers:**

| Layer            | Purpose                                  |
| ---------------- | ---------------------------------------- |
| **Public**       | Load Balancers, NAT Gateway              |
| **Private App**  | EKS Worker Nodes                         |
| **Private Data** | Databases & storage (no internet access) |

---

## 1️⃣ Network Infrastructure (VPC)

A custom VPC ensures strict separation between public access, application logic, and data storage.

### 1.1 VPC & Subnet Layout

| Resource     | Name                  | CIDR          | AZ         |
| ------------ | --------------------- | ------------- | ---------- |
| VPC          | `openedx-vpc`         | `10.0.0.0/16` | —          |
| Public       | public-subnet-1       | 10.0.1.0/24   | us-east-1a |
| Public       | public-subnet-2       | 10.0.2.0/24   | us-east-1b |
| Private App  | private-app-subnet-1  | 10.0.3.0/24   | us-east-1a |
| Private App  | private-app-subnet-2  | 10.0.4.0/24   | us-east-1b |
| Private Data | private-data-subnet-1 | 10.0.5.0/24   | us-east-1a |
| Private Data | private-data-subnet-2 | 10.0.6.0/24   | us-east-1b |

---

### 1.2 Manual Setup (AWS Console)

1. Create VPC → `openedx-vpc`
2. Create all subnets listed above
3. Create & attach Internet Gateway → `openedx-igw`
4. Create NAT Gateway in `public-subnet-1`
5. Configure Route Tables:

**Public RT**

```
0.0.0.0/0 → Internet Gateway
```

**Private App RT**

```
0.0.0.0/0 → NAT Gateway
```

**Private Data RT**

```
Local traffic only (No internet)
```

---

### 1.3 Automated Setup (Terraform)

**Source:** `terraform/vpc/vpc.tf`

```bash
cd terraform/vpc
terraform init
terraform apply -auto-approve
```

---

## 2️⃣ Relational Database Layer (RDS MySQL)

To ensure persistence and security, MySQL runs inside private subnets using **Amazon RDS**.

### 2.1 Security Group

**Name:** `openedx-data-sg`

Allow inbound from VPC CIDR:

| Port | Service |
| ---- | ------- |
| 3306 | MySQL   |
| 6379 | Redis   |

---

### 2.2 Provision MySQL (Console)

* Engine: MySQL 8.0
* Instance: `db.t3.medium`
* VPC: openedx-vpc
* Subnet Group: Private Data
* Public Access: ❌ Disabled

---

### 2.3 Terraform Deployment

**Source:** `terraform/databases/mysql.tf`

```bash
cd terraform/databases
terraform init
terraform apply -auto-approve
```

---

## 3️⃣ Caching & Queue Layer (Redis)

Open edX uses Redis for caching, sessions, and Celery queues.

Managed via **Amazon ElastiCache**.

### Console Setup

* Cluster Mode: Disabled
* Node Type: `cache.t3.medium`
* Subnet Group: Private Data subnets
* Security Group: `openedx-data-sg`

---

### Terraform Deployment

**Source:** `terraform/databases/redis.tf`

```bash
cd terraform/databases
terraform init
terraform apply -auto-approve
```

---

## 4️⃣ NoSQL Databases (StatefulSets)

MongoDB and Elasticsearch run **inside Kubernetes** using StatefulSets and persistent storage.

### Purpose

**MongoDB**

* Modulestore
* Course structure & content

**Elasticsearch**

* Search & indexing

Storage uses **Amazon Elastic Block Store** (`gp3`).

---

### Deploy Storage & Databases

```bash
kubectl apply -f k8s/storage-class.yaml
kubectl apply -f k8s/mongodb.yaml
kubectl apply -f k8s/elasticsearch.yaml
```

---

### Verify Persistence

```bash
kubectl get pods
kubectl get pvc
```

Ensure:

✔ Pods are **Running**
✔ PVCs are **Bound**

---

## 5️⃣ Kubernetes Cluster Setup (EKS)

Deploy the control plane and worker nodes using **Amazon Web Services** managed Kubernetes.

### Cluster Configuration

* Cluster Role: `openedx-eks-cluster-role`
* VPC: openedx-vpc
* Subnets: Public + Private App
* Node Group: `openedx-workers-ng`
* Instance: `t3.large`

---

### Terraform Deployment

**Source:** `terraform/eks/main.tf`

```bash
cd terraform/eks
terraform init
terraform apply -auto-approve
```

---

## 6️⃣ Application Deployment (Tutor)

### Connect to Cluster

```bash
aws configure
aws eks update-kubeconfig --region us-east-1 --name openedx-cluster
```

---

### Configure External Services

```bash
tutor config save --set MYSQL_HOST="<rds-endpoint>.amazonaws.com"
tutor config save --set REDIS_HOST="<elasticache-endpoint>.amazonaws.com"
```

---

### Launch Open edX

```bash
tutor config save
tutor k8s launch
```

---

## 7️⃣ Monitoring & Ingress

### 7.1 Monitoring Stack (Prometheus + Grafana)

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set grafana.service.type=LoadBalancer
```

---

### 7.2 CDN & Ingress

**Traffic Flow**

User → CloudFront → AWS WAF → LoadBalancer → Nginx Ingress → Open edX

Components:

* Nginx Ingress Controller
* AWS CloudFront (CDN)
* AWS WAF protection
* AWS Certificate Manager (SSL)

---

## 8️⃣ Autoscaling Verification

Validate Horizontal Pod Autoscaler (HPA) behavior.

### Generate Load

```bash
kubectl run -i --tty load-generator \
--rm --image=busybox:1.28 \
--restart=Never -n openedx \
-- /bin/sh -c "while sleep 0.01; do wget -q -O- http://lms:8000; done"
```

---

### Watch Scaling

```bash
kubectl get hpa -n openedx -w
```

Pods will scale automatically when CPU exceeds threshold.

---

## ✅ Deployment Complete

Your Open edX platform is now:

✔ Highly Available
✔ Secure & Isolated
✔ Autoscaling Ready
✔ Production Hardened
✔ Cloud-Native

---


