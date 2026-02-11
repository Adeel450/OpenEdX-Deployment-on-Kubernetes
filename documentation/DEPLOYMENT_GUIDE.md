# OpenEdX Deployment Guide on AWS EKS

This guide provides a comprehensive, step-by-step walkthrough for deploying a production-ready OpenEdX platform on AWS Elastic Kubernetes Service (EKS).

The deployment architecture is designed for **High Availability (HA)**, **Security**, and **Scalability** using a custom VPC, private subnets for data/apps, and public subnets for load balancers.

---

## Architecture Overview

* **VPC CIDR:** `10.0.0.0/16`
* **Availability Zones:** 2 (`us-east-1a`, `us-east-1b`)
* **Subnet Strategy:**
    * **Public (Layer 1):** Load Balancers, NAT Gateways, Bastion Host.
    * **Private App (Layer 2):** EKS Worker Nodes (Application Logic).
    * **Private Data (Layer 3):** Databases (RDS, Mongo, Redis, Elastic) - **No Internet Access**.

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

Alternatively, provision the network using the provided Terraform script.

* **Source Code:** `terraform/vpc/vpc.tf`

**Deployment Command:**

```bash
cd terraform/vpc
terraform init
terraform apply -auto-approve
Step 2: External Database Layer Setup (RDS & Security)
To ensure data persistence and security, we deploy MySQL on AWS RDS inside isolated private subnets.

2.1 Create Database Security Group
Define firewall rules to allow traffic only from the Application Layer.

Name: openedx-data-sg

VPC: openedx-vpc

Inbound Rules: Allow 10.0.0.0/16 (VPC CIDR) on ports:

3306 (MySQL)

27017 (MongoDB)

6379 (Redis)

9200 (Elasticsearch)

2.2 Create DB Subnet Group
Go to RDS > Subnet groups > Create DB subnet group.

Name: openedx-db-subnet-group

Subnets: Select ONLY the two Private Data Subnets (10.0.5.0/24, 10.0.6.0/24).

2.3 Provision MySQL Database (AWS RDS)
Go to RDS > Create database > Standard create > MySQL.

Version: MySQL 8.0.x.

Settings:

Identifier: openedx-mysql

Master Username: admin (Save your password!)

Instance: db.t3.medium

Connectivity:

VPC: openedx-vpc

Subnet Group: openedx-db-subnet-group

Public Access: NO

Security Group: Select openedx-data-sg.

2.4 Option B: Setup via Terraform
Source Code: terraform/databases/mysql.tf

Deployment Command:

Bash
cd terraform/databases
terraform init
terraform apply -auto-approve
Step 3: Compute Layer Setup (Utility & Bastion)
We require two EC2 instances:

Utility Server (Private): Hosts NoSQL databases (Mongo, Redis, Elastic).

Bastion Host (Public): Jump Server for secure access.

3.1 Launch Utility Server (Private)
Name: openedx-data-utility

AMI: Ubuntu 22.04 LTS

Instance Type: t3.medium (4GB RAM is required for Elasticsearch).

Subnet: private-data-subnet-1 (Private).

Public IP: Disable.

Security Group: openedx-utility-sg (Allow traffic from 10.0.0.0/16).

3.2 Launch Bastion Host (Public)
Name: openedx-bastion

AMI: Ubuntu 22.04 LTS

Instance Type: t2.micro

Subnet: public-subnet-1 (Public).

Public IP: Enable.

Security Group: openedx-bastion-sg (Allow SSH from My IP).

3.3 Option B: Setup via Terraform
Source Code: terraform/databases/utility.tf

Deployment Command:

Bash
cd terraform/databases
terraform init
terraform apply -auto-approve
Step 4: NoSQL Database Setup (Docker)
We install MongoDB, Redis, and Elasticsearch on the private Utility Server.

4.1 Secure Access via SSH Agent Forwarding
Since the Utility server has no Public IP, connect via the Bastion.

1. Load your key (Local Machine):

Bash
ssh-add adeel-key.pem
2. Connect to Bastion:

Bash
ssh -A ubuntu@<BASTION-PUBLIC-IP>
3. Jump to Utility Server:

Bash
ssh ubuntu@10.0.5.90  # Replace with Utility Server Private IP
4.2 Install Docker Engine
Run on Utility Server (Ensure NAT Gateway is active):

Bash
sudo apt update
sudo apt install -y docker.io docker-compose-v2
sudo usermod -aG docker $USER
4.3 Configure System & Storage
Bash
# Create Persistent Directories
sudo mkdir -p /openedx/data/{mongo,redis,elasticsearch}
sudo chmod -R 777 /openedx/data

# Increase Memory Map Limit for Elasticsearch
sudo sysctl -w vm.max_map_count=262144
echo "vm.max_map_count=262144" | sudo tee -a /etc/sysctl.conf
4.4 Deploy Databases
Create a docker-compose.yml file using the content from scripts/docker-compose.yml in the repository.

Launch:

Bash
sudo docker compose up -d
sudo docker ps
Step 5: Kubernetes Cluster Setup (AWS EKS)
Deploy the EKS Control Plane and Worker Nodes.

5.1 Create EKS Cluster & Node Groups
Role: openedx-eks-cluster-role

VPC: openedx-vpc

Subnets: Select Public and Private App subnets.

Node Group: openedx-workers-ng (Instance: t3.large, Subnets: Private App).

5.2 Option B: Setup via Terraform
Source Code: terraform/eks/main.tf

Deployment Command:

Bash
cd terraform/eks
terraform init
terraform apply -auto-approve
Step 6: Deployment Station & Application Launch
Configure the Bastion Host to manage the cluster and launch OpenEdX using Tutor.

6.1 Install Tools on Bastion
Bash
# AWS CLI
curl "[https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip](https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip)" -o "awscliv2.zip"
unzip awscliv2.zip && sudo ./aws/install

# Kubectl
curl -LO "[https://dl.k8s.io/release/$(curl](https://dl.k8s.io/release/$(curl) -L -s [https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl](https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl)"
chmod +x kubectl && sudo mv kubectl /usr/local/bin/

# Tutor
sudo apt install -y python3-pip python3-venv
python3 -m venv venv
source venv/bin/activate
pip install "tutor[full]"
6.2 Configure Access
Bash
# Configure AWS Credentials
aws configure

# Connect to Cluster
aws eks update-kubeconfig --region us-east-1 --name openedx-cluster
6.3 Configure OpenEdX (Tutor)
Initialize Configuration:

Bash
tutor config save --interactive
External DB Configuration:

Edit config.yml to point to RDS and Utility Server IPs.

Bash
nano "$(tutor config printroot)/config.yml"
(Append the external database configuration block referencing your RDS Endpoint and Utility Server IP).

6.4 Launch Deployment
Bash
tutor config save
tutor k8s launch
Step 7: Post-Deployment Configuration (Monitoring & Ingress)
Once the core platform is running, we enable the monitoring stack and finalize the Ingress configuration to expose the platform via an AWS Application Load Balancer (ALB).

7.1 Enable Monitoring (Prometheus & Grafana)
We use the official Helm charts to deploy a lightweight monitoring stack specifically for the EKS cluster.

1. Add Helm Repositories:

Bash
helm repo add prometheus-community [https://prometheus-community.github.io/helm-charts](https://prometheus-community.github.io/helm-charts)
helm repo update
2. Install Prometheus & Grafana Stack:

Bash
helm install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set grafana.service.type=LoadBalancer
3. Verify Installation:

Bash
kubectl get pods -n monitoring
7.2 Finalize Ingress Controller (Public Access)
By default, the Nginx Ingress Controller might not assign an external address immediately. We patch the service to ensure it provisions a public Load Balancer.

1. Patch Ingress Service:

Bash
kubectl patch svc -n ingress-nginx ingress-nginx-controller \
  -p '{"spec": {"type": "LoadBalancer"}}'
2. Get Load Balancer URL:

Bash
kubectl get svc -n ingress-nginx ingress-nginx-controller
Copy the EXTERNAL-IP (e.g., a4d...us-east-1.elb.amazonaws.com). This is your LMS URL.

Step 8: Autoscaling Verification (HPA Stress Test)
To ensure the platform meets Hyperscale Readiness criteria, we validate the Horizontal Pod Autoscaler (HPA) using synthetic load.

8.1 Setup Load Generators
Ensure the load scripts are executable.

Bash
chmod +x scripts/*.sh
8.2 Run Load Test
Execute the unified load script. This creates internal ephemeral pods to flood LMS and CMS services.

Bash
./scripts/generate_load.sh
8.3 Verify Scaling
Watch the HPA status in a separate terminal. You should see replicas increase from 1 to 3 as CPU usage exceeds 50%.

Bash
kubectl get hpa -n openedx -w
8.4 Cleanup
Stop the load generators.

Bash
./scripts/stop_load.sh
