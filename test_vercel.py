import requests
import json

def test_vercel_deployment():
    """Test Vercel deployment"""
    
    base_url = "https://browser-tracking-obz04i0k1-winduajis-projects.vercel.app"
    api_token = "BrowserTracker2024SecureToken"
    
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json'
    }
    
    print(f"=== Testing Vercel Deployment ===")
    print(f"URL: {base_url}")
    print(f"Token: {api_token[:20]}...")
    print()
    
    # Test health endpoint
    print("1. Testing Health Endpoint:")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
            print("   ✅ Health check passed")
        else:
            print(f"   ❌ Health check failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return False
    
    print()
    
    # Test API authentication
    print("2. Testing API Authentication:")
    try:
        response = requests.get(f"{base_url}/api/activity?hours=1&limit=1", 
                              headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {data}")
            print("   ✅ API authentication passed")
        else:
            print(f"   ❌ API authentication failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ API authentication error: {e}")
        return False
    
    print()
    
    # Test registration
    print("3. Testing Client Registration:")
    try:
        test_data = {
            'hostname': 'test-vercel-client',
            'mac_address': '00:11:22:33:44:55',
            'local_ip': '192.168.1.100',
            'username': 'test-user',
            'os_info': {'system': 'Windows', 'version': '10'}
        }
        
        response = requests.post(f"{base_url}/api/register", 
                               json=test_data, headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {data}")
            print("   ✅ Client registration passed")
            return True
        else:
            print(f"   ❌ Client registration failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Client registration error: {e}")
        return False

if __name__ == '__main__':
    success = test_vercel_deployment()
    
    if success:
        print("\n🎉 Vercel deployment is working perfectly!")
        print("\n📋 Next Steps:")
        print("1. Copy 'vercel_client_configs' folder to target PCs")
        print("2. Run 'install_client.bat' on target PCs")
        print("3. Clients will connect to Vercel server automatically")
        print("4. Monitor activity via Vercel dashboard or local GUI")
    else:
        print("\n❌ Vercel deployment has issues")
        print("Please check server logs and configuration")
    
    input("\nPress Enter to exit...")
