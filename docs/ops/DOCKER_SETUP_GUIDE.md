# Docker Setup - Quick Reference

## Overview
The Athens EHS System now has complete Docker support with both development and production configurations. The existing virtual environment (venv) is preserved and unaffected.

## Quick Start

### 1. Interactive Setup (Recommended)
```bash
./docker-setup.sh
```

### 2. Manual Commands

#### Development Environment
```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Stop services
docker-compose -f docker-compose.dev.yml down
```

#### Production Environment
```bash
# Start production environment
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Services & Ports

### Development
- **Frontend**: http://localhost:5173 (Vite dev server)
- **Backend**: http://localhost:8000 (Django dev server)
- **Database**: localhost:5432 (PostgreSQL)
- **Redis**: localhost:6379
- **pgAdmin**: http://localhost:5050 (with --profile tools)
- **Redis Insight**: http://localhost:8001 (with --profile tools)
- **MailHog**: http://localhost:8025 (with --profile tools)

### Production
- **Frontend**: http://localhost:80 (Nginx)
- **Backend**: http://localhost:8000 (Gunicorn)
- **Database**: localhost:5432 (PostgreSQL)
- **Redis**: localhost:6379
- **Load Balancer**: http://localhost:80 (Nginx - optional)

## Development Tools
```bash
# Start development tools (pgAdmin, Redis Insight, MailHog)
docker-compose -f docker-compose.dev.yml --profile tools up -d

# Access pgAdmin
# URL: http://localhost:5050
# Email: admin@ehs-system.local
# Password: admin123
```

## Database Management

### Run Migrations
```bash
# Development
docker-compose -f docker-compose.dev.yml exec backend python manage.py migrate

# Production
docker-compose exec backend python manage.py migrate
```

### Create Superuser
```bash
# Development
docker-compose -f docker-compose.dev.yml exec backend python manage.py createsuperuser

# Production
docker-compose exec backend python manage.py createsuperuser
```

### Database Shell
```bash
# Development
docker-compose -f docker-compose.dev.yml exec backend python manage.py dbshell

# Production
docker-compose exec backend python manage.py dbshell
```

## File Structure
```
/var/www/athens/
├── docker-compose.yml          # Production configuration
├── docker-compose.dev.yml      # Development configuration
├── docker-setup.sh            # Interactive setup script
├── .env                       # Environment variables
├── nginx/
│   ├── nginx.conf            # Load balancer configuration
│   └── ssl/                  # SSL certificates (if needed)
├── database/
│   └── init/
│       └── 01-init.sh       # Database initialization
├── backend/
│   └── Dockerfile           # Backend container definition
└── frontend/
    ├── Dockerfile           # Frontend container definition
    └── nginx.conf          # Frontend nginx configuration
```

## Environment Variables
Key variables in `.env`:
- `SECRET_KEY`: Django secret key
- `DEBUG`: Debug mode (True/False)
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`: Database credentials
- `REDIS_PASSWORD`: Redis password
- `ALLOWED_HOSTS`: Allowed hostnames
- `CORS_ALLOWED_ORIGINS`: CORS origins

## Troubleshooting

### Check Container Status
```bash
docker-compose ps
docker-compose -f docker-compose.dev.yml ps
```

### View Container Logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs backend
docker-compose logs frontend
```

### Restart Services
```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
```

### Clean Up
```bash
# Stop and remove containers
docker-compose down

# Remove volumes (WARNING: This deletes data)
docker-compose down -v

# Clean up unused Docker resources
docker system prune -f
```

### Access Container Shell
```bash
# Backend container
docker-compose exec backend bash

# Database container
docker-compose exec database psql -U ehs_prod_user -d ehs_management_prod
```

## Security Notes
- Production containers run as non-root users
- Security headers are configured in Nginx
- Rate limiting is enabled for API endpoints
- SSL/TLS support is ready (certificates needed)

## Performance Features
- Multi-stage Docker builds for smaller images
- Gzip compression enabled
- Static file caching
- Connection pooling for database and Redis
- Health checks for all services

## Coexistence with Existing Setup
- Docker setup is completely separate from existing venv
- Both can run simultaneously on different ports
- No interference with current development workflow
- Easy to switch between Docker and venv environments