"""
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
                f.write(f"[{timestamp}] {message}\n")
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
