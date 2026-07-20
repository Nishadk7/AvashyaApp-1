#!/bin/bash
# ==============================================================================
# AWS EC2 UserData / Provisioning Script: WEB TIER (EC2 Instance #1)
# OS: Amazon Linux 2023 / Ubuntu 22.04 / 24.04
# Port: 5000 (or 80)
# ==============================================================================

sudo yum update -y
sudo yum install -y python3 python3-pip git 

# Clone repository directly into user working directory
git clone https://github.com/Nishadk7/AvashyaApp-1.git
cd AvashyaApp-1

# Configure frontend API endpoint (Replace YOUR_APP_EC2_PUBLIC_IP with App EC2 Instance #2 Public IP)
echo 'window.API_BASE = "http://YOUR_APP_EC2_PUBLIC_IP:8000/api";' > frontend/config.js

# Run static web server in background
nohup python3 frontend/server.py > web_tier.log 2>&1 &

echo "Web Tier EC2 Setup Complete! Listening on Port 5000."
