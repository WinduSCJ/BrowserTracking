@echo off
setlocal enabledelayedexpansion

echo ========================================
echo  Browser Tracking Agent - Quick Install
echo ========================================
echo.

REM Change to script directory
cd /d "%~dp0"
echo Current directory: %CD%

REM Check if INSTALL.py exists
if not exist "INSTALL.py" (
    echo ERROR: INSTALL.py not found in current directory
    echo Please make sure you extracted the ZIP file completely
    echo and run this batch file from the extracted folder.
    echo.
    pause
    exit /b 1
)

REM Check for Python
echo Checking for Python installation...
python --version >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ Python found, starting installation...
    echo.
    python INSTALL.py
    set install_result=!errorlevel!
) else (
    echo ⚠️  Python not found, attempting installation with full installer...
    echo.
    python INSTALL.py
    set install_result=!errorlevel!
)

echo.
if !install_result! == 0 (
    echo ✅ Installation completed successfully!
    echo.
    echo The Browser Tracking Agent has been installed and will start
    echo automatically on next Windows boot.
    echo.
    echo To start the agent now, you can:
    echo 1. Restart your computer, OR
    echo 2. Run the agent manually from the installation directory
    echo.
    echo Dashboard: https://browser-tracking.vercel.app
) else (
    echo ❌ Installation failed with error code: !install_result!
    echo.
    echo Please try the following:
    echo 1. Run this batch file as Administrator
    echo 2. Check your internet connection
    echo 3. Temporarily disable antivirus software
    echo 4. Contact support if the problem persists
)

echo.
pause
