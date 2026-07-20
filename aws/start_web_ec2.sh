#!/bin/bash
# ==============================================================================
# Script: Start Web Tier Frontend Server (Post-EC2 Start)
# Usage: ./aws/start_web_ec2.sh
# Prompts for App EC2 Public IP, updates config.js, and starts Web server.
# ==============================================================================

# Prompt user for App EC2 Instance #2 Public IP
read -p "Enter App EC2 Instance Public IP address: " APP_IP

if [ -z "$APP_IP" ]; then
    echo "❌ Error: App EC2 Public IP cannot be empty!"
    exit 1
fi

# Update frontend/config.js with the new App EC2 Public IP
echo "window.API_BASE = \"http://${APP_IP}:8000/api\";" > "$HOME/AvashyaApp-1/frontend/config.js"

# Kill any existing web tier process
pkill -9 -f "$HOME/AvashyaApp-1/frontend/server.py" 2>/dev/null || pkill -9 -f "frontend/server.py" 2>/dev/null

# Refresh/truncate log file
> "$HOME/AvashyaApp-1/web_tier.log"

# Launch static web server in background
nohup python3 "$HOME/AvashyaApp-1/frontend/server.py" > "$HOME/AvashyaApp-1/web_tier.log" 2>&1 &

echo "============================================================"
echo "🚀 Web Tier Server Started on Port 5000!"
echo "👉 Connected REST API: http://${APP_IP}:8000/api"
echo "👉 Logs: $HOME/AvashyaApp-1/web_tier.log"
echo "============================================================"
