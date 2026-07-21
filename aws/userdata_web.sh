#!/bin/bash
# ==============================================================================
# UserData Script for Web Tier Launch Template (avashya-web-lt)
# Runs automatically on EC2 instance boot in Auto Scaling Groups.
# Configures Nginx Reverse Proxy, CloudWatch Logs Agent & Web Tier.
# ==============================================================================

# 1. Update packages and install core dependencies & Nginx
yum update -y
yum install -y python3 git nginx amazon-cloudwatch-agent

# 2. Configure Amazon CloudWatch Logs Agent for Web Tier & Nginx
mkdir -p /opt/aws/amazon-cloudwatch-agent/etc/
cat << 'EOF' > /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json
{
  "agent": {
    "metrics_collection_interval": 60,
    "run_as_user": "root"
  },
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/home/ec2-user/AvashyaApp-1/web_tier.log",
            "log_group_name": "/aws/ec2/AvashyaApp/WebTier",
            "log_stream_name": "{instance_id}",
            "timestamp_format": "%Y-%m-%d %H:%M:%S"
          },
          {
            "file_path": "/var/log/nginx/access.log",
            "log_group_name": "/aws/ec2/AvashyaApp/NginxAccess",
            "log_stream_name": "{instance_id}"
          },
          {
            "file_path": "/var/log/nginx/error.log",
            "log_group_name": "/aws/ec2/AvashyaApp/NginxError",
            "log_stream_name": "{instance_id}"
          }
        ]
      }
    }
  }
}
EOF

# Start and enable Amazon CloudWatch Agent Service
/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
    -a fetch-config -m ec2 -s -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json

# 3. Clone/pull latest repository into /home/ec2-user
cd /home/ec2-user
if [ ! -d "AvashyaApp-1" ]; then
    git clone https://github.com/Nishadk7/AvashyaApp-1.git
fi
cd AvashyaApp-1
git pull origin main
chown -R ec2-user:ec2-user /home/ec2-user/AvashyaApp-1

# 4. Configure Same-Origin /api Relative Path in config.js
echo 'window.API_BASE = "/api";' > /home/ec2-user/AvashyaApp-1/frontend/config.js

# 5. Configure Nginx Reverse Proxy (/etc/nginx/conf.d/avashya_web.conf)
cat << 'EOF' > /etc/nginx/conf.d/avashya_web.conf
server {
    listen 80;
    server_name _;

    # Serve static Web Tier SPA frontend
    location / {
        root /home/ec2-user/AvashyaApp-1/frontend;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # Nginx Reverse Proxy for REST API (/api/*)
    location /api/ {
        # ==============================================================================
        # 🚀 PRODUCTION (INTERNAL ALB):
        # Uncomment line below & replace with your Internal ALB DNS name when created:
        # proxy_pass http://internal-app-alb-123456789.ap-south-1.elb.amazonaws.com:8000/api/;
        # ==============================================================================

        # 🧪 TESTING MODE (DIRECT APP EC2 / LOCAL):
        proxy_pass http://65.0.45.153:8000/api/;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Ensure permissions & enable/start Nginx
chmod 755 /home/ec2-user /home/ec2-user/AvashyaApp-1 /home/ec2-user/AvashyaApp-1/frontend
systemctl enable nginx
systemctl restart nginx

# 6. Fallback Python Web Server on Port 5000
su - ec2-user -c "cd /home/ec2-user/AvashyaApp-1 && nohup python3 -u frontend/server.py > web_tier.log 2>&1 &"
