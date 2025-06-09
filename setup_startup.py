"""
Setup Browser Tracking Agent for Windows Startup
Creates scheduled tasks and startup entries
"""

import os
import sys
import subprocess
import winreg
import json

class StartupManager:
    def __init__(self):
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.agent_dir = os.path.join(self.current_dir, "vercel_client_configs")
        self.agent_script = os.path.join(self.agent_dir, "enhanced_agent.py")
        self.gui_script = os.path.join(self.current_dir, "simple_gui.py")
        
    def create_scheduled_task_agent(self):
        """Create scheduled task for agent to run at startup"""
        try:
            task_name = "BrowserTrackingAgent"
            python_exe = sys.executable
            
            # Remove existing task if exists
            subprocess.run(f'schtasks /delete /tn "{task_name}" /f', 
                         shell=True, capture_output=True)
            
            # Create new task
            cmd = f'''schtasks /create /tn "{task_name}" /tr "\\"{python_exe}\\" \\"{self.agent_script}\\" --start" /sc onlogon /ru "%USERNAME%" /rl limited /f'''
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✓ Agent scheduled task created successfully")
                return True
            else:
                print(f"✗ Failed to create agent task: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"✗ Error creating agent task: {e}")
            return False
    
    def create_scheduled_task_gui(self):
        """Create scheduled task for GUI to run at startup"""
        try:
            task_name = "BrowserTrackingGUI"
            python_exe = sys.executable
            
            # Remove existing task if exists
            subprocess.run(f'schtasks /delete /tn "{task_name}" /f', 
                         shell=True, capture_output=True)
            
            # Create new task (delayed start)
            cmd = f'''schtasks /create /tn "{task_name}" /tr "\\"{python_exe}\\" \\"{self.gui_script}\\"" /sc onlogon /ru "%USERNAME%" /rl limited /delay 0001:00 /f'''
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✓ GUI scheduled task created successfully")
                return True
            else:
                print(f"✗ Failed to create GUI task: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"✗ Error creating GUI task: {e}")
            return False
    
    def add_to_registry_startup(self):
        """Add GUI to Windows registry startup"""
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                               r"Software\Microsoft\Windows\CurrentVersion\Run", 
                               0, winreg.KEY_SET_VALUE)
            
            python_exe = sys.executable
            startup_command = f'"{python_exe}" "{self.gui_script}"'
            
            winreg.SetValueEx(key, "BrowserTrackingGUI", 0, winreg.REG_SZ, startup_command)
            winreg.CloseKey(key)
            
            print("✓ GUI added to Windows startup registry")
            return True
            
        except Exception as e:
            print(f"✗ Error adding to registry: {e}")
            return False
    
    def create_startup_batch(self):
        """Create startup batch files"""
        try:
            # Agent startup batch
            agent_batch = os.path.join(self.current_dir, "start_agent_background.bat")
            agent_content = f'''@echo off
cd /d "{self.agent_dir}"
start /min "{sys.executable}" enhanced_agent.py --start
'''
            with open(agent_batch, 'w') as f:
                f.write(agent_content)
            
            # GUI startup batch
            gui_batch = os.path.join(self.current_dir, "start_gui_background.bat")
            gui_content = f'''@echo off
timeout /t 30 /nobreak >nul
cd /d "{self.current_dir}"
start /min "{sys.executable}" simple_gui.py
'''
            with open(gui_batch, 'w') as f:
                f.write(gui_content)
            
            print("✓ Startup batch files created")
            return True
            
        except Exception as e:
            print(f"✗ Error creating batch files: {e}")
            return False
    
    def create_agent_service_script(self):
        """Create persistent agent service script"""
        service_script = os.path.join(self.current_dir, "agent_service.py")
        
        service_content = '''"""
Browser Tracking Agent Service
Runs continuously in background and restarts if crashed
"""

import subprocess
import time
import os
import sys
from datetime import datetime

class AgentService:
    def __init__(self):
        self.agent_dir = os.path.join(os.path.dirname(__file__), "vercel_client_configs")
        self.agent_script = os.path.join(self.agent_dir, "enhanced_agent.py")
        self.running = True
        self.process = None
        
    def log(self, message):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")
        
        # Also log to file
        try:
            log_file = os.path.join(self.agent_dir, "service.log")
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] {message}\\n")
        except:
            pass
    
    def start_agent(self):
        """Start the agent process"""
        try:
            self.log("Starting agent process...")
            self.process = subprocess.Popen(
                [sys.executable, self.agent_script, "--start"],
                cwd=self.agent_dir,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            self.log(f"Agent started with PID: {self.process.pid}")
            return True
        except Exception as e:
            self.log(f"Error starting agent: {e}")
            return False
    
    def check_agent(self):
        """Check if agent is still running"""
        if self.process is None:
            return False
        
        poll = self.process.poll()
        if poll is None:
            return True  # Still running
        else:
            self.log(f"Agent process exited with code: {poll}")
            return False
    
    def run_service(self):
        """Main service loop"""
        self.log("Agent service started")
        
        while self.running:
            try:
                # Check if agent is running
                if not self.check_agent():
                    self.log("Agent not running, attempting to start...")
                    if self.start_agent():
                        self.log("Agent restarted successfully")
                    else:
                        self.log("Failed to restart agent, will retry in 60 seconds")
                
                # Wait before next check
                time.sleep(60)  # Check every minute
                
            except KeyboardInterrupt:
                self.log("Service interrupted by user")
                self.running = False
            except Exception as e:
                self.log(f"Service error: {e}")
                time.sleep(60)
        
        # Cleanup
        if self.process and self.process.poll() is None:
            self.log("Stopping agent process...")
            self.process.terminate()
        
        self.log("Agent service stopped")

if __name__ == "__main__":
    service = AgentService()
    service.run_service()
'''
        
        try:
            with open(service_script, 'w', encoding='utf-8') as f:
                f.write(service_content)
            print("✓ Agent service script created")
            return True
        except Exception as e:
            print(f"✗ Error creating service script: {e}")
            return False
    
    def setup_all(self):
        """Setup all startup methods"""
        print("Setting up Browser Tracking Agent for Windows startup...")
        print("=" * 60)
        
        success_count = 0
        total_count = 5
        
        # 1. Create scheduled tasks
        if self.create_scheduled_task_agent():
            success_count += 1
        
        if self.create_scheduled_task_gui():
            success_count += 1
        
        # 2. Add to registry startup
        if self.add_to_registry_startup():
            success_count += 1
        
        # 3. Create batch files
        if self.create_startup_batch():
            success_count += 1
        
        # 4. Create service script
        if self.create_agent_service_script():
            success_count += 1
        
        print("=" * 60)
        print(f"Setup completed: {success_count}/{total_count} items successful")
        
        if success_count >= 3:
            print("✓ Startup setup successful!")
            print("\nThe agent will now:")
            print("  • Start automatically when Windows boots")
            print("  • Run in background continuously")
            print("  • Restart automatically if crashed")
            print("  • GUI will start 1 minute after login")
        else:
            print("⚠ Partial setup completed. Some features may not work.")
        
        return success_count >= 3
    
    def remove_all(self):
        """Remove all startup entries"""
        print("Removing Browser Tracking Agent from Windows startup...")
        print("=" * 60)
        
        # Remove scheduled tasks
        subprocess.run('schtasks /delete /tn "BrowserTrackingAgent" /f', 
                     shell=True, capture_output=True)
        subprocess.run('schtasks /delete /tn "BrowserTrackingGUI" /f', 
                     shell=True, capture_output=True)
        
        # Remove from registry
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                               r"Software\Microsoft\Windows\CurrentVersion\Run", 
                               0, winreg.KEY_SET_VALUE)
            winreg.DeleteValue(key, "BrowserTrackingGUI")
            winreg.CloseKey(key)
        except:
            pass
        
        print("✓ Startup entries removed")

def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--remove":
        manager = StartupManager()
        manager.remove_all()
    else:
        manager = StartupManager()
        manager.setup_all()
        
        print("\nNext steps:")
        print("1. Restart your computer to test startup")
        print("2. Or run 'Launch GUI.bat' to start manually")
        print("3. Use GUI to control agent start/stop")
        print("\nTo remove startup: python setup_startup.py --remove")

if __name__ == "__main__":
    main()
