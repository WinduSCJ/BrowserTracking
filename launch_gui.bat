@echo off
echo ========================================
echo  Browser Tracking Agent GUI Launcher
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Python not found. Please install Python first.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if GUI file exists
if not exist "%~dp0agent_gui.py" (
    echo [ERROR] agent_gui.py not found in current directory
    pause
    exit /b 1
)

REM Check if agent directory exists
if not exist "%~dp0vercel_client_configs" (
    echo [ERROR] vercel_client_configs directory not found
    echo Please ensure the agent files are properly installed
    pause
    exit /b 1
)

echo [INFO] Starting Browser Tracking Agent GUI...
echo.

REM Launch GUI
python "%~dp0agent_gui.py"

REM If GUI exits, show message
echo.
echo [INFO] GUI closed
pause
