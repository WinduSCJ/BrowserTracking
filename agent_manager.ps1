# Browser Tracking Agent Manager (PowerShell)
# Advanced process management for the agent

param(
    [string]$Action = "menu"
)

$AgentDir = Join-Path $PSScriptRoot "vercel_client_configs"
$AgentScript = Join-Path $AgentDir "enhanced_agent.py"

function Show-Menu {
    Clear-Host
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host " Browser Tracking Agent Manager" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. 🚀 Start Agent (Background)" -ForegroundColor Green
    Write-Host "2. 🛑 Stop Agent" -ForegroundColor Red
    Write-Host "3. 📊 Check Status" -ForegroundColor Yellow
    Write-Host "4. 🔗 Test Connection" -ForegroundColor Blue
    Write-Host "5. 🧪 Run Once" -ForegroundColor Magenta
    Write-Host "6. 💬 Interactive Mode" -ForegroundColor Cyan
    Write-Host "7. 📋 View Processes" -ForegroundColor White
    Write-Host "8. 🔪 Force Kill All" -ForegroundColor Red
    Write-Host "9. 📄 View Logs" -ForegroundColor Gray
    Write-Host "0. ❌ Exit" -ForegroundColor DarkGray
    Write-Host ""
}

function Test-AgentFiles {
    if (-not (Test-Path $AgentDir)) {
        Write-Host "❌ Agent directory not found: $AgentDir" -ForegroundColor Red
        return $false
    }
    
    if (-not (Test-Path $AgentScript)) {
        Write-Host "❌ Agent script not found: $AgentScript" -ForegroundColor Red
        return $false
    }
    
    return $true
}

function Start-Agent {
    Write-Host "🚀 Starting Browser Tracking Agent..." -ForegroundColor Green
    
    try {
        Set-Location $AgentDir
        
        # Start in background
        $process = Start-Process -FilePath "python" -ArgumentList "enhanced_agent.py --start" -WindowStyle Minimized -PassThru
        
        Write-Host "✅ Agent started in background (PID: $($process.Id))" -ForegroundColor Green
        
        # Wait and check status
        Start-Sleep -Seconds 2
        Get-AgentStatus
        
    } catch {
        Write-Host "❌ Failed to start agent: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Stop-Agent {
    Write-Host "🛑 Stopping Browser Tracking Agent..." -ForegroundColor Yellow
    
    try {
        Set-Location $AgentDir
        
        # Graceful stop
        $result = & python enhanced_agent.py --stop 2>&1
        Write-Host "📤 Stop command sent" -ForegroundColor Yellow
        
        # Wait a moment
        Start-Sleep -Seconds 2
        
        # Check if still running
        $processes = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object {
            $_.CommandLine -like "*enhanced_agent.py*"
        }
        
        if ($processes) {
            Write-Host "⚠️ Agent still running, force stopping..." -ForegroundColor Yellow
            $processes | Stop-Process -Force
            Write-Host "✅ Agent force stopped" -ForegroundColor Green
        } else {
            Write-Host "✅ Agent stopped gracefully" -ForegroundColor Green
        }
        
    } catch {
        Write-Host "❌ Error stopping agent: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Get-AgentStatus {
    Write-Host "📊 Checking Agent Status..." -ForegroundColor Yellow
    
    try {
        Set-Location $AgentDir
        $result = & python enhanced_agent.py --status 2>&1
        Write-Host $result -ForegroundColor White
        
    } catch {
        Write-Host "❌ Error checking status: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Test-Connection {
    Write-Host "🔗 Testing Server Connection..." -ForegroundColor Blue
    
    try {
        Set-Location $AgentDir
        $result = & python enhanced_agent.py --test 2>&1
        Write-Host $result -ForegroundColor White
        
    } catch {
        Write-Host "❌ Error testing connection: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Invoke-RunOnce {
    Write-Host "🧪 Running One-Time Collection..." -ForegroundColor Magenta
    
    try {
        Set-Location $AgentDir
        $result = & python enhanced_agent.py --once 2>&1
        Write-Host $result -ForegroundColor White
        
    } catch {
        Write-Host "❌ Error running collection: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Start-InteractiveMode {
    Write-Host "💬 Starting Interactive Mode..." -ForegroundColor Cyan
    Write-Host "Type 'quit' to return to menu" -ForegroundColor Gray
    Write-Host ""
    
    try {
        Set-Location $AgentDir
        & python enhanced_agent.py
        
    } catch {
        Write-Host "❌ Error in interactive mode: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Show-Processes {
    Write-Host "📋 Agent-Related Processes:" -ForegroundColor White
    Write-Host "========================================" -ForegroundColor Gray
    
    try {
        $processes = Get-Process -Name "python" -ErrorAction SilentlyContinue
        
        if ($processes) {
            foreach ($proc in $processes) {
                $cmdLine = $proc.CommandLine
                if ($cmdLine -like "*enhanced_agent*" -or $cmdLine -like "*agent.py*") {
                    Write-Host "🔍 PID: $($proc.Id) | Name: $($proc.ProcessName) | Status: $($proc.Responding)" -ForegroundColor Yellow
                    Write-Host "   Command: $cmdLine" -ForegroundColor Gray
                }
            }
        } else {
            Write-Host "ℹ️ No Python processes found" -ForegroundColor Gray
        }
        
    } catch {
        Write-Host "❌ Error listing processes: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Stop-AllAgentProcesses {
    Write-Host "🔪 Force Killing All Agent Processes..." -ForegroundColor Red
    
    $confirm = Read-Host "⚠️ This will forcefully kill all agent processes. Continue? (y/N)"
    
    if ($confirm -eq 'y' -or $confirm -eq 'Y') {
        try {
            $processes = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object {
                $_.CommandLine -like "*enhanced_agent*" -or $_.CommandLine -like "*agent.py*"
            }
            
            if ($processes) {
                $processes | Stop-Process -Force
                Write-Host "✅ Killed $($processes.Count) agent processes" -ForegroundColor Green
            } else {
                Write-Host "ℹ️ No agent processes found" -ForegroundColor Gray
            }
            
        } catch {
            Write-Host "❌ Error killing processes: $($_.Exception.Message)" -ForegroundColor Red
        }
    } else {
        Write-Host "ℹ️ Operation cancelled" -ForegroundColor Gray
    }
}

function Show-Logs {
    Write-Host "📄 Recent Agent Logs:" -ForegroundColor White
    Write-Host "========================================" -ForegroundColor Gray
    
    $logFile = Join-Path $AgentDir "agent.log"
    
    if (Test-Path $logFile) {
        Get-Content $logFile -Tail 20 | ForEach-Object {
            Write-Host $_ -ForegroundColor Gray
        }
    } else {
        Write-Host "ℹ️ No log file found" -ForegroundColor Gray
    }
}

# Main execution
if (-not (Test-AgentFiles)) {
    Read-Host "Press Enter to exit"
    exit 1
}

if ($Action -ne "menu") {
    switch ($Action.ToLower()) {
        "start" { Start-Agent }
        "stop" { Stop-Agent }
        "status" { Get-AgentStatus }
        "test" { Test-Connection }
        "once" { Invoke-RunOnce }
        "kill" { Stop-AllAgentProcesses }
        default { Write-Host "❌ Unknown action: $Action" -ForegroundColor Red }
    }
    exit 0
}

# Interactive menu
while ($true) {
    Show-Menu
    $choice = Read-Host "Select option (0-9)"
    
    switch ($choice) {
        "1" { Start-Agent; Read-Host "`nPress Enter to continue" }
        "2" { Stop-Agent; Read-Host "`nPress Enter to continue" }
        "3" { Get-AgentStatus; Read-Host "`nPress Enter to continue" }
        "4" { Test-Connection; Read-Host "`nPress Enter to continue" }
        "5" { Invoke-RunOnce; Read-Host "`nPress Enter to continue" }
        "6" { Start-InteractiveMode }
        "7" { Show-Processes; Read-Host "`nPress Enter to continue" }
        "8" { Stop-AllAgentProcesses; Read-Host "`nPress Enter to continue" }
        "9" { Show-Logs; Read-Host "`nPress Enter to continue" }
        "0" { Write-Host "👋 Goodbye!" -ForegroundColor Green; break }
        default { Write-Host "❌ Invalid choice. Please try again." -ForegroundColor Red; Start-Sleep 1 }
    }
}
