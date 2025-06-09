# Cloud Provider Setup Guide

## 🚀 **Option 1: DigitalOcean (Recommended)**

### Advantages:
- Simple setup
- $5/month droplet sufficient
- Good network performance in Asia
- Easy DNS management

### Setup Steps:
```bash
# 1. Create Droplet
# - Ubuntu 22.04 LTS
# - Basic plan: $5/month (1GB RAM, 1 vCPU)
# - Choose datacenter closest to your location

# 2. Connect via SSH
ssh root@your-droplet-ip

# 3. Upload deployment files
scp -r . root@your-droplet-ip:/root/browser-tracking/

# 4. Run deployment
cd /root/browser-tracking
chmod +x deploy_cloud.sh
./deploy_cloud.sh monitoring.yourisp.com admin@yourisp.com

# 5. Configure DNS
# Add A record: monitoring.yourisp.com -> your-droplet-ip
```

## 🌐 **Option 2: AWS EC2**

### Setup Steps:
```bash
# 1. Launch EC2 Instance
# - Ubuntu Server 22.04 LTS
# - t2.micro (free tier) or t3.small
# - Security Group: Allow ports 22, 80, 443, 5000

# 2. Connect and deploy
ssh -i your-key.pem ubuntu@your-ec2-ip
sudo apt update
git clone your-repo
cd browser-tracking
sudo ./deploy_cloud.sh monitoring.yourisp.com admin@yourisp.com

# 3. Configure Route 53 or external DNS
```

## ☁️ **Option 3: Google Cloud Platform**

### Setup Steps:
```bash
# 1. Create Compute Engine VM
# - Ubuntu 22.04 LTS
# - e2-micro (free tier) or e2-small
# - Allow HTTP/HTTPS traffic

# 2. Deploy
gcloud compute ssh your-instance
sudo apt update
# Upload files and run deploy_cloud.sh

# 3. Configure Cloud DNS
```

## 🔧 **Option 4: VPS Providers (Vultr, Linode, etc.)**

### General Steps:
```bash
# 1. Create VPS with Ubuntu 22.04
# 2. Upload deployment files
# 3. Run deploy_cloud.sh
# 4. Configure DNS with your domain provider
```

## 🏠 **Option 5: Self-Hosted with Dynamic DNS**

### For home server with dynamic IP:
```bash
# 1. Setup Dynamic DNS (DuckDNS, No-IP, etc.)
# 2. Configure router port forwarding: 80, 443, 5000
# 3. Run deployment script
# 4. Use dynamic DNS domain for clients
```

## 📋 **Quick Start Commands**

### DigitalOcean One-Click Setup:
```bash
# Create droplet and run:
curl -sSL https://raw.githubusercontent.com/your-repo/deploy_cloud.sh | bash -s monitoring.yourisp.com admin@yourisp.com
```

### Manual Setup:
```bash
# 1. Upload files to server
scp -r . user@server:/path/to/browser-tracking/

# 2. SSH to server
ssh user@server

# 3. Run deployment
cd /path/to/browser-tracking
chmod +x deploy_cloud.sh
./deploy_cloud.sh your-domain.com your-email@domain.com
```

## 🔒 **Security Considerations**

### Firewall Rules:
```bash
# Allow only necessary ports
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP (redirects to HTTPS)
sudo ufw allow 443/tcp  # HTTPS
sudo ufw allow 5000/tcp # API (can be restricted to 443 only)
sudo ufw enable
```

### SSL Certificate Auto-Renewal:
```bash
# Add to crontab
echo "0 12 * * * /usr/bin/certbot renew --quiet && docker-compose restart nginx" | crontab -
```

## 💰 **Cost Estimates**

| Provider | Plan | Monthly Cost | Specs |
|----------|------|--------------|-------|
| DigitalOcean | Basic Droplet | $5 | 1GB RAM, 1 vCPU |
| AWS | t2.micro | Free/~$8 | 1GB RAM, 1 vCPU |
| Google Cloud | e2-micro | Free/~$6 | 1GB RAM, 1 vCPU |
| Vultr | Regular | $5 | 1GB RAM, 1 vCPU |
| Linode | Nanode | $5 | 1GB RAM, 1 vCPU |

## 🌍 **Recommended Datacenter Locations**

For Indonesia/Asia:
- DigitalOcean: Singapore
- AWS: ap-southeast-1 (Singapore)
- Google Cloud: asia-southeast1 (Singapore)
- Vultr: Singapore
- Linode: Singapore

## 📊 **Performance Monitoring**

### Monitor server resources:
```bash
# Check system resources
htop
df -h
docker stats

# Check application logs
docker-compose logs -f browser-tracking-server

# Monitor SSL certificate expiry
openssl x509 -in ./ssl/monitoring.yourisp.com.pem -text -noout | grep "Not After"
```
