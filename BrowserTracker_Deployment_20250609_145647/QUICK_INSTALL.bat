@echo off
echo Browser Tracking Agent - Quick Installer
echo ========================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check for Python
python --version >nul 2>&1
if %errorlevel% == 0 (
    echo Python found, starting installation...
    python INSTALL.py
) else (
    echo Python not found, starting full installation...
    python INSTALL.py
)

echo.
echo Installation completed!
pause
