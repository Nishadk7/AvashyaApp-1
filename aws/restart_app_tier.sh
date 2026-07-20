#!/bin/bash
# ==============================================================================
# Script: Restart App Tier FastAPI Backend
# Usage: ./aws/restart_app_tier.sh
# Uses absolute paths, inherits shell ENV variables, and refreshes app_tier.log
# ==============================================================================

# 1. Kill any existing backend process
pkill -9 -f "$HOME/AvashyaApp-1/backend/app.py" 2>/dev/null || pkill -9 -f "backend/app.py" 2>/dev/null

# 2. Refresh/truncate log file
> "$HOME/AvashyaApp-1/app_tier.log"

# 3. Launch new process in background using absolute paths
nohup "$HOME/AvashyaApp-1/.venv/bin/python" "$HOME/AvashyaApp-1/backend/app.py" > "$HOME/AvashyaApp-1/app_tier.log" 2>&1 &

echo "[App Tier] Backend restarted successfully on Port 8000."
echo "[App Tier] Log file refreshed at: $HOME/AvashyaApp-1/app_tier.log"
