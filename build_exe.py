import PyInstaller.__main__
import os
import sys
import shutil

def build_agent():
    """Build agent.py into executable"""
    
    # PyInstaller arguments
    args = [
        'agent.py',
        '--onefile',
        '--noconsole',
        '--name=BrowserTrackingAgent',
        '--add-data=config.json;.',
        '--hidden-import=win32timezone',
        '--hidden-import=pywintypes',
        '--hidden-import=win32api',
        '--hidden-import=win32con',
        '--hidden-import=win32event',
        '--hidden-import=win32evtlogutil',
        '--hidden-import=win32service',
        '--hidden-import=win32serviceutil',
        '--hidden-import=servicemanager',
        '--distpath=dist',
        '--workpath=build',
        '--specpath=.',
    ]
    
    print("Building Browser Tracking Agent executable...")
    PyInstaller.__main__.run(args)
    print("Build completed!")

def build_installer():
    """Build installer.py into executable"""
    
    # PyInstaller arguments for installer
    args = [
        'installer.py',
        '--onefile',
        '--console',
        '--name=BrowserTrackingInstaller',
        '--add-data=agent.py;.',
        '--add-data=browser_reader.py;.',
        '--add-data=system_info.py;.',
        '--add-data=network_client.py;.',
        '--add-data=logger.py;.',
        '--add-data=config.json;.',
        '--distpath=dist',
        '--workpath=build',
        '--specpath=.',
    ]
    
    print("Building Browser Tracking Installer executable...")
    PyInstaller.__main__.run(args)
    print("Installer build completed!")

def build_server():
    """Build server.py into executable"""
    
    # PyInstaller arguments for server
    args = [
        'server.py',
        '--onefile',
        '--console',
        '--name=BrowserTrackingServer',
        '--add-data=database.py;.',
        '--add-data=logger.py;.',
        '--add-data=config.json;.',
        '--distpath=dist',
        '--workpath=build',
        '--specpath=.',
    ]
    
    print("Building Browser Tracking Server executable...")
    PyInstaller.__main__.run(args)
    print("Server build completed!")

def create_distribution_package():
    """Create distribution package with all necessary files"""
    
    dist_dir = "BrowserTrackingSystem"
    
    # Create distribution directory
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    os.makedirs(dist_dir)
    
    # Copy executables
    executables = [
        'dist/BrowserTrackingAgent.exe',
        'dist/BrowserTrackingInstaller.exe',
        'dist/BrowserTrackingServer.exe'
    ]
    
    for exe in executables:
        if os.path.exists(exe):
            shutil.copy2(exe, dist_dir)
            print(f"Copied {exe}")
    
    # Copy configuration and documentation
    files_to_copy = [
        'config.json',
        'requirements.txt'
    ]
    
    for file_name in files_to_copy:
        if os.path.exists(file_name):
            shutil.copy2(file_name, dist_dir)
            print(f"Copied {file_name}")
    
    # Create README
    readme_content = """# Browser Tracking System

## Files:
- BrowserTrackingServer.exe: Server application (run on monitoring server)
- BrowserTrackingInstaller.exe: Client installer (run on target PCs)
- BrowserTrackingAgent.exe: Client agent (installed by installer)
- config.json: Configuration file

## Setup Instructions:

### Server Setup:
1. Copy BrowserTrackingServer.exe and config.json to your server
2. Edit config.json to set your server URL and API token
3. Run BrowserTrackingServer.exe

### Client Deployment:
1. Copy BrowserTrackingInstaller.exe to target PC
2. Run BrowserTrackingInstaller.exe as administrator
3. The installer will:
   - Install Python if needed
   - Install the tracking agent
   - Configure automatic startup

## Configuration:
Edit config.json before deployment:
- Set server_url to your server's address
- Set api_token for authentication
- Adjust check_interval for data collection frequency

## Security:
- Use HTTPS in production
- Change default API token
- Restrict server access to internal network only
"""
    
    readme_path = os.path.join(dist_dir, 'README.txt')
    with open(readme_path, 'w') as f:
        f.write(readme_content)
    
    print(f"\nDistribution package created in: {dist_dir}")
    print("Contents:")
    for item in os.listdir(dist_dir):
        print(f"  - {item}")

def main():
    """Main build process"""
    print("=== Browser Tracking System Build Process ===\n")
    
    # Check if PyInstaller is available
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller not found. Installing...")
        import subprocess
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
    
    # Build all components
    try:
        build_agent()
        print()
        
        build_installer()
        print()
        
        build_server()
        print()
        
        create_distribution_package()
        
        print("\n=== Build Process Complete ===")
        print("All executables have been created successfully!")
        
    except Exception as e:
        print(f"Build failed: {e}")
        return False
    
    return True

if __name__ == '__main__':
    success = main()
    input("\nPress Enter to exit...")
    sys.exit(0 if success else 1)
