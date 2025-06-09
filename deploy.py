import os
import sys
import shutil
import json
import subprocess
from pathlib import Path

class BrowserTrackingDeployer:
    def __init__(self):
        self.project_dir = os.path.dirname(os.path.abspath(__file__))
        self.deploy_dir = os.path.join(self.project_dir, "deployment")
        
    def create_deployment_package(self):
        """Create deployment package"""
        print("Creating deployment package...")
        
        # Create deployment directory
        if os.path.exists(self.deploy_dir):
            shutil.rmtree(self.deploy_dir)
        os.makedirs(self.deploy_dir)
        
        # Server package
        server_dir = os.path.join(self.deploy_dir, "server")
        os.makedirs(server_dir)
        
        server_files = [
            'server.py', 'database.py', 'logger.py', 'monitor_gui.py',
            'config.json', 'requirements.txt', 'run_system.py'
        ]
        
        for file in server_files:
            if os.path.exists(file):
                shutil.copy2(file, server_dir)
        
        # Client package
        client_dir = os.path.join(self.deploy_dir, "client")
        os.makedirs(client_dir)
        
        client_files = [
            'agent.py', 'browser_reader.py', 'system_info.py',
            'network_client.py', 'logger.py', 'installer.py',
            'config.json', 'requirements.txt'
        ]
        
        for file in client_files:
            if os.path.exists(file):
                shutil.copy2(file, client_dir)
        
        # Tools package
        tools_dir = os.path.join(self.deploy_dir, "tools")
        os.makedirs(tools_dir)
        
        tools_files = [
            'build_exe.py', 'test_system.py', 'deploy.py'
        ]
        
        for file in tools_files:
            if os.path.exists(file):
                shutil.copy2(file, tools_dir)
        
        print(f"Deployment package created in: {self.deploy_dir}")
        return True
    
    def create_server_config(self, server_ip, port=5000):
        """Create server configuration"""
        config_path = os.path.join(self.deploy_dir, "server", "config.json")
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Update server config
            config['server']['host'] = "0.0.0.0"
            config['server']['port'] = port
            
            # Update client config template
            config['client']['server_url'] = f"http://{server_ip}:{port}"
            
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=4)
            
            print(f"Server config updated: {server_ip}:{port}")
            return True
            
        except Exception as e:
            print(f"Error updating server config: {e}")
            return False
    
    def create_client_config(self, server_url, api_token):
        """Create client configuration"""
        config_path = os.path.join(self.deploy_dir, "client", "config.json")
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Update client config
            config['client']['server_url'] = server_url
            config['client']['api_token'] = api_token
            config['security']['api_token'] = api_token
            
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=4)
            
            print(f"Client config updated: {server_url}")
            return True
            
        except Exception as e:
            print(f"Error updating client config: {e}")
            return False
    
    def create_installation_scripts(self):
        """Create installation scripts"""
        
        # Server installation script
        server_install = os.path.join(self.deploy_dir, "install_server.bat")
        server_script = """@echo off
echo Installing Browser Tracking Server...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found. Please install Python first.
    pause
    exit /b 1
)

REM Install dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

REM Create database
echo Initializing database...
python -c "from database import BrowserTrackingDB; BrowserTrackingDB()"

echo Server installation complete!
echo Run 'python server.py' to start the server
echo Or run 'python run_system.py' for GUI management
pause
"""
        
        with open(server_install, 'w') as f:
            f.write(server_script)
        
        # Client installation script
        client_install = os.path.join(self.deploy_dir, "install_client.bat")
        client_script = """@echo off
echo Installing Browser Tracking Client...

REM Run the installer
python installer.py

echo Client installation complete!
pause
"""
        
        with open(client_install, 'w') as f:
            f.write(client_script)
        
        print("Installation scripts created")
        return True
    
    def create_documentation(self):
        """Create deployment documentation"""
        
        readme_content = """# Browser Tracking System - Deployment Package

## Quick Setup Guide

### Server Setup (Run on monitoring server):

1. Copy the 'server' folder to your monitoring server
2. Edit config.json:
   - Set your server IP address
   - Change the API token for security
3. Run install_server.bat (or manually install dependencies)
4. Start server: python server.py
5. Optional: Use GUI manager: python run_system.py

### Client Deployment (Run on target PCs):

1. Copy the 'client' folder to target PC
2. Edit config.json:
   - Set server_url to your server address
   - Set api_token to match server token
3. Run install_client.bat (or python installer.py)
4. Client will auto-start on boot

### Configuration

#### Server Config (server/config.json):
```json
{
    "server": {
        "host": "0.0.0.0",
        "port": 5000
    },
    "security": {
        "api_token": "your-secure-token"
    }
}
```

#### Client Config (client/config.json):
```json
{
    "client": {
        "server_url": "http://your-server-ip:5000",
        "api_token": "your-secure-token",
        "check_interval": 300
    }
}
```

### Network Requirements

- Server: Open port 5000 (or configured port)
- Clients: HTTP access to server
- Firewall: Allow connections from client IPs

### Monitoring

- GUI Monitor: python monitor_gui.py
- System Manager: python run_system.py
- Database: SQLite file in server directory

### Troubleshooting

1. Check network connectivity between client and server
2. Verify API tokens match between client and server
3. Check firewall settings
4. Review log files for errors
5. Run test_system.py for diagnostics

### Security Notes

- Change default API token before deployment
- Use HTTPS in production (configure SSL in config.json)
- Restrict server access to internal network
- Monitor log files for suspicious activity

### Support

- Check log files in installation directories
- Run test scripts for diagnostics
- Verify configuration files
- Test network connectivity
"""
        
        readme_path = os.path.join(self.deploy_dir, "README.txt")
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        
        print("Documentation created")
        return True
    
    def interactive_setup(self):
        """Interactive deployment setup"""
        print("=== Browser Tracking System Deployment Setup ===\n")
        
        # Get server information
        server_ip = input("Enter server IP address (e.g., 192.168.1.100): ").strip()
        if not server_ip:
            server_ip = "localhost"
        
        port = input("Enter server port (default 5000): ").strip()
        if not port:
            port = 5000
        else:
            port = int(port)
        
        # Generate API token
        import secrets
        api_token = input("Enter API token (leave blank to generate): ").strip()
        if not api_token:
            api_token = secrets.token_urlsafe(32)
            print(f"Generated API token: {api_token}")
        
        # Create deployment package
        if not self.create_deployment_package():
            print("Failed to create deployment package")
            return False
        
        # Configure server
        if not self.create_server_config(server_ip, port):
            print("Failed to configure server")
            return False
        
        # Configure client
        server_url = f"http://{server_ip}:{port}"
        if not self.create_client_config(server_url, api_token):
            print("Failed to configure client")
            return False
        
        # Create installation scripts
        if not self.create_installation_scripts():
            print("Failed to create installation scripts")
            return False
        
        # Create documentation
        if not self.create_documentation():
            print("Failed to create documentation")
            return False
        
        print("\n=== Deployment Package Created Successfully! ===")
        print(f"Location: {self.deploy_dir}")
        print(f"Server URL: {server_url}")
        print(f"API Token: {api_token}")
        print("\nNext steps:")
        print("1. Copy 'server' folder to your monitoring server")
        print("2. Copy 'client' folder to target PCs")
        print("3. Run installation scripts on respective machines")
        print("4. Start monitoring!")
        
        return True

def main():
    deployer = BrowserTrackingDeployer()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        # Automatic deployment with default settings
        deployer.create_deployment_package()
        deployer.create_server_config("localhost")
        deployer.create_client_config("http://localhost:5000", "BrowserTracker2024SecureToken")
        deployer.create_installation_scripts()
        deployer.create_documentation()
        print("Automatic deployment package created")
    else:
        # Interactive setup
        deployer.interactive_setup()
    
    input("\nPress Enter to exit...")

if __name__ == '__main__':
    main()
