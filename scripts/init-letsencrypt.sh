#!/bin/bash

# Initialize Let's Encrypt certificates for lsiddd.space
# This script should be run once before starting the production deployment

set -e

DOMAIN="lsiddd.space"
EMAIL="admin@lsiddd.space"  # Change this to your email
STAGING=${1:-0}  # Set to 1 for staging certificates (testing)

# Create directories
mkdir -p certbot/conf certbot/www

echo "### Checking for existing certificates for $DOMAIN..."
if [ -d "certbot/conf/live/$DOMAIN" ]; then
    echo "Existing certificates found for $DOMAIN. Skipping certificate generation."
    echo "To force renewal, delete the certbot/conf/live/$DOMAIN directory."
    exit 0
fi

echo "### Downloading recommended TLS parameters..."
mkdir -p certbot/conf
if [ ! -e "certbot/conf/options-ssl-nginx.conf" ] || [ ! -e "certbot/conf/ssl-dhparams.pem" ]; then
    curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf > certbot/conf/options-ssl-nginx.conf
    curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot/certbot/ssl-dhparams.pem > certbot/conf/ssl-dhparams.pem
fi

echo "### Creating temporary nginx configuration..."
cat > nginx/nginx-temp.conf << EOF
events {
    worker_connections 1024;
}

http {
    server {
        listen 80;
        server_name $DOMAIN www.$DOMAIN;

        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }

        location / {
            return 404;
        }
    }
}
EOF

echo "### Starting temporary nginx..."
docker-compose -f docker-compose.yml -f docker-compose.prod.yml run --rm --service-ports nginx nginx -c /etc/nginx/nginx-temp.conf -g "daemon off;" &
NGINX_PID=$!

# Wait for nginx to start
sleep 5

echo "### Requesting Let's Encrypt certificate for $DOMAIN..."

# Select appropriate certificate server
if [ $STAGING != "0" ]; then
    echo "### Using staging server for testing..."
    CERT_SERVER="https://acme-staging-v02.api.letsencrypt.org/directory"
else
    echo "### Using production server..."
    CERT_SERVER="https://acme-v02.api.letsencrypt.org/directory"
fi

# Request certificate
docker-compose -f docker-compose.yml -f docker-compose.prod.yml run --rm certbot \
    certbot certonly --webroot -w /var/www/certbot \
    --server $CERT_SERVER \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    -d $DOMAIN \
    -d www.$DOMAIN

# Stop temporary nginx
kill $NGINX_PID 2>/dev/null || true

echo "### Certificate obtained successfully!"
echo "### Starting production deployment..."

# Restore original nginx config and start production services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

echo "### Deployment complete!"
echo "### Your application should be available at: https://$DOMAIN"
echo "### Certificates will auto-renew every 12 hours"