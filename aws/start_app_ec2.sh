#!/bin/bash
# ==============================================================================
# Script: Start App Tier REST API (Post-EC2 Start)
# Usage: ./aws/start_app_ec2.sh
# Runs FastAPI backend using absolute paths and existing environment variables.
# ==============================================================================

# 1. Kill any existing backend process
pkill -9 -f "$HOME/AvashyaApp-1/backend/app.py" 2>/dev/null || pkill -9 -f "backend/app.py" 2>/dev/null

# 2. Refresh/truncate log file
> "$HOME/AvashyaApp-1/app_tier.log"

# 3. Launch FastAPI REST API server in background
nohup "$HOME/AvashyaApp-1/.venv/bin/python" "$HOME/AvashyaApp-1/backend/app.py" > "$HOME/AvashyaApp-1/app_tier.log" 2>&1 &

echo "============================================================"
echo "🚀 App Tier REST API Started on Port 8000!"
echo "👉 Logs: $HOME/AvashyaApp-1/app_tier.log"
echo "============================================================"
