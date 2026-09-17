# 🚀 SBM Hostels - Deployment Guide

Your SBM Hostels web portal is production-ready with all configuration files generated. Below are the two deployment options:

---

## 🌐 Option 1: 100% Free Cloud Deployment (24/7 Online on Render.com)

**Render.com** offers free hosting for Python Flask web applications with SSL (`https://`).

### Step-by-Step Instructions (Takes ~3 minutes):

1. **Upload your code to GitHub**:
   - Go to [github.com](https://github.com) and create a free account (if you don't have one).
   - Create a new repository named `sbm-hostels`.
   - Upload the files from `C:\Users\P Rahul\.gemini\antigravity\scratch\sbm_hostels` to your repository (or drag-and-drop all files via the GitHub web interface).

2. **Deploy on Render**:
   - Go to [render.com](https://render.com) and sign in with your GitHub account.
   - Click **New +** > **Web Service**.
   - Connect your `sbm-hostels` repository.
   - Render will automatically detect the pre-configured settings:
     - **Runtime**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt && python database.py`
     - **Start Command**: `gunicorn wsgi:app`
     - **Instance Type**: `Free`
   - Click **Create Web Service**.

3. **Your Live Website**:
   - Within 2 minutes, Render will provide a permanent live URL:
     **`https://sbm-hostels.onrender.com`**
   - You can access this URL from anywhere in the world on any phone, laptop, or tablet!

---

## 🐍 Option 2: Free Hosting on PythonAnywhere

1. Sign up at [pythonanywhere.com](https://www.pythonanywhere.com/) (Free Beginner account).
2. Go to the **Files** tab and upload the `sbm_hostels` project files.
3. Open a **Bash Console** and run:
   ```bash
   pip install -r requirements.txt
   python database.py
   ```
4. Go to the **Web** tab:
   - Click **Add a new web app**.
   - Select **Flask** > **Python 3.10** (or your preferred version).
   - Set the path to `wsgi.py`.
   - Click **Reload**.
5. Your app will be live at: `https://yourusername.pythonanywhere.com`

---

## 🏠 Option 3: Hostel Local Network Deployment (Instant Wi-Fi Access)

If you have a computer or laptop at the hostel reception/office, you can run the production server locally so all computers, phones, and tablets on the hostel Wi-Fi can access it without uploading anything to the internet.

1. Double-click **`run_production.bat`** in the project folder.
2. The server starts with **Waitress** (a multi-threaded production WSGI server).
3. **Devices on the same Wi-Fi network can visit**:
   - **`http://192.168.1.64:5000`** (Hostel Wi-Fi access)
   - **`http://127.0.0.1:5000`** (Host machine access)

---

## 📁 Pre-Configured Production Files Included:
- **`requirements.txt`**: Includes `Flask`, `Werkzeug`, `Jinja2`, `gunicorn`, `waitress`.
- **`Procfile`**: Defines the web worker process `web: gunicorn wsgi:app`.
- **`wsgi.py`**: Production WSGI entry point that auto-initializes database tables.
- **`render.yaml`**: Infrastructure-as-code blueprint for Render.
- **`vercel.json`**: Serverless configuration for Vercel.
- **`server_production.py`**: Production WSGI server using Waitress.
- **`run_production.bat`**: One-click launcher for the production server.
