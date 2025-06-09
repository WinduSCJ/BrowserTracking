import os
import sys
import subprocess
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json

class BrowserTrackingManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Browser Tracking System Manager")
        self.root.geometry("800x600")
        
        self.server_process = None
        self.monitor_process = None
        
        self.setup_ui()
        self.check_dependencies()
    
    def setup_ui(self):
        """Setup user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Browser Tracking System Manager", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # Control buttons frame
        control_frame = ttk.LabelFrame(main_frame, text="System Control", padding="10")
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        control_frame.columnconfigure(0, weight=1)
        
        # Server controls
        server_frame = ttk.Frame(control_frame)
        server_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(server_frame, text="Server:").pack(side=tk.LEFT)
        self.server_btn = ttk.Button(server_frame, text="Start Server", 
                                    command=self.toggle_server)
        self.server_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        self.server_status = ttk.Label(server_frame, text="Stopped", foreground="red")
        self.server_status.pack(side=tk.LEFT, padx=(10, 0))
        
        # Monitor controls
        monitor_frame = ttk.Frame(control_frame)
        monitor_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(monitor_frame, text="Monitor:").pack(side=tk.LEFT)
        self.monitor_btn = ttk.Button(monitor_frame, text="Start Monitor", 
                                     command=self.toggle_monitor)
        self.monitor_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        self.monitor_status = ttk.Label(monitor_frame, text="Stopped", foreground="red")
        self.monitor_status.pack(side=tk.LEFT, padx=(10, 0))
        
        # Tools frame
        tools_frame = ttk.LabelFrame(main_frame, text="Tools", padding="10")
        tools_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        tools_buttons = [
            ("Test System", self.test_system),
            ("Build Executables", self.build_executables),
            ("Open Config", self.open_config),
            ("View Database", self.view_database),
            ("Clear Logs", self.clear_logs)
        ]
        
        for i, (text, command) in enumerate(tools_buttons):
            btn = ttk.Button(tools_frame, text=text, command=command)
            btn.grid(row=i//3, column=i%3, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # Configure grid weights for tools frame
        for i in range(3):
            tools_frame.columnconfigure(i, weight=1)
        
        # Log frame
        log_frame = ttk.LabelFrame(main_frame, text="System Log", padding="10")
        log_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=15)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Clear log button
        clear_log_btn = ttk.Button(log_frame, text="Clear Log", command=self.clear_log_display)
        clear_log_btn.grid(row=1, column=0, pady=(5, 0))
    
    def log_message(self, message):
        """Add message to log display"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def clear_log_display(self):
        """Clear log display"""
        self.log_text.delete(1.0, tk.END)
    
    def check_dependencies(self):
        """Check if all dependencies are available"""
        self.log_message("Checking dependencies...")
        
        required_files = [
            'server.py', 'agent.py', 'database.py', 'browser_reader.py',
            'system_info.py', 'network_client.py', 'logger.py', 'config.json'
        ]
        
        missing_files = []
        for file in required_files:
            if not os.path.exists(file):
                missing_files.append(file)
        
        if missing_files:
            self.log_message(f"Missing files: {', '.join(missing_files)}")
            messagebox.showerror("Missing Files", 
                               f"Required files missing:\n{chr(10).join(missing_files)}")
        else:
            self.log_message("All required files found")
        
        # Check Python packages
        try:
            import flask, requests, psutil
            self.log_message("Required Python packages available")
        except ImportError as e:
            self.log_message(f"Missing Python package: {e}")
            messagebox.showwarning("Missing Packages", 
                                 "Some Python packages are missing. Run: pip install -r requirements.txt")
    
    def toggle_server(self):
        """Start/stop server"""
        if self.server_process is None:
            self.start_server()
        else:
            self.stop_server()
    
    def start_server(self):
        """Start the server"""
        try:
            self.log_message("Starting server...")
            self.server_process = subprocess.Popen([sys.executable, 'server.py'],
                                                  stdout=subprocess.PIPE,
                                                  stderr=subprocess.PIPE,
                                                  text=True)
            
            self.server_btn.config(text="Stop Server")
            self.server_status.config(text="Running", foreground="green")
            self.log_message("Server started successfully")
            
            # Start monitoring server output
            threading.Thread(target=self.monitor_server_output, daemon=True).start()
            
        except Exception as e:
            self.log_message(f"Failed to start server: {e}")
            messagebox.showerror("Error", f"Failed to start server: {e}")
    
    def stop_server(self):
        """Stop the server"""
        if self.server_process:
            self.log_message("Stopping server...")
            self.server_process.terminate()
            self.server_process.wait()
            self.server_process = None
            
            self.server_btn.config(text="Start Server")
            self.server_status.config(text="Stopped", foreground="red")
            self.log_message("Server stopped")
    
    def monitor_server_output(self):
        """Monitor server output"""
        if self.server_process:
            for line in iter(self.server_process.stdout.readline, ''):
                if line:
                    self.root.after(0, lambda l=line.strip(): self.log_message(f"Server: {l}"))
                if self.server_process.poll() is not None:
                    break
    
    def toggle_monitor(self):
        """Start/stop monitor GUI"""
        if self.monitor_process is None:
            self.start_monitor()
        else:
            self.stop_monitor()
    
    def start_monitor(self):
        """Start monitor GUI"""
        try:
            self.log_message("Starting monitor GUI...")
            self.monitor_process = subprocess.Popen([sys.executable, 'monitor_gui.py'])
            
            self.monitor_btn.config(text="Stop Monitor")
            self.monitor_status.config(text="Running", foreground="green")
            self.log_message("Monitor GUI started")
            
        except Exception as e:
            self.log_message(f"Failed to start monitor: {e}")
            messagebox.showerror("Error", f"Failed to start monitor: {e}")
    
    def stop_monitor(self):
        """Stop monitor GUI"""
        if self.monitor_process:
            self.log_message("Stopping monitor GUI...")
            self.monitor_process.terminate()
            self.monitor_process = None
            
            self.monitor_btn.config(text="Start Monitor")
            self.monitor_status.config(text="Stopped", foreground="red")
            self.log_message("Monitor GUI stopped")
    
    def test_system(self):
        """Run system tests"""
        self.log_message("Running system tests...")
        try:
            result = subprocess.run([sys.executable, 'test_system.py'], 
                                  capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                self.log_message("System tests completed successfully")
            else:
                self.log_message(f"System tests failed: {result.stderr}")
            
            # Show detailed results in a new window
            self.show_test_results(result.stdout)
            
        except Exception as e:
            self.log_message(f"Error running tests: {e}")
            messagebox.showerror("Error", f"Error running tests: {e}")
    
    def show_test_results(self, results):
        """Show test results in a new window"""
        results_window = tk.Toplevel(self.root)
        results_window.title("Test Results")
        results_window.geometry("600x400")
        
        text_widget = scrolledtext.ScrolledText(results_window, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(1.0, results)
    
    def build_executables(self):
        """Build executables"""
        self.log_message("Building executables...")
        try:
            result = subprocess.run([sys.executable, 'build_exe.py'], 
                                  capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                self.log_message("Executables built successfully")
                messagebox.showinfo("Success", "Executables built successfully!\nCheck the 'dist' folder.")
            else:
                self.log_message(f"Build failed: {result.stderr}")
                messagebox.showerror("Build Failed", f"Build failed:\n{result.stderr}")
                
        except Exception as e:
            self.log_message(f"Error building executables: {e}")
            messagebox.showerror("Error", f"Error building executables: {e}")
    
    def open_config(self):
        """Open configuration file"""
        try:
            if os.name == 'nt':  # Windows
                os.startfile('config.json')
            else:  # Linux/Mac
                subprocess.run(['xdg-open', 'config.json'])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open config file: {e}")
    
    def view_database(self):
        """View database contents"""
        try:
            from database import BrowserTrackingDB
            db = BrowserTrackingDB()
            activity = db.get_recent_activity(24, 100)
            
            # Show in new window
            db_window = tk.Toplevel(self.root)
            db_window.title("Database Contents")
            db_window.geometry("800x600")
            
            text_widget = scrolledtext.ScrolledText(db_window, wrap=tk.WORD)
            text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            content = f"Recent Activity ({len(activity)} entries):\n\n"
            for entry in activity[:50]:  # Show first 50
                content += f"Time: {entry['visit_time']}\n"
                content += f"Host: {entry['hostname']} | User: {entry['username']}\n"
                content += f"URL: {entry['url']}\n"
                content += f"Title: {entry['title']}\n"
                content += "-" * 50 + "\n"
            
            text_widget.insert(1.0, content)
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not view database: {e}")
    
    def clear_logs(self):
        """Clear log files"""
        try:
            log_files = ['browser_tracking.log']
            for log_file in log_files:
                if os.path.exists(log_file):
                    os.remove(log_file)
            
            self.log_message("Log files cleared")
            messagebox.showinfo("Success", "Log files cleared successfully")
            
        except Exception as e:
            self.log_message(f"Error clearing logs: {e}")
            messagebox.showerror("Error", f"Error clearing logs: {e}")
    
    def on_closing(self):
        """Handle window closing"""
        if self.server_process or self.monitor_process:
            if messagebox.askokcancel("Quit", "Stop all processes and quit?"):
                self.stop_server()
                self.stop_monitor()
                self.root.destroy()
        else:
            self.root.destroy()

def main():
    root = tk.Tk()
    app = BrowserTrackingManager(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == '__main__':
    main()
