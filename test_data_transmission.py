"""
Test Data Transmission for Browser Tracker
Simple test to verify data is being sent correctly
"""

import requests
import json
import time
from datetime import datetime

def test_data_transmission():
    """Test if data is being transmitted to server"""
    print("🧪 Testing Data Transmission")
    print("="*40)
    
    api_base = "https://browser-tracking.vercel.app"
    headers = {
        'Authorization': 'Bearer BrowserTracker2024SecureToken',
        'Content-Type': 'application/json'
    }
    
    # Get initial activity count
    try:
        response = requests.get(f"{api_base}/api/activity?hours=1&limit=5", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            initial_count = len(data.get('activity', []))
            print(f"📊 Initial activity count: {initial_count}")
            
            if initial_count > 0:
                print("\n📋 Recent Activities:")
                for i, activity in enumerate(data['activity'][:3]):
                    title = activity.get('title', 'No title')[:40]
                    url = activity.get('url', 'No URL')[:50]
                    visit_time = activity.get('visit_time', '')
                    
                    print(f"  {i+1}. {title}")
                    print(f"     URL: {url}")
                    print(f"     Time: {visit_time}")
                    print()
            
            return True
        else:
            print(f"❌ Failed to get activity: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error getting activity: {e}")
        return False

def monitor_new_data():
    """Monitor for new data over time"""
    print("\n🔄 Monitoring for New Data")
    print("="*40)
    print("Watching for new activities... (Press Ctrl+C to stop)")
    
    api_base = "https://browser-tracking.vercel.app"
    headers = {
        'Authorization': 'Bearer BrowserTracker2024SecureToken',
        'Content-Type': 'application/json'
    }
    
    last_count = 0
    check_count = 0
    
    try:
        while True:
            check_count += 1
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            try:
                response = requests.get(f"{api_base}/api/activity?hours=1&limit=10", headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    current_count = len(data.get('activity', []))
                    
                    if current_count > last_count:
                        new_activities = current_count - last_count
                        print(f"[{timestamp}] 🔔 {new_activities} NEW activities detected! Total: {current_count}")
                        
                        # Show latest activity
                        activities = data.get('activity', [])
                        if activities:
                            latest = activities[0]
                            title = latest.get('title', 'No title')[:40]
                            url = latest.get('url', 'No URL')[:50]
                            hostname = latest.get('hostname', 'Unknown')
                            
                            print(f"           Latest: {title}")
                            print(f"           URL: {url}")
                            print(f"           From: {hostname}")
                        
                        last_count = current_count
                    elif last_count == 0:
                        last_count = current_count
                        print(f"[{timestamp}] 📊 Baseline: {current_count} activities")
                    else:
                        # Show periodic status
                        if check_count % 6 == 0:  # Every minute (10s * 6)
                            print(f"[{timestamp}] 💓 Monitoring... ({current_count} activities)")
                else:
                    print(f"[{timestamp}] ❌ API Error: {response.status_code}")
                
            except Exception as e:
                print(f"[{timestamp}] ❌ Error: {e}")
            
            time.sleep(10)  # Check every 10 seconds
            
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped by user")

def test_server_health():
    """Test server health"""
    print("🔍 Testing Server Health")
    print("="*30)
    
    try:
        response = requests.get("https://browser-tracking.vercel.app/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Server Status: {data.get('status', 'unknown')}")
            print(f"📅 Server Time: {data.get('timestamp', 'unknown')}")
            return True
        else:
            print(f"❌ Server returned: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Server connection failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Browser Tracker Data Transmission Test")
    print("="*50)
    
    # Test server health first
    if not test_server_health():
        print("\n❌ Server is not accessible. Cannot proceed with tests.")
        return
    
    print("\nChoose test mode:")
    print("1. Quick data transmission test")
    print("2. Monitor for new data (continuous)")
    print("3. Both tests")
    
    try:
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == "1":
            success = test_data_transmission()
            if success:
                print("\n🎉 Data transmission test completed!")
            else:
                print("\n⚠️ Data transmission test failed")
                
        elif choice == "2":
            monitor_new_data()
            
        elif choice == "3":
            success = test_data_transmission()
            if success:
                print("\n🎉 Data transmission test passed!")
                print("\nStarting continuous monitoring...")
                time.sleep(2)
                monitor_new_data()
            else:
                print("\n⚠️ Data transmission test failed")
                
        else:
            print("Invalid choice. Running quick test...")
            test_data_transmission()
            
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test error: {e}")

if __name__ == "__main__":
    main()
