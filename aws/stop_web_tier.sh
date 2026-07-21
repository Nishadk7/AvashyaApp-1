#!/bin/bash
# ==============================================================================
# Script: Stop Web Tier Frontend Server
# Usage: ./aws/stop_web_tier.sh
# ==============================================================================

# 1. Kill running web tier process or process listening on Port 5000
fuser -k 5000/tcp 2>/dev/null || true
pkill -9 -f "$HOME/AvashyaApp-1/frontend/server.py" 2>/dev/null || true
pkill -9 -f "frontend/server.py" 2>/dev/null || true

# 2. Refresh/truncate the log file
> "$HOME/AvashyaApp-1/web_tier.log"

echo "[Web Tier] Process stopped and web_tier.log refreshed."
