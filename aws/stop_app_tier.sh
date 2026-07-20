#!/bin/bash
# ==============================================================================
# Script: Stop App Tier FastAPI Backend
# Usage: ./aws/stop_app_tier.sh
# ==============================================================================

# 1. Kill running backend process without resetting ENV variables
pkill -9 -f "$HOME/AvashyaApp-1/backend/app.py" 2>/dev/null || pkill -9 -f "backend/app.py" 2>/dev/null

# 2. Refresh/truncate the log file
> "$HOME/AvashyaApp-1/app_tier.log"

echo "[App Tier] Process stopped and app_tier.log refreshed."
