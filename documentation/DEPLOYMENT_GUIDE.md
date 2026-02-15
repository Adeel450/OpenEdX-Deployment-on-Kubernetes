
---

```markdown
# Open edX Deployment Guide on AWS EKS

This guide provides a comprehensive, step-by-step walkthrough for deploying a production-ready Open edX platform on AWS Elastic Kubernetes Service (EKS).

The deployment architecture is designed for **High Availability (HA)**, **Security**, and **Scalability** using a custom VPC, private subnets for data/apps, and public subnets for load balancers. 

---

## Architecture Overview

* **VPC CIDR:** `10.0.0.0/16`
* **Availability Zones:** 2 (`us-east-1a`, `us-east-1b`)
* **Subnet Strategy:**
    * **Public (Layer 1):** Load Balancers, NAT Gateways.
    * **Private App (Layer 2):** EKS Worker Nodes (Application Logic).
    * **Private Data (Layer 3):** Databases (RDS, ElastiCache, EBS Volumes) - **No Internet Access**.

---

## Step 1: Network Infrastructure Setup (VPC)

We utilize a custom VPC architecture with 6 subnets to ensure strict isolation between public and private resources.

### 1.1 VPC & Subnet Configuration

| Resource Type | Name | CIDR Block | Availability Zone |
| :--- | :--- | :--- | :--- |
| **VPC** | `openedx-vpc` | `10.0.0.0/16` | - |
| **Public Subnet** | `public-subnet-1` | `10.0.1.0/24` | us-east-1a |
| **Public Subnet** | `public-subnet-2` | `10.0.2.0/24` | us-east-1b |
| **Private App Subnet** | `private-app-subnet-1` | `10.0.3.0/24` | us-east-1a |
| **Private App Subnet** | `private-app-subnet-2` | `10.0.4.0/24` | us-east-1b |
| **Private Data Subnet** | `private-data-subnet-1` | `10.0.5.0/24` | us-east-1a |
| **Private Data Subnet** | `private-data-subnet-2` | `10.0.6.0/24` | us-east-1b |

### 1.2 Option A: Setup via AWS Console (Manual)
1.  **Create VPC:** Name it `openedx-vpc` with CIDR `10.0.0.0/16`.
2.  **Create Subnets:** Create the 6 subnets listed above in their respective AZs.
3.  **Internet Gateway (IGW):** Create `openedx-igw` and attach to VPC.
4.  **NAT Gateway:** Create `openedx-nat` in `public-subnet-1` (Allocate Elastic IP).
5.  **Route Tables:**
    * **Public RT:** Routes `0.0.0.0/0` → `IGW`. Associate with both Public Subnets.
    * **Private App RT:** Routes `0.0.0.0/0` → `NAT Gateway`. Associate with both Private App Subnets.
    * **Private Data RT:** No internet routes (Local traffic only). Associate with both Private Data Subnets.

### 1.3 Option B: Setup via Terraform (Automated)
* **Source Code:** `terraform/vpc/vpc.tf`

**Deployment Command:**
```bash
cd terraform/vpc
terraform init
terraform apply -auto-approve

```

---

## Step 2: Relational Database Layer (AWS RDS)

To ensure data persistence and security, we deploy MySQL on AWS RDS inside isolated private subnets.

### 2.1 Create Database Security Group

* **Name:** `openedx-data-sg`
* **Inbound Rules:** Allow `10.0.0.0/16` (VPC CIDR) on ports: `3306` (MySQL), `6379` (Redis).

### 2.2 Provision MySQL Database (AWS RDS)

Go to RDS > Create database > Standard create > MySQL.

* **Version:** MySQL 8.0.x
* **Instance:** `db.t3.medium`
* **Connectivity:** VPC: `openedx-vpc`, Subnet Group: Private Data Subnets, Public Access: NO.

### 2.3 Option B: Setup via Terraform

* **Source Code:** `terraform/databases/mysql.tf`

**Deployment Command:**

```bash
cd terraform/databases
terraform init
terraform apply -auto-approve

```

---

## Step 3: Caching & Task Queue Layer (AWS ElastiCache Redis)

Open edX heavily relies on Redis for caching and Celery task management. We use fully managed AWS ElastiCache for high availability.

### 3.1 Provision Redis Cluster (AWS Console)

1. Go to **ElastiCache** > **Redis clusters** > **Create cluster**.
2. **Cluster Mode:** Disabled (Standard for Open edX default config).
3. **Node Type:** `cache.t3.medium`.
4. **Subnet Group:** Select the Private Data Subnets (`10.0.5.0/24`, `10.0.6.0/24`).
5. **Security Group:** Attach `openedx-data-sg` (allowing port `6379`).

### 3.2 Setup via Terraform (Automated)

All caching infrastructure is codified using Terraform for rapid deployment.

* **Source Code:** `terraform/databases/redis.tf`

**Deployment Command:**

```bash
cd terraform/databases
terraform init
terraform apply -auto-approve

```

---

## Step 4: NoSQL Databases (Kubernetes StatefulSets)

Instead of using standalone EC2 instances, MongoDB and Elasticsearch are deployed natively within the EKS cluster utilizing **StatefulSets** and **Persistent Volume Claims (PVCs)** attached to AWS EBS `gp3` volumes.

### 4.1 Apply Storage Class & StatefulSets

Navigate to the Kubernetes manifests directory to deploy the databases. These manifests include built-in Liveness and Readiness probes.

```bash
kubectl apply -f k8s/storage-class.yaml
kubectl apply -f k8s/mongodb.yaml
kubectl apply -f k8s/elasticsearch.yaml

```

### 4.2 Verify Data Persistence

```bash
kubectl get pods -n default
kubectl get pvc -n default

```

*Ensure both `mongodb-0` and `elasticsearch-0` are in `Running` state and PVCs are `Bound`.*

---

## Step 5: Kubernetes Cluster Setup (AWS EKS)

Deploy the EKS Control Plane and Worker Nodes.

### 5.1 Create EKS Cluster & Node Groups

* **Role:** `openedx-eks-cluster-role`
* **VPC:** `openedx-vpc`
* **Subnets:** Select Public and Private App subnets.
* **Node Group:** `openedx-workers-ng` (Instance: `t3.large`, Subnets: Private App).

### 5.2 Option B: Setup via Terraform

* **Source Code:** `terraform/eks/main.tf`

**Deployment Command:**

```bash
cd terraform/eks
terraform init
terraform apply -auto-approve

```

---

## Step 6: Application Launch (Tutor)

Configure your local deployment station or CI/CD runner to manage the cluster and launch Open edX using Tutor.

### 6.1 Connect to EKS Cluster

```bash
aws configure
aws eks update-kubeconfig --region us-east-1 --name openedx-cluster

```

### 6.2 Configure Open edX External Connections

Edit the Tutor `config.yml` to point to your managed AWS services (RDS and ElastiCache) and internal K8s StatefulSets.

```bash
tutor config save --set MYSQL_HOST="<rds-endpoint>.amazonaws.com"
tutor config save --set REDIS_HOST="<elasticache-endpoint>.amazonaws.com"

```

### 6.3 Launch Deployment

```bash
tutor config save
tutor k8s launch

```

---

## Step 7: Post-Deployment Configuration (Monitoring & Ingress)

### 7.1 Enable Monitoring (Prometheus & Grafana)

We use the official Helm charts to deploy a lightweight monitoring stack.

```bash
helm repo add prometheus-community [https://prometheus-community.github.io/helm-charts](https://prometheus-community.github.io/helm-charts)
helm repo update
helm install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set grafana.service.type=LoadBalancer

```

### 7.2 CloudFront & Ingress Configuration

1. **Nginx Ingress:** Configured as a LoadBalancer.
2. **AWS CloudFront:** Configured as a CDN bridging traffic to the EKS LoadBalancer, providing **AWS WAF (Web Application Firewall)** and SSL/TLS termination via AWS Certificate Manager (ACM).

---

## Step 8: Autoscaling Verification (HPA Stress Test)

To ensure the platform meets **Hyperscale Readiness** criteria, we validate the Horizontal Pod Autoscaler (HPA).

### 8.1 Setup & Run Load Generator

This creates internal ephemeral pods to flood LMS and CMS services.

```bash
kubectl run -i --tty load-generator --rm --image=busybox:1.28 --restart=Never -n openedx -- /bin/sh -c "while sleep 0.01; do wget -q -O- http://lms:8000; done"

```

### 8.2 Verify Scaling

Watch the HPA status in a separate terminal. Replicas will dynamically scale up as CPU usage exceeds the 50% target.

```bash
kubectl get hpa -n openedx -w

```

```
