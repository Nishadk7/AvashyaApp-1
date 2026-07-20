#!/bin/bash
# ==============================================================================
# Script: Stop Web Tier Frontend Server
# Usage: ./aws/stop_web_tier.sh
# ==============================================================================

# 1. Kill running web tier process without resetting ENV variables
pkill -9 -f "$HOME/AvashyaApp-1/frontend/server.py" 2>/dev/null || pkill -9 -f "frontend/server.py" 2>/dev/null

# 2. Refresh/truncate the log file
> "$HOME/AvashyaApp-1/web_tier.log"

echo "[Web Tier] Process stopped and web_tier.log refreshed."
