#!/bin/bash
# ==============================================================================
# AWS EC2 UserData / Provisioning Script: APPLICATION REST API TIER (EC2 Instance #2)
# OS: Amazon Linux 2023 / Ubuntu 22.04 / 24.04
# Port: 8000
# Target Services: Amazon RDS (PostgreSQL with IAM Auth) & Amazon S3 (boto3)
# ==============================================================================

yum update -y || apt-get update -y
yum install -y python3 python3-pip git gcc python3-devel postgresql-devel || apt-get install -y python3 python3-pip git python3-dev libpq-dev

mkdir -p /opt/avashya-drop
cd /opt/avashya-drop

# git clone <YOUR_GIT_REPO_URL> .

python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -r backend/requirements.txt

# Export AWS RDS IAM Database Auth Environment Variables
export RDSHOST="your-rds-endpoint.c123456789.ap-south-1.rds.amazonaws.com"
export DBUSER="nishad"
export DBNAME="postgres"
export DBPORT="5432"
export AWS_REGION="ap-south-1"

# Export Amazon S3 Environment Variables
export STORAGE_PROVIDER="s3"
export S3_BUCKET_NAME="avashya-drop-uploads-2026"

# Run FastAPI REST API server on 0.0.0.0:8000
nohup .venv/bin/python backend/app.py > /var/log/app_tier.log 2>&1 &

echo "Application REST API Tier EC2 Setup Complete! Connected to RDS IAM Auth & S3 on Port 8000."
