# Production Environment Setup

This guide covers deploying the multi-tenant financial tools API to production using Docker and cloud infrastructure.

## Prerequisites

- **Docker & Docker Compose**
- **Domain name** with SSL certificate
- **Cloud provider** (AWS, GCP, Azure, DigitalOcean)
- **SSL certificate** (Let's Encrypt or commercial)
- **Database backups** strategy
- **Monitoring** and logging solutions

## Production Architecture

### Services Overview

- **App Servers**: 2+ FastAPI instances behind load balancer
- **Nginx**: Reverse proxy and load balancer
- **PostgreSQL**: Primary database
- **Redis**: Caching and session storage
- **Celery**: Background task processing
- **Prometheus**: Metrics collection
- **Monitoring**: Health checks and alerts

### Infrastructure Requirements

- **CPU**: 2+ vCPUs per app instance
- **RAM**: 4GB+ per app instance
- **Storage**: 50GB+ for database
- **Network**: High bandwidth for API traffic

## Quick Deployment

### 1. Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Reboot or logout/login
```

### 2. Application Deployment
```bash
# Clone repository
git clone <repository-url>
cd finance-tool-api/backend

# Create production environment file
cp .env.example .env.prod
nano .env.prod
```

### 3. Production Environment Configuration
```bash
# .env.prod
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Database - Use managed PostgreSQL
DATABASE_URL=postgresql+asyncpg://user:secure_password@prod-db-host:5432/fastapi_prod

# Redis - Use managed Redis
REDIS_URL=redis://prod-redis-host:6379

# Security - Generate strong keys
SECRET_KEY=your-production-secret-key-32-chars-minimum
ENCRYPTION_KEY=your-production-encryption-key

# Stripe - Production keys
STRIPE_API_KEY=sk_live_your_stripe_live_key
STRIPE_WEBHOOK_SECRET=whsec_your_production_webhook_secret

# LLM - Production API key
OPENROUTER_API_KEY=sk-or-v1-your-production-key

# CORS - Production domains
CORS_ORIGINS=["https://yourdomain.com", "https://app.yourdomain.com"]

# Rate Limiting - Production values
RATE_LIMIT_TIMES=100
RATE_LIMIT_SECONDS=60

# Workers
WORKERS=4
```

### 4. SSL Certificate Setup
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot certonly --standalone -d yourdomain.com

# Certificate paths for nginx
SSL_CERT=/etc/letsencrypt/live/yourdomain.com/fullchain.pem
SSL_KEY=/etc/letsencrypt/live/yourdomain.com/privkey.pem
```

### 5. Deploy with Docker Compose
```bash
# Use production compose file
docker-compose -f docker-compose.prod.yml up -d

# Check deployment
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs -f
```

## Database Setup

### Managed PostgreSQL (Recommended)
```bash
# AWS RDS, Google Cloud SQL, or Azure Database
# Create database instance with:
# - PostgreSQL 15+
# - 50GB+ storage
# - Multi-AZ deployment
# - Automated backups
# - Encryption at rest
```

### Database Migration
```bash
# Run migrations on production
docker-compose -f docker-compose.prod.yml exec app1 alembic upgrade head

# Verify migration
docker-compose -f docker-compose.prod.yml exec db psql -U user -d fastapi_prod -c "SELECT * FROM alembic_version;"
```

## Load Balancing & Scaling

### Nginx Configuration
```nginx
# /etc/nginx/sites-available/yourdomain.com
upstream app_backend {
    server app1:8000;
    server app2:8000;
}

server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://app_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /metrics {
        proxy_pass http://app_backend;
        allow 10.0.0.0/8;  # Restrict to internal network
        deny all;
    }
}
```

### Horizontal Scaling
```bash
# Scale application instances
docker-compose -f docker-compose.prod.yml up -d --scale app1=3 --scale app2=3

# Update nginx upstream configuration accordingly
```

## Monitoring & Observability

### Prometheus Metrics
```bash
# Access metrics
curl https://yourdomain.com/metrics

# Configure Prometheus scraping
scrape_configs:
  - job_name: 'fastapi-app'
    static_configs:
      - targets: ['yourdomain.com:443']
    metrics_path: '/metrics'
    scheme: 'https'
```

### Health Checks
```bash
# Application health
curl https://yourdomain.com/health

# Database connectivity
curl https://yourdomain.com/health/db

# External services
curl https://yourdomain.com/health/external
```

### Logging
```bash
# Application logs
docker-compose -f docker-compose.prod.yml logs -f app1 app2

# Centralized logging (ELK Stack, CloudWatch, etc.)
# Configure log shipping to external service
```

## Security Configuration

### Network Security
```bash
# Configure firewall
sudo ufw enable
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8000/tcp  # For health checks

# Security groups (cloud provider)
# - Allow inbound: 80, 443, 22
# - Restrict to known IPs for SSH
```

### Application Security
```bash
# Environment variables
export SECRET_KEY="strong-production-key"
export ENCRYPTION_KEY="strong-encryption-key"

# File permissions
sudo chown -R www-data:www-data /opt/fastapi-app
sudo chmod -R 755 /opt/fastapi-app
sudo chmod 600 /opt/fastapi-app/.env.prod
```

### SSL/TLS Configuration
```nginx
# Strong SSL configuration
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
ssl_prefer_server_ciphers off;
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;
```

## Backup Strategy

### Database Backups
```bash
# Automated backups (if using managed database)
# Or manual backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose -f docker-compose.prod.yml exec db pg_dump -U user fastapi_prod > backup_$DATE.sql

# Upload to S3 or cloud storage
aws s3 cp backup_$DATE.sql s3://your-backup-bucket/
```

### Application Backups
```bash
# Backup environment and configuration
tar -czf config_backup_$DATE.tar.gz .env.prod docker-compose.prod.yml nginx.conf

# Backup SSL certificates
sudo tar -czf ssl_backup_$DATE.tar.gz /etc/letsencrypt/
```

## Performance Optimization

### Application Configuration
```bash
# Production settings
WORKERS=4
WORKER_CLASS=uvicorn.workers.UvicornWorker
WORKER_CONNECTIONS=1000
MAX_REQUESTS=1000
MAX_REQUESTS_JITTER=50
```

### Database Optimization
```bash
# Connection pooling
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30
DATABASE_POOL_TIMEOUT=30

# Query optimization
# Add database indexes for frequently queried columns
# Monitor slow queries
```

### Caching Strategy
```bash
# Redis configuration
REDIS_CACHE_TTL=3600
REDIS_MAX_CONNECTIONS=20

# Cache frequently accessed data
# User subscriptions, tier limits, etc.
```

## Deployment Automation

### CI/CD Pipeline
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to production
        run: |
          echo "Deploying to production server"
          # Add deployment commands
```

### Blue-Green Deployment
```bash
# Deploy new version
docker-compose -f docker-compose.prod.yml up -d --scale app1=0 --scale app2=2 app1

# Test new version
curl https://yourdomain.com/health

# Switch traffic to new version
docker-compose -f docker-compose.prod.yml up -d --scale app1=2 --scale app2=0

# Clean up old version
docker-compose -f docker-compose.prod.yml up -d --scale app2=0
```

## Troubleshooting Production

### Common Issues

#### High CPU Usage
```bash
# Check running processes
docker stats

# Check application logs
docker-compose -f docker-compose.prod.yml logs --tail=100 app1

# Scale up instances
docker-compose -f docker-compose.prod.yml up -d --scale app1=4
```

#### Database Connection Issues
```bash
# Check database connectivity
docker-compose -f docker-compose.prod.yml exec app1 python -c "import asyncpg; print('DB OK')"

# Restart database
docker-compose -f docker-compose.prod.yml restart db
```

#### Memory Issues
```bash
# Check memory usage
docker stats

# Restart services
docker-compose -f docker-compose.prod.yml restart

# Add swap space if needed
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## Maintenance Tasks

### Regular Updates
```bash
# Update Docker images
docker-compose -f docker-compose.prod.yml pull

# Update application
git pull origin main
docker-compose -f docker-compose.prod.yml up -d --build

# Update SSL certificates
sudo certbot renew
```

### Monitoring Alerts
- CPU usage > 80%
- Memory usage > 85%
- Database connection errors
- Response time > 2 seconds
- Error rate > 5%

## Cost Optimization

### Resource Rightsizing
- Monitor usage patterns
- Adjust instance sizes based on load
- Use spot instances for non-critical workloads

### Database Optimization
- Archive old data
- Use read replicas for analytics
- Optimize query performance

## Support & Maintenance

- **Monitoring**: Set up alerts for critical metrics
- **Backups**: Test backup restoration regularly
- **Updates**: Keep dependencies updated
- **Security**: Regular security audits
- **Documentation**: Maintain runbooks for common procedures

## Additional Resources

- [Docker Production Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Nginx Configuration](https://nginx.org/en/docs/)
- [PostgreSQL Tuning](https://wiki.postgresql.org/wiki/Tuning_Your_PostgreSQL_Server)
- [Redis Production Setup](https://redis.io/topics/admin)