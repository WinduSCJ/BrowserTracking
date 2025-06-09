#!/bin/bash

# Browser Tracking System - Cloud Deployment Script
# Usage: ./deploy_cloud.sh [domain] [email]

set -e

DOMAIN=${1:-monitoring.yourisp.com}
EMAIL=${2:-admin@yourisp.com}

echo "=== Browser Tracking System - Cloud Deployment ==="
echo "Domain: $DOMAIN"
echo "Email: $EMAIL"
echo ""

# Update system
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Docker
echo "Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
fi

# Install Docker Compose
echo "Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Install Certbot for SSL
echo "Installing Certbot..."
sudo apt install -y certbot python3-certbot-nginx

# Create SSL directory
echo "Creating SSL directory..."
sudo mkdir -p /etc/ssl/browser-tracking
mkdir -p ./ssl

# Generate SSL certificate with Let's Encrypt
echo "Generating SSL certificate for $DOMAIN..."
if [ ! -f "./ssl/$DOMAIN.pem" ]; then
    sudo certbot certonly --standalone \
        --email $EMAIL \
        --agree-tos \
        --no-eff-email \
        -d $DOMAIN
    
    # Copy certificates
    sudo cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem ./ssl/$DOMAIN.pem
    sudo cp /etc/letsencrypt/live/$DOMAIN/privkey.pem ./ssl/$DOMAIN.key
    sudo chown $USER:$USER ./ssl/$DOMAIN.*
fi

# Update nginx configuration with actual domain
echo "Updating nginx configuration..."
sed -i "s/monitoring.yourisp.com/$DOMAIN/g" nginx.conf

# Update cloud config with actual domain
echo "Updating cloud configuration..."
sed -i "s/monitoring.yourisp.com/$DOMAIN/g" cloud_config.json
sed -i "s|/etc/ssl/certs/monitoring.yourisp.com.pem|/etc/ssl/certs/$DOMAIN.pem|g" cloud_config.json
sed -i "s|/etc/ssl/private/monitoring.yourisp.com.key|/etc/ssl/certs/$DOMAIN.key|g" cloud_config.json

# Create firewall rules
echo "Configuring firewall..."
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 5000/tcp
sudo ufw --force enable

# Build and start services
echo "Building and starting services..."
docker-compose down || true
docker-compose build
docker-compose up -d

# Wait for services to start
echo "Waiting for services to start..."
sleep 30

# Test deployment
echo "Testing deployment..."
if curl -f https://$DOMAIN/health; then
    echo "✅ Deployment successful!"
    echo ""
    echo "=== Deployment Information ==="
    echo "Server URL: https://$DOMAIN:5000"
    echo "Health Check: https://$DOMAIN/health"
    echo "API Endpoint: https://$DOMAIN/api/"
    echo ""
    echo "=== Client Configuration ==="
    echo "Update your client config.json with:"
    echo "\"server_url\": \"https://$DOMAIN:5000\""
    echo ""
    echo "=== SSL Certificate Renewal ==="
    echo "Add to crontab for auto-renewal:"
    echo "0 12 * * * /usr/bin/certbot renew --quiet && docker-compose restart nginx"
else
    echo "❌ Deployment failed!"
    echo "Check logs with: docker-compose logs"
    exit 1
fi

echo ""
echo "=== Next Steps ==="
echo "1. Update DNS A record: $DOMAIN -> $(curl -s ifconfig.me)"
echo "2. Update client configurations with server URL"
echo "3. Deploy clients to target PCs"
echo "4. Monitor logs: docker-compose logs -f"
