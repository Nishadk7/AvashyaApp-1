# AWS EC2 2-Instance Deployment Guide (Default VPC)

This guide walks you through deploying **Avashya Drop** onto **2 separate AWS EC2 instances** in your AWS account's **Default VPC** without complex Auto Scaling Groups, custom VPC setups, or Load Balancers.

---

## 📐 Architecture Overview

```text
[ User Laptop Browser ]
        │
        ├─── HTTP Port 5000 ───> [ EC2 Instance #1: Web Tier ] (Default VPC)
        │                          Serves static HTML/JS (frontend/)
        │
        └─── HTTP Port 8000 ───> [ EC2 Instance #2: App Tier ] (Default VPC)
                                   Runs FastAPI REST API + SQLite + Uploads
```

---

## Step 1: Create Security Groups in Default VPC

Go to **AWS Console &rarr; EC2 &rarr; Security Groups &rarr; Create Security Group**.

### 🛡️ Security Group 1: `avashya-web-sg` (For Web Tier EC2 #1)
* **VPC**: Default VPC
* **Inbound Rules**:
  - `Custom TCP` | Port `5000` | Source `0.0.0.0/0` (Allows web traffic from browser)
  - `SSH` | Port `22` | Source `My IP` (For SSH management)

### 🛡️ Security Group 2: `avashya-app-sg` (For App Tier EC2 #2)
* **VPC**: Default VPC
* **Inbound Rules**:
  - `Custom TCP` | Port `8000` | Source `0.0.0.0/0` (Allows REST API requests from web browser/frontend)
  - `SSH` | Port `22` | Source `My IP` (For SSH management)

---

## Step 2: Launch EC2 Instance #2 (App Tier REST API)

Launch the **Backend API EC2 Instance** first so we get its Public IP.

1. Go to **AWS Console &rarr; EC2 &rarr; Launch Instance**.
2. **Name**: `Avashya-App-Tier-EC2`
3. **AMI**: Amazon Linux 2023 AMI (or Ubuntu 24.04 LTS).
4. **Instance Type**: `t2.micro` or `t3.micro` (Free Tier eligible).
5. **Key Pair**: Select your EC2 Key Pair.
6. **Network Settings**:
   - **VPC**: Default VPC
   - **Auto-assign Public IP**: Enable
   - **Security Group**: Select `avashya-app-sg`
7. Click **Launch Instance**.
8. Note the **Public IPv4 Address** of this instance (e.g. `54.210.12.34`).

### Configure App Tier EC2 Instance #2
SSH into Instance #2:
```bash
ssh -i your-key.pem ec2-user@<APP_EC2_PUBLIC_IP>
```

Run setup commands:
```bash
# Update OS & Install Python 3 + Git
sudo yum update -y
sudo yum install -y python3 python3-pip git

# Upload your project folder or git clone:
git clone <YOUR_PROJECT_REPO> avashya-drop
cd avashya-drop

# Create Virtual Environment & Install Dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt

# Launch Backend REST API in Background on Port 8000 (listening on 0.0.0.0)
nohup python3 backend/app.py > app.log 2>&1 &
```

Verify backend is running:
```bash
curl http://127.0.0.1:8000/api/users
```
*(Should return JSON `[{"username":"nishad",...}]`)*

---

## Step 3: Launch EC2 Instance #1 (Web Tier Frontend)

1. Go to **AWS Console &rarr; EC2 &rarr; Launch Instance**.
2. **Name**: `Avashya-Web-Tier-EC2`
3. **AMI**: Amazon Linux 2023 AMI (or Ubuntu 24.04 LTS).
4. **Instance Type**: `t2.micro` or `t3.micro`.
5. **Key Pair**: Select your EC2 Key Pair.
6. **Network Settings**:
   - **VPC**: Default VPC
   - **Auto-assign Public IP**: Enable
   - **Security Group**: Select `avashya-web-sg`
7. Click **Launch Instance**.
8. Note the **Public IPv4 Address** of Web Instance #1 (e.g. `34.201.88.99`).

### Configure Web Tier EC2 Instance #1
SSH into Instance #1:
```bash
ssh -i your-key.pem ec2-user@<WEB_EC2_PUBLIC_IP>
```

Run setup commands:
```bash
sudo yum update -y
sudo yum install -y python3 git

git clone <YOUR_PROJECT_REPO> avashya-drop
cd avashya-drop

# Update frontend/config.js to point to App EC2 Instance #2's Public IP
cat <<EOF > frontend/config.js
window.API_BASE = "http://<APP_EC2_PUBLIC_IP>:8000/api";
console.log('[Avashya Drop Web Tier] Connected API Endpoint:', window.API_BASE);
EOF

# Launch Web Tier static server in background on Port 5000
nohup python3 frontend/server.py > web.log 2>&1 &
```

---

## Step 4: Test the Live 2-Tier Application!

1. Open your browser and navigate to:
   👉 **`http://<WEB_EC2_PUBLIC_IP>:5000`**

2. You will see the **Avashya Drop** single-page web dashboard served from **EC2 Instance #1**!
3. Click any of the 1-click demo user buttons (`nishad`, `supreeth`, `varun`). The Web Tier on EC2 #1 will communicate with the REST API on **EC2 Instance #2** (`http://<APP_EC2_PUBLIC_IP>:8000/api/auth/login`).
4. Upload files, add custom AWS Metadata Tags, and search across items!

---

## 🎯 Talking Points for Your Senior Mentors Presentation

- **Default VPC Simplicity**: *"We validated our 2-tier decoupled architecture locally and in AWS by deploying independent Web and Application EC2 instances inside the Default VPC."*
- **Network Security Groups**: *"The Web Tier EC2 instance accepts public HTTP traffic on Port 5000. The App Tier EC2 instance accepts API calls on Port 8000 and connects to isolated SQLite/S3 storage."*
- **Path to Production**: *"This 2-EC2 setup proves that our Web Tier is completely decoupled from our REST API. Moving to production requires wrapping the Web Tier in an S3 bucket / CloudFront CDN and placing the App Tier EC2 instances into an Auto Scaling Group behind an Application Load Balancer."*
