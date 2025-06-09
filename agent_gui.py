"""
Browser Tracking Agent GUI
User-friendly interface for controlling the agent
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
import threading
import json
import os
import sys
from datetime import datetime
import time
import webbrowser

try:
    import pystray
    from PIL import Image, ImageDraw
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False

class AgentGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Browser Tracking Agent Control Panel")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Set icon and styling
        self.root.configure(bg='#f0f0f0')
        
        # Agent configuration
        self.agent_dir = os.path.join(os.path.dirname(__file__), "vercel_client_configs")
        self.agent_script = os.path.join(self.agent_dir, "enhanced_agent.py")
        
        # Status variables
        self.agent_status = tk.StringVar(value="Unknown")
        self.server_status = tk.StringVar(value="Unknown")
        self.last_update = tk.StringVar(value="Never")
        
        # Create GUI elements
        self.create_widgets()
        
        # Start status monitoring
        self.monitor_status()
        
    def create_widgets(self):
        """Create all GUI widgets"""
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="[SEARCH] Browser Tracking Agent", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Status Frame
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        status_frame.columnconfigure(1, weight=1)
        
        # Agent Status
        ttk.Label(status_frame, text="Agent Status:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.status_label = ttk.Label(status_frame, textvariable=self.agent_status, 
                                     font=('Arial', 10, 'bold'))
        self.status_label.grid(row=0, column=1, sticky=tk.W)
        
        # Server Status
        ttk.Label(status_frame, text="Server Status:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.server_label = ttk.Label(status_frame, textvariable=self.server_status,
                                     font=('Arial', 10, 'bold'))
        self.server_label.grid(row=1, column=1, sticky=tk.W)
        
        # Last Update
        ttk.Label(status_frame, text="Last Update:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Label(status_frame, textvariable=self.last_update).grid(row=2, column=1, sticky=tk.W)
        
        # Control Buttons Frame
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        control_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Buttons
        self.start_btn = ttk.Button(control_frame, text="[START] Start Agent", 
                                   command=self.start_agent, width=15)
        self.start_btn.grid(row=0, column=0, padx=(0, 5))
        
        self.stop_btn = ttk.Button(control_frame, text="[STOP_SIGN] Stop Agent", 
                                  command=self.stop_agent, width=15)
        self.stop_btn.grid(row=0, column=1, padx=5)
        
        self.test_btn = ttk.Button(control_frame, text="[LINK] Test Connection", 
                                  command=self.test_connection, width=15)
        self.test_btn.grid(row=0, column=2, padx=5)
        
        self.once_btn = ttk.Button(control_frame, text="[TEST] Run Once", 
                                  command=self.run_once, width=15)
        self.once_btn.grid(row=0, column=3, padx=(5, 0))
        
        # Second row of buttons
        self.refresh_btn = ttk.Button(control_frame, text="[COUNTERCLOCKWISE] Refresh Status", 
                                     command=self.refresh_status, width=15)
        self.refresh_btn.grid(row=1, column=0, padx=(0, 5), pady=(5, 0))
        
        self.dashboard_btn = ttk.Button(control_frame, text="[STATS] Open Dashboard", 
                                       command=self.open_dashboard, width=15)
        self.dashboard_btn.grid(row=1, column=1, padx=5, pady=(5, 0))
        
        self.config_btn = ttk.Button(control_frame, text="[SETTINGS] Edit Config", 
                                    command=self.edit_config, width=15)
        self.config_btn.grid(row=1, column=2, padx=5, pady=(5, 0))
        
        self.exit_btn = ttk.Button(control_frame, text="[ERROR] Exit", 
                                  command=self.exit_app, width=15)
        self.exit_btn.grid(row=1, column=3, padx=(5, 0), pady=(5, 0))
        
        # Settings Frame
        settings_frame = ttk.LabelFrame(main_frame, text="Quick Settings", padding="10")
        settings_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Auto-start checkbox
        self.auto_start_var = tk.BooleanVar()
        self.auto_start_check = ttk.Checkbutton(settings_frame, text="Auto-start agent on GUI launch",
                                               variable=self.auto_start_var,
                                               command=self.toggle_auto_start)
        self.auto_start_check.grid(row=0, column=0, sticky=tk.W)
        
        # Interval setting
        ttk.Label(settings_frame, text="Collection Interval (seconds):").grid(row=0, column=1, padx=(20, 5))
        self.interval_var = tk.StringVar(value="60")
        self.interval_entry = ttk.Entry(settings_frame, textvariable=self.interval_var, width=10)
        self.interval_entry.grid(row=0, column=2)
        
        # Log Frame
        log_frame = ttk.LabelFrame(main_frame, text="Activity Log", padding="10")
        log_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Log text area
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Clear log button
        ttk.Button(log_frame, text="Clear Log", command=self.clear_log).grid(row=1, column=0, pady=(5, 0))
        
        # Initial log message
        self.log_message("GUI started. Ready to control Browser Tracking Agent.")
        
    def log_message(self, message):
        """Add message to log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        
        # Keep only last 1000 lines
        lines = self.log_text.get("1.0", tk.END).split('\n')
        if len(lines) > 1000:
            self.log_text.delete("1.0", f"{len(lines)-1000}.0")
    
    def run_agent_command(self, command, show_output=True):
        """Run agent command and return output"""
        try:
            if not os.path.exists(self.agent_script):
                self.log_message(f"[ERROR] Agent script not found: {self.agent_script}")
                return False, "Agent script not found"
            
            cmd = ["python", self.agent_script, command]
            
            result = subprocess.run(cmd, cwd=self.agent_dir, capture_output=True, 
                                  text=True, timeout=30)
            
            if show_output and result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        self.log_message(line)
            
            if result.stderr:
                self.log_message(f"[WARNING_SIGN] Error: {result.stderr}")
            
            return result.returncode == 0, result.stdout
            
        except subprocess.TimeoutExpired:
            self.log_message("[WARNING_SIGN] Command timed out")
            return False, "Timeout"
        except Exception as e:
            self.log_message(f"[ERROR] Error running command: {e}")
            return False, str(e)
    
    def start_agent(self):
        """Start the agent"""
        self.log_message("[START] Starting agent...")
        self.start_btn.config(state='disabled')
        
        def start_thread():
            try:
                # Start agent in background
                subprocess.Popen(["python", self.agent_script, "--start"], 
                               cwd=self.agent_dir, creationflags=subprocess.CREATE_NO_WINDOW)
                
                self.log_message("[OK] Agent start command sent")
                time.sleep(2)  # Wait for agent to initialize
                self.refresh_status()
                
            except Exception as e:
                self.log_message(f"[ERROR] Failed to start agent: {e}")
            finally:
                self.start_btn.config(state='normal')
        
        threading.Thread(target=start_thread, daemon=True).start()
    
    def stop_agent(self):
        """Stop the agent"""
        self.log_message("[STOP_SIGN] Stopping agent...")
        self.stop_btn.config(state='disabled')
        
        def stop_thread():
            try:
                success, output = self.run_agent_command("--stop", show_output=False)
                if success:
                    self.log_message("[OK] Agent stopped successfully")
                else:
                    self.log_message("[WARNING_SIGN] Stop command completed with warnings")
                
                time.sleep(1)
                self.refresh_status()
                
            except Exception as e:
                self.log_message(f"[ERROR] Error stopping agent: {e}")
            finally:
                self.stop_btn.config(state='normal')
        
        threading.Thread(target=stop_thread, daemon=True).start()
    
    def test_connection(self):
        """Test server connection"""
        self.log_message("[LINK] Testing server connection...")
        self.test_btn.config(state='disabled')
        
        def test_thread():
            try:
                success, output = self.run_agent_command("--test")
                if success:
                    self.log_message("[OK] Connection test completed")
                else:
                    self.log_message("[ERROR] Connection test failed")
                    
            except Exception as e:
                self.log_message(f"[ERROR] Error testing connection: {e}")
            finally:
                self.test_btn.config(state='normal')
        
        threading.Thread(target=test_thread, daemon=True).start()
    
    def run_once(self):
        """Run one-time data collection"""
        self.log_message("[TEST] Running one-time data collection...")
        self.once_btn.config(state='disabled')
        
        def once_thread():
            try:
                success, output = self.run_agent_command("--once")
                if success:
                    self.log_message("[OK] One-time collection completed")
                else:
                    self.log_message("[ERROR] One-time collection failed")
                    
            except Exception as e:
                self.log_message(f"[ERROR] Error in one-time collection: {e}")
            finally:
                self.once_btn.config(state='normal')
        
        threading.Thread(target=once_thread, daemon=True).start()
    
    def refresh_status(self):
        """Refresh agent and server status"""
        def status_thread():
            try:
                # Get agent status
                success, output = self.run_agent_command("--status", show_output=False)
                
                if "running" in output.lower():
                    self.agent_status.set("🟢 Running")
                    self.status_label.config(foreground='green')
                elif "stopped" in output.lower():
                    self.agent_status.set("🔴 Stopped")
                    self.status_label.config(foreground='red')
                else:
                    self.agent_status.set("🟡 Unknown")
                    self.status_label.config(foreground='orange')
                
                # Test server connection
                success, output = self.run_agent_command("--test", show_output=False)
                if "online" in output.lower() or "healthy" in output.lower():
                    self.server_status.set("🟢 Online")
                    self.server_label.config(foreground='green')
                else:
                    self.server_status.set("🔴 Offline")
                    self.server_label.config(foreground='red')
                
                self.last_update.set(datetime.now().strftime("%H:%M:%S"))
                
            except Exception as e:
                self.log_message(f"[WARNING_SIGN] Error refreshing status: {e}")
        
        threading.Thread(target=status_thread, daemon=True).start()
    
    def monitor_status(self):
        """Monitor status periodically"""
        self.refresh_status()
        # Schedule next update in 30 seconds
        self.root.after(30000, self.monitor_status)
    
    def open_dashboard(self):
        """Open web dashboard"""
        try:
            import webbrowser
            webbrowser.open("https://browser-tracking.vercel.app")
            self.log_message("[STATS] Dashboard opened in browser")
        except Exception as e:
            self.log_message(f"[ERROR] Error opening dashboard: {e}")
    
    def edit_config(self):
        """Open config file for editing"""
        try:
            config_file = os.path.join(self.agent_dir, "config.json")
            if os.path.exists(config_file):
                os.startfile(config_file)
                self.log_message("[SETTINGS] Config file opened for editing")
            else:
                self.log_message("[ERROR] Config file not found")
        except Exception as e:
            self.log_message(f"[ERROR] Error opening config: {e}")
    
    def toggle_auto_start(self):
        """Toggle auto-start setting"""
        if self.auto_start_var.get():
            self.log_message("[OK] Auto-start enabled")
            # Auto-start agent if not running
            if "Stopped" in self.agent_status.get():
                self.start_agent()
        else:
            self.log_message("[INFO] Auto-start disabled")
    
    def clear_log(self):
        """Clear the log"""
        self.log_text.delete(1.0, tk.END)
        self.log_message("Log cleared")
    
    def exit_app(self):
        """Exit the application"""
        if messagebox.askyesno("Exit", "Do you want to exit the GUI?\n\n(Agent will continue running in background)"):
            self.root.quit()

def main():
    """Main function"""
    root = tk.Tk()
    app = AgentGUI(root)
    
    # Center window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()
