@echo off
echo Browser Tracking Client Installer
echo Server: https://your-ngrok-url.ngrok.io:5000
echo.

REM Check admin privileges
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running with administrator privileges...
) else (
    echo This script requires administrator privileges.
    echo Please run as administrator.
    pause
    exit /b 1
)

REM Install client
echo Installing Browser Tracking Client...
python installer.py

echo.
echo Installation complete!
echo The client will connect to: https://your-ngrok-url.ngrok.io:5000
echo.
pause
