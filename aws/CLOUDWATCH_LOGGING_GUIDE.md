# 📊 Amazon CloudWatch Logs & Monitoring Guide

This guide explains how to stream application and web logs (`app_tier.log` and `web_tier.log`) directly to **AWS CloudWatch Logs** in production using the official **Amazon CloudWatch Agent**.

---

## 🏛️ Architecture Overview

```text
[ App Tier EC2 Instance ]                                 [ AWS CloudWatch Logs ]
   app_tier.log ──────> [ Amazon CloudWatch Agent ] ──────> Log Group: /aws/ec2/AvashyaApp/AppTier
                                                               log_stream: {instance_id}

[ Web Tier EC2 Instance ]                                 [ AWS CloudWatch Logs ]
   web_tier.log ──────> [ Amazon CloudWatch Agent ] ──────> Log Group: /aws/ec2/AvashyaApp/WebTier
                                                               log_stream: {instance_id}
```

---

## Step 1: Update EC2 IAM Role Permissions

Your EC2 IAM Role (`Avashya-EC2-App-Role`) needs permission to write log streams to CloudWatch.

Attach the AWS-managed policy **`CloudWatchAgentServerPolicy`** to your EC2 IAM Role:

1. Go to **AWS Console &rarr; IAM &rarr; Roles &rarr; Select `Avashya-EC2-App-Role`**.
2. Click **Add permissions &rarr; Attach policies**.
3. Search for **`CloudWatchAgentServerPolicy`** &rarr; Select it &rarr; Click **Add permissions**.

---

## Step 2: CloudWatch Agent Configuration (`amazon-cloudwatch-agent.json`)

Create the CloudWatch Agent configuration file on your EC2 instance at `/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json`:

```json
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
          },
          {
            "file_path": "/home/ec2-user/AvashyaApp-1/web_tier.log",
            "log_group_name": "/aws/ec2/AvashyaApp/WebTier",
            "log_stream_name": "{instance_id}",
            "timestamp_format": "%Y-%m-%d %H:%M:%S"
          }
        ]
      }
    }
  }
}
```

---

## Step 3: Add CloudWatch Agent to EC2 UserData / Launch Template

To make CloudWatch logging 100% automated for every new instance created by your Auto Scaling Group, add these lines to your **Launch Template UserData** script (`aws/userdata_app.sh`):

```bash
# 1. Install Amazon CloudWatch Agent
yum install -y amazon-cloudwatch-agent

# 2. Download/Write CloudWatch Agent Config
cat << 'EOF' > /opt/aws/amazon-cloudwatch-agent/bin/config.json
{
  "agent": { "run_as_user": "root" },
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/home/ec2-user/AvashyaApp-1/app_tier.log",
            "log_group_name": "/aws/ec2/AvashyaApp/AppTier",
            "log_stream_name": "{instance_id}"
          }
        ]
      }
    }
  }
}
EOF

# 3. Start CloudWatch Agent Service
/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
    -a fetch-config -m ec2 -s -c file:/opt/aws/amazon-cloudwatch-agent/bin/config.json
```

---

## 🔍 Step 4: Querying Logs in CloudWatch Insights

Once logs start streaming, you can inspect and search logs in real time across all Auto Scaling Group instances simultaneously:

1. Go to **AWS Console &rarr; CloudWatch &rarr; Logs &rarr; Logs Insights**.
2. Select Log Group **`/aws/ec2/AvashyaApp/AppTier`**.
3. Run this query to instantly find all errors or exceptions:

```sql
fields @timestamp, @message
| filter @message like /Error/ or @message like /Exception/ or @message like /500/
| sort @timestamp desc
| limit 100
```

---

## 🚨 Step 5: Setting Up CloudWatch Alarms & SNS Notifications

You can trigger automatic alerts when errors spike:

1. Go to **CloudWatch &rarr; Alarms &rarr; Create Alarm**.
2. Select Metric: **`/aws/ec2/AvashyaApp/AppTier` &rarr; ErrorCount**.
3. Set Condition: **Greater than 5 errors in 5 minutes**.
4. Action: Send notification to **Amazon SNS Topic `Avashya-Alerts`** (emails your engineering team!).
