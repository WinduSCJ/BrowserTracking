import json
import os
import shutil
import sys

def generate_vercel_client_config(vercel_url, api_token="BrowserTracker2024SecureToken"):
    """Generate client configuration for Vercel deployment"""
    
    print(f"=== Generating Client Configuration for Vercel ===")
    print(f"Vercel URL: {vercel_url}")
    print(f"API Token: {api_token[:20]}...")
    
    # Ensure URL has https
    if not vercel_url.startswith('http'):
        vercel_url = f"https://{vercel_url}"
    
    # Create output directory
    output_dir = "vercel_client_configs"
    os.makedirs(output_dir, exist_ok=True)
    
    # Client configuration
    client_config = {
        "server": {
            "host": "0.0.0.0",
            "port": 5000,
            "debug": False,
            "ssl_enabled": False,
            "ssl_cert": "",
            "ssl_key": ""
        },
        "database": {
            "path": "browser_tracking.db"
        },
        "security": {
            "api_token": api_token,
            "encryption_key": "client-encryption-key"
        },
        "client": {
            "server_url": vercel_url,
            "api_token": api_token,
            "check_interval": 300,
            "batch_size": 100,
            "retry_attempts": 5,
            "retry_delay": 60,
            "timeout": 30
        },
        "logging": {
            "level": "INFO",
            "max_file_size": "50KB",
            "max_files": 5,
            "log_file": "browser_tracking.log"
        }
    }
    
    # Save client config
    config_path = os.path.join(output_dir, "config.json")
    with open(config_path, 'w') as f:
        json.dump(client_config, f, indent=4)
    
    # Copy client files
    client_files = [
        'agent.py',
        'browser_reader.py',
        'system_info.py',
        'network_client.py',
        'logger.py',
        'installer.py',
        'requirements.txt'
    ]
    
    for file in client_files:
        if os.path.exists(file):
            shutil.copy2(file, output_dir)
            print(f"Copied {file}")
    
    # Create client installer script
    installer_script = f"""@echo off
echo Browser Tracking Client Installer (Vercel Server)
echo Server: {vercel_url}
echo.

REM Check admin privileges
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running with administrator privileges...
) else (
    echo This script requires administrator privileges.
    echo Please run as administrator.
    pause
    exit /b 1
)

REM Test server connectivity
echo Testing server connectivity...
curl -f {vercel_url}/health
if %errorLevel% == 0 (
    echo Server is reachable
) else (
    echo Cannot reach server at {vercel_url}
    echo Please check internet connectivity
    pause
    exit /b 1
)

REM Install client
echo Installing Browser Tracking Client...
python installer.py

echo.
echo Installation complete!
echo The client will connect to: {vercel_url}
echo.
pause
"""
    
    installer_path = os.path.join(output_dir, "install_client.bat")
    with open(installer_path, 'w') as f:
        f.write(installer_script)
    
    # Create test script
    test_script = f"""import requests
import json

def test_connection():
    server_url = "{vercel_url}"
    api_token = "{api_token}"
    
    headers = {{
        'Authorization': f'Bearer {{api_token}}',
        'Content-Type': 'application/json'
    }}
    
    print(f"Testing connection to {{server_url}}")
    
    try:
        # Test health endpoint
        response = requests.get(f"{{server_url}}/health", timeout=10)
        if response.status_code == 200:
            print("Server is reachable")
            print(f"Response: {{response.json()}}")
        else:
            print(f"Server returned status {{response.status_code}}")
            return False
        
        # Test API endpoint
        response = requests.get(f"{{server_url}}/api/activity?hours=1&limit=1", 
                              headers=headers, timeout=10)
        if response.status_code == 200:
            print("API authentication successful")
            return True
        else:
            print(f"API authentication failed: {{response.status_code}}")
            return False
            
    except Exception as e:
        print(f"Connection failed: {{e}}")
        return False

if __name__ == '__main__':
    if test_connection():
        print("\\nClient configuration is ready for deployment!")
    else:
        print("\\nPlease check server status and internet connectivity")
    input("\\nPress Enter to exit...")
"""
    
    test_path = os.path.join(output_dir, "test_connection.py")
    with open(test_path, 'w', encoding='utf-8') as f:
        f.write(test_script)
    
    # Create README
    readme_content = f"""# Browser Tracking Client Configuration (Vercel)

## Server Information
- Server URL: {vercel_url}
- API Token: {api_token}
- Deployment: Vercel Serverless

## Installation Instructions

### Automatic Installation:
1. Copy this entire folder to target PC
2. Run `install_client.bat` as Administrator
3. Client will auto-start on boot

### Manual Installation:
1. Install Python 3.11+ if not present
2. Run: `pip install -r requirements.txt`
3. Run: `python installer.py`

### Testing:
- Run `python test_connection.py` to test server connectivity
- Run `python agent.py --once` for one-time data collection test

## Configuration
The config.json file is pre-configured for Vercel server.
No manual configuration needed.

## Advantages of Vercel Deployment
- Global CDN and edge locations
- Automatic HTTPS
- High availability
- No server maintenance required
- Scales automatically

## Troubleshooting
1. Ensure internet connectivity
2. Check firewall settings (allow outbound HTTPS)
3. Verify server URL is accessible: {vercel_url}/health
4. Check API token matches server configuration

## Support
- Check logs in browser_tracking.log
- Run test_connection.py for diagnostics
- Verify network connectivity to Vercel
"""
    
    readme_path = os.path.join(output_dir, "README.txt")
    with open(readme_path, 'w') as f:
        f.write(readme_content)
    
    print(f"\nClient configuration generated successfully!")
    print(f"Location: {os.path.abspath(output_dir)}")
    print(f"Server URL: {vercel_url}")
    print(f"API Token: {api_token}")
    
    return output_dir

def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_vercel_client.py <vercel_url>")
        print("Example: python generate_vercel_client.py browser-tracking.vercel.app")
        print("Example: python generate_vercel_client.py https://browser-tracking-abc123.vercel.app")
        sys.exit(1)
    
    vercel_url = sys.argv[1]
    api_token = sys.argv[2] if len(sys.argv) > 2 else "BrowserTracker2024SecureToken"
    
    generate_vercel_client_config(vercel_url, api_token)

if __name__ == '__main__':
    main()
