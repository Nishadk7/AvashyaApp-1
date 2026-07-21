# 📐 Avashya Drop - Technical Architecture Summary & VPC/ASG Roadmap

This document provides a detailed technical summary of the decoupled 2-tier architecture built for **Avashya Drop**, along with the production blueprint for deploying into a **Custom Private VPC** with **Auto Scaling Groups (ASG)**.

---

## 🏛️ PART 1: Technical Summary of Current Build

```text
[ Client Web Browser ]
         │
         ├─── HTTP Port 5000 ───> [ Web Tier EC2 #1 ] (Presentation Layer)
         │                           Frontend SPA (HTML5/CSS3/Vanilla JS)
         │                           Configured via frontend/config.js
         │
         └─── HTTP Port 8000 ───> [ App Tier REST API EC2 #2 ] (Application Layer)
                                     FastAPI REST API + SQLAlchemy ORM
                                     │
                    ┌────────────────┴────────────────┐
                    ▼                                 ▼
      [ Amazon RDS PostgreSQL ]          [ Amazon S3 Bucket ]
      IAM DB Auth via boto3              boto3 Object Uploads &
      psycopg2 Creator Pattern           Zero-Trust Pre-Signed URLs
```

### 1. Presentation / Web Tier (`frontend/`)
- **Technology**: Pure HTML5, CSS3 (Bootstrap 5 dark theme), Vanilla JavaScript.
- **Hosting**: Lightweight Python static web server on Port 5000 (`frontend/server.py` with `socketserver.TCPServer.allow_reuse_address = True`).
- **Decoupled API Binding**: Uses `frontend/config.js` (`window.API_BASE = "http://<APP_HOST>:8000/api"` or `"/api"`).
- **Features**:
  - 1-click quick developer logins (`nishad`, `supreeth`, `varun`).
  - Interactive AWS Key-Value Metadata Tag builder.
  - Multi-attribute filtering (uploader, file type, upload date, keyword search).
  - Drag-and-drop upload modal.

### 2. Application REST API Tier (`backend/`)
- **Technology**: FastAPI (running on Port 8000 via Uvicorn).
- **Security & Identity**: JWT Token Authentication (`HS256`, 24-hour expiration) with Password Hashing via `passlib[bcrypt]`.
- **CORS Configuration**: Enabled cross-origin requests (`allow_origins=["*"]`) to accept requests from Web Tier on Port 5000 or ALB.
- **REST Endpoints**:
  - `POST /api/auth/register` & `POST /api/auth/login`
  - `GET /api/auth/me` (Token verification)
  - `GET /api/users` & `GET /api/items` (Filtered item query with tag joins)
  - `POST /api/items/upload` (Form array parsing & streaming S3 upload)
  - `DELETE /api/items/{id}` (Database row & S3 object deletion)

### 3. Data Tier (Amazon RDS PostgreSQL)
- **Database Engine**: Amazon RDS PostgreSQL instance (`avashya-db-instance-instance-1...`).
- **Connection Driver**: [`backend/database.py`](file:///c:/Users/nishad/Desktop/AvashyaApp%231/backend/database.py) using SQLAlchemy ORM + `psycopg2` + `boto3`.
- **Authentication**: **AWS IAM Database Authentication** (`boto3.client('rds').generate_db_auth_token(...)` dynamically supplied via a `psycopg2` engine creator callback).
- **Schema Management**: Automatic table creation (`users`, `items`, `item_tags`) on engine startup using `Base.metadata.create_all(bind=engine)`.

### 4. Object Storage Tier (Amazon S3)
- **Service Class**: `S3StorageService` in [`backend/storage.py`](file:///c:/Users/nishad/Desktop/AvashyaApp%231/backend/storage.py) using `boto3`.
- **Storage Bucket**: `s3://avashya-drop-uploads-2026/uploads/<uuid>.<ext>`.
- **Zero-Trust Security**: Bucket public access is **100% blocked**. Downloads generate short-lived, encrypted **Amazon S3 Pre-Signed URLs** (`s3_client.generate_presigned_url('get_object', ...)`).

### 5. IAM Security & Deployment Shell Automation (`aws/`)
- **IAM Role**: Attached `Avashya-EC2-App-Role` with `rds-db:connect`, `s3:*`, and `rds:*` permissions.
- **Management Scripts**:
  - `aws/start_app_ec2.sh` & `aws/restart_app_tier.sh`: Launches FastAPI backend on Port 8000 with unbuffered live logging (`python -u`).
  - `aws/start_web_ec2.sh` & `aws/restart_web_tier.sh`: Interactively prompts for App EC2 Public IP, updates `config.js`, and launches Web server on Port 5000.
  - `aws/clear_items.py`: Wipes database items for clean demo resets.

---

## 🌐 PART 2: Roadmap Blueprint for Custom Private VPC & Auto Scaling Groups (ASG)

To transition this architecture into a production-grade enterprise deployment inside a **Custom Private VPC**:

```text
==================================== CUSTOM VPC (10.0.0.0/16) ====================================
                                              │
                                              ▼
                    ┌───────────────────────────────────────────────────┐
                    │      Public Subnets (10.0.1.0/24, 10.0.2.0/24)   │
                    │   - Internet Gateway (IGW)                        │
                    │   - Application Load Balancer (ALB - Port 80/443) │
                    │   - NAT Gateways (AZ-a, AZ-b)                     │
                    └─────────────────────────┬─────────────────────────┘
                                              │
                    ┌─────────────────────────┴─────────────────────────┐
                    │  Path Routing: /api/*                             │
                    ▼                                                   ▼
┌──────────────────────────────────────────────┐    ┌──────────────────────────────────────────────┐
│  Private App Subnets (10.0.10.0/24, .20.0/24)│    │  Private Web Subnets (Or S3 Static Hosting)  │
│  - App Tier Auto Scaling Group (ASG)         │    │  - Web Tier Auto Scaling Group (ASG)         │
│  - EC2 Instances (Private IPs Only)          │    │  - EC2 Instances (Port 5000)                 │
└──────────────────────┬───────────────────────┘    └──────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│  Isolated Data Subnets (10.0.100.0/24, .200) │
│  - Amazon RDS PostgreSQL Multi-AZ            │
│  - Amazon S3 Gateway Endpoint (Free)         │
└──────────────────────────────────────────────┘
==================================================================================================
```

### 1. Custom VPC Subnet Layout
- **CIDR Block**: `10.0.0.0/16` across 2 Availability Zones (`ap-south-1a`, `ap-south-1b`).
- **Subnet Segmentation**:
  - `Public Subnet 1` (`10.0.1.0/24`) & `Public Subnet 2` (`10.0.2.0/24`): Holds ALB and NAT Gateways.
  - `Private App Subnet 1` (`10.0.10.0/24`) & `Private App Subnet 2` (`10.0.20.0/24`): Holds App Tier EC2 Auto Scaling Group.
  - `Isolated Data Subnet 1` (`10.0.100.0/24`) & `Isolated Data Subnet 2` (`10.0.200.0/24`): Holds Amazon RDS PostgreSQL Multi-AZ instance.

### 2. Application Load Balancer (ALB) Setup
- **Public Entry Point**: Listens on HTTP Port 80 (or HTTPS 443).
- **Target Groups**:
  - `avashya-app-tg`: Target type `Instance`, Port 8000, Health check `/api/users`.
  - `avashya-web-tg`: Target type `Instance`, Port 5000, Health check `/index.html`.
- **Listener Rules**:
  - **IF** `Path is /api/*` &rarr; Forward to `avashya-app-tg`.
  - **DEFAULT** `Path is /*` &rarr; Forward to `avashya-web-tg`.

### 3. Launch Templates (LT) Specs
- **App Tier Launch Template (`avashya-app-lt`)**:
  - AMI: Amazon Linux 2023.
  - Instance Type: `t3.micro`.
  - IAM Role: `Avashya-EC2-App-Role` (with `rds-db:connect` and `s3:*`).
  - Security Group: Inbound TCP Port 8000 from ALB Security Group only.
  - UserData: Pinned execution of `aws/setup_app_ec2.sh`.
- **Web Tier Launch Template (`avashya-web-lt`)**:
  - Security Group: Inbound TCP Port 5000 from ALB Security Group only.
  - UserData: Pinned execution of `aws/setup_web_ec2.sh` (with `window.API_BASE = "/api"`).

### 4. Auto Scaling Group (ASG) Policies
- **App Tier ASG**:
  - Min Size: `2`, Desired Capacity: `2`, Max Size: `6`.
  - Subnets: `Private App Subnet 1` & `Private App Subnet 2`.
  - Scaling Policy: Target Tracking Scaling Policy (Maintain Average CPU Utilization at 70%).
- **Web Tier ASG**:
  - Min Size: `2`, Desired Capacity: `2`, Max Size: `4`.
  - Scaling Policy: Target Tracking Scaling Policy (Maintain Average Request Count per Target).

### 5. Network Egress & VPC Endpoints
- **NAT Gateway**: Placed in Public Subnets to allow App EC2 instances in Private Subnets to make outbound IAM DB Auth requests to AWS STS / RDS.
- **Amazon S3 VPC Gateway Endpoint**: Free VPC endpoint attached to Private App Subnets for direct, high-bandwidth S3 transfers without traversing NAT Gateways.

---

## 🌟 Presentation Talking Points for Senior Mentors

> 1. **Zero-Trust Decoupled Tiers**: *"Our Web Presentation Tier is completely decoupled from our Application REST API Tier. The frontend operates with relative `/api` paths, making it ready for static S3/CloudFront hosting or ALB routing without code changes."*
> 2. **IAM Database Authentication & Pre-Signed S3 URLs**: *"We eliminate hardcoded credentials in the data layer. Database connections use short-lived IAM Auth tokens generated dynamically via `boto3`, and S3 object downloads use zero-trust Pre-Signed URLs with 1-hour expiration."*
> 3. **Stateless Auto Scaling Readiness**: *"Our App Tier EC2 instances store zero session state or uploads locally. All session tokens are JWT-encoded and all storage streams to S3/RDS, enabling our Auto Scaling Groups to scale up or replace instances seamlessly across Availability Zones."*
