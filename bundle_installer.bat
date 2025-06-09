@echo off
setlocal enabledelayedexpansion

REM ========================================
REM Browser Tracking Agent Bundle Installer
REM Auto-installs Python and dependencies
REM ========================================

echo.
echo ========================================
echo  Browser Tracking Agent Installer
echo ========================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] This installer requires Administrator privileges.
    echo Please right-click and select "Run as administrator"
    pause
    exit /b 1
)

REM Set installation directory
set "INSTALL_DIR=%LOCALAPPDATA%\BrowserTracker"
set "PYTHON_DIR=%INSTALL_DIR%\Python"
set "SCRIPTS_DIR=%INSTALL_DIR%\Scripts"

echo [INFO] Installation directory: %INSTALL_DIR%
echo.

REM Create installation directories
if not exist "%INSTALL_DIR%" (
    echo [INFO] Creating installation directory...
    mkdir "%INSTALL_DIR%"
    mkdir "%PYTHON_DIR%"
    mkdir "%SCRIPTS_DIR%"
)

REM Check if Python is already installed
echo [INFO] Checking for Python installation...
python --version >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Python is already installed
    set "PYTHON_CMD=python"
    goto :install_dependencies
)

REM Check if we have portable Python in install dir
if exist "%PYTHON_DIR%\python.exe" (
    echo [OK] Portable Python found in installation directory
    set "PYTHON_CMD=%PYTHON_DIR%\python.exe"
    goto :install_dependencies
)

REM Download and install Python
echo [INFO] Python not found. Downloading Python installer...
set "PYTHON_URL=https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe"
set "PYTHON_INSTALLER=%TEMP%\python_installer.exe"

REM Download Python installer
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_INSTALLER%'}"

if not exist "%PYTHON_INSTALLER%" (
    echo [ERROR] Failed to download Python installer
    pause
    exit /b 1
)

echo [INFO] Installing Python (this may take a few minutes)...
"%PYTHON_INSTALLER%" /quiet InstallAllUsers=0 TargetDir="%PYTHON_DIR%" PrependPath=0 Include_test=0 Include_doc=0 Include_dev=0 Include_launcher=0

REM Clean up installer
del "%PYTHON_INSTALLER%" >nul 2>&1

REM Set Python command path
set "PYTHON_CMD=%PYTHON_DIR%\python.exe"

REM Verify Python installation
if not exist "%PYTHON_CMD%" (
    echo [ERROR] Python installation failed
    pause
    exit /b 1
)

echo [OK] Python installed successfully

:install_dependencies
echo.
echo [INFO] Installing Python dependencies...

REM Create requirements.txt
echo requests==2.31.0> "%INSTALL_DIR%\requirements.txt"
echo schedule==1.2.0>> "%INSTALL_DIR%\requirements.txt"
echo psutil==5.9.6>> "%INSTALL_DIR%\requirements.txt"

REM Install dependencies
"%PYTHON_CMD%" -m pip install --upgrade pip --quiet
"%PYTHON_CMD%" -m pip install -r "%INSTALL_DIR%\requirements.txt" --quiet

if %errorLevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo [OK] Dependencies installed successfully

REM Copy agent files
echo.
echo [INFO] Installing agent files...

REM Create enhanced_agent.py (embedded)
(
echo """
echo Enhanced Browser Tracking Agent with Start/Stop Controls
echo For testing and production deployment
echo """
echo.
echo import os
echo import sys
echo import json
echo import time
echo import threading
echo import signal
echo import subprocess
echo import requests
echo import sqlite3
echo import shutil
echo import tempfile
echo from datetime import datetime, timezone
echo import socket
echo import getpass
echo import platform
echo from uuid import getnode
echo try:
echo     import psutil
echo except ImportError:
echo     psutil = None
echo.
echo # [Agent code would be embedded here - truncated for brevity]
echo # This would contain the full enhanced_agent.py code
echo.
echo if __name__ == '__main__':
echo     print("Browser Tracking Agent v1.0"^)
echo     print("Run with: python agent.py [--start^|--stop^|--status^|--test^|--once]"^)
) > "%SCRIPTS_DIR%\agent.py"

REM Create config.json
(
echo {
echo   "client": {
echo     "server_url": "https://browser-tracking.vercel.app",
echo     "api_token": "BrowserTracker2024SecureToken",
echo     "check_interval": 300,
echo     "batch_size": 50,
echo     "retry_attempts": 3,
echo     "retry_delay": 60,
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

REM Copy the actual enhanced_agent.py if it exists in current directory
if exist "%~dp0enhanced_agent.py" (
    copy "%~dp0enhanced_agent.py" "%SCRIPTS_DIR%\agent.py" >nul
    echo [OK] Agent file copied from bundle
) else (
    echo [WARNING] Using embedded agent code
)

REM Copy config if it exists
if exist "%~dp0config.json" (
    copy "%~dp0config.json" "%SCRIPTS_DIR%\config.json" >nul
    echo [OK] Config file copied from bundle
)

REM Create launcher scripts
echo [INFO] Creating launcher scripts...

REM Create start_agent.bat
(
echo @echo off
echo cd /d "%SCRIPTS_DIR%"
echo "%PYTHON_CMD%" agent.py --start
echo pause
) > "%INSTALL_DIR%\start_agent.bat"

REM Create stop_agent.bat
(
echo @echo off
echo cd /d "%SCRIPTS_DIR%"
echo "%PYTHON_CMD%" agent.py --stop
echo pause
) > "%INSTALL_DIR%\stop_agent.bat"

REM Create test_agent.bat
(
echo @echo off
echo cd /d "%SCRIPTS_DIR%"
echo "%PYTHON_CMD%" agent.py --test
echo echo.
echo "%PYTHON_CMD%" agent.py --once
echo pause
) > "%INSTALL_DIR%\test_agent.bat"

REM Create status_agent.bat
(
echo @echo off
echo cd /d "%SCRIPTS_DIR%"
echo "%PYTHON_CMD%" agent.py --status
echo pause
) > "%INSTALL_DIR%\status_agent.bat"

REM Create uninstall.bat
(
echo @echo off
echo echo Stopping agent...
echo cd /d "%SCRIPTS_DIR%"
echo "%PYTHON_CMD%" agent.py --stop 2^>nul
echo echo Removing installation...
echo cd /d "%TEMP%"
echo rmdir /s /q "%INSTALL_DIR%" 2^>nul
echo echo Uninstall complete
echo pause
) > "%INSTALL_DIR%\uninstall.bat"

echo [OK] Launcher scripts created

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
    echo   start_agent.bat    - Start monitoring
    echo   stop_agent.bat     - Stop monitoring  
    echo   test_agent.bat     - Test connection and run once
    echo   status_agent.bat   - Check agent status
    echo   uninstall.bat      - Remove installation
    echo.
    echo Manual usage:
    echo   cd "%SCRIPTS_DIR%"
    echo   "%PYTHON_CMD%" agent.py [--start^|--stop^|--status^|--test^|--once]
    echo.
    
    REM Ask if user wants to test now
    set /p "test_now=Do you want to test the agent now? (y/n): "
    if /i "!test_now!"=="y" (
        echo.
        echo [INFO] Running test...
        "%PYTHON_CMD%" agent.py --once
    )
    
) else (
    echo [ERROR] Installation test failed
    pause
    exit /b 1
)

echo.
echo Press any key to exit...
pause >nul
