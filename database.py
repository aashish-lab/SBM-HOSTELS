"""
database.py - Database setup and operations for SBM Hostels
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sbm_hostels.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # Admins table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            email TEXT
        )
    ''')
    
    # Students / Candidates table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admission_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            password TEXT NOT NULL DEFAULT 'student123',
            joining_date TEXT NOT NULL,
            room_bed TEXT NOT NULL,
            monthly_fee REAL NOT NULL DEFAULT 6000.0,
            fee_due_date TEXT NOT NULL,
            amount_paid REAL NOT NULL DEFAULT 0.0,
            remaining_fee REAL NOT NULL DEFAULT 6000.0,
            student_phone TEXT NOT NULL,
            parent_phone TEXT NOT NULL,
            attendance_attended INTEGER NOT NULL DEFAULT 26,
            attendance_total INTEGER NOT NULL DEFAULT 30,
            food_required TEXT NOT NULL DEFAULT 'Yes',
            status TEXT NOT NULL DEFAULT 'Active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Fee payments history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fee_payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            payment_date TEXT NOT NULL,
            payment_method TEXT DEFAULT 'UPI / Cash',
            remarks TEXT,
            FOREIGN KEY (student_id) REFERENCES students (id)
        )
    ''')
    
    # Seed default Admin if not exists
    cursor.execute('SELECT COUNT(*) FROM admins')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO admins (username, password, name, email)
            VALUES (?, ?, ?, ?)
        ''', ('admin', 'sbmhostels123', 'SBM Hostels Owner', 'owner@sbmhostels.com'))
        
    # Seed default Students if not exists
    cursor.execute('SELECT COUNT(*) FROM students')
    if cursor.fetchone()[0] == 0:
        sample_students = [
            (
                'SBM-2026-101',
                'Aashis rudra',
                'student123',
                '12-09-2026',
                'Room 203',
                6000.0,
                '10-10-2026',
                6000.0,
                0.0,
                '9876543210',
                '9765432109',
                26,
                30,
                'Yes',
                'Active'
            ),
            (
                'SBM-2026-102',
                'Rahul Sharma',
                'student123',
                '15-08-2026',
                'Room 105',
                6000.0,
                '05-10-2026',
                4000.0,
                2000.0,
                '9811223344',
                '9711223344',
                28,
                30,
                'Yes',
                'Active'
            ),
            (
                'SBM-2026-103',
                'Kiran Patel',
                'student123',
                '01-09-2026',
                'Room 301',
                5500.0,
                '01-10-2026',
                5500.0,
                0.0,
                '9844556677',
                '9744556677',
                24,
                30,
                'No',
                'Active'
            ),
            (
                'SBM-2026-104',
                'Vikram Verma',
                'student123',
                '10-07-2026',
                'Room 204',
                6000.0,
                '10-09-2026',
                0.0,
                6000.0,
                '9899001122',
                '9799001122',
                22,
                30,
                'Yes',
                'Active'
            )
        ]
        
        cursor.executemany('''
            INSERT INTO students (
                admission_id, name, password, joining_date, room_bed,
                monthly_fee, fee_due_date, amount_paid, remaining_fee,
                student_phone, parent_phone, attendance_attended, attendance_total,
                food_required, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_students)
        
    conn.commit()
    conn.close()

def get_next_admission_id():
    """Generates the next sequential admission ID like SBM-2026-105"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT admission_id FROM students ORDER BY id DESC LIMIT 1')
    row = cursor.fetchone()
    conn.close()
    
    current_year = datetime.now().year
    if row and row['admission_id']:
        try:
            parts = row['admission_id'].split('-')
            if len(parts) == 3 and parts[0] == 'SBM':
                num = int(parts[2]) + 1
                return f"SBM-{current_year}-{num}"
        except Exception:
            pass
    return f"SBM-{current_year}-101"

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully at:", DB_PATH)
