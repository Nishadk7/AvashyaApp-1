# 🚀 AWS Launch Templates, Nginx Reverse Proxy & CloudWatch Setup Guide

This guide explains how to create and test your **AWS Launch Templates** (`avashya-app-lt` and `avashya-web-lt`) with built-in **Nginx Reverse Proxy** and **Amazon CloudWatch Agent** log streaming.

---

## 📂 Updated UserData Scripts in Repository (`aws/`):

1. **[`aws/userdata_web.sh`](file:///c:/Users/nishad/Desktop/AvashyaApp%231/aws/userdata_web.sh)**:
   - Installs **Nginx** and configures an Nginx Reverse Proxy (`/etc/nginx/conf.d/avashya_web.conf`).
   - Routes static SPA files from `/frontend` on HTTP Port 80.
   - Proxies `/api/` traffic with zero CORS preflight delays.
   - Contains a clearly commented section for swapping from **Testing Mode** to **Production Internal ALB Mode**.
   - Configures CloudWatch log streaming for `web_tier.log`, `/var/log/nginx/access.log`, and `/var/log/nginx/error.log`.

2. **[`aws/userdata_app.sh`](file:///c:/Users/nishad/Desktop/AvashyaApp%231/aws/userdata_app.sh)**:
   - Installs `amazon-cloudwatch-agent`.
   - Configures real-time streaming of `app_tier.log` to CloudWatch Log Group **`/aws/ec2/AvashyaApp/AppTier`**.
   - Exports RDS IAM Auth & S3 environment variables and launches FastAPI REST API.

---

## ⚙️ Nginx Reverse Proxy Configuration Breakdown

Inside `/etc/nginx/conf.d/avashya_web.conf`:

```nginx
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
        # 🚀 PRODUCTION MODE (INTERNAL ALB):
        # Uncomment line below & replace with your Internal ALB DNS name when created:
        # proxy_pass http://internal-app-alb-123456789.ap-south-1.elb.amazonaws.com:8000/api/;
        # ==============================================================================

        # 🧪 TESTING MODE (DIRECT APP EC2 / LOCAL):
        proxy_pass http://127.0.0.1:8000/api/;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 📋 Step-by-Step Launch Template Creation (AWS Console)

### 1. Create Web Tier Launch Template (`avashya-web-lt`)
1. Go to **AWS Console &rarr; EC2 &rarr; Launch Templates &rarr; Create launch template**.
2. **Name**: `avashya-web-lt` | **Version**: `v1`
3. **AMI**: Amazon Linux 2023 AMI.
4. **Instance Type**: `t2.micro` (or `t3.micro`).
5. **Security Group**: Select `avashya-web-sg` (Ensure HTTP Port 80 is open).
6. **User data**: Copy and paste the full contents of [`aws/userdata_web.sh`](file:///c:/Users/nishad/Desktop/AvashyaApp%231/aws/userdata_web.sh).
7. Click **Create launch template**.

### 2. Create App Tier Launch Template (`avashya-app-lt`)
1. Go to **AWS Console &rarr; EC2 &rarr; Launch Templates &rarr; Create launch template**.
2. **Name**: `avashya-app-lt` | **Version**: `v1`
3. **AMI**: Amazon Linux 2023 AMI.
4. **Instance Type**: `t2.micro` (or `t3.micro`).
5. **Security Group**: Select `avashya-app-sg` (Ensure Port 8000 is open).
6. **IAM Instance Profile**: Select `Avashya-EC2-App-Role`.
7. **User data**: Copy and paste the full contents of [`aws/userdata_app.sh`](file:///c:/Users/nishad/Desktop/AvashyaApp%231/aws/userdata_app.sh).
8. Click **Create launch template**.

---

## 🧪 Testing Your Templates Now & Updating Later

1. **Testing Right Now**:
   - Launch an instance from `avashya-web-lt`. Nginx will start automatically on HTTP Port 80, serving your frontend and logging access/errors to CloudWatch!
2. **Updating for Production Later**:
   - When you create your Internal Private ALB later, simply edit `/etc/nginx/conf.d/avashya_web.conf` (or update `userdata_web.sh`), uncomment the production `proxy_pass http://internal-app-alb...`, and run `sudo systemctl reload nginx`!
