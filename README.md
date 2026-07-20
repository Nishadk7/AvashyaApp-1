# Avashya Drop - Decoupled 2-Tier AWS Architecture Prototype

**Avashya Drop** is a decoupled web application designed to demonstrate enterprise AWS architectural patterns locally:
- **Presentation / Web Tier (`frontend/`)**: Mimics **Amazon S3 Static Website Hosting** (or local Nginx) running on **Port 5000**.
- **Application / REST API Tier (`backend/`)**: Runs a **FastAPI REST API** on **Port 8000** (mimicking EC2 Auto Scaling Group / ECS Containers in private subnets).
- **Data Tier (`backend/uploads/` & `app.db`)**: Isolated SQLite database (`app.db`) and local object storage directory.

---

## 🚀 How to Run in Two Separate Terminals

### Terminal 1: Launch Application REST API Tier (Port 8000)

Open your **first terminal** window and run:

```powershell
# Navigate to workspace directory
cd "c:\Users\nishad\Desktop\AvashyaApp#1"

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Start FastAPI REST API on Port 8000
python backend/app.py
```

*Terminal 1 output:*
```text
Starting Avashya Drop Backend REST API on Port 8000...
INFO: Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

---

### Terminal 2: Launch Web Tier (S3 Static Hosting / Nginx - Port 5000)

Open a **second terminal** window and run:

**Option A: Using Python Static Web Server (S3 Pattern)**
```powershell
cd "c:\Users\nishad\Desktop\AvashyaApp#1"
.\.venv\Scripts\Activate.ps1

python frontend/server.py
```

**Option B: Using Local Nginx (Optional)**
```bash
nginx -c "c:/Users/nishad/Desktop/AvashyaApp#1/frontend/nginx.conf"
```

*Terminal 2 output:*
```text
============================================================
🚀 Avashya Drop Web Tier (S3 / Nginx Pattern) Running!
👉 Local Web URL: http://127.0.0.1:5000
👉 Backend API  : http://127.0.0.1:8000
============================================================
```

---

## 🌐 Accessing the Application

Open your web browser and navigate to:
👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 🔑 Pre-Seeded Demo Accounts (1-Click Login)

The backend API automatically seeds 3 default demo accounts on startup:

| Username | Password | Email |
| :--- | :--- | :--- |
| `nishad` | `nishad` | `nishad@avashya.com` |
| `supreeth` | `supreeth` | `supreeth@avashya.com` |
| `varun` | `varun` | `varun@avashya.com` |

---

## 🗺️ AWS Architecture Mapping

| Component | Local Prototype | AWS Target Production Component |
| :--- | :--- | :--- |
| **Web Tier** | `frontend/` (Port 5000) | **Amazon S3 Static Website Hosting** (Public Bucket / Nginx) |
| **App Tier** | `backend/app.py` (Port 8000) | **AWS EC2 Auto Scaling Group** / **AWS ECS Fargate** (Private Subnets) |
| **Database** | `app.db` | **Amazon RDS PostgreSQL / MySQL** (Multi-AZ Data Subnets) |
| **Storage** | `backend/uploads/` | **Amazon S3 Bucket** (IAM Instance Profile Roles & Pre-Signed URLs) |
