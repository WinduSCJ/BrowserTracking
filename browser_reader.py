import os
import sqlite3
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
import tempfile
from logger import setup_logger

logger = setup_logger(__name__)

class ChromeHistoryReader:
    def __init__(self):
        self.chrome_paths = self._get_chrome_paths()
    
    def _get_chrome_paths(self):
        """Get Chrome profile paths for different OS"""
        paths = []
        
        # Windows paths
        if os.name == 'nt':
            base_paths = [
                os.path.expanduser(r'~\AppData\Local\Google\Chrome\User Data'),
                os.path.expanduser(r'~\AppData\Local\Chromium\User Data'),
            ]
        else:
            # Linux/Mac paths (for future compatibility)
            base_paths = [
                os.path.expanduser('~/.config/google-chrome'),
                os.path.expanduser('~/.config/chromium'),
                os.path.expanduser('~/Library/Application Support/Google/Chrome'),
            ]
        
        for base_path in base_paths:
            if os.path.exists(base_path):
                paths.append(base_path)
        
        return paths
    
    def _get_profiles(self, chrome_path):
        """Get all Chrome profiles from a Chrome installation"""
        profiles = []
        
        try:
            # Default profile
            default_profile = os.path.join(chrome_path, 'Default')
            if os.path.exists(default_profile):
                profiles.append({
                    'name': 'Default',
                    'path': default_profile,
                    'is_active': True
                })
            
            # Additional profiles (Profile 1, Profile 2, etc.)
            for item in os.listdir(chrome_path):
                item_path = os.path.join(chrome_path, item)
                if os.path.isdir(item_path) and item.startswith('Profile '):
                    profiles.append({
                        'name': item,
                        'path': item_path,
                        'is_active': False
                    })
            
        except Exception as e:
            logger.error(f"Error getting profiles from {chrome_path}: {e}")
        
        return profiles
    
    def _get_gmail_accounts(self, profile_path):
        """Extract Gmail accounts from Chrome profile"""
        gmail_accounts = []
        
        try:
            # Try to read from Preferences file
            prefs_file = os.path.join(profile_path, 'Preferences')
            if os.path.exists(prefs_file):
                with open(prefs_file, 'r', encoding='utf-8') as f:
                    prefs = json.load(f)
                
                # Look for account info in various places
                account_info = prefs.get('account_info', [])
                for account in account_info:
                    email = account.get('email')
                    if email and '@gmail.com' in email.lower():
                        gmail_accounts.append(email)
                
                # Also check signin info
                signin = prefs.get('signin', {})
                allowed_usernames = signin.get('allowed_usernames', [])
                for username in allowed_usernames:
                    if '@gmail.com' in username.lower():
                        gmail_accounts.append(username)
        
        except Exception as e:
            logger.debug(f"Could not extract Gmail accounts from {profile_path}: {e}")
        
        return list(set(gmail_accounts))  # Remove duplicates
    
    def _read_history_db(self, profile_path, limit=1000):
        """Read history from Chrome's History database"""
        history_entries = []
        
        try:
            history_db_path = os.path.join(profile_path, 'History')
            
            if not os.path.exists(history_db_path):
                return history_entries
            
            # Create temporary copy (Chrome locks the original file)
            with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as temp_file:
                temp_db_path = temp_file.name
            
            try:
                shutil.copy2(history_db_path, temp_db_path)
            except Exception as e:
                logger.warning(f"Could not copy history database: {e}")
                return history_entries
            
            # Read from temporary database
            conn = sqlite3.connect(temp_db_path)
            cursor = conn.cursor()
            
            # Query recent history
            cursor.execute('''
                SELECT url, title, visit_count, last_visit_time
                FROM urls
                WHERE last_visit_time > 0
                ORDER BY last_visit_time DESC
                LIMIT ?
            ''', (limit,))
            
            results = cursor.fetchall()
            
            for row in results:
                url, title, visit_count, chrome_time = row
                
                # Convert Chrome timestamp to Python datetime
                # Chrome uses microseconds since January 1, 1601 UTC
                if chrome_time > 0:
                    # Convert Chrome time to Unix timestamp
                    unix_timestamp = (chrome_time - 11644473600000000) / 1000000
                    visit_time = datetime.fromtimestamp(unix_timestamp, tz=timezone.utc)
                else:
                    visit_time = datetime.now(tz=timezone.utc)
                
                history_entries.append({
                    'url': url,
                    'title': title or '',
                    'visit_count': visit_count,
                    'visit_time': visit_time.isoformat(),
                    'browser_type': 'Chrome'
                })
            
            conn.close()
            
            # Clean up temporary file
            try:
                os.unlink(temp_db_path)
            except:
                pass
                
        except Exception as e:
            logger.error(f"Error reading history from {profile_path}: {e}")
        
        return history_entries
    
    def get_all_browsing_data(self, limit_per_profile=500):
        """Get browsing data from all Chrome profiles"""
        all_data = {
            'profiles': [],
            'browsing_history': []
        }
        
        for chrome_path in self.chrome_paths:
            profiles = self._get_profiles(chrome_path)
            
            for profile in profiles:
                profile_path = profile['path']
                
                # Get Gmail accounts for this profile
                gmail_accounts = self._get_gmail_accounts(profile_path)
                profile['gmail_accounts'] = gmail_accounts
                
                # Get browsing history
                history = self._read_history_db(profile_path, limit_per_profile)
                
                # Add profile info to each history entry
                for entry in history:
                    entry['profile_name'] = profile['name']
                    entry['gmail_account'] = gmail_accounts[0] if gmail_accounts else None
                
                all_data['browsing_history'].extend(history)
                all_data['profiles'].append(profile)
        
        logger.info(f"Retrieved {len(all_data['browsing_history'])} history entries from {len(all_data['profiles'])} profiles")
        return all_data
    
    def get_recent_history(self, hours=24, limit=1000):
        """Get recent browsing history within specified hours"""
        cutoff_time = datetime.now(tz=timezone.utc).timestamp() - (hours * 3600)
        
        all_data = self.get_all_browsing_data(limit)
        recent_history = []
        
        for entry in all_data['browsing_history']:
            try:
                entry_time = datetime.fromisoformat(entry['visit_time'].replace('Z', '+00:00'))
                if entry_time.timestamp() >= cutoff_time:
                    recent_history.append(entry)
            except:
                # If we can't parse the time, include it anyway
                recent_history.append(entry)
        
        return {
            'profiles': all_data['profiles'],
            'browsing_history': recent_history[:limit]
        }
