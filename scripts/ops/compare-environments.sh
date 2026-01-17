#!/bin/bash

# ============================================================================
# EHS Management System - venv vs Docker Comparison Script
# ============================================================================
# Deep investigation and validation of environment parity
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo ""
    echo "============================================================================"
    echo "$1"
    echo "============================================================================"
}

# Function to check venv configuration
check_venv_config() {
    print_header "VENV ENVIRONMENT ANALYSIS"
    
    cd /var/www/athens/backend
    
    if [ ! -d "venv" ]; then
        print_error "Virtual environment not found"
        return 1
    fi
    
    print_status "Activating virtual environment..."
    source venv/bin/activate
    
    # Check Django configuration
    print_status "Checking Django configuration..."
    DJANGO_SETTINGS_MODULE=backend.settings python -c "
import django
django.setup()
from django.conf import settings
import os

print('=== VENV CONFIGURATION ===')
print(f'DEBUG: {settings.DEBUG}')
print(f'SECRET_KEY: {settings.SECRET_KEY[:20]}...')
print(f'ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}')
print(f'DATABASE ENGINE: {settings.DATABASES[\"default\"][\"ENGINE\"]}')
print(f'DATABASE NAME: {settings.DATABASES[\"default\"][\"NAME\"]}')
print(f'DATABASE USER: {settings.DATABASES[\"default\"][\"USER\"]}')
print(f'DATABASE HOST: {settings.DATABASES[\"default\"][\"HOST\"]}')
print(f'DATABASE PORT: {settings.DATABASES[\"default\"][\"PORT\"]}')
print(f'CORS_ALLOW_ALL_ORIGINS: {getattr(settings, \"CORS_ALLOW_ALL_ORIGINS\", \"Not set\")}')
print(f'CORS_ALLOWED_ORIGINS: {getattr(settings, \"CORS_ALLOWED_ORIGINS\", \"Not set\")}')
print(f'REDIS CONFIG: {settings.CHANNEL_LAYERS[\"default\"][\"CONFIG\"][\"hosts\"]}')
print(f'CELERY_BROKER_URL: {getattr(settings, \"CELERY_BROKER_URL\", \"Not set\")}')
print(f'MEDIA_ROOT: {settings.MEDIA_ROOT}')
print(f'STATIC_ROOT: {settings.STATIC_ROOT}')
print(f'INSTALLED_APPS count: {len(settings.INSTALLED_APPS)}')
"
    
    # Check installed packages
    print_status "Checking installed packages..."
    pip list | grep -E "(Django|psycopg|redis|channels)" || true
    
    # Check database connectivity
    print_status "Checking database connectivity..."
    DJANGO_SETTINGS_MODULE=backend.settings python -c "
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute('SELECT version();')
        result = cursor.fetchone()
        print(f'Database connection: SUCCESS - {result[0][:50]}...')
except Exception as e:
    print(f'Database connection: FAILED - {e}')
"
    
    deactivate
}

# Function to check Docker configuration
check_docker_config() {
    print_header "DOCKER ENVIRONMENT ANALYSIS"
    
    # Check if Docker containers are running
    print_status "Checking Docker container status..."
    
    if ! docker-compose ps | grep -q "Up"; then
        print_warning "Docker containers not running. Starting them..."
        docker-compose -f docker-compose.dev.yml up -d
        sleep 30
    fi
    
    # Check backend configuration
    print_status "Checking Docker backend configuration..."
    docker-compose -f docker-compose.dev.yml exec -T backend python -c "
import django
import os
django.setup()
from django.conf import settings

print('=== DOCKER CONFIGURATION ===')
print(f'DEBUG: {settings.DEBUG}')
print(f'SECRET_KEY: {settings.SECRET_KEY[:20]}...')
print(f'ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}')
print(f'DATABASE ENGINE: {settings.DATABASES[\"default\"][\"ENGINE\"]}')
print(f'DATABASE NAME: {settings.DATABASES[\"default\"][\"NAME\"]}')
print(f'DATABASE USER: {settings.DATABASES[\"default\"][\"USER\"]}')
print(f'DATABASE HOST: {settings.DATABASES[\"default\"][\"HOST\"]}')
print(f'DATABASE PORT: {settings.DATABASES[\"default\"][\"PORT\"]}')
print(f'CORS_ALLOW_ALL_ORIGINS: {getattr(settings, \"CORS_ALLOW_ALL_ORIGINS\", \"Not set\")}')
print(f'CORS_ALLOWED_ORIGINS: {getattr(settings, \"CORS_ALLOWED_ORIGINS\", \"Not set\")}')
print(f'REDIS CONFIG: {settings.CHANNEL_LAYERS[\"default\"][\"CONFIG\"][\"hosts\"]}')
print(f'CELERY_BROKER_URL: {getattr(settings, \"CELERY_BROKER_URL\", \"Not set\")}')
print(f'MEDIA_ROOT: {settings.MEDIA_ROOT}')
print(f'STATIC_ROOT: {settings.STATIC_ROOT}')
print(f'INSTALLED_APPS count: {len(settings.INSTALLED_APPS)}')
" 2>/dev/null || print_error "Failed to get Docker backend configuration"
    
    # Check database connectivity
    print_status "Checking Docker database connectivity..."
    docker-compose -f docker-compose.dev.yml exec -T backend python -c "
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute('SELECT version();')
        result = cursor.fetchone()
        print(f'Database connection: SUCCESS - {result[0][:50]}...')
except Exception as e:
    print(f'Database connection: FAILED - {e}')
" 2>/dev/null || print_error "Failed to check Docker database connectivity"
    
    # Check Redis connectivity
    print_status "Checking Docker Redis connectivity..."
    docker-compose -f docker-compose.dev.yml exec -T redis redis-cli ping 2>/dev/null || print_error "Redis not responding"
}

# Function to compare configurations
compare_configurations() {
    print_header "CONFIGURATION COMPARISON"
    
    print_status "Comparing key configuration parameters..."
    
    # Create temporary files for comparison
    temp_venv="/tmp/venv_config.txt"
    temp_docker="/tmp/docker_config.txt"
    
    # Get venv config
    cd /var/www/athens/backend
    source venv/bin/activate
    DJANGO_SETTINGS_MODULE=backend.settings python -c "
import django
django.setup()
from django.conf import settings

config = {
    'DEBUG': settings.DEBUG,
    'DB_ENGINE': settings.DATABASES['default']['ENGINE'],
    'DB_NAME': settings.DATABASES['default']['NAME'],
    'DB_USER': settings.DATABASES['default']['USER'],
    'DB_HOST': settings.DATABASES['default']['HOST'],
    'DB_PORT': settings.DATABASES['default']['PORT'],
    'CORS_ALLOW_ALL': getattr(settings, 'CORS_ALLOW_ALL_ORIGINS', False),
    'APPS_COUNT': len(settings.INSTALLED_APPS),
}

for key, value in sorted(config.items()):
    print(f'{key}={value}')
" > "$temp_venv" 2>/dev/null
    deactivate
    
    # Get Docker config
    docker-compose -f docker-compose.dev.yml exec -T backend python -c "
import django
django.setup()
from django.conf import settings

config = {
    'DEBUG': settings.DEBUG,
    'DB_ENGINE': settings.DATABASES['default']['ENGINE'],
    'DB_NAME': settings.DATABASES['default']['NAME'],
    'DB_USER': settings.DATABASES['default']['USER'],
    'DB_HOST': settings.DATABASES['default']['HOST'],
    'DB_PORT': settings.DATABASES['default']['PORT'],
    'CORS_ALLOW_ALL': getattr(settings, 'CORS_ALLOW_ALL_ORIGINS', False),
    'APPS_COUNT': len(settings.INSTALLED_APPS),
}

for key, value in sorted(config.items()):
    print(f'{key}={value}')
" > "$temp_docker" 2>/dev/null
    
    # Compare configurations
    echo ""
    echo "VENV Configuration:"
    cat "$temp_venv"
    echo ""
    echo "Docker Configuration:"
    cat "$temp_docker"
    echo ""
    
    if diff -q "$temp_venv" "$temp_docker" > /dev/null; then
        print_success "Configurations match perfectly!"
    else
        print_warning "Configuration differences found:"
        diff "$temp_venv" "$temp_docker" || true
    fi
    
    # Cleanup
    rm -f "$temp_venv" "$temp_docker"
}

# Function to test API endpoints
test_api_endpoints() {
    print_header "API ENDPOINT TESTING"
    
    # Test venv endpoints
    print_status "Testing venv API endpoints..."
    
    # Check if venv server is running
    if ! curl -s http://localhost:8000/health/ > /dev/null 2>&1; then
        print_warning "venv server not running. Please start it manually."
    else
        print_success "venv health endpoint: $(curl -s http://localhost:8000/health/ | jq -r '.status' 2>/dev/null || echo 'OK')"
        print_success "venv admin endpoint: $(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/admin/)"
    fi
    
    # Test Docker endpoints
    print_status "Testing Docker API endpoints..."
    
    if ! curl -s http://localhost:8000/health/ > /dev/null 2>&1; then
        print_warning "Docker backend not accessible on port 8000"
    else
        print_success "Docker health endpoint: $(curl -s http://localhost:8000/health/ | jq -r '.status' 2>/dev/null || echo 'OK')"
        print_success "Docker admin endpoint: $(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/admin/)"
    fi
    
    # Test frontend endpoints
    print_status "Testing frontend endpoints..."
    
    if curl -s http://localhost:5173/ > /dev/null 2>&1; then
        print_success "Docker frontend accessible on port 5173"
    else
        print_warning "Docker frontend not accessible on port 5173"
    fi
}

# Function to check migrations
check_migrations() {
    print_header "MIGRATION STATUS COMPARISON"
    
    print_status "Checking venv migrations..."
    cd /var/www/athens/backend
    source venv/bin/activate
    DJANGO_SETTINGS_MODULE=backend.settings python manage.py showmigrations --list | head -10
    deactivate
    
    print_status "Checking Docker migrations..."
    docker-compose -f docker-compose.dev.yml exec -T backend python manage.py showmigrations --list | head -10 2>/dev/null || print_error "Failed to check Docker migrations"
}

# Function to generate recommendations
generate_recommendations() {
    print_header "RECOMMENDATIONS"
    
    print_status "Based on the analysis, here are the recommendations:"
    echo ""
    echo "1. Environment Parity:"
    echo "   - Both environments should use identical database credentials"
    echo "   - Redis configuration should match (no password in both)"
    echo "   - CORS settings should be identical"
    echo ""
    echo "2. Development Workflow:"
    echo "   - Use Docker for consistent development environment"
    echo "   - Keep venv for quick debugging and testing"
    echo "   - Ensure both environments use same Django settings"
    echo ""
    echo "3. Production Readiness:"
    echo "   - Docker environment is more production-ready"
    echo "   - Includes proper health checks and monitoring"
    echo "   - Better resource isolation and scalability"
    echo ""
    echo "4. Migration Strategy:"
    echo "   - Run migrations in both environments"
    echo "   - Ensure database schema consistency"
    echo "   - Test all features in both environments"
}

# Main execution
main() {
    print_header "EHS MANAGEMENT SYSTEM - ENVIRONMENT COMPARISON"
    print_status "Starting comprehensive analysis of venv vs Docker environments"
    
    # Check prerequisites
    if ! command -v docker &> /dev/null; then
        print_error "Docker not installed"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose not installed"
        exit 1
    fi
    
    # Run analysis
    check_venv_config
    check_docker_config
    compare_configurations
    test_api_endpoints
    check_migrations
    generate_recommendations
    
    print_header "ANALYSIS COMPLETE"
    print_success "Environment comparison completed successfully"
}

# Run main function
main "$@"