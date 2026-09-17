@echo off
echo =================================================================
echo        STARTING SBM HOSTELS MULTI-THREADED PRODUCTION SERVER     
echo =================================================================
echo Local Machine:    http://127.0.0.1:5000
echo Hostel Wi-Fi/LAN: http://192.168.1.64:5000
echo.
echo Owner Login:      admin / sbmhostels123
echo Candidate Login:  SBM-2026-101 / student123
echo =================================================================
python server_production.py
pause
