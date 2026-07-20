#!/bin/bash
# ==============================================================================
# Script: Restart App Tier FastAPI Backend
# Usage: ./aws/restart_app_tier.sh
# Explicitly exports RDS & S3 environment variables and restarts FastAPI.
# ==============================================================================

# 1. Export AWS RDS IAM Database Auth Environment Variables
export RDSHOST="avashya-db-instance-instance-1.czoekaswcg9j.ap-south-1.rds.amazonaws.com"
export DBUSER="nishad"
export DBNAME="postgres"
export DBPORT="5432"
export AWS_REGION="ap-south-1"

# 2. Export Amazon S3 Environment Variables
export STORAGE_PROVIDER="s3"
export S3_BUCKET_NAME="avashya-drop-uploads-2026"

# 3. Kill any process listening on Port 8000 or running backend/app.py
fuser -k 8000/tcp 2>/dev/null || true
pkill -9 -f "$HOME/AvashyaApp-1/backend/app.py" 2>/dev/null || true
pkill -9 -f "backend/app.py" 2>/dev/null || true

# 4. Refresh/truncate log file
> "$HOME/AvashyaApp-1/app_tier.log"

# 5. Launch new process in background using absolute paths
nohup "$HOME/AvashyaApp-1/.venv/bin/python" "$HOME/AvashyaApp-1/backend/app.py" > "$HOME/AvashyaApp-1/app_tier.log" 2>&1 &

echo "============================================================"
echo "[App Tier] Backend restarted on Port 8000!"
echo "👉 Connected Database: Amazon RDS ($RDSHOST)"
echo "👉 Connected Storage : Amazon S3 ($S3_BUCKET_NAME)"
echo "👉 Log file refreshed: $HOME/AvashyaApp-1/app_tier.log"
echo "============================================================"
