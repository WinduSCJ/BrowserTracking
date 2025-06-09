@echo off
echo ========================================
echo  Browser Tracking Agent - Stop All
echo ========================================
echo.

REM Stop agent via command
echo [INFO] Stopping agent...
cd /d "%~dp0vercel_client_configs"
python enhanced_agent.py --stop 2>nul

REM Stop background service
echo [INFO] Stopping background service...
cd /d "%~dp0"
python background_service.py --stop 2>nul

REM Kill any remaining processes
echo [INFO] Cleaning up processes...
taskkill /f /im python.exe /fi "WINDOWTITLE eq Browser Tracking*" 2>nul
taskkill /f /im python.exe /fi "COMMANDLINE eq *enhanced_agent.py*" 2>nul
taskkill /f /im python.exe /fi "COMMANDLINE eq *background_service.py*" 2>nul

echo.
echo [OK] Browser Tracking Agent stopped
pause
