"""
test_app.py - Automated verification tests for SBM Hostels portal
"""

import unittest
from app import app
import database

class SBMHostelTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret'
        self.client = app.test_client()
        database.init_db()

    def test_database_aashis_rudra_record(self):
        """Verify the user's specific sample candidate record in the database"""
        conn = database.get_db()
        student = conn.execute("SELECT * FROM students WHERE admission_id = 'SBM-2026-101'").fetchone()
        conn.close()

        self.assertIsNotNone(student, "Aashis rudra record must exist")
        self.assertEqual(student['admission_id'], 'SBM-2026-101')
        self.assertEqual(student['name'], 'Aashis rudra')
        self.assertEqual(student['joining_date'], '12-09-2026')
        self.assertEqual(student['room_bed'], 'Room 203')
        self.assertEqual(student['monthly_fee'], 6000.0)
        self.assertEqual(student['fee_due_date'], '10-10-2026')
        self.assertEqual(student['amount_paid'], 6000.0)
        self.assertEqual(student['remaining_fee'], 0.0)
        self.assertEqual(student['attendance_attended'], 26)
        self.assertEqual(student['attendance_total'], 30)
        self.assertEqual(student['food_required'], 'Yes')
        self.assertEqual(student['status'], 'Active')
        print("[PASS] Aashis rudra record verified with all 12 exact fields!")

    def test_index_page(self):
        """Verify landing page loads with links to Admin and Candidate portals"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'SBM HOSTELS', response.data)
        self.assertIn(b'Owner / Admin Portal', response.data)
        self.assertIn(b'Candidate / Student Portal', response.data)
        print("[PASS] Landing page loads properly")

    def test_admin_login_and_dashboard(self):
        """Verify admin login and dashboard rendering with 12 columns"""
        # Login with admin
        response = self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'sbmhostels123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Owner Control Panel', response.data)
        self.assertIn(b'SBM-2026-101', response.data)
        self.assertIn(b'Aashis rudra', response.data)
        self.assertIn(b'Room 203', response.data)
        self.assertIn(b'12-09-2026', response.data)
        self.assertIn(b'10-10-2026', response.data)
        self.assertIn(b'26/30 days', response.data)
        print("[PASS] Admin authentication and table rendering verified")

    def test_student_login_and_dashboard(self):
        """Verify student login using Admission ID and access to student dashboard"""
        response = self.client.post('/student/login', data={
            'admission_id': 'SBM-2026-101',
            'password': 'student123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Aashis rudra', response.data)
        self.assertIn(b'SBM-2026-101', response.data)
        self.assertIn(b'Room 203', response.data)
        self.assertIn(b'/ 30 Days', response.data)
        self.assertIn(b'Food & Mess Subscription', response.data)
        print("[PASS] Candidate login and profile dashboard verified")

    def test_payment_update(self):
        """Verify fee payment updates remaining fee dynamically"""
        # Log in as admin
        self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'sbmhostels123'
        })

        # Find Rahul Sharma (SBM-2026-102) who has remaining 2000
        conn = database.get_db()
        rahul = conn.execute("SELECT id, monthly_fee FROM students WHERE admission_id = 'SBM-2026-102'").fetchone()
        conn.close()

        # Update Rahul to fully paid (6000)
        response = self.client.post(f'/admin/payment/{rahul["id"]}', data={
            'amount_paid': '6000'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        conn = database.get_db()
        updated = conn.execute("SELECT amount_paid, remaining_fee FROM students WHERE id = ?", (rahul['id'],)).fetchone()
        conn.close()

        self.assertEqual(updated['amount_paid'], 6000.0)
        self.assertEqual(updated['remaining_fee'], 0.0)
        print("[PASS] Fee payment update calculation verified")

    def test_printable_receipt(self):
        """Verify receipt generation works for candidate"""
        # Login as student
        self.client.post('/student/login', data={
            'admission_id': 'SBM-2026-101',
            'password': 'student123'
        })
        conn = database.get_db()
        student = conn.execute("SELECT id FROM students WHERE admission_id = 'SBM-2026-101'").fetchone()
        conn.close()

        response = self.client.get(f'/receipt/{student["id"]}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Resident Receipt', response.data)
        self.assertIn(b'Aashis rudra', response.data)
        print("[PASS] Printable fee receipt verified")

    def test_in_portal_inline_edit(self):
        """Verify in-portal inline editing for all 12 candidate fields"""
        # Login as admin
        self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'sbmhostels123'
        })
        conn = database.get_db()
        student = conn.execute("SELECT id FROM students WHERE admission_id = 'SBM-2026-101'").fetchone()
        conn.close()

        # Update candidate inline with all 12 parameters
        edit_payload = {
            'admission_id': 'SBM-2026-101',
            'name': 'Aashis rudra (Verified)',
            'joining_date': '12-09-2026',
            'room_bed': 'Room 203 - Premium',
            'monthly_fee': 6500.0,
            'fee_due_date': '15-10-2026',
            'amount_paid': 6500.0,
            'student_phone': '9899887766',
            'parent_phone': '9799887766',
            'attendance_attended': 28,
            'attendance_total': 30,
            'food_required': 'Yes',
            'status': 'Active'
        }

        response = self.client.post(
            f'/admin/inline_edit/{student["id"]}',
            json=edit_payload
        )
        self.assertEqual(response.status_code, 200)
        res_data = response.get_json()
        self.assertTrue(res_data['success'])
        self.assertEqual(res_data['student']['name'], 'Aashis rudra (Verified)')
        self.assertEqual(res_data['student']['room_bed'], 'Room 203 - Premium')
        self.assertEqual(res_data['student']['monthly_fee'], 6500.0)
        self.assertEqual(res_data['student']['remaining_fee'], 0.0)
        self.assertIn('room_occupancy', res_data['stats'])
        print("[PASS] In-portal inline edit verified with real-time stats response")

if __name__ == '__main__':
    unittest.main()
