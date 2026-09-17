"""
app.py - Main Flask Application for SBM Hostels Portal
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import os
from functools import wraps
from datetime import datetime
import database

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'sbm-hostel-secure-secret-key-2026')

# Helper Decorators for Access Control
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Please log in as an administrator/owner to access this area.', 'warning')
            return redirect(url_for('login_admin'))
        return f(*args, **kwargs)
    return decorated_function

def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'student':
            flash('Please log in with your Admission ID to view your student portal.', 'warning')
            return redirect(url_for('login_student'))
        return f(*args, **kwargs)
    return decorated_function

# Context processor for current year/date
@app.context_processor
def inject_global_vars():
    return {
        'current_year': datetime.now().year,
        'current_date': datetime.now().strftime('%d-%m-%Y')
    }

# ----------------- PUBLIC ROUTES ----------------- #

@app.route('/')
def index():
    return render_template('index.html')

# ----------------- ADMIN AUTH & PORTAL ----------------- #

@app.route('/admin/login', methods=['GET', 'POST'])
def login_admin():
    if session.get('role') == 'admin':
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        conn = database.get_db()
        admin = conn.execute(
            'SELECT * FROM admins WHERE username = ? AND password = ?',
            (username, password)
        ).fetchone()
        conn.close()

        if admin:
            session.clear()
            session['role'] = 'admin'
            session['admin_id'] = admin['id']
            session['name'] = admin['name']
            session['username'] = admin['username']
            flash(f"Welcome back, {admin['name']}!", 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin username or password. Please try again.', 'error')

    return render_template('login_admin.html')

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    flash('You have been logged out from the Owner Portal.', 'info')
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    conn = database.get_db()
    students = conn.execute('SELECT * FROM students ORDER BY id ASC').fetchall()
    conn.close()

    # Calculate aggregate summary stats
    total_students = len(students)
    active_students = sum(1 for s in students if s['status'] == 'Active')
    total_fee = sum(s['monthly_fee'] for s in students)
    total_paid = sum(s['amount_paid'] for s in students)
    total_remaining = sum(s['remaining_fee'] for s in students)
    food_count = sum(1 for s in students if s['food_required'] == 'Yes')
    occupied_rooms = len(set(s['room_bed'] for s in students if s['status'] == 'Active'))

    stats = {
        'total_students': total_students,
        'active_students': active_students,
        'total_fee': total_fee,
        'total_paid': total_paid,
        'total_remaining': total_remaining,
        'food_count': food_count,
        'room_occupancy': occupied_rooms
    }

    next_id = database.get_next_admission_id()

    return render_template(
        'admin_dashboard.html',
        students=students,
        stats=stats,
        next_admission_id=next_id
    )

@app.route('/admin/add_student', methods=['POST'])
@admin_required
def add_student():
    admission_id = request.form.get('admission_id', '').strip().upper()
    name = request.form.get('name', '').strip()
    password = request.form.get('password', 'student123').strip()
    joining_date = request.form.get('joining_date', '').strip()
    room_bed = request.form.get('room_bed', '').strip()
    
    try:
        monthly_fee = float(request.form.get('monthly_fee', 6000.0))
    except ValueError:
        monthly_fee = 6000.0

    fee_due_date = request.form.get('fee_due_date', '').strip()

    try:
        amount_paid = float(request.form.get('amount_paid', 0.0))
    except ValueError:
        amount_paid = 0.0

    remaining_fee = max(0.0, monthly_fee - amount_paid)
    student_phone = request.form.get('student_phone', '').strip()
    parent_phone = request.form.get('parent_phone', '').strip()

    try:
        attendance_attended = int(request.form.get('attendance_attended', 26))
        attendance_total = int(request.form.get('attendance_total', 30))
    except ValueError:
        attendance_attended, attendance_total = 26, 30

    food_required = request.form.get('food_required', 'Yes')
    status = request.form.get('status', 'Active')

    conn = database.get_db()
    try:
        conn.execute('''
            INSERT INTO students (
                admission_id, name, password, joining_date, room_bed,
                monthly_fee, fee_due_date, amount_paid, remaining_fee,
                student_phone, parent_phone, attendance_attended, attendance_total,
                food_required, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            admission_id, name, password, joining_date, room_bed,
            monthly_fee, fee_due_date, amount_paid, remaining_fee,
            student_phone, parent_phone, attendance_attended, attendance_total,
            food_required, status
        ))
        conn.commit()
        flash(f'Candidate {name} ({admission_id}) enrolled successfully!', 'success')
    except sqlite3.IntegrityError:
        flash(f'Error: Admission ID "{admission_id}" already exists. Please choose a unique ID.', 'error')
    except Exception as e:
        flash(f'Error enrolling candidate: {str(e)}', 'error')
    finally:
        conn.close()

    return redirect(url_for('admin_dashboard'))

@app.route('/admin/edit_student/<int:student_id>', methods=['GET', 'POST'])
@admin_required
def edit_student(student_id):
    conn = database.get_db()
    student = conn.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()

    if not student:
        conn.close()
        flash('Candidate not found.', 'error')
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        admission_id = request.form.get('admission_id', '').strip().upper()
        name = request.form.get('name', '').strip()
        password = request.form.get('password', '').strip()
        joining_date = request.form.get('joining_date', '').strip()
        room_bed = request.form.get('room_bed', '').strip()

        try:
            monthly_fee = float(request.form.get('monthly_fee', 6000.0))
        except ValueError:
            monthly_fee = 6000.0

        fee_due_date = request.form.get('fee_due_date', '').strip()

        try:
            amount_paid = float(request.form.get('amount_paid', 0.0))
        except ValueError:
            amount_paid = 0.0

        remaining_fee = max(0.0, monthly_fee - amount_paid)
        student_phone = request.form.get('student_phone', '').strip()
        parent_phone = request.form.get('parent_phone', '').strip()

        try:
            attendance_attended = int(request.form.get('attendance_attended', 26))
            attendance_total = int(request.form.get('attendance_total', 30))
        except ValueError:
            attendance_attended, attendance_total = 26, 30

        food_required = request.form.get('food_required', 'Yes')
        status = request.form.get('status', 'Active')

        try:
            conn.execute('''
                UPDATE students SET
                    admission_id = ?, name = ?, password = ?, joining_date = ?, room_bed = ?,
                    monthly_fee = ?, fee_due_date = ?, amount_paid = ?, remaining_fee = ?,
                    student_phone = ?, parent_phone = ?, attendance_attended = ?, attendance_total = ?,
                    food_required = ?, status = ?
                WHERE id = ?
            ''', (
                admission_id, name, password, joining_date, room_bed,
                monthly_fee, fee_due_date, amount_paid, remaining_fee,
                student_phone, parent_phone, attendance_attended, attendance_total,
                food_required, status, student_id
            ))
            conn.commit()
            flash(f'Record for {name} ({admission_id}) updated successfully!', 'success')
            conn.close()
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            flash(f'Error updating record: {str(e)}', 'error')

    conn.close()
    return render_template('edit_student.html', student=student)

@app.route('/admin/delete_student/<int:student_id>')
@admin_required
def delete_student(student_id):
    conn = database.get_db()
    student = conn.execute('SELECT name, admission_id FROM students WHERE id = ?', (student_id,)).fetchone()
    if student:
        conn.execute('DELETE FROM students WHERE id = ?', (student_id,))
        conn.commit()
        flash(f'Candidate {student["name"]} ({student["admission_id"]}) has been removed.', 'info')
    conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/payment/<int:student_id>', methods=['POST'])
@admin_required
def update_payment(student_id):
    conn = database.get_db()
    student = conn.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()
    
    if student:
        try:
            new_amount_paid = float(request.form.get('amount_paid', 0.0))
            monthly_fee = student['monthly_fee']
            new_remaining = max(0.0, monthly_fee - new_amount_paid)

            conn.execute('''
                UPDATE students 
                SET amount_paid = ?, remaining_fee = ?
                WHERE id = ?
            ''', (new_amount_paid, new_remaining, student_id))
            conn.commit()
            flash(f'Payment updated for {student["name"]}. Paid: ₹{new_amount_paid:,.0f}, Due: ₹{new_remaining:,.0f}', 'success')
        except Exception as e:
            flash(f'Payment update error: {str(e)}', 'error')

    conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/inline_edit/<int:student_id>', methods=['POST'])
@admin_required
def inline_edit_student(student_id):
    """Allows instant in-portal editing of all 12 candidate parameters directly from the dashboard"""
    data = request.get_json(silent=True) or request.form
    conn = database.get_db()
    existing = conn.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()
    
    if not existing:
        conn.close()
        return jsonify({'success': False, 'message': 'Candidate record not found.'}), 404

    try:
        admission_id = data.get('admission_id', existing['admission_id']).strip().upper()
        name = data.get('name', existing['name']).strip()
        joining_date = data.get('joining_date', existing['joining_date']).strip()
        room_bed = data.get('room_bed', existing['room_bed']).strip()
        monthly_fee = float(data.get('monthly_fee', existing['monthly_fee']))
        fee_due_date = data.get('fee_due_date', existing['fee_due_date']).strip()
        amount_paid = float(data.get('amount_paid', existing['amount_paid']))
        remaining_fee = max(0.0, monthly_fee - amount_paid)
        student_phone = data.get('student_phone', existing['student_phone']).strip()
        parent_phone = data.get('parent_phone', existing['parent_phone']).strip()
        attendance_attended = int(data.get('attendance_attended', existing['attendance_attended']))
        attendance_total = int(data.get('attendance_total', existing['attendance_total']))
        food_required = data.get('food_required', existing['food_required']).strip()
        status = data.get('status', existing['status']).strip()

        conn.execute('''
            UPDATE students SET
                admission_id = ?, name = ?, joining_date = ?, room_bed = ?,
                monthly_fee = ?, fee_due_date = ?, amount_paid = ?, remaining_fee = ?,
                student_phone = ?, parent_phone = ?, attendance_attended = ?, attendance_total = ?,
                food_required = ?, status = ?
            WHERE id = ?
        ''', (
            admission_id, name, joining_date, room_bed,
            monthly_fee, fee_due_date, amount_paid, remaining_fee,
            student_phone, parent_phone, attendance_attended, attendance_total,
            food_required, status, student_id
        ))
        conn.commit()

        # Recalculate summary metrics across all students
        all_students = conn.execute('SELECT * FROM students').fetchall()
        total_students = len(all_students)
        active_students = sum(1 for s in all_students if s['status'] == 'Active')
        total_fee = sum(s['monthly_fee'] for s in all_students)
        total_paid = sum(s['amount_paid'] for s in all_students)
        total_remaining = sum(s['remaining_fee'] for s in all_students)
        food_count = sum(1 for s in all_students if s['food_required'] == 'Yes')
        occupied_rooms = len(set(s['room_bed'] for s in all_students if s['status'] == 'Active'))

        updated_student = conn.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()
        conn.close()

        return jsonify({
            'success': True,
            'message': f'Record for {name} ({admission_id}) updated successfully!',
            'student': dict(updated_student),
            'stats': {
                'total_students': total_students,
                'active_students': active_students,
                'total_fee': total_fee,
                'total_paid': total_paid,
                'total_remaining': total_remaining,
                'food_count': food_count,
                'room_occupancy': occupied_rooms
            }
        })
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'message': f'Update error: {str(e)}'}), 500

# ----------------- CANDIDATE / STUDENT AUTH & PORTAL ----------------- #

@app.route('/student/login', methods=['GET', 'POST'])
def login_student():
    if session.get('role') == 'student':
        return redirect(url_for('student_dashboard'))

    if request.method == 'POST':
        admission_id = request.form.get('admission_id', '').strip().upper()
        password = request.form.get('password', '').strip()

        conn = database.get_db()
        student = conn.execute(
            'SELECT * FROM students WHERE UPPER(admission_id) = ? AND password = ?',
            (admission_id, password)
        ).fetchone()
        conn.close()

        if student:
            session.clear()
            session['role'] = 'student'
            session['student_id'] = student['id']
            session['admission_id'] = student['admission_id']
            session['name'] = student['name']
            flash(f"Welcome, {student['name']}!", 'success')
            return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid Admission ID or Password. Please check your credentials.', 'error')

    return render_template('login_student.html')

@app.route('/student/logout')
def student_logout():
    session.clear()
    flash('You have logged out from your resident portal.', 'info')
    return redirect(url_for('index'))

@app.route('/student/dashboard')
@student_required
def student_dashboard():
    student_id = session.get('student_id')
    conn = database.get_db()
    student = conn.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()
    conn.close()

    if not student:
        flash('Candidate profile not found.', 'error')
        return redirect(url_for('student_logout'))

    return render_template('student_dashboard.html', student=student)

@app.route('/receipt/<int:student_id>')
def student_receipt(student_id):
    # Allow access if user is admin or the logged-in student themselves
    if session.get('role') != 'admin' and session.get('student_id') != student_id:
        flash('Unauthorized access to receipt.', 'error')
        return redirect(url_for('index'))

    conn = database.get_db()
    student = conn.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()
    conn.close()

    if not student:
        flash('Receipt record not found.', 'error')
        return redirect(url_for('index'))

    return render_template('receipt.html', student=student)

# ----------------- RUN SERVER ----------------- #

if __name__ == '__main__':
    database.init_db()
    print("SBM Hostels portal starting on http://127.0.0.1:5000 ...")
    app.run(host='0.0.0.0', port=5000, debug=True)
