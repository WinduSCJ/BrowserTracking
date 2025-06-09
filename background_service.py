"""
Background Service for Browser Tracking Agent
Ensures agent runs continuously and restarts if needed
"""

import subprocess
import time
import os
import sys
import json
import threading
import signal
from datetime import datetime

class BackgroundService:
    def __init__(self):
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.agent_dir = os.path.join(self.current_dir, "vercel_client_configs")
        self.agent_script = os.path.join(self.agent_dir, "enhanced_agent.py")
        self.log_file = os.path.join(self.agent_dir, "background_service.log")
        self.status_file = os.path.join(self.agent_dir, "service_status.json")
        
        self.running = True
        self.agent_process = None
        self.check_interval = 30  # Check every 30 seconds
        self.restart_count = 0
        self.max_restarts = 10
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.log(f"Received signal {signum}, shutting down service...")
        self.running = False
        self.stop_agent()
    
    def log(self, message):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        
        print(log_entry)
        
        # Write to log file
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry + "\n")
            
            # Keep log file size manageable (last 1000 lines)
            self.trim_log_file()
            
        except Exception as e:
            print(f"Error writing to log: {e}")
    
    def trim_log_file(self):
        """Keep log file to last 1000 lines"""
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                if len(lines) > 1000:
                    with open(self.log_file, 'w', encoding='utf-8') as f:
                        f.writelines(lines[-1000:])
        except:
            pass
    
    def save_status(self, status):
        """Save service status to file"""
        try:
            status_data = {
                'service_status': status,
                'agent_running': self.is_agent_running(),
                'restart_count': self.restart_count,
                'last_update': datetime.now().isoformat(),
                'pid': os.getpid()
            }
            
            with open(self.status_file, 'w') as f:
                json.dump(status_data, f, indent=2)
                
        except Exception as e:
            self.log(f"Error saving status: {e}")
    
    def is_agent_running(self):
        """Check if agent process is running"""
        if self.agent_process is None:
            return False
        
        poll = self.agent_process.poll()
        return poll is None
    
    def start_agent(self):
        """Start the agent process"""
        try:
            if self.is_agent_running():
                self.log("Agent already running")
                return True
            
            self.log("Starting agent process...")
            
            # Start agent in background
            self.agent_process = subprocess.Popen(
                [sys.executable, self.agent_script, "--start"],
                cwd=self.agent_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            self.log(f"Agent started with PID: {self.agent_process.pid}")
            self.restart_count += 1
            return True
            
        except Exception as e:
            self.log(f"Error starting agent: {e}")
            return False
    
    def stop_agent(self):
        """Stop the agent process"""
        try:
            if self.agent_process and self.is_agent_running():
                self.log("Stopping agent process...")
                
                # Try graceful stop first
                try:
                    subprocess.run([sys.executable, self.agent_script, "--stop"], 
                                 cwd=self.agent_dir, timeout=10)
                    time.sleep(2)
                except:
                    pass
                
                # Force terminate if still running
                if self.is_agent_running():
                    self.agent_process.terminate()
                    time.sleep(2)
                    
                    if self.is_agent_running():
                        self.agent_process.kill()
                
                self.log("Agent stopped")
                
        except Exception as e:
            self.log(f"Error stopping agent: {e}")
    
    def check_agent_health(self):
        """Check if agent is healthy and collecting data"""
        try:
            # Run a quick test
            result = subprocess.run(
                [sys.executable, self.agent_script, "--status"],
                cwd=self.agent_dir,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and "running" in result.stdout.lower():
                return True
            else:
                self.log("Agent health check failed")
                return False
                
        except Exception as e:
            self.log(f"Error checking agent health: {e}")
            return False
    
    def run_service(self):
        """Main service loop"""
        self.log("Background service started")
        self.save_status("running")
        
        # Initial agent start
        self.start_agent()
        
        while self.running:
            try:
                # Check if we've exceeded max restarts
                if self.restart_count > self.max_restarts:
                    self.log(f"Max restarts ({self.max_restarts}) exceeded. Stopping service.")
                    break
                
                # Check if agent is running
                if not self.is_agent_running():
                    self.log("Agent process not running, attempting restart...")
                    if self.start_agent():
                        self.log("Agent restarted successfully")
                    else:
                        self.log("Failed to restart agent")
                
                # Health check every 5 minutes
                elif self.restart_count % 10 == 0:  # Every 10 checks (5 minutes)
                    if not self.check_agent_health():
                        self.log("Agent health check failed, restarting...")
                        self.stop_agent()
                        time.sleep(5)
                        self.start_agent()
                
                # Update status
                self.save_status("running")
                
                # Wait before next check
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                self.log("Service interrupted by user")
                break
            except Exception as e:
                self.log(f"Service error: {e}")
                time.sleep(self.check_interval)
        
        # Cleanup
        self.log("Shutting down background service...")
        self.stop_agent()
        self.save_status("stopped")
        self.log("Background service stopped")
    
    def run_once(self):
        """Run agent once for testing"""
        self.log("Running agent once for testing...")
        try:
            result = subprocess.run(
                [sys.executable, self.agent_script, "--once"],
                cwd=self.agent_dir,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                self.log("Test run completed successfully")
                if result.stdout:
                    for line in result.stdout.strip().split('\n'):
                        if line.strip():
                            self.log(f"Agent: {line}")
            else:
                self.log("Test run failed")
                if result.stderr:
                    self.log(f"Error: {result.stderr}")
                    
        except Exception as e:
            self.log(f"Error in test run: {e}")

def main():
    """Main function"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        service = BackgroundService()
        
        if command == "--start":
            service.run_service()
        elif command == "--stop":
            service.stop_agent()
        elif command == "--test":
            service.run_once()
        elif command == "--status":
            try:
                with open(service.status_file, 'r') as f:
                    status = json.load(f)
                print(json.dumps(status, indent=2))
            except:
                print("Service not running or status file not found")
        else:
            print("Usage: python background_service.py [--start|--stop|--test|--status]")
    else:
        # Default: run service
        service = BackgroundService()
        service.run_service()

if __name__ == "__main__":
    main()
