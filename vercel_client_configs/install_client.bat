@echo off
echo Browser Tracking Client Installer (Vercel Server)
echo Server: https://browser-tracking-28tr6vyd7-winduajis-projects.vercel.app
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

REM Test server connectivity
echo Testing server connectivity...
curl -f https://browser-tracking-28tr6vyd7-winduajis-projects.vercel.app/health
if %errorLevel% == 0 (
    echo Server is reachable
) else (
    echo Cannot reach server at https://browser-tracking-28tr6vyd7-winduajis-projects.vercel.app
    echo Please check internet connectivity
    pause
    exit /b 1
)

REM Install client
echo Installing Browser Tracking Client...
python installer.py

echo.
echo Installation complete!
echo The client will connect to: https://browser-tracking-28tr6vyd7-winduajis-projects.vercel.app
echo.
pause
