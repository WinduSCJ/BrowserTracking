import requests
import json

def test_connection():
    server_url = "https://browser-tracking.vercel.app"
    api_token = "BrowserTracker2024SecureToken"
    
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json'
    }
    
    print(f"Testing connection to {server_url}")
    
    try:
        # Test health endpoint
        response = requests.get(f"{server_url}/health", timeout=10)
        if response.status_code == 200:
            print("Server is reachable")
            print(f"Response: {response.json()}")
        else:
            print(f"Server returned status {response.status_code}")
            return False
        
        # Test API endpoint
        response = requests.get(f"{server_url}/api/activity?hours=1&limit=1", 
                              headers=headers, timeout=10)
        if response.status_code == 200:
            print("API authentication successful")
            return True
        else:
            print(f"API authentication failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Connection failed: {e}")
        return False

if __name__ == '__main__':
    if test_connection():
        print("\nClient configuration is ready for deployment!")
    else:
        print("\nPlease check server status and internet connectivity")
    input("\nPress Enter to exit...")
