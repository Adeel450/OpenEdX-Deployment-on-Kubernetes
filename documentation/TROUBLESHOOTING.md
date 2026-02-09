🔧 OpenEdX Infrastructure Troubleshooting Log
This document serves as a technical knowledge base, documenting specific issues encountered during the deployment of OpenEdX on AWS EKS and their verified resolutions.

1. Application Deployment & Tutor Issues
Issue 1.1: LMS & CMS Connection Refused (CrashLoopBackOff)
Symptom: During tutor k8s launch, the lms and cms pods failed to start. Logs showed: MySQLdb.OperationalError: (2003, "Can't connect to MySQL server on 'rds-endpoint' (110)"). Root Cause:

Security Groups: The RDS Security Group (openedx-data-sg) did not allow inbound traffic on port 3306 from the Private App Subnets (where EKS nodes reside).

Missing Migrations: The database tables were not created because the initial connection failed. Solution:

Security Group Update: Modified openedx-data-sg to allow Inbound TCP 3306 from 10.0.3.0/24 and 10.0.4.0/24.

Manual Migration: Ran the migration commands manually to initialize the DB:


tutor k8s run lms ./manage.py lms migrate
tutor k8s run cms ./manage.py cms migrate
Issue 1.2: Redundant Reverse Proxy Conflict (Caddy vs. AWS ALB)
Symptom: Tutor attempted to deploy Caddy as a reverse proxy/web server, which conflicted with our architecture utilizing AWS Application Load Balancer (ALB) and Nginx Ingress Controller. This caused "Plugin Errors" and routing confusion. Root Cause: Default Tutor configuration assumes it handles SSL/Termination via Caddy, whereas we offloaded this to AWS ALB. Solution:

Manifest Customization: Manually removed the kind: Deployment block for caddy from k8s-manifest/tutor-manifest/deployments.yml.

Config Map Adjustment: Retained the mfe-caddy-config in kustomization.yaml as it is required internally for Micro-Frontends (MFE) routing, even if the main Caddy server is removed.

Issue 1.3: MongoDB Authorization Failure during Migration
Symptom: During launch or migration jobs, the process failed with a traceback pointing to pymongo. Logs: pymongo.errors.OperationFailure: command find requires authentication, full error: {'ok': 0.0, 'errmsg': 'command find requires authentication', 'code': 13, 'codeName': 'Unauthorized'} Root Cause: The External MongoDB container on the Utility Server was started with the --auth flag (enforcing security), but the OpenEdX configuration (config.yml) was missing the MONGODB_USERNAME and MONGODB_PASSWORD parameters. Solution:

Edit Configuration: Added the missing credentials to config.yml:

YAML
MONGODB_USERNAME: "admin"
MONGODB_PASSWORD: "YourPassword"
Apply Changes: Regenerated configuration and re-ran migration:


tutor config save
tutor k8s run lms ./manage.py lms migrate
2. Infrastructure & Compute Layer Issues
Issue 2.1: Elasticsearch Container Immediate Exit (Exit Code 78/137)
Symptom: On the Utility Server, the Elasticsearch container would start and immediately crash. Root Cause:

Insufficient RAM: The instance type t3.micro (1GB RAM) triggered an OOM (Out of Memory) kill.

Kernel Limit: The host's virtual memory map count was too low. Solution:

Vertical Scaling: Upgraded the Utility Server to t3.medium (4GB RAM).

Kernel Tuning: Applied the following command on the host:


sudo sysctl -w vm.max_map_count=262144
# Persisted in /etc/sysctl.conf
Issue 2.2: "Temporary Failure resolving 'archive.ubuntu.com'"
Symptom: sudo apt update or docker install failed on the Private Utility Server. Root Cause: The server was deployed in the Private Data Subnet which, by our design, has no internet access (not connected to NAT Gateway) for maximum security. Solution:

Temporary Route: Edited the openedx-private-data-rt route table to route 0.0.0.0/0 -> NAT Gateway.

Install: Performed necessary installations.

Revert: Removed the route immediately to restore isolation.

3. Kubernetes (EKS) & Permissions
Issue 3.1: "Cluster role missing" during EKS Creation
Symptom: AWS Console blocked EKS Cluster creation with permission errors. Root Cause: We initially attempted to enable "EKS Auto Mode". This feature requires specific, pre-configured IAM roles that were not part of our custom Terraform/IAM setup. Solution: Disabled "EKS Auto Mode" and manually selected our custom openedx-eks-cluster-role.

Issue 3.2: Worker Nodes Not Joining the Cluster
Symptom: The Control Plane was active, but kubectl get nodes returned No resources found. Root Cause: The Worker Node Group was misconfigured to launch in Public Subnets. EKS worker nodes must be in private subnets to communicate securely with the Control Plane endpoint. Solution: Recreated the Node Group and strictly selected Private App Subnets (10.0.3.0/24, 10.0.4.0/24) in the networking configuration.

Issue 3.3: "localhost:8080 was refused" (Kubectl)
Symptom: Running sudo kubectl get pods failed. Root Cause: Using sudo switches context to the Root user, which does not have the ~/.kube/config file configured. Solution: Ran all kubectl and helm commands as the standard ubuntu user (without sudo).

4. Access & Networking
Issue 4.1: SSH Timeout to Private Utility Server
Symptom: Attempting ssh ubuntu@10.0.5.90 timed out. Root Cause: Direct SSH to private IPs is impossible from the internet. Solution: Utilized SSH Agent Forwarding via the Bastion Host:

ssh-add adeel-key.pem (Local)

ssh -A ubuntu@<BASTION-IP> (Connect to Bastion)

ssh ubuntu@10.0.5.90 (Jump to Utility)
