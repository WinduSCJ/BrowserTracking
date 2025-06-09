"""
Debug Chrome History - Check for fresh data
"""

import os
import sqlite3
import shutil
import tempfile
from datetime import datetime, timezone

def check_chrome_history():
    """Check Chrome history for recent entries"""
    
    chrome_base = os.path.expanduser(r'~\AppData\Local\Google\Chrome\User Data')
    if not os.path.exists(chrome_base):
        print("Chrome not found")
        return
    
    print(f"Chrome base: {chrome_base}")
    print("=" * 60)
    
    # Check all profiles
    profiles = ['Default']
    for item in os.listdir(chrome_base):
        if item.startswith('Profile '):
            profiles.append(item)
    
    print(f"Found {len(profiles)} profiles: {profiles}")
    print("=" * 60)
    
    for profile_name in profiles:
        profile_path = os.path.join(chrome_base, profile_name)
        history_db = os.path.join(profile_path, 'History')
        
        if not os.path.exists(history_db):
            print(f"{profile_name}: No history database")
            continue
        
        try:
            # Copy database
            with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as temp_file:
                temp_db = temp_file.name
            
            shutil.copy2(history_db, temp_db)
            
            # Read recent history (last 1 hour)
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            
            # Get current time in Chrome format
            now = datetime.now(tz=timezone.utc)
            one_hour_ago = now.timestamp() - 3600  # 1 hour ago
            chrome_time_threshold = int((one_hour_ago + 11644473600) * 1000000)
            
            cursor.execute('''
                SELECT url, title, visit_count, last_visit_time,
                       datetime((last_visit_time - 11644473600000000) / 1000000, 'unixepoch') as visit_datetime
                FROM urls
                WHERE last_visit_time > ?
                ORDER BY last_visit_time DESC
                LIMIT 20
            ''', (chrome_time_threshold,))
            
            results = cursor.fetchall()
            
            print(f"\n{profile_name}: {len(results)} recent entries (last 1 hour)")
            print("-" * 40)
            
            for i, (url, title, visit_count, chrome_time, visit_datetime) in enumerate(results):
                print(f"{i+1}. {visit_datetime}")
                print(f"   URL: {url}")
                print(f"   Title: {title}")
                print(f"   Visits: {visit_count}")
                print()
                
                # Check for "asu" specifically
                if "asu" in url.lower() or (title and "asu" in title.lower()):
                    print(f"   *** FOUND 'asu' in {profile_name}! ***")
                    print()
            
            conn.close()
            os.unlink(temp_db)
            
        except Exception as e:
            print(f"{profile_name}: Error - {e}")
    
    print("=" * 60)
    print("Debug complete")

if __name__ == "__main__":
    check_chrome_history()
