#!/bin/bash

# Deploy GuardianAI in production mode with HTTPS
# Usage: ./scripts/deploy.sh [staging|production]

set -e

MODE=${1:-production}
DOMAIN="lsiddd.space"

echo "🚀 Starting GuardianAI deployment in $MODE mode..."

# Check if Docker and Docker Compose are available
if ! command -v docker &> /dev/null || ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker and Docker Compose are required. Please install them first."
    exit 1
fi

# Check if domain points to this server (optional check)
echo "🌐 Checking domain configuration for $DOMAIN..."
SERVER_IP=$(curl -s ifconfig.me)
DOMAIN_IP=$(dig +short $DOMAIN | tail -n1)

if [ "$SERVER_IP" != "$DOMAIN_IP" ]; then
    echo "⚠️  Warning: Domain $DOMAIN (IP: $DOMAIN_IP) does not point to this server (IP: $SERVER_IP)"
    echo "   Make sure your DNS is configured correctly before proceeding."
    read -p "   Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create necessary directories
mkdir -p certbot/conf certbot/www nginx/ssl

# Check for existing certificates
if [ ! -d "certbot/conf/live/$DOMAIN" ]; then
    echo "📜 No SSL certificates found. Initializing Let's Encrypt..."
    
    if [ "$MODE" == "staging" ]; then
        echo "🧪 Using staging certificates for testing..."
        ./scripts/init-letsencrypt.sh 1
    else
        echo "🔒 Using production certificates..."
        ./scripts/init-letsencrypt.sh 0
    fi
else
    echo "📜 SSL certificates found. Skipping certificate generation."
fi

# Build and start services
echo "🔨 Building and starting services..."
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Health check
echo "🩺 Performing health checks..."
if curl -f -s https://$DOMAIN/health > /dev/null; then
    echo "✅ HTTPS health check passed"
else
    echo "⚠️  HTTPS health check failed, but services may still be starting..."
fi

# Display status
echo ""
echo "📊 Deployment Status:"
docker-compose -f docker-compose.yml -f docker-compose.prod.yml ps

echo ""
echo "🎉 Deployment complete!"
echo ""
echo "🌐 Your application is available at:"
echo "   • HTTPS: https://$DOMAIN"
echo "   • HTTP:  http://$DOMAIN (redirects to HTTPS)"
echo ""
echo "📋 Management commands:"
echo "   • View logs:    docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs -f"
echo "   • Stop:         docker-compose -f docker-compose.yml -f docker-compose.prod.yml down"
echo "   • Restart:      docker-compose -f docker-compose.yml -f docker-compose.prod.yml restart"
echo "   • SSL renewal:  docker-compose -f docker-compose.yml -f docker-compose.prod.yml exec certbot certbot renew"
echo ""
echo "🔒 SSL certificates will automatically renew every 12 hours."