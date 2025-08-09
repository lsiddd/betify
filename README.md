# GuardianAI - Fraud Detection Dashboard

A comprehensive fraud detection and risk analysis platform built with Streamlit, featuring real-time monitoring, machine learning insights, and investigative tools.

## Features

- 🔍 **Real-time Fraud Monitoring** - Live transaction analysis and alert system
- 🤖 **ML-Powered Risk Scoring** - Advanced machine learning models for fraud detection
- 📊 **Interactive Dashboards** - Comprehensive analytics and visualization
- 🔍 **Investigation Tools** - Deep-dive analysis for suspected fraud cases
- 🌙 **Dark/Light Theme** - Customizable UI with theme switching
- 🔒 **Production HTTPS** - SSL-secured deployment with automatic certificate management

## Quick Start (Development)

```bash
# Clone and navigate to project
cd betify_demo

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

Access the app at `http://localhost:8501`

## Production Deployment (HTTPS)

### Prerequisites

- Docker and Docker Compose installed
- Domain `lsiddd.space` pointing to your server's IP address
- Ports 80 and 443 available

### Deploy with HTTPS

```bash
# Deploy to production with SSL certificates
./scripts/deploy.sh production

# Or deploy with staging certificates for testing
./scripts/deploy.sh staging
```

The deployment script will:
1. ✅ Check domain configuration
2. 🔒 Generate SSL certificates via Let's Encrypt
3. 🚀 Start all services with HTTPS
4. 🔄 Set up automatic certificate renewal

### Manual Deployment Steps

If you prefer manual deployment:

```bash
# 1. Initialize SSL certificates (one-time setup)
./scripts/init-letsencrypt.sh

# 2. Start production services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 3. Check status
docker-compose -f docker-compose.yml -f docker-compose.prod.yml ps
```

## Management Commands

```bash
# View application logs
docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs -f guardian-ai

# View all service logs
docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs -f

# Restart services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml restart

# Stop all services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml down

# Force SSL certificate renewal
docker-compose -f docker-compose.yml -f docker-compose.prod.yml exec certbot certbot renew --force-renewal
```

## Architecture

### Development Mode
- **Streamlit App**: Runs directly on port 8501
- **Hot Reload**: Code changes automatically reflected

### Production Mode  
- **Nginx Reverse Proxy**: Handles SSL termination and routing
- **Let's Encrypt**: Automatic SSL certificate management  
- **Streamlit App**: Runs in Docker container behind proxy
- **Auto-renewal**: Certificates renew automatically every 12 hours

## Security Features

- 🔒 **HTTPS Only**: All traffic redirected to SSL
- 🛡️ **Security Headers**: HSTS, CSP, XSS protection
- 🚫 **Rate Limiting**: Protection against abuse
- 🔐 **Modern TLS**: TLS 1.2/1.3 with strong cipher suites
- 🌐 **OCSP Stapling**: Improved SSL performance

## File Structure

```
betify_demo/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container configuration
├── docker-compose.yml          # Development setup
├── docker-compose.prod.yml     # Production override
├── nginx/
│   └── nginx.conf             # Nginx configuration
├── scripts/
│   ├── deploy.sh              # Production deployment script
│   └── init-letsencrypt.sh    # SSL certificate initialization
└── certbot/                   # SSL certificates (auto-generated)
```

## Monitoring

- **Application**: Available at `https://lsiddd.space`
- **Health Check**: `https://lsiddd.space/health`  
- **SSL Status**: Certificates auto-renew, check logs for renewal status

## Troubleshooting

### SSL Certificate Issues
```bash
# Check certificate status
docker-compose -f docker-compose.yml -f docker-compose.prod.yml exec certbot certbot certificates

# Test certificate renewal
docker-compose -f docker-compose.yml -f docker-compose.prod.yml exec certbot certbot renew --dry-run
```

### Domain Configuration
```bash
# Verify domain points to server
dig +short lsiddd.space
curl -I http://lsiddd.space
```

### Service Issues
```bash
# Check all service status
docker-compose -f docker-compose.yml -f docker-compose.prod.yml ps

# Restart specific service
docker-compose -f docker-compose.yml -f docker-compose.prod.yml restart guardian-ai
```

## Development

To contribute to this project:

1. Make changes to `app.py` or other source files
2. Test locally with `streamlit run app.py`
3. Test production deployment with staging certificates
4. Deploy to production

The application features a comprehensive fraud detection system with multiple analysis modes and real-time monitoring capabilities.