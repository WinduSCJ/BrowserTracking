import sqlite3
import json
from datetime import datetime
from logger import setup_logger

logger = setup_logger(__name__)

class BrowserTrackingDB:
    def __init__(self, db_path="browser_tracking.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create clients table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hostname TEXT NOT NULL,
                    mac_address TEXT UNIQUE NOT NULL,
                    local_ip TEXT,
                    username TEXT,
                    os_info TEXT,
                    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create browsing_history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS browsing_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id INTEGER,
                    url TEXT NOT NULL,
                    title TEXT,
                    visit_time TIMESTAMP,
                    browser_type TEXT DEFAULT 'Chrome',
                    profile_name TEXT,
                    gmail_account TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (client_id) REFERENCES clients (id)
                )
            ''')
            
            # Create browser_profiles table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS browser_profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id INTEGER,
                    profile_name TEXT,
                    profile_path TEXT,
                    gmail_accounts TEXT,
                    is_active BOOLEAN DEFAULT 0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (client_id) REFERENCES clients (id)
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_client_mac ON clients(mac_address)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_history_client ON browsing_history(client_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_history_time ON browsing_history(visit_time)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_profiles_client ON browser_profiles(client_id)')
            
            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def get_or_create_client(self, hostname, mac_address, local_ip, username, os_info):
        """Get existing client or create new one"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if client exists
            cursor.execute('SELECT id FROM clients WHERE mac_address = ?', (mac_address,))
            result = cursor.fetchone()
            
            if result:
                client_id = result[0]
                # Update last seen and other info
                cursor.execute('''
                    UPDATE clients
                    SET hostname = ?, local_ip = ?, username = ?, os_info = ?, last_seen = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (hostname, local_ip, username, json.dumps(os_info), client_id))
            else:
                # Create new client
                cursor.execute('''
                    INSERT INTO clients (hostname, mac_address, local_ip, username, os_info)
                    VALUES (?, ?, ?, ?, ?)
                ''', (hostname, mac_address, local_ip, username, json.dumps(os_info)))
                client_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            return client_id
            
        except Exception as e:
            logger.error(f"Error managing client: {e}")
            return None
    
    def insert_browsing_data(self, client_id, browsing_data):
        """Insert browsing history data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for entry in browsing_data:
                cursor.execute('''
                    INSERT INTO browsing_history 
                    (client_id, url, title, visit_time, browser_type, profile_name, gmail_account)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    client_id,
                    entry.get('url'),
                    entry.get('title'),
                    entry.get('visit_time'),
                    entry.get('browser_type', 'Chrome'),
                    entry.get('profile_name'),
                    entry.get('gmail_account')
                ))
            
            conn.commit()
            conn.close()
            logger.info(f"Inserted {len(browsing_data)} browsing entries for client {client_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error inserting browsing data: {e}")
            return False
    
    def update_browser_profiles(self, client_id, profiles_data):
        """Update browser profiles information"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Clear existing profiles for this client
            cursor.execute('DELETE FROM browser_profiles WHERE client_id = ?', (client_id,))
            
            # Insert new profiles
            for profile in profiles_data:
                cursor.execute('''
                    INSERT INTO browser_profiles 
                    (client_id, profile_name, profile_path, gmail_accounts, is_active)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    client_id,
                    profile.get('name'),
                    profile.get('path'),
                    json.dumps(profile.get('gmail_accounts', [])),
                    profile.get('is_active', False)
                ))
            
            conn.commit()
            conn.close()
            logger.info(f"Updated {len(profiles_data)} profiles for client {client_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating browser profiles: {e}")
            return False
    
    def get_recent_activity(self, hours=24, limit=1000):
        """Get recent browsing activity"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT c.hostname, c.username, bh.url, bh.title, bh.visit_time, 
                       bh.profile_name, bh.gmail_account, c.local_ip
                FROM browsing_history bh
                JOIN clients c ON bh.client_id = c.id
                WHERE bh.visit_time >= datetime('now', '-{} hours')
                ORDER BY bh.visit_time DESC
                LIMIT ?
            '''.format(hours), (limit,))
            
            results = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'hostname': row[0],
                    'username': row[1],
                    'url': row[2],
                    'title': row[3],
                    'visit_time': row[4],
                    'profile_name': row[5],
                    'gmail_account': row[6],
                    'local_ip': row[7]
                }
                for row in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting recent activity: {e}")
            return []
