@echo off
echo ========================================
echo  Stopping Browser Tracking Agent
echo ========================================
echo.

REM Method 1: Graceful stop via command
echo [INFO] Sending stop command to agent...
cd /d "%~dp0vercel_client_configs"
python enhanced_agent.py --stop 2>nul

REM Method 2: Kill processes if still running
echo [INFO] Checking for running agent processes...
tasklist /fi "imagename eq python.exe" /fi "windowtitle eq Browser Tracking Agent*" 2>nul | find "python.exe" >nul
if %errorLevel% equ 0 (
    echo [INFO] Found running agent processes, terminating...
    taskkill /f /im python.exe /fi "windowtitle eq Browser Tracking Agent*" 2>nul
)

REM Method 3: Kill by command line pattern
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq python.exe" /fo csv ^| findstr "enhanced_agent.py"') do (
    echo [INFO] Killing process %%i
    taskkill /f /pid %%i 2>nul
)

echo.
echo [OK] Agent stop procedures completed
echo.

REM Check final status
echo [INFO] Final status check...
python enhanced_agent.py --status 2>nul

echo.
echo Press any key to exit...
pause >nul
