import json
import sys
import os
import shutil

def generate_client_config(domain, api_token, output_dir="client_configs"):
    """Generate client configuration for deployment"""
    
    print(f"=== Generating Client Configuration ===")
    print(f"Domain: {domain}")
    print(f"API Token: {api_token[:20]}...")
    print(f"Output Directory: {output_dir}")
    
    # Create output directory
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
            "server_url": f"https://{domain}:5000",
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
echo Browser Tracking Client Installer
echo Server: https://{domain}:5000
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

REM Install client
echo Installing Browser Tracking Client...
python installer.py

echo.
echo Installation complete!
echo The client will connect to: https://{domain}:5000
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
    server_url = "https://{domain}:5000"
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
            print("✅ Server is reachable")
            print(f"Response: {{response.json()}}")
        else:
            print(f"❌ Server returned status {{response.status_code}}")
            return False
        
        # Test API endpoint
        response = requests.get(f"{{server_url}}/api/activity?hours=1&limit=1", 
                              headers=headers, timeout=10)
        if response.status_code == 200:
            print("✅ API authentication successful")
            return True
        else:
            print(f"❌ API authentication failed: {{response.status_code}}")
            return False
            
    except Exception as e:
        print(f"❌ Connection failed: {{e}}")
        return False

if __name__ == '__main__':
    if test_connection():
        print("\\n🎉 Client configuration is ready for deployment!")
    else:
        print("\\n⚠️ Please check server status and network connectivity")
    input("\\nPress Enter to exit...")
"""
    
    test_path = os.path.join(output_dir, "test_connection.py")
    with open(test_path, 'w') as f:
        f.write(test_script)
    
    # Create README
    readme_content = f"""# Browser Tracking Client Configuration

## Server Information
- Server URL: https://{domain}:5000
- API Token: {api_token}

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
The config.json file is pre-configured for your server.
No manual configuration needed.

## Troubleshooting
1. Ensure internet connectivity
2. Check firewall settings (allow outbound HTTPS)
3. Verify server URL is accessible from target network
4. Check API token matches server configuration

## Support
- Check logs in browser_tracking.log
- Run test_connection.py for diagnostics
- Verify network connectivity to {domain}
"""
    
    readme_path = os.path.join(output_dir, "README.txt")
    with open(readme_path, 'w') as f:
        f.write(readme_content)
    
    print(f"\n✅ Client configuration generated successfully!")
    print(f"📁 Location: {os.path.abspath(output_dir)}")
    print(f"🌐 Server URL: https://{domain}:5000")
    print(f"🔑 API Token: {api_token}")
    
    return output_dir

def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_client_config.py <domain> <api_token>")
        print("Example: python generate_client_config.py monitoring.yourisp.com GWcuPABCAitXmqdKX5eJu8tQAW5zzMAfswGc-Ik9IfU")
        sys.exit(1)
    
    domain = sys.argv[1]
    api_token = sys.argv[2]
    
    generate_client_config(domain, api_token)

if __name__ == '__main__':
    main()
