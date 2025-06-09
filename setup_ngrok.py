import os
import sys
import subprocess
import urllib.request
import zipfile
import json

def download_ngrok():
    """Download and setup ngrok"""
    print("=== Setting up Ngrok for Quick Deployment ===")
    
    # Check if ngrok already exists
    if os.path.exists("ngrok.exe"):
        print("✅ Ngrok already downloaded")
        return True
    
    print("📥 Downloading ngrok...")
    
    # Download ngrok for Windows
    ngrok_url = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip"
    
    try:
        urllib.request.urlretrieve(ngrok_url, "ngrok.zip")
        print("✅ Downloaded ngrok.zip")
        
        # Extract ngrok
        with zipfile.ZipFile("ngrok.zip", 'r') as zip_ref:
            zip_ref.extractall(".")
        
        # Clean up
        os.remove("ngrok.zip")
        
        print("✅ Ngrok extracted successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error downloading ngrok: {e}")
        return False

def setup_ngrok_auth():
    """Setup ngrok authentication"""
    print("\n🔑 Ngrok Authentication Setup")
    print("1. Go to https://dashboard.ngrok.com/get-started/your-authtoken")
    print("2. Sign up for free account")
    print("3. Copy your authtoken")
    
    authtoken = input("\nEnter your ngrok authtoken (or press Enter to skip): ").strip()
    
    if authtoken:
        try:
            result = subprocess.run(["ngrok.exe", "config", "add-authtoken", authtoken], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Authtoken configured successfully")
                return True
            else:
                print(f"❌ Error configuring authtoken: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    else:
        print("⚠️ Skipping authtoken setup (limited to 2 hours)")
        return True

def start_ngrok_tunnel():
    """Start ngrok tunnel"""
    print("\n🚀 Starting ngrok tunnel...")
    
    try:
        # Start ngrok in background
        process = subprocess.Popen(["ngrok.exe", "http", "5000", "--log=stdout"], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 text=True)
        
        print("✅ Ngrok tunnel started")
        print("⏳ Waiting for tunnel to establish...")
        
        # Wait a bit for tunnel to establish
        import time
        time.sleep(5)
        
        # Get tunnel URL
        try:
            import requests
            response = requests.get("http://localhost:4040/api/tunnels")
            tunnels = response.json()
            
            if tunnels.get('tunnels'):
                tunnel_url = tunnels['tunnels'][0]['public_url']
                if tunnel_url.startswith('http://'):
                    tunnel_url = tunnel_url.replace('http://', 'https://')
                
                print(f"🌐 Tunnel URL: {tunnel_url}")
                return tunnel_url, process
            else:
                print("❌ No tunnels found")
                return None, process
                
        except Exception as e:
            print(f"⚠️ Could not get tunnel URL automatically: {e}")
            print("📋 Check ngrok dashboard at: http://localhost:4040")
            return "https://your-ngrok-url.ngrok.io", process
            
    except Exception as e:
        print(f"❌ Error starting ngrok: {e}")
        return None, None

def main():
    """Main setup function"""
    if not download_ngrok():
        print("❌ Failed to download ngrok")
        return False
    
    if not setup_ngrok_auth():
        print("⚠️ Ngrok auth setup incomplete")
    
    tunnel_url, process = start_ngrok_tunnel()
    
    if tunnel_url:
        print(f"\n🎉 Ngrok setup complete!")
        print(f"📡 Public URL: {tunnel_url}")
        print(f"🔧 Local Server: http://localhost:5000")
        print(f"📊 Ngrok Dashboard: http://localhost:4040")
        
        # Update client config
        try:
            domain = tunnel_url.replace('https://', '').replace('http://', '')
            print(f"\n🔄 Updating client configuration for: {domain}")
            
            # Generate client config for ngrok URL
            import subprocess
            result = subprocess.run([
                sys.executable, "generate_client_config.py", 
                domain, "GWcuPABCAitXmqdKX5eJu8tQAW5zzMAfswGc-Ik9IfU"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Client configuration updated")
            else:
                print(f"⚠️ Client config update failed: {result.stderr}")
                
        except Exception as e:
            print(f"⚠️ Could not update client config: {e}")
        
        print(f"\n📋 Next Steps:")
        print(f"1. Start your server: python server.py")
        print(f"2. Test connection: curl {tunnel_url}/health")
        print(f"3. Deploy clients with updated config")
        print(f"4. Monitor at: http://localhost:4040")
        
        return True
    else:
        print("❌ Failed to start ngrok tunnel")
        return False

if __name__ == '__main__':
    main()
    input("\nPress Enter to exit...")
