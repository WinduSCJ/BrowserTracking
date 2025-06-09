import os
import sys
import subprocess
import urllib.request
import tempfile
import shutil
from pathlib import Path

class PythonInstaller:
    def __init__(self):
        self.python_version = "3.11.7"
        self.python_url = f"https://www.python.org/ftp/python/{self.python_version}/python-{self.python_version}-amd64.exe"
        self.install_dir = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'BrowserTracking')
    
    def check_python(self):
        """Check if Python is already installed"""
        try:
            result = subprocess.run([sys.executable, '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"Python already installed: {result.stdout.strip()}")
                return True
        except:
            pass
        
        # Try common Python paths
        python_paths = [
            'python',
            'python3',
            'py',
            r'C:\Python311\python.exe',
            r'C:\Python310\python.exe',
            r'C:\Python39\python.exe'
        ]
        
        for python_path in python_paths:
            try:
                result = subprocess.run([python_path, '--version'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"Found Python: {result.stdout.strip()}")
                    return python_path
            except:
                continue
        
        return False
    
    def download_python(self):
        """Download Python installer"""
        print(f"Downloading Python {self.python_version}...")
        
        temp_dir = tempfile.gettempdir()
        installer_path = os.path.join(temp_dir, f"python-{self.python_version}-installer.exe")
        
        try:
            urllib.request.urlretrieve(self.python_url, installer_path)
            print(f"Downloaded Python installer to: {installer_path}")
            return installer_path
        except Exception as e:
            print(f"Error downloading Python: {e}")
            return None
    
    def install_python(self, installer_path):
        """Install Python silently"""
        print("Installing Python...")
        
        install_cmd = [
            installer_path,
            '/quiet',
            'InstallAllUsers=0',
            'PrependPath=1',
            'Include_test=0',
            'Include_doc=0',
            'Include_dev=0',
            'Include_debug=0',
            'Include_launcher=1',
            'InstallLauncherAllUsers=0'
        ]
        
        try:
            result = subprocess.run(install_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print("Python installed successfully")
                return True
            else:
                print(f"Python installation failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"Error installing Python: {e}")
            return False
    
    def install_dependencies(self, python_exe=None):
        """Install required Python packages"""
        if not python_exe:
            python_exe = sys.executable
        
        print("Installing dependencies...")
        
        packages = [
            'flask==2.3.3',
            'flask-cors==4.0.0',
            'requests==2.31.0',
            'psutil==5.9.6',
            'pywin32==306',
            'schedule==1.2.0',
            'cryptography==41.0.7'
        ]
        
        for package in packages:
            try:
                print(f"Installing {package}...")
                result = subprocess.run([python_exe, '-m', 'pip', 'install', package], 
                                      capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"Warning: Failed to install {package}: {result.stderr}")
            except Exception as e:
                print(f"Error installing {package}: {e}")
    
    def setup_installation_directory(self):
        """Create installation directory and copy files"""
        print(f"Setting up installation directory: {self.install_dir}")
        
        try:
            os.makedirs(self.install_dir, exist_ok=True)
            
            # List of files to copy
            files_to_copy = [
                'agent.py',
                'browser_reader.py',
                'system_info.py',
                'network_client.py',
                'logger.py',
                'config.json'
            ]
            
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            for file_name in files_to_copy:
                src_path = os.path.join(current_dir, file_name)
                dst_path = os.path.join(self.install_dir, file_name)
                
                if os.path.exists(src_path):
                    shutil.copy2(src_path, dst_path)
                    print(f"Copied {file_name}")
                else:
                    print(f"Warning: {file_name} not found")
            
            return True
            
        except Exception as e:
            print(f"Error setting up installation directory: {e}")
            return False
    
    def create_startup_script(self):
        """Create startup script"""
        startup_script = os.path.join(self.install_dir, 'start_agent.bat')
        
        script_content = f'''@echo off
cd /d "{self.install_dir}"
python agent.py --daemon
'''
        
        try:
            with open(startup_script, 'w') as f:
                f.write(script_content)
            print(f"Created startup script: {startup_script}")
            return startup_script
        except Exception as e:
            print(f"Error creating startup script: {e}")
            return None
    
    def add_to_startup(self, script_path):
        """Add to Windows startup"""
        try:
            startup_folder = os.path.join(
                os.environ['APPDATA'], 
                'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup'
            )
            
            startup_link = os.path.join(startup_folder, 'BrowserTrackingAgent.bat')
            shutil.copy2(script_path, startup_link)
            
            print(f"Added to startup: {startup_link}")
            return True
            
        except Exception as e:
            print(f"Error adding to startup: {e}")
            return False
    
    def install(self):
        """Main installation process"""
        print("=== Browser Tracking Agent Installer ===")
        
        # Check if Python is installed
        python_exe = self.check_python()
        
        if not python_exe:
            print("Python not found. Installing Python...")
            
            # Download Python installer
            installer_path = self.download_python()
            if not installer_path:
                print("Failed to download Python installer")
                return False
            
            # Install Python
            if not self.install_python(installer_path):
                print("Failed to install Python")
                return False
            
            # Clean up installer
            try:
                os.remove(installer_path)
            except:
                pass
            
            # Use default Python path after installation
            python_exe = 'python'
        
        # Install dependencies
        self.install_dependencies(python_exe if isinstance(python_exe, str) else None)
        
        # Setup installation directory
        if not self.setup_installation_directory():
            print("Failed to setup installation directory")
            return False
        
        # Create startup script
        startup_script = self.create_startup_script()
        if not startup_script:
            print("Failed to create startup script")
            return False
        
        # Add to startup
        if self.add_to_startup(startup_script):
            print("Successfully added to startup")
        else:
            print("Warning: Could not add to startup automatically")
        
        print("\n=== Installation Complete ===")
        print(f"Installation directory: {self.install_dir}")
        print("The agent will start automatically on next boot.")
        print("To start now, run the startup script or restart your computer.")
        
        return True

def main():
    installer = PythonInstaller()
    success = installer.install()
    
    if success:
        print("\nInstallation completed successfully!")
    else:
        print("\nInstallation failed!")
    
    input("Press Enter to exit...")

if __name__ == '__main__':
    main()
