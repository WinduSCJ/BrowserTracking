# Browser Tracking Client Configuration (Vercel)

## Server Information
- Server URL: https://browser-tracking-obz04i0k1-winduajis-projects.vercel.app
- API Token: BrowserTracker2024SecureToken
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
3. Verify server URL is accessible: https://browser-tracking-obz04i0k1-winduajis-projects.vercel.app/health
4. Check API token matches server configuration

## Support
- Check logs in browser_tracking.log
- Run test_connection.py for diagnostics
- Verify network connectivity to Vercel
