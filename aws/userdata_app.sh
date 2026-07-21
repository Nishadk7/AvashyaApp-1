#!/bin/bash
# ==============================================================================
# UserData Script for App Tier Launch Template (avashya-app-lt)
# Runs automatically on EC2 instance boot in Auto Scaling Groups.
# Configures CloudWatch Logs Agent & starts FastAPI REST API.
# ==============================================================================

# 1. Update packages and install core dependencies
yum update -y
yum install -y python3 python3-pip git postgresql15 amazon-cloudwatch-agent

# 2. Configure Amazon CloudWatch Logs Agent for App Tier
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
            "file_path": "/home/ec2-user/AvashyaApp-1/app_tier.log",
            "log_group_name": "/aws/ec2/AvashyaApp/AppTier",
            "log_stream_name": "{instance_id}",
            "timestamp_format": "%Y-%m-%d %H:%M:%S"
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

# 4. Setup Virtual Environment & dependencies
su - ec2-user -c "cd /home/ec2-user/AvashyaApp-1 && python3 -m venv .venv && source .venv/bin/activate && pip install -r backend/requirements.txt"

# 5. Start App Tier REST API
su - ec2-user -c "cd /home/ec2-user/AvashyaApp-1 && ./aws/start_app_ec2.sh"
