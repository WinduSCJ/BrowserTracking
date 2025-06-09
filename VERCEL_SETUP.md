# 🚀 Vercel Setup Instructions

## Issue: Authentication Required

Vercel project memerlukan authentication. Untuk memperbaiki ini:

### Option 1: Disable Vercel Authentication (Recommended)

1. **Go to Vercel Dashboard**: https://vercel.com/winduajis-projects/browser-tracking
2. **Settings Tab** → **General**
3. **Scroll to "Deployment Protection"**
4. **Disable "Vercel Authentication"** atau set ke "None"
5. **Save Changes**
6. **Redeploy** project

### Option 2: Set Environment Variables

1. **Go to Vercel Dashboard**: https://vercel.com/winduajis-projects/browser-tracking
2. **Settings Tab** → **Environment Variables**
3. **Add these variables**:
   ```
   VERCEL_ENV=production
   DISABLE_AUTH=true
   ```
4. **Redeploy** project

### Option 3: Use Custom Domain (Advanced)

1. **Add Custom Domain** di Vercel settings
2. **Point DNS** ke Vercel
3. **Custom domain** tidak memerlukan Vercel auth

## Current URLs:

- **Project Dashboard**: https://vercel.com/winduajis-projects/browser-tracking
- **Current Deployment**: https://browser-tracking-obz04i0k1-winduajis-projects.vercel.app
- **GitHub Repo**: https://github.com/WinduSCJ/BrowserTracking

## After Fixing Authentication:

1. **Test Health Endpoint**:
   ```bash
   curl https://browser-tracking-obz04i0k1-winduajis-projects.vercel.app/health
   ```

2. **Test API Endpoint**:
   ```bash
   curl -H "Authorization: Bearer BrowserTracker2024SecureToken" \
        https://browser-tracking-obz04i0k1-winduajis-projects.vercel.app/api/activity
   ```

3. **Generate New Client Configs**:
   ```bash
   python generate_vercel_client.py browser-tracking-obz04i0k1-winduajis-projects.vercel.app
   ```

4. **Deploy Clients**:
   - Copy `vercel_client_configs/` to target PCs
   - Run `install_client.bat` as Administrator

## Alternative: Use Different Deployment

If Vercel authentication cannot be disabled:

### Railway Deployment:
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

### Render Deployment:
1. Connect GitHub repo to Render
2. Deploy as Web Service
3. Use Python environment

### Heroku Deployment:
```bash
# Install Heroku CLI
# Create Procfile: web: python app.py
heroku create browser-tracking-app
git push heroku main
```

## Next Steps:

1. **Fix Vercel authentication** using Option 1 above
2. **Test deployment** with provided URLs
3. **Deploy clients** to target PCs
4. **Monitor activity** via API endpoints

The system is ready - just need to fix the authentication issue!
