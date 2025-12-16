# 🚀 **EHS Management System - Production Deployment Guide**

## 📋 **Table of Contents**
- [Prerequisites](#prerequisites)
- [Security Configuration](#security-configuration)
- [Environment Setup](#environment-setup)
- [Docker Deployment](#docker-deployment)
- [Database Setup](#database-setup)
- [SSL/HTTPS Configuration](#ssl-https-configuration)
- [Monitoring & Logging](#monitoring--logging)
- [Backup & Recovery](#backup--recovery)
- [Troubleshooting](#troubleshooting)

---

## 🔧 **Prerequisites**

### **System Requirements**
- **OS**: Ubuntu 20.04+ / CentOS 8+ / RHEL 8+
- **CPU**: 4+ cores (8+ recommended for production)
- **RAM**: 8GB minimum (16GB+ recommended)
- **Storage**: 100GB+ SSD
- **Network**: Static IP with domain name

### **Software Requirements**
```bash
# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install additional tools
sudo apt update && sudo apt install -y \
    nginx \
    certbot \
    python3-certbot-nginx \
    htop \
    curl \
    git
```

---

## 🔐 **Security Configuration**

### **1. Generate Secure Keys**
```bash
# Generate Django SECRET_KEY
python3 -c "import secrets; print(''.join(secrets.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*(-_=+)') for _ in range(50)))"

# Generate database password
openssl rand -base64 32

# Generate Redis password
openssl rand -base64 32
```

### **2. Create Production Environment File**
```bash
# Copy and configure environment files
cp backend/.env.example backend/.env
cp frontedn/.env.example frontedn/.env.local

# Edit with your production values
nano backend/.env
nano frontedn/.env.local
```

### **3. Set File Permissions**
```bash
# Secure environment files
chmod 600 backend/.env
chmod 600 frontedn/.env.local
chown root:root backend/.env frontedn/.env.local
```

---

## 🌍 **Environment Setup**

### **Backend Environment (.env)**
```bash
# Security Configuration
SECRET_KEY=your-generated-50-character-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database Configuration
DB_NAME=ehs_management_prod
DB_USER=ehs_prod_user
DB_PASSWORD=your-secure-database-password
DB_HOST=database
DB_PORT=5432

# Redis Configuration
REDIS_PASSWORD=your-secure-redis-password

# CORS & Security
CORS_ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com
CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://www.your-domain.com

# SSL Settings
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Email Configuration
EMAIL_HOST=smtp.your-provider.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@your-domain.com
EMAIL_HOST_PASSWORD=your-email-password
```

### **Frontend Environment (.env.local)**
```bash
# API Configuration
VITE_API_BASE_URL=https://api.your-domain.com
VITE_NODE_ENV=production
VITE_DEBUG=false

# Security
VITE_SECURE_COOKIES=true
VITE_ENABLE_CSP=true

# WebSocket
VITE_WEBSOCKET_URL=wss://api.your-domain.com/ws/
```

---

## 🐳 **Docker Deployment**

### **1. Production Deployment**
```bash
# Clone repository
git clone https://github.com/your-org/ehs-management-system.git
cd ehs-management-system

# Build and start services
docker-compose up -d

# Check service status
docker-compose ps
docker-compose logs -f
```

### **2. Development Deployment**
```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# With development tools
docker-compose -f docker-compose.dev.yml --profile tools up -d

# Access development tools:
# - pgAdmin: http://localhost:5050
# - Redis Insight: http://localhost:8001
# - MailHog: http://localhost:8025
```

### **3. Service Management**
```bash
# View logs
docker-compose logs -f [service_name]

# Restart services
docker-compose restart [service_name]

# Update services
docker-compose pull
docker-compose up -d

# Scale services
docker-compose up -d --scale backend=3
```

---

## 🗄️ **Database Setup**

### **1. Initial Setup**
```bash
# Run migrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Load initial data (if available)
docker-compose exec backend python manage.py loaddata initial_data.json
```

### **2. Database Backup**
```bash
# Create backup
docker-compose exec database pg_dump -U ehs_prod_user ehs_management_prod > backup_$(date +%Y%m%d_%H%M%S).sql

# Automated backup script
cat > backup_db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/ehs-system"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
docker-compose exec -T database pg_dump -U ehs_prod_user ehs_management_prod > $BACKUP_DIR/backup_$DATE.sql
gzip $BACKUP_DIR/backup_$DATE.sql
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete
EOF

chmod +x backup_db.sh
```

### **3. Database Restore**
```bash
# Restore from backup
gunzip -c backup_20250107_120000.sql.gz | docker-compose exec -T database psql -U ehs_prod_user -d ehs_management_prod
```

---

## 🔒 **SSL/HTTPS Configuration**

### **1. Let's Encrypt SSL**
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### **2. Custom SSL Certificate**
```bash
# Create SSL directory
mkdir -p nginx/ssl

# Copy your certificates
cp your-domain.crt nginx/ssl/
cp your-domain.key nginx/ssl/

# Set permissions
chmod 600 nginx/ssl/*
```

---

## 📊 **Monitoring & Logging**

### **1. Log Management**
```bash
# View application logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Log rotation configuration
cat > /etc/logrotate.d/ehs-system << 'EOF'
/var/lib/docker/containers/*/*.log {
    daily
    missingok
    rotate 30
    compress
    notifempty
    create 644 root root
    postrotate
        /bin/kill -USR1 $(cat /var/run/docker.pid) 2>/dev/null || true
    endscript
}
EOF
```

### **2. Health Monitoring**
```bash
# Health check script
cat > health_check.sh << 'EOF'
#!/bin/bash
SERVICES=("frontend" "backend" "database" "redis")
for service in "${SERVICES[@]}"; do
    if ! docker-compose ps $service | grep -q "Up"; then
        echo "ALERT: $service is down!"
        # Send notification (email, Slack, etc.)
    fi
done
EOF

chmod +x health_check.sh

# Add to crontab
echo "*/5 * * * * /path/to/health_check.sh" | crontab -
```

---

## 💾 **Backup & Recovery**

### **1. Complete System Backup**
```bash
# Backup script
cat > full_backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/ehs-system"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Database backup
docker-compose exec -T database pg_dump -U ehs_prod_user ehs_management_prod | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Media files backup
docker run --rm -v ehs-management-system_media_files:/data -v $BACKUP_DIR:/backup alpine tar czf /backup/media_$DATE.tar.gz -C /data .

# Configuration backup
tar czf $BACKUP_DIR/config_$DATE.tar.gz backend/.env frontedn/.env.local docker-compose.yml

# Cleanup old backups (keep 30 days)
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete
EOF

chmod +x full_backup.sh
```

### **2. Disaster Recovery**
```bash
# Recovery procedure
1. Restore configuration files
2. Start database service: docker-compose up -d database
3. Restore database: gunzip -c db_backup.sql.gz | docker-compose exec -T database psql -U ehs_prod_user -d ehs_management_prod
4. Restore media files: docker run --rm -v ehs-management-system_media_files:/data -v /backup:/backup alpine tar xzf /backup/media_backup.tar.gz -C /data
5. Start all services: docker-compose up -d
```

---

## 🔧 **Troubleshooting**

### **Common Issues**

#### **1. Service Won't Start**
```bash
# Check logs
docker-compose logs [service_name]

# Check resource usage
docker stats

# Restart service
docker-compose restart [service_name]
```

#### **2. Database Connection Issues**
```bash
# Check database status
docker-compose exec database pg_isready -U ehs_prod_user

# Reset database connection
docker-compose restart backend
```

#### **3. SSL Certificate Issues**
```bash
# Check certificate status
sudo certbot certificates

# Renew certificate
sudo certbot renew --force-renewal
```

#### **4. Performance Issues**
```bash
# Monitor resource usage
htop
docker stats

# Scale services
docker-compose up -d --scale backend=3

# Check database performance
docker-compose exec database psql -U ehs_prod_user -d ehs_management_prod -c "SELECT * FROM pg_stat_activity;"
```

---

## 📞 **Support & Maintenance**

### **Regular Maintenance Tasks**
- [ ] Weekly: Check logs and system health
- [ ] Weekly: Update Docker images
- [ ] Monthly: Review and rotate logs
- [ ] Monthly: Test backup and recovery procedures
- [ ] Quarterly: Security audit and updates
- [ ] Quarterly: Performance optimization review

### **Emergency Contacts**
- **System Administrator**: admin@your-domain.com
- **Development Team**: dev@your-domain.com
- **24/7 Support**: +1-XXX-XXX-XXXX

---

**Document Version**: 1.0  
**Last Updated**: January 2025  
**Next Review**: April 2025
