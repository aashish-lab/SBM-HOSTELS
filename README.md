# SBM Hostels - Management Web Portal

A dedicated, full-stack hostel residency management system tailored for the owners and residents of **SBM Hostels**.

---

## 🌟 Key Features

### 1. 🛡️ Owner / Admin Control Panel
- **Exclusive Access**: Protected login accessible only to the hostel owner and administrators.
- **Master Resident Admission Roster**: Displays all 12 core resident parameters requested:
  1. **Admission ID** (e.g., `SBM-2026-101`)
  2. **Student Name** (e.g., `Aashis rudra`)
  3. **Joining Date** (e.g., `12-09-2026`)
  4. **Room / Bed** (e.g., `Room 203`)
  5. **Monthly Fee** (e.g., `₹6,000`)
  6. **Fee Due Date** (e.g., `10-10-2026`)
  7. **Amount Paid** (e.g., `₹6,000`)
  8. **Remaining Fee** (e.g., `₹0`, dynamically auto-calculated `Monthly Fee - Amount Paid`)
  9. **Student Phone** (e.g., `9876543210`)
  10. **Parent Phone** (e.g., `9765432109`)
  11. **Attendance** (e.g., `26/30 days` with percentage badge)
  12. **Food Required** (`Yes` / `No` mess subscription status)
  13. **Status** (`Active` / `Vacated`)
- **Key Operations**:
  - Add New Candidate with automatic sequential Admission ID suggestion (`SBM-YYYY-XXX`).
  - Update payments with one-click full clearance or partial installments.
  - Full candidate profile editor and removal tools.
  - Live search by Name, Admission ID, or Room.
  - Filter by Fee status (Fully Paid vs Due) and Food requirement (Yes vs No).
  - Print full resident roster or individual candidate fee receipts.

### 2. 🎓 Candidate / Student Portal
- **Secure Candidate Login**: Sign in using your unique Admission ID (`SBM-2026-101`) and password.
- **Digital Resident Card**: Displays room allocation, joining date, and status.
- **Fee Due Tracker**: Immediate visual notification of due dates and outstanding balance.
- **Attendance Monitor**: Monthly physical log progress bar (e.g. `26/30 Days`).
- **Food / Mess Timings**: Real-time indication of food subscription and meal times.
- **Printable Fee Receipt**: Download or print official fee invoice slips.

---

## 🚀 How to Run the Website

### Option 1: Double-Click Startup
Double-click `run.bat` in this folder.

### Option 2: Command Line
Open a terminal in `C:\Users\P Rahul\.gemini\antigravity\scratch\sbm_hostels` and run:
```bash
python app.py
```
Open your browser and navigate to:
**[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 🔑 Default Login Credentials

### Owner / Admin Login
- **URL**: `http://127.0.0.1:5000/admin/login`
- **Username**: `admin`
- **Password**: `sbmhostels123`

### Candidate Login (Preloaded Sample Resident)
- **URL**: `http://127.0.0.1:5000/student/login`
- **Admission ID**: `SBM-2026-101`
- **Password**: `student123`
*(Student Name: Aashis rudra | Room 203 | Monthly Fee ₹6,000 | Remaining ₹0)*

---

## 🧪 Automated Testing
Run the comprehensive test suite anytime:
```bash
python test_app.py
```
