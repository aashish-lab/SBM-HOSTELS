"""
wsgi.py - Production WSGI entry point for SBM Hostels deployment
"""

import database
from app import app

# Ensure database tables and initial seed data are initialized
database.init_db()

# Expose app for WSGI servers like Gunicorn or Waitress
if __name__ == "__main__":
    app.run()
