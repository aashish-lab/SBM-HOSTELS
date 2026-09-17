"""
server_production.py - Production multi-threaded WSGI server using Waitress
"""

from waitress import serve
from app import app
import database

if __name__ == '__main__':
    database.init_db()
    print("=================================================================")
    print("          SBM HOSTELS - PRODUCTION WSGI SERVER RUNNING           ")
    print("=================================================================")
    print("Local Machine:   http://127.0.0.1:5000")
    print("Hostel Wi-Fi/LAN: http://192.168.1.64:5000")
    print("=================================================================")
    print("Serving multi-threaded requests on port 5000...")
    serve(app, host='0.0.0.0', port=5000, threads=8)
