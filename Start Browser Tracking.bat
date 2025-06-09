@echo off
echo ========================================
echo  Browser Tracking Agent - Quick Start
echo ========================================
echo.

REM Start background service
echo [INFO] Starting background service...
start /min python background_service.py --start

REM Wait a moment
timeout /t 3 /nobreak >nul

REM Start GUI
echo [INFO] Starting GUI...
python simple_gui.py

echo.
echo [INFO] Browser Tracking Agent started
echo Background service will continue running even if GUI is closed
pause
