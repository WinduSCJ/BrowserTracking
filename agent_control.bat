@echo off
setlocal enabledelayedexpansion

echo ========================================
echo  Browser Tracking Agent Control Panel
echo ========================================
echo.

REM Set agent directory
set "AGENT_DIR=%~dp0vercel_client_configs"
set "PYTHON_CMD=python"

REM Check if agent directory exists
if not exist "%AGENT_DIR%" (
    echo [ERROR] Agent directory not found: %AGENT_DIR%
    pause
    exit /b 1
)

REM Check if enhanced_agent.py exists
if not exist "%AGENT_DIR%\enhanced_agent.py" (
    echo [ERROR] enhanced_agent.py not found in %AGENT_DIR%
    pause
    exit /b 1
)

:menu
echo.
echo ========================================
echo  Agent Control Menu
echo ========================================
echo.
echo 1. Start Agent (Background Monitoring)
echo 2. Stop Agent
echo 3. Check Agent Status
echo 4. Test Connection
echo 5. Run Once (Single Collection)
echo 6. Interactive Mode
echo 7. View Recent Logs
echo 8. Kill All Agent Processes
echo 9. Exit
echo.
set /p "choice=Select option (1-9): "

if "%choice%"=="1" goto start_agent
if "%choice%"=="2" goto stop_agent
if "%choice%"=="3" goto status_agent
if "%choice%"=="4" goto test_agent
if "%choice%"=="5" goto run_once
if "%choice%"=="6" goto interactive_mode
if "%choice%"=="7" goto view_logs
if "%choice%"=="8" goto kill_processes
if "%choice%"=="9" goto exit
echo Invalid choice. Please try again.
goto menu

:start_agent
echo.
echo [INFO] Starting Browser Tracking Agent...
cd /d "%AGENT_DIR%"
start /min cmd /c "%PYTHON_CMD% enhanced_agent.py --start"
echo [OK] Agent started in background
echo Check status with option 3
timeout /t 3 /nobreak >nul
goto menu

:stop_agent
echo.
echo [INFO] Stopping Browser Tracking Agent...
cd /d "%AGENT_DIR%"
%PYTHON_CMD% enhanced_agent.py --stop
echo [OK] Stop command sent
timeout /t 2 /nobreak >nul
goto menu

:status_agent
echo.
echo [INFO] Checking Agent Status...
cd /d "%AGENT_DIR%"
%PYTHON_CMD% enhanced_agent.py --status
echo.
pause
goto menu

:test_agent
echo.
echo [INFO] Testing Server Connection...
cd /d "%AGENT_DIR%"
%PYTHON_CMD% enhanced_agent.py --test
echo.
pause
goto menu

:run_once
echo.
echo [INFO] Running One-Time Data Collection...
cd /d "%AGENT_DIR%"
%PYTHON_CMD% enhanced_agent.py --once
echo.
pause
goto menu

:interactive_mode
echo.
echo [INFO] Starting Interactive Mode...
echo Type 'quit' to return to this menu
echo.
cd /d "%AGENT_DIR%"
%PYTHON_CMD% enhanced_agent.py
goto menu

:view_logs
echo.
echo [INFO] Recent Agent Logs:
echo ========================================
cd /d "%AGENT_DIR%"
if exist "agent.log" (
    type agent.log | more
) else (
    echo No log file found
)
echo.
pause
goto menu

:kill_processes
echo.
echo [WARNING] This will forcefully kill all Python processes
echo that might be running the agent.
set /p "confirm=Are you sure? (y/n): "
if /i "!confirm!"=="y" (
    echo [INFO] Killing agent processes...
    taskkill /f /im python.exe /fi "WINDOWTITLE eq Browser Tracking Agent*" 2>nul
    taskkill /f /im python.exe /fi "COMMANDLINE eq *enhanced_agent.py*" 2>nul
    echo [OK] Process kill commands sent
) else (
    echo [INFO] Operation cancelled
)
echo.
pause
goto menu

:exit
echo.
echo [INFO] Exiting Agent Control Panel
echo.
exit /b 0
