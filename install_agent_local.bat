@echo off
setlocal enabledelayedexpansion

echo ========================================
echo  Browser Tracking Agent - Local Setup
echo ========================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [INFO] Requesting Administrator privileges...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo [INFO] Running as Administrator - OK
echo.

REM Set installation directory
set "INSTALL_DIR=%LOCALAPPDATA%\BrowserTracker"
set "SCRIPTS_DIR=%INSTALL_DIR%\Scripts"

echo [INFO] Installation directory: %INSTALL_DIR%
echo.

REM Create installation directories
if not exist "%INSTALL_DIR%" (
    echo [INFO] Creating installation directory...
    mkdir "%INSTALL_DIR%"
    mkdir "%SCRIPTS_DIR%"
)

REM Check if Python is available
echo [INFO] Checking Python installation...
python --version >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Python is available
    set "PYTHON_CMD=python"
) else (
    echo [ERROR] Python not found. Please install Python first.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Install required packages
echo [INFO] Installing required Python packages...
%PYTHON_CMD% -m pip install requests schedule psutil --quiet --user

if %errorLevel% neq 0 (
    echo [ERROR] Failed to install Python packages
    pause
    exit /b 1
)

echo [OK] Python packages installed

REM Copy agent files from current directory
echo [INFO] Installing agent files...

if exist "%~dp0enhanced_agent.py" (
    copy "%~dp0enhanced_agent.py" "%SCRIPTS_DIR%\agent.py" >nul
    echo [OK] Agent file copied
) else (
    echo [ERROR] enhanced_agent.py not found in current directory
    pause
    exit /b 1
)

if exist "%~dp0vercel_client_configs\config.json" (
    copy "%~dp0vercel_client_configs\config.json" "%SCRIPTS_DIR%\config.json" >nul
    echo [OK] Config file copied
) else (
    echo [WARNING] Config file not found, creating default...
    (
        echo {
        echo   "client": {
        echo     "server_url": "https://browser-tracking.vercel.app",
        echo     "api_token": "BrowserTracker2024SecureToken",
        echo     "check_interval": 60,
        echo     "batch_size": 50,
        echo     "retry_attempts": 3,
        echo     "retry_delay": 30,
        echo     "timeout": 30
        echo   },
        echo   "logging": {
        echo     "level": "INFO",
        echo     "max_file_size": "10KB",
        echo     "max_files": 3,
        echo     "log_file": "agent.log"
        echo   }
        echo }
    ) > "%SCRIPTS_DIR%\config.json"
    echo [OK] Default config created
)

REM Create launcher scripts
echo [INFO] Creating launcher scripts...

REM Start Agent (Background)
(
echo @echo off
echo echo Starting Browser Tracking Agent...
echo cd /d "%SCRIPTS_DIR%"
echo start /min "%PYTHON_CMD%" agent.py --start
echo echo Agent started in background
echo timeout /t 3 /nobreak ^>nul
) > "%INSTALL_DIR%\start_agent.bat"

REM Stop Agent
(
echo @echo off
echo echo Stopping Browser Tracking Agent...
echo cd /d "%SCRIPTS_DIR%"
echo "%PYTHON_CMD%" agent.py --stop
echo echo Agent stopped
echo pause
) > "%INSTALL_DIR%\stop_agent.bat"

REM Test Agent
(
echo @echo off
echo echo Testing Browser Tracking Agent...
echo cd /d "%SCRIPTS_DIR%"
echo "%PYTHON_CMD%" agent.py --test
echo echo.
echo echo Running one-time collection...
echo "%PYTHON_CMD%" agent.py --once
echo pause
) > "%INSTALL_DIR%\test_agent.bat"

REM Status Agent
(
echo @echo off
echo echo Checking Agent Status...
echo cd /d "%SCRIPTS_DIR%"
echo "%PYTHON_CMD%" agent.py --status
echo pause
) > "%INSTALL_DIR%\status_agent.bat"

REM Interactive Agent
(
echo @echo off
echo echo Browser Tracking Agent - Interactive Mode
echo cd /d "%SCRIPTS_DIR%"
echo "%PYTHON_CMD%" agent.py
) > "%INSTALL_DIR%\interactive_agent.bat"

echo [OK] Launcher scripts created

REM Create Windows scheduled task for auto-start
echo [INFO] Creating Windows scheduled task...
schtasks /query /tn "BrowserTrackingAgent" >nul 2>&1
if %errorLevel% equ 0 (
    echo [INFO] Removing existing scheduled task...
    schtasks /delete /tn "BrowserTrackingAgent" /f >nul
)

schtasks /create /tn "BrowserTrackingAgent" /tr "\"%PYTHON_CMD%\" \"%SCRIPTS_DIR%\agent.py\" --start" /sc onlogon /ru "%USERNAME%" /rl limited /f >nul

if %errorLevel% equ 0 (
    echo [OK] Scheduled task created (will start on next login)
) else (
    echo [WARNING] Failed to create scheduled task
)

REM Test installation
echo.
echo [INFO] Testing installation...
cd /d "%SCRIPTS_DIR%"
"%PYTHON_CMD%" agent.py --test

if %errorLevel% equ 0 (
    echo.
    echo ========================================
    echo  Installation Complete!
    echo ========================================
    echo.
    echo Installation directory: %INSTALL_DIR%
    echo.
    echo Available commands:
    echo   start_agent.bat      - Start monitoring in background
    echo   stop_agent.bat       - Stop monitoring
    echo   test_agent.bat       - Test connection and run once
    echo   status_agent.bat     - Check agent status
    echo   interactive_agent.bat - Interactive mode
    echo.
    echo The agent will automatically start on next login.
    echo.
    
    set /p "start_now=Do you want to start the agent now? (y/n): "
    if /i "!start_now!"=="y" (
        echo.
        echo [INFO] Starting agent in background...
        start /min "%PYTHON_CMD%" agent.py --start
        echo [OK] Agent started! Check status with status_agent.bat
        timeout /t 3 /nobreak >nul
        
        echo.
        echo [INFO] Running initial test...
        "%PYTHON_CMD%" agent.py --once
    )
    
) else (
    echo [ERROR] Installation test failed
    pause
    exit /b 1
)

echo.
echo [INFO] Setup complete! Agent is ready for monitoring.
echo Press any key to exit...
pause >nul
