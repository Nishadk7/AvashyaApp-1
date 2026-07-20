#!/bin/bash
# ==============================================================================
# AWS EC2 UserData / Provisioning Script: WEB TIER (EC2 Instance #1)
# OS: Amazon Linux 2023 / Ubuntu 22.04 / 24.04
# Port: 5000 (or 80)
# ==============================================================================

# Update packages and install Python 3 & Git
yum update -y || apt-get update -y
yum install -y python3 python3-pip git || apt-get install -y python3 python3-pip git

# Clone or set up workspace directory
mkdir -p /opt/avashya-drop
cd /opt/avashya-drop

# If pulling from GitHub / Git repo:
# git clone <YOUR_GIT_REPO_URL> .

# Configure Environment Variables
# REPLACE <APP_EC2_PUBLIC_IP> with EC2 Instance #2's Public IP or Public DNS
APP_EC2_IP="${APP_EC2_PUBLIC_IP:-127.0.0.1}"

cat <<EOF > frontend/config.js
// Avashya Drop Web Tier Config (AWS EC2 Instance #1)
window.API_BASE = "http://${APP_EC2_IP}:8000/api";
console.log('[Avashya Drop Web Tier] Connected API Endpoint:', window.API_BASE);
EOF

# Run static web server in background
nohup python3 frontend/server.py > /var/log/web_tier.log 2>&1 &

echo "Web Tier EC2 Setup Complete! Listening on Port 5000."
