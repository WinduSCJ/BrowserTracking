@echo off
echo ========================================
echo  Starting Browser Tracking Agent
echo ========================================
echo.

REM Check if agent is already running
echo [INFO] Checking current agent status...
cd /d "%~dp0vercel_client_configs"
python enhanced_agent.py --status 2>nul

echo.
echo [INFO] Starting Browser Tracking Agent in background...

REM Start agent in minimized window
start /min cmd /c "python enhanced_agent.py --start"

echo [OK] Agent started in background
echo.

REM Wait a moment and check status
echo [INFO] Waiting for agent to initialize...
timeout /t 3 /nobreak >nul

echo [INFO] Checking agent status...
python enhanced_agent.py --status 2>nul

echo.
echo [INFO] Agent is now running in background
echo.
echo To stop the agent, run: stop_agent.bat
echo To check status, run: agent_control.bat
echo.
echo Press any key to exit...
pause >nul
