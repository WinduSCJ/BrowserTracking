from database import BrowserTrackingDB

def main():
    print("=== Browser Tracking Database Content ===")
    
    db = BrowserTrackingDB()
    
    # Get recent activity
    activity = db.get_recent_activity(24, 20)
    
    print(f"\nFound {len(activity)} recent activities:")
    print("-" * 80)
    
    for i, entry in enumerate(activity[:10], 1):
        print(f"{i}. Host: {entry['hostname']}")
        print(f"   User: {entry['username']}")
        print(f"   URL: {entry['url'][:60]}...")
        print(f"   Time: {entry['visit_time']}")
        print(f"   Profile: {entry['profile_name']}")
        print(f"   Gmail: {entry['gmail_account']}")
        print("-" * 80)

if __name__ == '__main__':
    main()
