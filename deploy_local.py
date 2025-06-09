import os
import sys
import json
import socket
import subprocess
import threading
import time
from datetime import datetime

def get_local_ip():
    """Get local IP address"""
    try:
        # Connect to a remote server to get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"

def get_public_ip():
    """Get public IP address"""
    try:
        import requests
        response = requests.get('https://api.ipify.org', timeout=10)
        return response.text.strip()
    except:
        return None

def check_port_open(ip, port):
    """Check if port is accessible"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except:
        return False

def update_config_for_local_deployment(local_ip, port=5000):
    """Update configuration for local deployment"""
    
    # Update main config
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        config['server']['host'] = '0.0.0.0'  # Listen on all interfaces
        config['server']['port'] = port
        config['client']['server_url'] = f'http://{local_ip}:{port}'
        
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)
        
        print(f"✅ Updated main config for {local_ip}:{port}")
        
    except Exception as e:
        print(f"❌ Error updating main config: {e}")
        return False
    
    # Generate client config
    try:
        api_token = config['security']['api_token']
        
        client_config = {
            "server": {
                "host": "0.0.0.0",
                "port": port,
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
                "server_url": f"http://{local_ip}:{port}",
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
        
        # Create local client configs directory
        os.makedirs('local_client_configs', exist_ok=True)
        
        with open('local_client_configs/config.json', 'w') as f:
            json.dump(client_config, f, indent=4)
        
        # Copy client files
        import shutil
        client_files = [
            'agent.py', 'browser_reader.py', 'system_info.py',
            'network_client.py', 'logger.py', 'installer.py', 'requirements.txt'
        ]
        
        for file in client_files:
            if os.path.exists(file):
                shutil.copy2(file, 'local_client_configs/')
        
        print(f"✅ Generated client config for {local_ip}:{port}")
        return True
        
    except Exception as e:
        print(f"❌ Error generating client config: {e}")
        return False

def create_client_installer(local_ip, port, api_token):
    """Create client installer script"""
    
    installer_script = f"""@echo off
echo Browser Tracking Client Installer (Local Server)
echo Server: http://{local_ip}:{port}
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
curl -f http://{local_ip}:{port}/health
if %errorLevel% == 0 (
    echo ✅ Server is reachable
) else (
    echo ❌ Cannot reach server at http://{local_ip}:{port}
    echo Please check:
    echo 1. Server is running
    echo 2. Firewall allows port {port}
    echo 3. Network connectivity
    pause
    exit /b 1
)

REM Install client
echo Installing Browser Tracking Client...
python installer.py

echo.
echo Installation complete!
echo The client will connect to: http://{local_ip}:{port}
echo.
pause
"""
    
    with open('local_client_configs/install_client.bat', 'w') as f:
        f.write(installer_script)
    
    # Create test script
    test_script = f"""import requests
import json

def test_connection():
    server_url = "http://{local_ip}:{port}"
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
    
    with open('local_client_configs/test_connection.py', 'w', encoding='utf-8') as f:
        f.write(test_script)

def check_firewall_rules(port):
    """Check Windows firewall rules"""
    try:
        # Check if port is allowed in firewall
        result = subprocess.run([
            'netsh', 'advfirewall', 'firewall', 'show', 'rule', 
            f'name=Browser Tracking Server Port {port}'
        ], capture_output=True, text=True)
        
        if 'No rules match' in result.stdout:
            print(f"⚠️ Firewall rule for port {port} not found")
            
            # Ask user if they want to add firewall rule
            response = input(f"Add Windows firewall rule for port {port}? (y/n): ").lower()
            if response == 'y':
                add_firewall_rule(port)
        else:
            print(f"✅ Firewall rule for port {port} exists")
            
    except Exception as e:
        print(f"⚠️ Could not check firewall rules: {e}")

def add_firewall_rule(port):
    """Add Windows firewall rule"""
    try:
        # Add inbound rule
        result = subprocess.run([
            'netsh', 'advfirewall', 'firewall', 'add', 'rule',
            f'name=Browser Tracking Server Port {port}',
            'dir=in', 'action=allow', 'protocol=TCP', f'localport={port}'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Added firewall rule for port {port}")
        else:
            print(f"❌ Failed to add firewall rule: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error adding firewall rule: {e}")

def main():
    """Main deployment function"""
    print("=== Browser Tracking System - Local Deployment ===")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Get network information
    local_ip = get_local_ip()
    public_ip = get_public_ip()
    port = 5000
    
    print(f"🌐 Network Information:")
    print(f"   Local IP: {local_ip}")
    print(f"   Public IP: {public_ip}")
    print(f"   Server Port: {port}")
    print()
    
    # Update configurations
    print("🔧 Updating configurations...")
    if not update_config_for_local_deployment(local_ip, port):
        print("❌ Failed to update configurations")
        return False
    
    # Create client installer
    print("📦 Creating client installer...")
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        api_token = config['security']['api_token']
        create_client_installer(local_ip, port, api_token)
        print("✅ Client installer created")
    except Exception as e:
        print(f"❌ Error creating client installer: {e}")
    
    # Check firewall
    print("🔥 Checking firewall rules...")
    check_firewall_rules(port)
    
    print()
    print("=== Deployment Information ===")
    print(f"🖥️  Server URL (Local Network): http://{local_ip}:{port}")
    if public_ip:
        print(f"🌍 Server URL (Public): http://{public_ip}:{port}")
        print(f"   ⚠️  Requires router port forwarding for external access")
    print(f"🔑 API Token: {api_token}")
    print(f"📁 Client Files: local_client_configs/")
    print()
    
    print("=== Next Steps ===")
    print("1. Start server: python server.py")
    print(f"2. Test locally: curl http://{local_ip}:{port}/health")
    print("3. Copy 'local_client_configs' folder to target PCs")
    print("4. Run 'install_client.bat' on target PCs")
    print("5. Monitor with: python monitor_gui.py")
    print()
    
    # Option to start server immediately
    start_server = input("Start server now? (y/n): ").lower()
    if start_server == 'y':
        print("🚀 Starting server...")
        try:
            subprocess.Popen([sys.executable, 'server.py'])
            print("✅ Server started in background")
            
            # Wait a moment and test
            time.sleep(3)
            
            try:
                import requests
                response = requests.get(f'http://{local_ip}:{port}/health', timeout=5)
                if response.status_code == 200:
                    print("✅ Server is responding")
                    print(f"📊 Health check: {response.json()}")
                else:
                    print(f"⚠️ Server returned status {response.status_code}")
            except Exception as e:
                print(f"⚠️ Could not test server: {e}")
                
        except Exception as e:
            print(f"❌ Error starting server: {e}")
    
    print()
    print("🎉 Local deployment setup complete!")
    return True

if __name__ == '__main__':
    success = main()
    input("\nPress Enter to exit...")
    sys.exit(0 if success else 1)
