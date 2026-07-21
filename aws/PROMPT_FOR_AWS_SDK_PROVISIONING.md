# 🚀 Master Antigravity Prompt: Enterprise 3-Tier AWS CDK (Python) Infrastructure-as-Code

Copy and paste the prompt below into your target Antigravity AI session to automatically generate full, production-ready AWS CDK Python code with 100% automated connection wiring.

---

```markdown
<TASK_CONTEXT>
You are an expert AWS Cloud Infrastructure Architect. I need you to generate production-ready Infrastructure-as-Code in AWS CDK v2 (Python) to deploy a highly available, decoupled 3-Tier Web Application across 2 Availability Zones inside a custom Amazon VPC.
</TASK_CONTEXT>

<APPLICATION_ARCHITECTURE_SPEC>
The application consists of:
1. Web Tier: Static SPA frontend (HTML5/Bootstrap 5/JS) served on Port 5000 and reverse-proxied via Nginx on Port 80.
2. App Tier: FastAPI REST API server running on Port 8000 (connected to Amazon RDS & Amazon S3).
3. Data Tier: Amazon RDS PostgreSQL database (with IAM DB Authentication enabled).
4. Object Storage: Amazon S3 bucket (`s3://avashya-drop-uploads-2026`) with 100% private access and short-lived S3 Pre-Signed URLs.
</APPLICATION_ARCHITECTURE_SPEC>

<VPC_NETWORK_TOPOLOGY>
Construct a custom Amazon VPC with the following specifications:
- CIDR Block: `10.0.0.0/16` across 2 Availability Zones (`ap-south-1a`, `ap-south-1b`).
- 6 Subnets total (2 of each type):
  1. Public Subnets (`10.0.1.0/24`, `10.0.2.0/24`): Attached to Internet Gateway (IGW) and NAT Gateways. Holds External Internet-Facing ALB.
  2. Private App Subnets (`10.0.10.0/24`, `10.0.20.0/24`): Egress routed through NAT Gateways. Holds App Tier Auto Scaling Group (Instances receive ONLY private IPs).
  3. Isolated Database Subnets (`10.0.100.0/24`, `10.0.200.0/24`): Completely isolated from the internet. Holds Amazon RDS Multi-AZ PostgreSQL instance.
- VPC Endpoints: Attach a free Amazon S3 Gateway VPC Endpoint to Private App Subnets.
</VPC_NETWORK_TOPOLOGY>

<SECURITY_GROUPS_CHAINING>
Implement strict principle-of-least-privilege Security Group chaining:
1. `External-ALB-SG`: Inbound HTTP (80) & HTTPS (443) from `0.0.0.0/0`.
2. `Web-Tier-SG`: Inbound HTTP (80/5000) ONLY from `External-ALB-SG`.
3. `Internal-ALB-SG`: Inbound HTTP (8000) ONLY from `Web-Tier-SG`.
4. `App-Tier-SG`: Inbound TCP (8000) ONLY from `Internal-ALB-SG`.
5. `RDS-Database-SG`: Inbound PostgreSQL (5432) ONLY from `App-Tier-SG`.
</SECURITY_GROUPS_CHAINING>

<AUTOMATED_DYNAMIC_CONNECTION_WIRING>
Ensure ALL connections between components are 100% automated using CDK dynamic string references in UserData (ZERO manual edits):
1. Web Tier -> Internal ALB: Inject `internal_alb.load_balancer_dns_name` into Nginx UserData (`proxy_pass http://<internal_alb_dns>:8000/api/;`).
2. App Tier -> RDS Database: Inject `db_instance.db_instance_endpoint_address` into App UserData (`export RDSHOST="<db_endpoint>"`).
3. App Tier -> S3 Bucket: Inject `s3_bucket.bucket_name` into App UserData (`export S3_BUCKET_NAME="<bucket_name>"`).
4. Auto-Target Registration: Register `Web-Tier-ASG` to `External-ALB` target group and `App-Tier-ASG` to `Internal-ALB` target group automatically.
</AUTOMATED_DYNAMIC_CONNECTION_WIRING>

<COMPUTE_AND_AUTOSCALING>
1. Launch Templates:
   - `avashya-web-lt`: Amazon Linux 2023 (`t3.micro`), attached to `Web-Tier-SG`. UserData script installs Nginx, configures `/etc/nginx/conf.d/avashya_web.conf` with dynamic Internal ALB DNS reference, installs `amazon-cloudwatch-agent`, clones repo `https://github.com/Nishadk7/AvashyaApp-1.git`, and starts Nginx & web server.
   - `avashya-app-lt`: Amazon Linux 2023 (`t3.micro`), attached to `App-Tier-SG` and IAM Role `Avashya-EC2-App-Role`. UserData script installs dependencies (`postgresql15`, `boto3`, `fastapi`), installs `amazon-cloudwatch-agent`, exports RDS & S3 environment variables dynamically, and launches `start_app_ec2.sh`.
2. Auto Scaling Groups:
   - `Web-Tier-ASG`: Min 2, Desired 2, Max 4 in `Public Subnets`, registered to `External-ALB` Target Group.
   - `App-Tier-ASG`: Min 2, Desired 2, Max 6 in `Private App Subnets`, registered to `Internal-ALB` Target Group.
   - Target Tracking Policy: Scale out when average CPU > 70%.
</COMPUTE_AND_AUTOSCALING>

<IAM_SECURITY_AND_MONITORING>
1. EC2 IAM Role (`Avashya-EC2-App-Role`):
   - Attached policies: `CloudWatchAgentServerPolicy`, `AmazonS3FullAccess`.
   - Custom Inline Policy for RDS IAM Auth:
     `{"Effect": "Allow", "Action": ["rds-db:connect", "rds:*"], "Resource": "*"}`.
2. CloudWatch Log Groups:
   - Stream `app_tier.log` to `/aws/ec2/AvashyaApp/AppTier`.
   - Stream `/var/log/nginx/access.log` to `/aws/ec2/AvashyaApp/NginxAccess`.
</IAM_SECURITY_AND_MONITORING>

<OUTPUT_REQUIREMENTS>
Generate clean, modular, fully executable AWS CDK v2 Python code (`app.py`, `vpc_stack.py`, `app_stack.py`) with:
1. Complete VPC, Subnet, Route Table, and NAT Gateway definitions.
2. Security Groups with full ingress/egress rules chained logically.
3. Target Groups, Load Balancers, Launch Templates, and Auto Scaling Groups.
4. Step-by-step CLI deployment instructions (`cdk synth`, `cdk deploy --all`).
```
