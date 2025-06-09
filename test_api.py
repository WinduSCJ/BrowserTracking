import requests
import json

def test_api():
    base_url = "http://localhost:5000"
    headers = {
        'Authorization': 'Bearer BrowserTracker2024SecureToken',
        'Content-Type': 'application/json'
    }
    
    print("=== Testing API Endpoints ===")
    
    # Test health
    print("\n1. Testing Health Endpoint:")
    response = requests.get(f"{base_url}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test activity
    print("\n2. Testing Activity Endpoint:")
    response = requests.get(f"{base_url}/api/activity?hours=24&limit=5", headers=headers)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Found {data['count']} activities")
    
    for i, activity in enumerate(data['activity'][:3], 1):
        print(f"  {i}. {activity['hostname']} - {activity['url'][:50]}...")
    
    print("\n=== API Test Complete ===")

if __name__ == '__main__':
    test_api()
