"""
Test Background Mode for Browser Tracker GUI
Tests the background functionality without GUI
"""

import time
import requests
import json
from datetime import datetime

def test_background_agent():
    """Test if background agent is still running"""
    print("🧪 Testing Background Agent")
    print("="*40)
    
    # Test server connection
    try:
        response = requests.get("https://browser-tracking.vercel.app/health", timeout=10)
        if response.status_code == 200:
            print("✅ Server is reachable")
        else:
            print(f"❌ Server returned {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Server connection failed: {e}")
        return False
    
    # Check for recent activity (last 5 minutes)
    try:
        headers = {
            'Authorization': 'Bearer BrowserTracker2024SecureToken',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            "https://browser-tracking.vercel.app/api/activity?hours=1&limit=5",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                activities = data.get('activity', [])
                print(f"📊 Found {len(activities)} recent activities")
                
                if activities:
                    print("\n📋 Recent Activities:")
                    for i, activity in enumerate(activities[:3]):
                        visit_time = activity.get('visit_time', '')
                        title = activity.get('title', 'No title')[:50]
                        url = activity.get('url', 'No URL')[:60]
                        
                        print(f"  {i+1}. {title}")
                        print(f"     URL: {url}")
                        print(f"     Time: {visit_time}")
                        print()
                
                return True
            else:
                print(f"❌ API error: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ API request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Activity check failed: {e}")
        return False

def monitor_activity_changes():
    """Monitor for activity changes over time"""
    print("\n🔄 Monitoring Activity Changes")
    print("="*40)
    print("Watching for new activities... (Press Ctrl+C to stop)")
    
    last_count = 0
    
    try:
        while True:
            try:
                headers = {
                    'Authorization': 'Bearer BrowserTracker2024SecureToken',
                    'Content-Type': 'application/json'
                }
                
                response = requests.get(
                    "https://browser-tracking.vercel.app/api/activity?hours=1&limit=10",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        current_count = len(data.get('activity', []))
                        
                        if current_count > last_count:
                            new_activities = current_count - last_count
                            timestamp = datetime.now().strftime("%H:%M:%S")
                            print(f"[{timestamp}] 🔔 {new_activities} new activities detected! Total: {current_count}")
                            
                            # Show latest activity
                            activities = data.get('activity', [])
                            if activities:
                                latest = activities[0]
                                title = latest.get('title', 'No title')[:40]
                                url = latest.get('url', 'No URL')[:50]
                                print(f"           Latest: {title}")
                                print(f"           URL: {url}")
                            
                            last_count = current_count
                        elif last_count == 0:
                            last_count = current_count
                            timestamp = datetime.now().strftime("%H:%M:%S")
                            print(f"[{timestamp}] 📊 Baseline: {current_count} activities")
                        else:
                            # No change, just show heartbeat every 30 seconds
                            timestamp = datetime.now().strftime("%H:%M:%S")
                            print(f"[{timestamp}] 💓 Monitoring... ({current_count} activities)")
                
                time.sleep(10)  # Check every 10 seconds
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"[{timestamp}] ❌ Error: {e}")
                time.sleep(10)
                
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped by user")

def main():
    """Main test function"""
    print("🚀 Browser Tracker Background Mode Test")
    print("="*50)
    
    print("\nChoose test mode:")
    print("1. Quick background agent test")
    print("2. Monitor activity changes (continuous)")
    print("3. Both tests")
    
    try:
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == "1":
            success = test_background_agent()
            if success:
                print("\n🎉 Background agent is working correctly!")
            else:
                print("\n⚠️ Background agent may not be running or has issues")
                
        elif choice == "2":
            monitor_activity_changes()
            
        elif choice == "3":
            success = test_background_agent()
            if success:
                print("\n🎉 Background agent test passed!")
                print("\nStarting continuous monitoring...")
                time.sleep(2)
                monitor_activity_changes()
            else:
                print("\n⚠️ Background agent test failed")
                
        else:
            print("Invalid choice. Running quick test...")
            test_background_agent()
            
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test error: {e}")

if __name__ == "__main__":
    main()
