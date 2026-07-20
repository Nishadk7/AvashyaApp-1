#!/bin/bash
# ==============================================================================
# AWS EC2 UserData / Provisioning Script: APPLICATION REST API TIER (EC2 Instance #2)
# OS: Amazon Linux 2023 / Ubuntu 22.04 / 24.04
# Port: 8000
# Target Services: Amazon RDS (PostgreSQL/MySQL) & Amazon S3 (boto3)
# ==============================================================================

# Update packages and install Python 3, Pip, PostgreSQL/MySQL dev tools, Git
yum update -y || apt-get update -y
yum install -y python3 python3-pip git gcc python3-devel postgresql-devel || apt-get install -y python3 python3-pip git python3-dev libpq-dev

# Set up app directory
mkdir -p /opt/avashya-drop
cd /opt/avashya-drop

# Clone or copy codebase
# git clone <YOUR_GIT_REPO_URL> .

# Create virtual environment and install dependencies
python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -r backend/requirements.txt

# Export AWS RDS and S3 Environment Variables
# REPLACE WITH YOUR ACTUAL AWS RDS ENDPOINT AND S3 BUCKET NAME:
export DATABASE_URL="${DATABASE_URL:-postgresql+psycopg2://admin:Password123!@your-rds-endpoint.us-east-1.rds.amazonaws.com:5432/postgres}"
export STORAGE_PROVIDER="s3"
export S3_BUCKET_NAME="${S3_BUCKET_NAME:-avashya-drop-uploads-2026}"
export AWS_REGION="${AWS_REGION:-us-east-1}"

# Run FastAPI REST API server on 0.0.0.0:8000
nohup .venv/bin/python backend/app.py > /var/log/app_tier.log 2>&1 &

echo "Application REST API Tier EC2 Setup Complete! Connected to RDS & S3 on Port 8000."
