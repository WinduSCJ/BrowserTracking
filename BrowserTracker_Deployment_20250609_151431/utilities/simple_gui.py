"""
Simple Browser Tracking Agent GUI
Lightweight interface for controlling the agent
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import threading
import os
import webbrowser
import winreg
import sys
import json
from datetime import datetime

class SimpleAgentGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Browser Tracking Agent")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Agent configuration
        self.agent_dir = os.path.join(os.path.dirname(__file__), "vercel_client_configs")
        self.agent_script = os.path.join(self.agent_dir, "enhanced_agent.py")
        
        # Create GUI
        self.create_widgets()

        # Auto-start agent if enabled
        self.auto_start_agent()

        # Initial status check
        self.check_status()
    
    def create_widgets(self):
        """Create GUI widgets"""
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Browser Tracking Agent Control", 
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_label = ttk.Label(status_frame, text="Status: Checking...", 
                                     font=('Arial', 10, 'bold'))
        self.status_label.pack()
        
        # Control buttons frame
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Button grid
        button_frame = ttk.Frame(control_frame)
        button_frame.pack()
        
        # Row 1
        self.start_btn = ttk.Button(button_frame, text="Start Agent", 
                                   command=self.start_agent, width=12)
        self.start_btn.grid(row=0, column=0, padx=5, pady=5)
        
        self.stop_btn = ttk.Button(button_frame, text="Stop Agent", 
                                  command=self.stop_agent, width=12)
        self.stop_btn.grid(row=0, column=1, padx=5, pady=5)
        
        self.test_btn = ttk.Button(button_frame, text="Test Connection", 
                                  command=self.test_connection, width=12)
        self.test_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # Row 2
        self.once_btn = ttk.Button(button_frame, text="Run Once", 
                                  command=self.run_once, width=12)
        self.once_btn.grid(row=1, column=0, padx=5, pady=5)
        
        self.status_btn = ttk.Button(button_frame, text="Check Status", 
                                    command=self.check_status, width=12)
        self.status_btn.grid(row=1, column=1, padx=5, pady=5)
        
        self.dashboard_btn = ttk.Button(button_frame, text="Open Dashboard", 
                                       command=self.open_dashboard, width=12)
        self.dashboard_btn.grid(row=1, column=2, padx=5, pady=5)
        
        # Log frame
        log_frame = ttk.LabelFrame(main_frame, text="Activity Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Log text area
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=70)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Bottom frame
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X)
        
        # Settings frame
        settings_frame = ttk.LabelFrame(main_frame, text="Startup Settings", padding="5")
        settings_frame.pack(fill=tk.X, pady=(0, 10))

        # Auto-start checkboxes
        self.auto_start_gui_var = tk.BooleanVar()
        self.auto_start_agent_var = tk.BooleanVar()

        ttk.Checkbutton(settings_frame, text="Start GUI on Windows startup",
                       variable=self.auto_start_gui_var,
                       command=self.toggle_gui_startup).pack(anchor=tk.W)

        ttk.Checkbutton(settings_frame, text="Auto-start agent when GUI opens",
                       variable=self.auto_start_agent_var,
                       command=self.toggle_agent_autostart).pack(anchor=tk.W)

        # Load current settings
        self.load_startup_settings()

        ttk.Button(bottom_frame, text="Clear Log",
                  command=self.clear_log).pack(side=tk.LEFT)

        ttk.Button(bottom_frame, text="Minimize to Tray",
                  command=self.minimize_to_tray).pack(side=tk.LEFT, padx=(10, 0))

        ttk.Button(bottom_frame, text="Exit",
                  command=self.exit_app).pack(side=tk.RIGHT)
        
        # Initial log message
        self.log_message("GUI started. Ready to control Browser Tracking Agent.")
    
    def log_message(self, message):
        """Add message to log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        
        # Keep only last 500 lines
        lines = self.log_text.get("1.0", tk.END).split('\n')
        if len(lines) > 500:
            self.log_text.delete("1.0", f"{len(lines)-500}.0")
    
    def run_command(self, command, show_output=True):
        """Run agent command"""
        try:
            if not os.path.exists(self.agent_script):
                self.log_message(f"ERROR: Agent script not found: {self.agent_script}")
                return False
            
            cmd = ["python", self.agent_script, command]
            
            result = subprocess.run(cmd, cwd=self.agent_dir, capture_output=True, 
                                  text=True, timeout=30)
            
            if show_output and result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        self.log_message(line)
            
            if result.stderr:
                self.log_message(f"ERROR: {result.stderr}")
            
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            self.log_message("ERROR: Command timed out")
            return False
        except Exception as e:
            self.log_message(f"ERROR: {e}")
            return False
    
    def start_agent(self):
        """Start the agent"""
        self.log_message("Starting agent...")
        self.start_btn.config(state='disabled')
        
        def start_thread():
            try:
                # Start agent in background
                subprocess.Popen(["python", self.agent_script, "--start"], 
                               cwd=self.agent_dir, 
                               creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
                
                self.log_message("Agent start command sent")
                self.root.after(2000, self.check_status)  # Check status after 2 seconds
                
            except Exception as e:
                self.log_message(f"ERROR: Failed to start agent: {e}")
            finally:
                self.start_btn.config(state='normal')
        
        threading.Thread(target=start_thread, daemon=True).start()
    
    def stop_agent(self):
        """Stop the agent"""
        self.log_message("Stopping agent...")
        self.stop_btn.config(state='disabled')
        
        def stop_thread():
            try:
                success = self.run_command("--stop", show_output=False)
                if success:
                    self.log_message("Agent stopped successfully")
                else:
                    self.log_message("Stop command completed")
                
                self.root.after(1000, self.check_status)  # Check status after 1 second
                
            except Exception as e:
                self.log_message(f"ERROR: {e}")
            finally:
                self.stop_btn.config(state='normal')
        
        threading.Thread(target=stop_thread, daemon=True).start()
    
    def test_connection(self):
        """Test server connection"""
        self.log_message("Testing server connection...")
        self.test_btn.config(state='disabled')
        
        def test_thread():
            try:
                success = self.run_command("--test")
                if success:
                    self.log_message("Connection test completed")
                else:
                    self.log_message("Connection test failed")
                    
            except Exception as e:
                self.log_message(f"ERROR: {e}")
            finally:
                self.test_btn.config(state='normal')
        
        threading.Thread(target=test_thread, daemon=True).start()
    
    def run_once(self):
        """Run one-time data collection"""
        self.log_message("Running one-time data collection...")
        self.once_btn.config(state='disabled')
        
        def once_thread():
            try:
                success = self.run_command("--once")
                if success:
                    self.log_message("One-time collection completed")
                else:
                    self.log_message("One-time collection failed")
                    
            except Exception as e:
                self.log_message(f"ERROR: {e}")
            finally:
                self.once_btn.config(state='normal')
        
        threading.Thread(target=once_thread, daemon=True).start()
    
    def check_status(self):
        """Check agent status"""
        def status_thread():
            try:
                # Get agent status
                result = subprocess.run(["python", self.agent_script, "--status"], 
                                      cwd=self.agent_dir, capture_output=True, 
                                      text=True, timeout=10)
                
                if "running" in result.stdout.lower():
                    self.status_label.config(text="Status: RUNNING", foreground='green')
                elif "stopped" in result.stdout.lower():
                    self.status_label.config(text="Status: STOPPED", foreground='red')
                else:
                    self.status_label.config(text="Status: UNKNOWN", foreground='orange')
                
            except Exception as e:
                self.status_label.config(text="Status: ERROR", foreground='red')
                self.log_message(f"ERROR checking status: {e}")
        
        threading.Thread(target=status_thread, daemon=True).start()
    
    def open_dashboard(self):
        """Open web dashboard"""
        try:
            webbrowser.open("https://browser-tracking.vercel.app")
            self.log_message("Dashboard opened in browser")
        except Exception as e:
            self.log_message(f"ERROR opening dashboard: {e}")
    
    def clear_log(self):
        """Clear the log"""
        self.log_text.delete(1.0, tk.END)
        self.log_message("Log cleared")
    
    def load_startup_settings(self):
        """Load startup settings from registry"""
        try:
            # Check if GUI is set to start on Windows startup
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                               r"Software\Microsoft\Windows\CurrentVersion\Run",
                               0, winreg.KEY_READ)
            try:
                winreg.QueryValueEx(key, "BrowserTrackingGUI")
                self.auto_start_gui_var.set(True)
            except FileNotFoundError:
                self.auto_start_gui_var.set(False)
            winreg.CloseKey(key)

            # Check agent auto-start setting (from file)
            settings_file = os.path.join(self.agent_dir, "gui_settings.json")
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    self.auto_start_agent_var.set(settings.get('auto_start_agent', False))

        except Exception as e:
            self.log_message(f"Error loading startup settings: {e}")

    def save_agent_setting(self, auto_start):
        """Save agent auto-start setting to file"""
        try:
            settings_file = os.path.join(self.agent_dir, "gui_settings.json")
            settings = {'auto_start_agent': auto_start}
            with open(settings_file, 'w') as f:
                json.dump(settings, f)
        except Exception as e:
            self.log_message(f"Error saving agent setting: {e}")

    def toggle_gui_startup(self):
        """Toggle GUI startup with Windows"""
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                               r"Software\Microsoft\Windows\CurrentVersion\Run",
                               0, winreg.KEY_SET_VALUE)

            if self.auto_start_gui_var.get():
                # Add to startup
                gui_path = os.path.abspath(__file__)
                python_path = sys.executable
                startup_command = f'"{python_path}" "{gui_path}"'
                winreg.SetValueEx(key, "BrowserTrackingGUI", 0, winreg.REG_SZ, startup_command)
                self.log_message("GUI added to Windows startup")
            else:
                # Remove from startup
                try:
                    winreg.DeleteValue(key, "BrowserTrackingGUI")
                    self.log_message("GUI removed from Windows startup")
                except FileNotFoundError:
                    pass

            winreg.CloseKey(key)

        except Exception as e:
            self.log_message(f"Error managing GUI startup: {e}")
            # Revert checkbox if failed
            self.auto_start_gui_var.set(not self.auto_start_gui_var.get())

    def toggle_agent_autostart(self):
        """Toggle agent auto-start when GUI opens"""
        auto_start = self.auto_start_agent_var.get()
        self.save_agent_setting(auto_start)

        if auto_start:
            self.log_message("Agent will auto-start when GUI opens")
        else:
            self.log_message("Agent auto-start disabled")

    def auto_start_agent(self):
        """Auto-start agent if enabled"""
        try:
            settings_file = os.path.join(self.agent_dir, "gui_settings.json")
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    if settings.get('auto_start_agent', False):
                        self.log_message("Auto-starting agent...")
                        self.start_agent()
        except Exception as e:
            self.log_message(f"Error in auto-start: {e}")

    def minimize_to_tray(self):
        """Minimize GUI to system tray (hide window)"""
        self.root.withdraw()  # Hide window
        self.log_message("GUI minimized. Agent continues running in background.")

        # Show notification
        try:
            import win10toast
            toaster = win10toast.ToastNotifier()
            toaster.show_toast("Browser Tracking Agent",
                             "GUI minimized. Agent running in background.",
                             duration=3)
        except:
            pass

    def restore_from_tray(self):
        """Restore GUI from system tray"""
        self.root.deiconify()  # Show window
        self.root.lift()       # Bring to front
        self.check_status()    # Refresh status

    def exit_app(self):
        """Exit the application"""
        result = messagebox.askyesnocancel(
            "Exit Options",
            "What would you like to do?\n\n"
            "Yes: Exit GUI only (agent continues in background)\n"
            "No: Exit GUI and stop agent\n"
            "Cancel: Return to GUI"
        )

        if result is True:  # Yes - Exit GUI only
            self.log_message("Exiting GUI. Agent continues in background.")
            self.root.quit()
        elif result is False:  # No - Exit GUI and stop agent
            self.log_message("Stopping agent and exiting GUI...")
            self.stop_agent()
            self.root.after(2000, self.root.quit)  # Wait 2 seconds then quit

def main():
    """Main function"""
    root = tk.Tk()
    app = SimpleAgentGUI(root)
    
    # Center window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()
