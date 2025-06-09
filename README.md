# Browser Tracking System

Sistem monitoring riwayat browsing untuk jaringan internal yang terdiri dari server pusat dan agent client yang berjalan secara background.

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/WinduSCJ/BrowserTracking.git)

## 🎯 Fitur Utama

- **Server Terpusat**: Menerima dan menyimpan data browsing dari multiple client
- **Agent Background**: Berjalan diam-diam di background tanpa mengganggu user
- **Auto-Install**: Installer otomatis untuk Python dan dependencies
- **Multi-Profile**: Mendukung multiple Chrome profiles dan Gmail accounts
- **Real-time Monitoring**: GUI monitoring untuk melihat aktivitas real-time
- **Secure**: Autentikasi token dan enkripsi data
- **Cross-Network**: Tidak tergantung pada segment jaringan yang sama

## 📁 Struktur File

```
Browser Tracking/
├── server.py              # Server API utama
├── database.py            # Database management
├── agent.py               # Client agent
├── browser_reader.py      # Chrome history reader
├── system_info.py         # System information collector
├── network_client.py      # Network communication
├── logger.py              # Logging system
├── installer.py           # Auto installer
├── build_exe.py           # Build executable
├── test_system.py         # Testing suite
├── monitor_gui.py         # Monitoring GUI
├── config.json            # Configuration
├── requirements.txt       # Python dependencies
└── README.md              # Dokumentasi
```

## 🚀 Quick Start

### Option 1: Vercel Deployment (Recommended)

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/WinduSCJ/BrowserTracking.git)

1. Click "Deploy with Vercel" button above
2. Connect your GitHub account
3. Deploy the project
4. Get your Vercel URL (e.g., `https://browser-tracking-abc123.vercel.app`)
5. Generate client configs: `python generate_vercel_client.py your-vercel-url`
6. Deploy clients to target PCs

### Option 2: Local Server

```bash
# Install dependencies
pip install -r requirements.txt

# Deploy locally
python deploy_local.py

# Monitor activity
python monitor_gui.py
```

### Option 3: Cloud Server

```bash
# Deploy to cloud (DigitalOcean, AWS, etc.)
./deploy_cloud.sh your-domain.com your-email@domain.com
```

## ⚙️ Konfigurasi

Edit `config.json` sebelum deployment:

```json
{
    "server": {
        "host": "0.0.0.0",
        "port": 5000
    },
    "client": {
        "server_url": "http://your-server.com:5000",
        "api_token": "your-secure-token",
        "check_interval": 300
    },
    "security": {
        "api_token": "your-secure-token"
    }
}
```

## 🔧 Komponen Sistem

### Server Components

- **server.py**: Flask API server untuk menerima data
- **database.py**: SQLite database management
- **monitor_gui.py**: GUI untuk monitoring aktivitas

### Client Components

- **agent.py**: Main agent yang berjalan di background
- **browser_reader.py**: Membaca history Chrome
- **system_info.py**: Mengumpulkan info sistem
- **network_client.py**: Komunikasi dengan server

### Deployment Tools

- **installer.py**: Auto-installer Python dan agent
- **build_exe.py**: Build executable dengan PyInstaller

## 📊 Database Schema

### Clients Table
- id, hostname, mac_address, local_ip, username, os_info
- first_seen, last_seen

### Browsing History Table
- id, client_id, url, title, visit_time
- browser_type, profile_name, gmail_account

### Browser Profiles Table
- id, client_id, profile_name, profile_path
- gmail_accounts, is_active

## 🔒 Keamanan

- **Token Authentication**: Semua API calls menggunakan Bearer token
- **HTTPS Support**: Konfigurasi SSL/TLS untuk production
- **Data Encryption**: Opsi enkripsi untuk data sensitif
- **Access Control**: Pembatasan akses berdasarkan IP/network

## 🌐 Network Requirements

- **Server**: Port 5000 (atau sesuai konfigurasi)
- **Client**: Akses HTTP/HTTPS ke server
- **Firewall**: Buka port server untuk client access

## 📱 Monitoring GUI

GUI monitoring menyediakan:
- **Recent Activity**: Daftar aktivitas browsing terbaru
- **Client Status**: Status semua client yang terdaftar
- **Statistics**: Statistik penggunaan dan top websites
- **Auto Refresh**: Refresh otomatis setiap 30 detik

## 🧪 Testing

```bash
# Test semua komponen
python test_system.py

# Test individual components
python -c "from browser_reader import ChromeHistoryReader; print(ChromeHistoryReader().get_recent_history())"
```

## 📦 Build & Distribution

```bash
# Build semua executable
python build_exe.py

# Output files:
# - BrowserTrackingServer.exe
# - BrowserTrackingInstaller.exe
# - BrowserTrackingAgent.exe
```

## 🔄 Deployment Workflow

1. **Server Setup**:
   - Install di server monitoring
   - Konfigurasi database dan network
   - Start server service

2. **Client Deployment**:
   - Copy installer ke target PC
   - Run installer sebagai admin
   - Agent auto-start pada boot

3. **Monitoring**:
   - Akses GUI monitoring
   - Monitor aktivitas real-time
   - Analisis data browsing

## ⚠️ Catatan Penting

- **Privacy**: Sistem ini untuk monitoring internal, pastikan compliance dengan kebijakan privacy
- **Performance**: Agent menggunakan minimal resources
- **Compatibility**: Tested pada Windows 10/11 dengan Chrome
- **Network**: Pastikan connectivity antara client dan server

## 🐛 Troubleshooting

### Client tidak connect ke server
- Check network connectivity
- Verify server URL dan port
- Check firewall settings

### Agent tidak start otomatis
- Run installer sebagai administrator
- Check Windows startup folder
- Verify Python installation

### Data tidak muncul di monitoring
- Check agent logs
- Verify database permissions
- Test API endpoints

## 📞 Support

Untuk support dan troubleshooting:
1. Check log files di installation directory
2. Run test_system.py untuk diagnosa
3. Verify network connectivity
4. Check configuration files

## 📄 License

Internal use only - Sesuai kebijakan perusahaan untuk monitoring jaringan internal.
