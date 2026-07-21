#!/bin/bash
# ==============================================================================
# Script: Restart Web Tier Frontend Server
# Usage: ./aws/restart_web_tier.sh
# Uses absolute paths, inherits shell ENV variables, and refreshes web_tier.log
# ==============================================================================

# 1. Kill any existing web tier process or process listening on Port 5000
fuser -k 5000/tcp 2>/dev/null || true
pkill -9 -f "$HOME/AvashyaApp-1/frontend/server.py" 2>/dev/null || true
pkill -9 -f "frontend/server.py" 2>/dev/null || true

# 2. Refresh/truncate log file
> "$HOME/AvashyaApp-1/web_tier.log"

# 3. Launch new process in background using absolute paths
nohup python3 "$HOME/AvashyaApp-1/frontend/server.py" > "$HOME/AvashyaApp-1/web_tier.log" 2>&1 &

echo "[Web Tier] Server restarted successfully on Port 5000."
echo "[Web Tier] Log file refreshed at: $HOME/AvashyaApp-1/web_tier.log"
