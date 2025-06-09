"""
Test Real-time Browser Tracking System
Tests various components and triggers
"""

import requests
import json
import time
import socket
import getpass
import platform
from uuid import getnode
from datetime import datetime, timezone

class RealtimeSystemTester:
    def __init__(self):
        self.api_base = "https://browser-tracking.vercel.app"
        self.api_token = "BrowserTracker2024SecureToken"
        self.client_id = None
        
        print("🧪 Real-time System Tester")
        print(f"🌐 Server: {self.api_base}")
        print("="*50)
    
    def get_system_info(self):
        """Get system information for client registration"""
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
    
    def test_server_health(self):
        """Test server health endpoint"""
        print("\n🔍 Testing Server Health...")
        try:
            response = requests.get(f"{self.api_base}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Server is healthy: {data.get('status')}")
                print(f"📅 Server time: {data.get('timestamp')}")
                return True
            else:
                print(f"❌ Server returned status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False
    
    def test_client_registration(self):
        """Test client registration"""
        print("\n🔗 Testing Client Registration...")
        try:
            system_info = self.get_system_info()
            if not system_info:
                return False
            
            headers = {
                'Authorization': f'Bearer {self.api_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                f"{self.api_base}/api/register",
                json=system_info,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.client_id = data.get('client_id')
                    print(f"✅ Client registered with ID: {self.client_id}")
                    print(f"📝 Message: {data.get('message')}")
                    return True
            
            print(f"❌ Registration failed: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
        except Exception as e:
            print(f"❌ Registration error: {e}")
            return False
    
    def test_manual_data_submission(self):
        """Test manual browsing data submission"""
        print("\n📤 Testing Manual Data Submission...")
        
        if not self.client_id:
            print("❌ No client ID - registration required first")
            return False
        
        try:
            # Create test browsing data
            test_data = [
                {
                    'url': 'https://www.google.com/search?q=realtime+test+manual',
                    'title': 'Manual Test - Google Search',
                    'visit_time': datetime.now(tz=timezone.utc).isoformat(),
                    'browser_type': 'Chrome',
                    'profile_name': 'Test Profile',
                    'gmail_account': 'test@gmail.com'
                },
                {
                    'url': 'https://github.com/test/realtime-system',
                    'title': 'Real-time System Test Repository',
                    'visit_time': datetime.now(tz=timezone.utc).isoformat(),
                    'browser_type': 'Chrome',
                    'profile_name': 'Test Profile',
                    'gmail_account': 'test@gmail.com'
                },
                {
                    'url': 'https://stackoverflow.com/questions/realtime-monitoring',
                    'title': 'Real-time Monitoring Questions - Stack Overflow',
                    'visit_time': datetime.now(tz=timezone.utc).isoformat(),
                    'browser_type': 'Chrome',
                    'profile_name': 'Test Profile',
                    'gmail_account': 'test@gmail.com'
                }
            ]
            
            headers = {
                'Authorization': f'Bearer {self.api_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'client_id': self.client_id,
                'browsing_data': test_data
            }
            
            print(f"📊 Sending {len(test_data)} test entries...")
            
            response = requests.post(
                f"{self.api_base}/api/browsing-data",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ Data submitted successfully!")
                    print(f"📝 Message: {data.get('message')}")
                    print(f"🔔 Real-time notified: {data.get('realtime_notified', False)}")
                    return True
            
            print(f"❌ Data submission failed: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
        except Exception as e:
            print(f"❌ Data submission error: {e}")
            return False
    
    def test_activity_retrieval(self):
        """Test activity data retrieval"""
        print("\n📊 Testing Activity Retrieval...")
        try:
            headers = {
                'Authorization': f'Bearer {self.api_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f"{self.api_base}/api/activity?hours=1&limit=10",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    activities = data.get('activity', [])
                    print(f"✅ Retrieved {len(activities)} activities")
                    
                    if activities:
                        print("\n📋 Recent Activities:")
                        for i, activity in enumerate(activities[:3]):
                            print(f"  {i+1}. {activity.get('title', 'No title')}")
                            print(f"     URL: {activity.get('url', 'No URL')}")
                            print(f"     Time: {activity.get('visit_time', 'No time')}")
                            print()
                    
                    return True
            
            print(f"❌ Activity retrieval failed: {response.status_code}")
            return False
            
        except Exception as e:
            print(f"❌ Activity retrieval error: {e}")
            return False
    
    def test_stats_endpoint(self):
        """Test real-time statistics endpoint"""
        print("\n📈 Testing Stats Endpoint...")
        try:
            headers = {
                'Authorization': f'Bearer {self.api_token}',
                'Content-Type': 'application/json'
            }

            response = requests.get(f"{self.api_base}/api/stats", headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    stats = data.get('stats', {})
                    print(f"✅ Stats retrieved successfully!")
                    print(f"📊 Total Activities: {stats.get('total_activities', 0)}")
                    print(f"👥 Active Clients: {stats.get('active_clients', 0)}")
                    print(f"🔗 SSE Connections: {stats.get('connected_sse_clients', 0)}")
                    print(f"🕒 Last Update: {stats.get('last_update', 'Unknown')}")
                    return True
            
            print(f"❌ Stats retrieval failed: {response.status_code}")
            return False
            
        except Exception as e:
            print(f"❌ Stats retrieval error: {e}")
            return False
    
    def run_full_test(self):
        """Run complete system test"""
        print("🚀 Starting Full Real-time System Test")
        print("="*50)
        
        tests = [
            ("Server Health", self.test_server_health),
            ("Client Registration", self.test_client_registration),
            ("Manual Data Submission", self.test_manual_data_submission),
            ("Activity Retrieval", self.test_activity_retrieval),
            ("Stats Endpoint", self.test_stats_endpoint)
        ]
        
        results = []
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
                
                if result:
                    print(f"✅ {test_name}: PASSED")
                else:
                    print(f"❌ {test_name}: FAILED")
                
                # Wait between tests
                time.sleep(2)
                
            except Exception as e:
                print(f"❌ {test_name}: ERROR - {e}")
                results.append((test_name, False))
        
        # Summary
        print("\n" + "="*50)
        print("📋 TEST SUMMARY")
        print("="*50)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name:.<30} {status}")
        
        print(f"\n🎯 Overall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! Real-time system is working correctly!")
        else:
            print("⚠️ Some tests failed. Check the logs above for details.")
        
        return passed == total

def main():
    """Main test function"""
    tester = RealtimeSystemTester()
    
    print("Choose test mode:")
    print("1. Full system test")
    print("2. Manual data trigger only")
    print("3. Quick health check")
    
    try:
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == "1":
            tester.run_full_test()
        elif choice == "2":
            if tester.test_server_health():
                if tester.test_client_registration():
                    tester.test_manual_data_submission()
        elif choice == "3":
            tester.test_server_health()
            tester.test_stats_endpoint()
        else:
            print("Invalid choice. Running full test...")
            tester.run_full_test()
            
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test error: {e}")

if __name__ == "__main__":
    main()
