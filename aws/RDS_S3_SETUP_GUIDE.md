# Amazon RDS & Amazon S3 Setup & Testing Guide

This guide walks you through connecting your **Avashya Drop** Application REST API Tier to a live **Amazon RDS Database Instance** and **Amazon S3 Storage Bucket** in AWS using `boto3` and **S3 Pre-Signed URLs** for zero-trust security.

---

## 🗄️ Part 1: Setting Up Amazon RDS (PostgreSQL or MySQL)

### Step 1: Create Amazon RDS Database Instance
1. Go to **AWS Console &rarr; RDS &rarr; Create Database**.
2. **Database Engine**: Choose **PostgreSQL** (or **MySQL**).
3. **Template**: Choose **Free Tier** (or Dev/Test).
4. **Settings**:
   - **DB Instance Identifier**: `avashya-db-instance`
   - **Master Username**: `admin`
   - **Master Password**: `Password123!` (or your preferred password).
5. **Connectivity**:
   - **VPC**: Select your **Default VPC**.
   - **Public Access**: Select **Yes** (if testing from local machine) or **No** (if testing strictly inside EC2).
   - **Existing VPC Security Groups**: Select a security group that allows inbound traffic on Port `5432` (PostgreSQL) or Port `3306` (MySQL).
6. Click **Create Database**.
7. Once created, copy the **Endpoint** string (e.g. `avashya-db-instance.c123456789.us-east-1.rds.amazonaws.com`).

### Step 2: Construct Database Connection String
- **PostgreSQL Connection String**:
  `postgresql+psycopg2://admin:Password123!@avashya-db-instance.c123456789.us-east-1.rds.amazonaws.com:5432/postgres`
- **MySQL Connection String**:
  `mysql+pymysql://admin:Password123!@avashya-db-instance.c123456789.us-east-1.rds.amazonaws.com:3306/postgres`

---

## 🪣 Part 2: Setting Up Amazon S3 Bucket

### Step 1: Create S3 Bucket
1. Go to **AWS Console &rarr; S3 &rarr; Create Bucket**.
2. **Bucket Name**: Enter a globally unique bucket name (e.g., `avashya-drop-uploads-2026`).
3. **AWS Region**: Select your AWS Region (e.g. `us-east-1`).
4. **Block Public Access**: Keep **Block ALL Public Access ENABLED**.
   *(Zero-Trust Architecture: Files do NOT need public access because our backend generates secure, short-lived **S3 Pre-Signed URLs** for downloads!)*
5. Click **Create Bucket**.

### Step 2: Attach IAM Role to EC2 Instance #2 (App Tier)
To allow EC2 Instance #2 to write/read S3 objects without hardcoding secret keys:
1. Go to **AWS Console &rarr; IAM &rarr; Roles &rarr; Create Role**.
2. **Trusted Entity**: Select **AWS Service** &rarr; **EC2**.
3. **Permissions**: Attach `AmazonS3FullAccess` (or custom policy for `s3:PutObject`, `s3:GetObject`, `s3:DeleteObject`).
4. **Role Name**: `Avashya-EC2-S3-Role` and click **Create Role**.
5. Go to **EC2 Console &rarr; Instances &rarr; Select `Avashya-App-Tier-EC2` &rarr; Actions &rarr; Security &rarr; Modify IAM Role**.
6. Attach `Avashya-EC2-S3-Role`.

---

## 🚀 Part 3: Running Backend with RDS & S3 Enabled

### Launching on EC2 Instance #2 (App Tier)
Export the environment variables before running `backend/app.py`:

```bash
cd /opt/avashya-drop
source .venv/bin/activate

# 1. Set Amazon RDS Connection String
export DATABASE_URL="postgresql+psycopg2://admin:Password123!@avashya-db-instance.c123456789.us-east-1.rds.amazonaws.com:5432/postgres"

# 2. Set Amazon S3 Storage Configuration
export STORAGE_PROVIDER="s3"
export S3_BUCKET_NAME="avashya-drop-uploads-2026"
export AWS_REGION="us-east-1"

# 3. Run FastAPI Backend API
python backend/app.py
```

---

## 🧪 Verification & Testing

1. **Verify RDS Tables**:
   On startup, FastAPI automatically runs `Base.metadata.create_all(bind=engine)`, creating the `users`, `items`, and `item_tags` tables inside Amazon RDS PostgreSQL/MySQL.

2. **Verify S3 Uploads**:
   Upload a file via the web dashboard (`http://<WEB_EC2_PUBLIC_IP>:5000`).
   Check your Amazon S3 Console: You will see the uploaded file saved in `s3://avashya-drop-uploads-2026/uploads/<uuid>.<ext>`.

3. **Verify S3 Pre-Signed URLs**:
   Click **"Access File"** on any dropped item. The URL generated will be a secure S3 Pre-Signed URL like:
   `https://avashya-drop-uploads-2026.s3.us-east-1.amazonaws.com/uploads/abcd.pdf?AWSAccessKeyId=...&Signature=...&Expires=...`
