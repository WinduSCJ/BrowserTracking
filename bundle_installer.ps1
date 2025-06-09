# Browser Tracking Agent Bundle Installer (PowerShell)
# Auto-installs Python and all dependencies

param(
    [string]$InstallPath = "$env:LOCALAPPDATA\BrowserTracker",
    [string]$ServerUrl = "https://browser-tracking.vercel.app",
    [switch]$Silent = $false
)

# Check if running as administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    if (-not $Silent) {
        Write-Host "❌ This installer requires Administrator privileges." -ForegroundColor Red
        Write-Host "Please right-click and select 'Run as Administrator'" -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
    }
    exit 1
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Browser Tracking Agent Installer" -ForegroundColor Cyan  
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Create installation directories
$PythonDir = Join-Path $InstallPath "Python"
$ScriptsDir = Join-Path $InstallPath "Scripts"

Write-Host "📁 Installation directory: $InstallPath" -ForegroundColor Green

if (-not (Test-Path $InstallPath)) {
    New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
    New-Item -ItemType Directory -Path $PythonDir -Force | Out-Null
    New-Item -ItemType Directory -Path $ScriptsDir -Force | Out-Null
    Write-Host "✅ Created installation directories" -ForegroundColor Green
}

# Function to test Python installation
function Test-Python {
    param([string]$PythonPath)
    try {
        $result = & $PythonPath --version 2>$null
        return $LASTEXITCODE -eq 0
    } catch {
        return $false
    }
}

# Check for existing Python installation
Write-Host "🔍 Checking for Python installation..." -ForegroundColor Yellow

$PythonCmd = $null
$PythonPaths = @(
    "python",
    "py",
    "$PythonDir\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
    "$env:PROGRAMFILES\Python311\python.exe"
)

foreach ($path in $PythonPaths) {
    if (Test-Python $path) {
        $PythonCmd = $path
        $version = & $path --version 2>$null
        Write-Host "✅ Found Python: $version at $path" -ForegroundColor Green
        break
    }
}

# Install Python if not found
if (-not $PythonCmd) {
    Write-Host "📥 Python not found. Downloading and installing..." -ForegroundColor Yellow
    
    $PythonUrl = "https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe"
    $PythonInstaller = "$env:TEMP\python_installer.exe"
    
    try {
        # Download Python installer
        Write-Host "⬇️ Downloading Python installer..." -ForegroundColor Yellow
        Invoke-WebRequest -Uri $PythonUrl -OutFile $PythonInstaller -UseBasicParsing
        
        # Install Python
        Write-Host "⚙️ Installing Python (this may take a few minutes)..." -ForegroundColor Yellow
        $installArgs = @(
            "/quiet",
            "InstallAllUsers=0",
            "TargetDir=$PythonDir",
            "PrependPath=0",
            "Include_test=0",
            "Include_doc=0",
            "Include_dev=0",
            "Include_launcher=0"
        )
        
        Start-Process -FilePath $PythonInstaller -ArgumentList $installArgs -Wait -WindowStyle Hidden
        
        # Clean up installer
        Remove-Item $PythonInstaller -Force -ErrorAction SilentlyContinue
        
        # Set Python command
        $PythonCmd = "$PythonDir\python.exe"
        
        if (Test-Python $PythonCmd) {
            Write-Host "✅ Python installed successfully" -ForegroundColor Green
        } else {
            throw "Python installation verification failed"
        }
        
    } catch {
        Write-Host "❌ Failed to install Python: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
}

# Install Python dependencies
Write-Host "📦 Installing Python dependencies..." -ForegroundColor Yellow

$RequirementsContent = @"
requests==2.31.0
schedule==1.2.0
psutil==5.9.6
"@

$RequirementsFile = Join-Path $InstallPath "requirements.txt"
$RequirementsContent | Out-File -FilePath $RequirementsFile -Encoding UTF8

try {
    # Upgrade pip
    & $PythonCmd -m pip install --upgrade pip --quiet
    
    # Install dependencies
    & $PythonCmd -m pip install -r $RequirementsFile --quiet
    
    Write-Host "✅ Dependencies installed successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to install dependencies: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Create agent files
Write-Host "📝 Creating agent files..." -ForegroundColor Yellow

# Create config.json
$ConfigContent = @{
    client = @{
        server_url = $ServerUrl
        api_token = "BrowserTracker2024SecureToken"
        check_interval = 300
        batch_size = 50
        retry_attempts = 3
        retry_delay = 60
        timeout = 30
    }
    logging = @{
        level = "INFO"
        max_file_size = "10KB"
        max_files = 3
        log_file = "agent.log"
    }
} | ConvertTo-Json -Depth 3

$ConfigFile = Join-Path $ScriptsDir "config.json"
$ConfigContent | Out-File -FilePath $ConfigFile -Encoding UTF8

# Copy enhanced_agent.py if it exists, otherwise create a minimal version
$AgentFile = Join-Path $ScriptsDir "agent.py"
$SourceAgent = Join-Path $PSScriptRoot "enhanced_agent.py"

if (Test-Path $SourceAgent) {
    Copy-Item $SourceAgent $AgentFile
    Write-Host "✅ Agent file copied from bundle" -ForegroundColor Green
} else {
    # Create minimal agent file
    $MinimalAgent = @'
"""
Browser Tracking Agent - Minimal Version
Run with: python agent.py [--start|--stop|--status|--test|--once]
"""

import sys
print("Browser Tracking Agent v1.0")
print("This is a minimal version. Please ensure enhanced_agent.py is available.")
print("Usage: python agent.py [--start|--stop|--status|--test|--once]")

if len(sys.argv) > 1 and sys.argv[1] == '--test':
    import requests
    try:
        response = requests.get("https://browser-tracking.vercel.app/health", timeout=10)
        if response.status_code == 200:
            print("✅ Server connection successful")
        else:
            print(f"❌ Server returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
'@
    
    $MinimalAgent | Out-File -FilePath $AgentFile -Encoding UTF8
    Write-Host "⚠️ Created minimal agent file" -ForegroundColor Yellow
}

# Create launcher scripts
Write-Host "🚀 Creating launcher scripts..." -ForegroundColor Yellow

# Start Agent
$StartScript = @"
@echo off
cd /d "$ScriptsDir"
"$PythonCmd" agent.py --start
pause
"@
$StartScript | Out-File -FilePath (Join-Path $InstallPath "start_agent.bat") -Encoding ASCII

# Stop Agent  
$StopScript = @"
@echo off
cd /d "$ScriptsDir"
"$PythonCmd" agent.py --stop
pause
"@
$StopScript | Out-File -FilePath (Join-Path $InstallPath "stop_agent.bat") -Encoding ASCII

# Test Agent
$TestScript = @"
@echo off
cd /d "$ScriptsDir"
echo Testing connection...
"$PythonCmd" agent.py --test
echo.
echo Running one-time collection...
"$PythonCmd" agent.py --once
pause
"@
$TestScript | Out-File -FilePath (Join-Path $InstallPath "test_agent.bat") -Encoding ASCII

# Status Agent
$StatusScript = @"
@echo off
cd /d "$ScriptsDir"
"$PythonCmd" agent.py --status
pause
"@
$StatusScript | Out-File -FilePath (Join-Path $InstallPath "status_agent.bat") -Encoding ASCII

# Uninstall
$UninstallScript = @"
@echo off
echo Stopping agent...
cd /d "$ScriptsDir"
"$PythonCmd" agent.py --stop 2>nul
echo Removing installation...
cd /d "%TEMP%"
rmdir /s /q "$InstallPath" 2>nul
echo Uninstall complete
pause
"@
$UninstallScript | Out-File -FilePath (Join-Path $InstallPath "uninstall.bat") -Encoding ASCII

Write-Host "✅ Launcher scripts created" -ForegroundColor Green

# Test installation
Write-Host "🧪 Testing installation..." -ForegroundColor Yellow

try {
    Set-Location $ScriptsDir
    $testResult = & $PythonCmd agent.py --test 2>&1
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host " Installation Complete!" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📁 Installation directory: $InstallPath" -ForegroundColor Green
    Write-Host ""
    Write-Host "🎮 Available commands:" -ForegroundColor Yellow
    Write-Host "  start_agent.bat    - Start monitoring" -ForegroundColor White
    Write-Host "  stop_agent.bat     - Stop monitoring" -ForegroundColor White
    Write-Host "  test_agent.bat     - Test connection and run once" -ForegroundColor White
    Write-Host "  status_agent.bat   - Check agent status" -ForegroundColor White
    Write-Host "  uninstall.bat      - Remove installation" -ForegroundColor White
    Write-Host ""
    Write-Host "💻 Manual usage:" -ForegroundColor Yellow
    Write-Host "  cd `"$ScriptsDir`"" -ForegroundColor White
    Write-Host "  `"$PythonCmd`" agent.py [--start|--stop|--status|--test|--once]" -ForegroundColor White
    Write-Host ""
    
    if (-not $Silent) {
        $testNow = Read-Host "Do you want to test the agent now? (y/n)"
        if ($testNow -eq 'y' -or $testNow -eq 'Y') {
            Write-Host ""
            Write-Host "🧪 Running test..." -ForegroundColor Yellow
            & $PythonCmd agent.py --once
        }
    }
    
} catch {
    Write-Host "❌ Installation test failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

if (-not $Silent) {
    Write-Host ""
    Read-Host "Press Enter to exit"
}
