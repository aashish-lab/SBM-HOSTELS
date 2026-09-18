"""
database.py
Database setup and operations for SBM Hostels
"""

import sqlite3
import os
from datetime import datetime, date

DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "sbm_hostels.db"
)


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON")

    return conn


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # -----------------------------------------------------
    # ADMINS TABLE
    # -----------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            email TEXT
        )
    """)

    # -----------------------------------------------------
    # STUDENTS / CANDIDATES TABLE
    # -----------------------------------------------------

    cursor.execute("""
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

            attendance_attended INTEGER NOT NULL DEFAULT 0,

            attendance_total INTEGER NOT NULL DEFAULT 30,

            food_required TEXT NOT NULL DEFAULT 'Yes'
                CHECK(food_required IN ('Yes', 'No')),

            status TEXT NOT NULL DEFAULT 'Active'
                CHECK(status IN ('Active', 'Inactive')),

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # -----------------------------------------------------
    # DAILY FOOD SELECTION TABLE
    # -----------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS food_selections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            student_id INTEGER NOT NULL,

            selection_date TEXT NOT NULL,

            food_type TEXT NOT NULL
                CHECK(food_type IN ('VEG', 'NON_VEG')),

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            UNIQUE(student_id, selection_date),

            FOREIGN KEY(student_id)
                REFERENCES students(id)
                ON DELETE CASCADE
        )
    """)

    # -----------------------------------------------------
    # FOOD SELECTION INDEXES
    # -----------------------------------------------------

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_food_selection_date
        ON food_selections(selection_date)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_food_selection_student_date
        ON food_selections(student_id, selection_date)
    """)

    # -----------------------------------------------------
    # FEE PAYMENTS HISTORY
    # -----------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fee_payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            student_id INTEGER NOT NULL,

            amount REAL NOT NULL,

            payment_date TEXT NOT NULL,

            payment_method TEXT DEFAULT 'UPI / Cash',

            remarks TEXT,

            FOREIGN KEY(student_id)
                REFERENCES students(id)
                ON DELETE CASCADE
        )
    """)

    # -----------------------------------------------------
    # SEED DEFAULT ADMIN
    # -----------------------------------------------------

    cursor.execute("SELECT COUNT(*) FROM admins")

    if cursor.fetchone()[0] == 0:

        cursor.execute("""
            INSERT INTO admins (
                username,
                password,
                name,
                email
            )
            VALUES (?, ?, ?, ?)
        """, (
            "admin",
            "sbmhostels123",
            "SBM Hostels Owner",
            "owner@sbmhostels.com"
        ))

    # -----------------------------------------------------
    # SEED SAMPLE STUDENTS
    # -----------------------------------------------------

    cursor.execute("SELECT COUNT(*) FROM students")

    if cursor.fetchone()[0] == 0:

        sample_students = [

            (
                "SBM-2026-101",
                "Aashis Rudra",
                "student123",
                "12-09-2026",
                "Room 203",
                6000.0,
                "10-10-2026",
                6000.0,
                0.0,
                "9876543210",
                "9765432109",
                26,
                30,
                "Yes",
                "Active"
            ),

            (
                "SBM-2026-102",
                "Rahul Sharma",
                "student123",
                "15-08-2026",
                "Room 105",
                6000.0,
                "05-10-2026",
                4000.0,
                2000.0,
                "9811223344",
                "9711223344",
                28,
                30,
                "Yes",
                "Active"
            ),

            (
                "SBM-2026-103",
                "Kiran Patel",
                "student123",
                "01-09-2026",
                "Room 301",
                5500.0,
                "01-10-2026",
                5500.0,
                0.0,
                "9844556677",
                "9744556677",
                24,
                30,
                "No",
                "Active"
            ),

            (
                "SBM-2026-104",
                "Vikram Verma",
                "student123",
                "10-07-2026",
                "Room 204",
                6000.0,
                "10-09-2026",
                0.0,
                6000.0,
                "9899001122",
                "9799001122",
                22,
                30,
                "Yes",
                "Active"
            )
        ]

        cursor.executemany("""
            INSERT INTO students (
                admission_id,
                name,
                password,
                joining_date,
                room_bed,
                monthly_fee,
                fee_due_date,
                amount_paid,
                remaining_fee,
                student_phone,
                parent_phone,
                attendance_attended,
                attendance_total,
                food_required,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_students)

    conn.commit()
    conn.close()


# =========================================================
# ADMISSION ID GENERATOR
# =========================================================

def get_next_admission_id():
    """
    Generates the next admission ID.

    Example:
        SBM-2026-101
        SBM-2026-102
        SBM-2026-103
    """

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT admission_id
        FROM students
        ORDER BY id DESC
        LIMIT 1
    """)

    row = cursor.fetchone()

    conn.close()

    current_year = datetime.now().year

    if row and row["admission_id"]:

        try:

            parts = row["admission_id"].split("-")

            if len(parts) == 3 and parts[0] == "SBM":

                number = int(parts[2]) + 1

                return f"SBM-{current_year}-{number}"

        except (ValueError, IndexError):
            pass

    return f"SBM-{current_year}-101"


# =========================================================
# FOOD RULES
# =========================================================

def is_non_veg_allowed(selection_date):
    """
    Non-Veg is allowed only on:

        Tuesday
        Wednesday
        Sunday

    Returns True/False.
    """

    if isinstance(selection_date, str):

        try:
            selection_date = datetime.strptime(
                selection_date,
                "%Y-%m-%d"
            ).date()

        except ValueError:

            try:
                selection_date = datetime.strptime(
                    selection_date,
                    "%d-%m-%Y"
                ).date()

            except ValueError:
                return False

    # Python weekday:
    # Monday = 0
    # Tuesday = 1
    # Wednesday = 2
    # Thursday = 3
    # Friday = 4
    # Saturday = 5
    # Sunday = 6

    return selection_date.weekday() in (1, 2, 6)


def get_allowed_food_types(selection_date):
    """
    Returns the food options available for a particular date.
    """

    if is_non_veg_allowed(selection_date):

        return ["VEG", "NON_VEG"]

    return ["VEG"]


# =========================================================
# SAVE / UPDATE FOOD SELECTION
# =========================================================

def save_food_selection(student_id, selection_date, food_type):
    """
    Saves or updates a student's food selection.

    Rules:
        Tuesday    -> VEG / NON_VEG
        Wednesday  -> VEG / NON_VEG
        Sunday     -> VEG / NON_VEG

        Monday     -> VEG only
        Thursday   -> VEG only
        Friday     -> VEG only
        Saturday   -> VEG only
    """

    food_type = food_type.upper().strip()

    allowed_foods = get_allowed_food_types(selection_date)

    if food_type not in allowed_foods:

        return {
            "success": False,
            "message": (
                f"{food_type} is not available on "
                f"{selection_date}. "
                f"Allowed: {', '.join(allowed_foods)}"
            )
        }

    # Normalize date to YYYY-MM-DD
    if isinstance(selection_date, str):

        try:

            parsed_date = datetime.strptime(
                selection_date,
                "%Y-%m-%d"
            ).date()

        except ValueError:

            parsed_date = datetime.strptime(
                selection_date,
                "%d-%m-%Y"
            ).date()

    else:

        parsed_date = selection_date

    normalized_date = parsed_date.strftime("%Y-%m-%d")

    conn = get_db()
    cursor = conn.cursor()

    # Check student
    cursor.execute("""
        SELECT id
        FROM students
        WHERE id = ?
    """, (student_id,))

    student = cursor.fetchone()

    if not student:

        conn.close()

        return {
            "success": False,
            "message": "Student not found."
        }

    # Insert or update selection
    cursor.execute("""
        INSERT INTO food_selections (
            student_id,
            selection_date,
            food_type
        )
        VALUES (?, ?, ?)

        ON CONFLICT(student_id, selection_date)
        DO UPDATE SET
            food_type = excluded.food_type,
            updated_at = CURRENT_TIMESTAMP
    """, (
        student_id,
        normalized_date,
        food_type
    ))

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "Food selection saved successfully.",
        "selection_date": normalized_date,
        "food_type": food_type
    }


# =========================================================
# GET STUDENT FOOD SELECTION
# =========================================================

def get_food_selection(student_id, selection_date):
    """
    Gets a student's food selection for a particular date.
    """

    if isinstance(selection_date, str):

        try:

            parsed_date = datetime.strptime(
                selection_date,
                "%Y-%m-%d"
            ).date()

        except ValueError:

            parsed_date = datetime.strptime(
                selection_date,
                "%d-%m-%Y"
            ).date()

    else:

        parsed_date = selection_date

    normalized_date = parsed_date.strftime("%Y-%m-%d")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            student_id,
            selection_date,
            food_type,
            created_at,
            updated_at
        FROM food_selections
        WHERE student_id = ?
        AND selection_date = ?
    """, (
        student_id,
        normalized_date
    ))

    row = cursor.fetchone()

    conn.close()

    if row:
        return dict(row)

    return None


# =========================================================
# GET FOOD COUNT FOR A DATE
# =========================================================

def get_food_count(selection_date):
    """
    Returns the number of VEG and NON_VEG meals
    required for a particular date.
    """

    if isinstance(selection_date, str):

        try:

            parsed_date = datetime.strptime(
                selection_date,
                "%Y-%m-%d"
            ).date()

        except ValueError:

            parsed_date = datetime.strptime(
                selection_date,
                "%d-%m-%Y"
            ).date()

    else:

        parsed_date = selection_date

    normalized_date = parsed_date.strftime("%Y-%m-%d")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            food_type,
            COUNT(*) AS total
        FROM food_selections
        WHERE selection_date = ?
        GROUP BY food_type
    """, (normalized_date,))

    rows = cursor.fetchall()

    conn.close()

    result = {
        "date": normalized_date,
        "veg": 0,
        "non_veg": 0,
        "total": 0
    }

    for row in rows:

        if row["food_type"] == "VEG":
            result["veg"] = row["total"]

        elif row["food_type"] == "NON_VEG":
            result["non_veg"] = row["total"]

    result["total"] = (
        result["veg"] +
        result["non_veg"]
    )

    return result


# =========================================================
# GET ALL FOOD SELECTIONS FOR A DATE
# =========================================================

def get_food_selections_by_date(selection_date):

    if isinstance(selection_date, str):

        try:

            parsed_date = datetime.strptime(
                selection_date,
                "%Y-%m-%d"
            ).date()

        except ValueError:

            parsed_date = datetime.strptime(
                selection_date,
                "%d-%m-%Y"
            ).date()

    else:

        parsed_date = selection_date

    normalized_date = parsed_date.strftime("%Y-%m-%d")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            fs.id,
            fs.student_id,
            s.admission_id,
            s.name,
            s.room_bed,
            fs.selection_date,
            fs.food_type
        FROM food_selections fs
        JOIN students s
            ON s.id = fs.student_id
        WHERE fs.selection_date = ?
        ORDER BY s.name
    """, (normalized_date,))

    rows = cursor.fetchall()

    conn.close()

    return [dict(row) for row in rows]


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    init_db()

    print("========================================")
    print("SBM Hostels Database")
    print("========================================")
    print("Database initialized successfully.")
    print("Database path:")
    print(DB_PATH)
    print("========================================")
