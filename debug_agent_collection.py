"""
Debug Agent Collection - Check what agent actually collects
"""

import os
import sqlite3
import shutil
import tempfile
from datetime import datetime, timezone

def debug_agent_collection():
    """Debug what the agent actually collects"""
    
    chrome_base = os.path.expanduser(r'~\AppData\Local\Google\Chrome\User Data')
    if not os.path.exists(chrome_base):
        print("Chrome not found")
        return
    
    print("DEBUGGING AGENT COLLECTION LOGIC")
    print("=" * 60)
    
    # Check all profiles like agent does
    profiles = ['Default']
    for item in os.listdir(chrome_base):
        if item.startswith('Profile '):
            profiles.append(item)
    
    all_history = []
    
    for profile_name in profiles:
        profile_path = os.path.join(chrome_base, profile_name)
        history_db = os.path.join(profile_path, 'History')
        
        if not os.path.exists(history_db):
            print(f"{profile_name}: No history database")
            continue
        
        try:
            # Copy database (like agent does)
            with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as temp_file:
                temp_db = temp_file.name
            
            shutil.copy2(history_db, temp_db)
            
            # Read history (EXACTLY like agent does)
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT url, title, visit_count, last_visit_time
                FROM urls
                WHERE last_visit_time > 0
                ORDER BY last_visit_time DESC
                LIMIT 50
            ''')
            
            profile_entries = 0
            print(f"\n{profile_name}: Processing...")
            
            for row in cursor.fetchall():
                url, title, visit_count, chrome_time = row
                
                # Skip internal URLs (like agent does)
                skip_patterns = [
                    'chrome://', 'chrome-extension://', 'edge://', 'about:',
                    'file://', 'localhost', '127.0.0.1', '192.168.', '10.0.', '172.16.'
                ]
                
                url_lower = url.lower()
                should_skip = any(pattern in url_lower for pattern in skip_patterns)
                
                if should_skip:
                    continue
                
                # Convert Chrome timestamp (like agent does)
                if chrome_time > 0:
                    unix_timestamp = (chrome_time - 11644473600000000) / 1000000
                    visit_time = datetime.fromtimestamp(unix_timestamp, tz=timezone.utc)
                else:
                    visit_time = datetime.now(tz=timezone.utc)
                
                # Check for "asu" or "shopee"
                if ("asu" in url.lower() or (title and "asu" in title.lower()) or
                    "shopee" in url.lower() or (title and "shopee" in title.lower())):
                    keyword = "asu" if "asu" in url.lower() or (title and "asu" in title.lower()) else "shopee"
                    print(f"   *** FOUND '{keyword}' entry! ***")
                    print(f"   URL: {url}")
                    print(f"   Title: {title}")
                    print(f"   Time: {visit_time}")
                    print(f"   Profile: {profile_name}")
                
                all_history.append({
                    'url': url[:2000],
                    'title': (title or '')[:500],
                    'visit_time': visit_time.isoformat(),
                    'browser_type': 'Chrome',
                    'profile_name': profile_name,
                    'gmail_account': None  # Simplified for debug
                })
                profile_entries += 1
            
            print(f"   Collected: {profile_entries} entries")
            conn.close()
            os.unlink(temp_db)
            
        except Exception as e:
            print(f"{profile_name}: Error - {e}")
    
    print(f"\nTOTAL COLLECTED: {len(all_history)} entries")

    # Sort by timestamp like the fixed agent does
    all_history.sort(key=lambda x: x['visit_time'], reverse=True)

    # Show what would be sent (first 50 like agent does)
    batch_size = 50
    to_send = all_history[:batch_size]
    
    print(f"\nWOULD SEND: {len(to_send)} entries")
    print("=" * 60)
    
    # Check if "asu" or "shopee" is in the batch to be sent
    keywords_found = {"asu": False, "shopee": False}
    for i, entry in enumerate(to_send):
        for keyword in keywords_found.keys():
            if keyword in entry['url'].lower() or keyword in entry['title'].lower():
                print(f"BATCH ENTRY {i+1}: *** {keyword.upper()} FOUND! ***")
                print(f"   URL: {entry['url']}")
                print(f"   Title: {entry['title']}")
                print(f"   Time: {entry['visit_time']}")
                print(f"   Profile: {entry['profile_name']}")
                print()
                keywords_found[keyword] = True

    if not any(keywords_found.values()):
        print("❌ Neither 'asu' nor 'shopee' found in batch to be sent!")
        print("This explains why they don't appear in dashboard.")

        # Show recent entries that would be sent
        print("\nRecent entries that WOULD be sent:")
        for i, entry in enumerate(to_send[:10]):
            print(f"{i+1}. {entry['visit_time']} - {entry['profile_name']}")
            print(f"   {entry['url'][:80]}...")
            print()
    else:
        found_keywords = [k for k, v in keywords_found.items() if v]
        print(f"✅ {', '.join(found_keywords).upper()} FOUND in batch - should appear in dashboard!")

if __name__ == "__main__":
    debug_agent_collection()
