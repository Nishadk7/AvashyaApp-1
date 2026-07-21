#!/bin/bash
# ==============================================================================
# Script: Start App Tier REST API (Post-EC2 Start)
# Usage: ./aws/start_app_ec2.sh
# Explicitly exports RDS & S3 environment variables and launches FastAPI.
# ==============================================================================

# 1. Export AWS RDS IAM Database Auth Environment Variables
export RDSHOST="${RDSHOST:-${RDS_ENDPOINT}}"
export DBUSER="${DBUSER:-postgres}"
export DBNAME="${DBNAME:-avashyadadb}"
export DBPORT="${DBPORT:-5432}"
export AWS_REGION="${AWS_REGION:-ap-south-1}"

# 2. Export Amazon S3 Environment Variables
export STORAGE_PROVIDER="s3"
export S3_BUCKET_NAME="${S3_BUCKET_NAME:-avashya-drop-uploads-2026}"

# 3. Kill any process listening on Port 8000 or running backend/app.py
fuser -k 8000/tcp 2>/dev/null || true
pkill -9 -f "$HOME/AvashyaApp-1/backend/app.py" 2>/dev/null || true
pkill -9 -f "backend/app.py" 2>/dev/null || true

# 4. Refresh/truncate log file
> "$HOME/AvashyaApp-1/app_tier.log"

# 5. Launch FastAPI REST API server in background
nohup "$HOME/AvashyaApp-1/.venv/bin/python" "$HOME/AvashyaApp-1/backend/app.py" > "$HOME/AvashyaApp-1/app_tier.log" 2>&1 &

echo "============================================================"
echo "🚀 App Tier REST API Started on Port 8000!"
echo "👉 Connected Database: Amazon RDS ($RDSHOST)"
echo "👉 Connected Storage : Amazon S3 ($S3_BUCKET_NAME)"
echo "👉 Logs              : $HOME/AvashyaApp-1/app_tier.log"
echo "============================================================"
