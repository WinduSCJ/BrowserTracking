
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
Package created: 2025-06-09 15:14:31
Version: 1.0
