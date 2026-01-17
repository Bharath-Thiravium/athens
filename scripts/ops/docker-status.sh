#!/bin/bash

# ============================================================================
# EHS Management System - Docker Status Monitor
# ============================================================================
# Monitor Docker containers and services health
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Function to check if container is running
check_container() {
    local container_name=$1
    local compose_file=$2
    
    if [ -n "$compose_file" ]; then
        status=$(docker-compose -f "$compose_file" ps -q "$container_name" 2>/dev/null)
    else
        status=$(docker-compose ps -q "$container_name" 2>/dev/null)
    fi
    
    if [ -n "$status" ]; then
        if [ -n "$compose_file" ]; then
            running=$(docker-compose -f "$compose_file" ps "$container_name" 2>/dev/null | grep "Up" || true)
        else
            running=$(docker-compose ps "$container_name" 2>/dev/null | grep "Up" || true)
        fi
        
        if [ -n "$running" ]; then
            print_success "$container_name is running"
            return 0
        else
            print_error "$container_name is not running"
            return 1
        fi
    else
        print_warning "$container_name not found"
        return 1
    fi
}

# Function to check service health
check_service_health() {
    local service_name=$1
    local url=$2
    local expected_status=${3:-200}
    
    print_status "Checking $service_name health..."
    
    if command -v curl &> /dev/null; then
        response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
        
        if [ "$response" = "$expected_status" ]; then
            print_success "$service_name is healthy (HTTP $response)"
            return 0
        else
            print_error "$service_name is unhealthy (HTTP $response)"
            return 1
        fi
    else
        print_warning "curl not available, skipping $service_name health check"
        return 1
    fi
}

# Function to check database connectivity
check_database() {
    local compose_file=$1
    
    print_status "Checking database connectivity..."
    
    if [ -n "$compose_file" ]; then
        result=$(docker-compose -f "$compose_file" exec -T database pg_isready -U athens_user -d athens_ehs 2>/dev/null || echo "failed")
    else
        result=$(docker-compose exec -T database pg_isready -U athens_user -d athens_ehs 2>/dev/null || echo "failed")
    fi
    
    if [[ "$result" == *"accepting connections"* ]]; then
        print_success "Database is accepting connections"
        return 0
    else
        print_error "Database is not accepting connections"
        return 1
    fi
}

# Function to check Redis connectivity
check_redis() {
    local compose_file=$1
    
    print_status "Checking Redis connectivity..."
    
    if [ -n "$compose_file" ]; then
        result=$(docker-compose -f "$compose_file" exec -T redis redis-cli ping 2>/dev/null || echo "failed")
    else
        result=$(docker-compose exec -T redis redis-cli --raw incr ping 2>/dev/null || echo "failed")
    fi
    
    if [[ "$result" == *"PONG"* ]] || [[ "$result" =~ ^[0-9]+$ ]]; then
        print_success "Redis is responding"
        return 0
    else
        print_error "Redis is not responding"
        return 1
    fi
}

# Function to show container logs
show_container_logs() {
    local container_name=$1
    local compose_file=$2
    local lines=${3:-50}
    
    echo ""
    print_status "Last $lines lines of $container_name logs:"
    echo "============================================================================"
    
    if [ -n "$compose_file" ]; then
        docker-compose -f "$compose_file" logs --tail="$lines" "$container_name" 2>/dev/null || print_error "Failed to get logs for $container_name"
    else
        docker-compose logs --tail="$lines" "$container_name" 2>/dev/null || print_error "Failed to get logs for $container_name"
    fi
    
    echo "============================================================================"
}

# Function to show resource usage
show_resource_usage() {
    print_status "Docker resource usage:"
    echo "============================================================================"
    
    if command -v docker &> /dev/null; then
        docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}" 2>/dev/null || print_error "Failed to get resource usage"
    else
        print_error "Docker not available"
    fi
    
    echo "============================================================================"
}

# Function to check environment
check_environment() {
    local env_type=$1
    
    echo ""
    echo "============================================================================"
    echo "EHS Management System - Docker Status Check ($env_type)"
    echo "============================================================================"
    echo ""
    
    local compose_file=""
    if [ "$env_type" = "development" ]; then
        compose_file="docker-compose.dev.yml"
    fi
    
    # Check containers
    print_status "Checking container status..."
    
    local containers=("database" "redis" "backend" "frontend")
    local all_running=true
    
    for container in "${containers[@]}"; do
        if ! check_container "$container" "$compose_file"; then
            all_running=false
        fi
    done
    
    echo ""
    
    # Check services health
    if [ "$all_running" = true ]; then
        print_status "Checking service health..."
        
        # Check database
        check_database "$compose_file"
        
        # Check Redis
        check_redis "$compose_file"
        
        # Check backend health
        if [ "$env_type" = "development" ]; then
            check_service_health "Backend API" "http://localhost:8000/health/"
            check_service_health "Frontend" "http://localhost:5173/"
        else
            check_service_health "Backend API" "http://localhost:8000/health/"
            check_service_health "Frontend" "http://localhost:80/"
        fi
        
        echo ""
        
        # Show resource usage
        show_resource_usage
        
    else
        print_warning "Some containers are not running. Skipping health checks."
        
        # Show logs for failed containers
        for container in "${containers[@]}"; do
            if ! check_container "$container" "$compose_file" &>/dev/null; then
                show_container_logs "$container" "$compose_file" 20
            fi
        done
    fi
}

# Main menu
show_menu() {
    echo ""
    echo "============================================================================"
    echo "EHS Management System - Docker Status Monitor"
    echo "============================================================================"
    echo ""
    echo "1. Check Development Environment"
    echo "2. Check Production Environment"
    echo "3. Show Resource Usage"
    echo "4. Show Container Logs"
    echo "5. Quick Health Check"
    echo "6. Exit"
    echo ""
}

# Main script
main() {
    if [ $# -eq 1 ]; then
        # Direct environment check
        case $1 in
            "dev"|"development")
                check_environment "development"
                ;;
            "prod"|"production")
                check_environment "production"
                ;;
            *)
                print_error "Invalid environment. Use 'dev' or 'prod'"
                exit 1
                ;;
        esac
        exit 0
    fi
    
    # Interactive mode
    while true; do
        show_menu
        read -p "Select an option (1-6): " choice
        
        case $choice in
            1)
                check_environment "development"
                ;;
            2)
                check_environment "production"
                ;;
            3)
                show_resource_usage
                ;;
            4)
                echo "Select environment:"
                echo "1. Development"
                echo "2. Production"
                read -p "Choice (1-2): " env_choice
                
                echo "Available containers: database, redis, backend, frontend"
                read -p "Container name: " container_name
                read -p "Number of lines (default 50): " lines
                lines=${lines:-50}
                
                case $env_choice in
                    1) show_container_logs "$container_name" "docker-compose.dev.yml" "$lines" ;;
                    2) show_container_logs "$container_name" "" "$lines" ;;
                    *) print_error "Invalid choice" ;;
                esac
                ;;
            5)
                print_status "Quick health check..."
                check_service_health "Backend (Dev)" "http://localhost:8000/health/" &
                check_service_health "Frontend (Dev)" "http://localhost:5173/" &
                check_service_health "Backend (Prod)" "http://localhost:8000/health/" &
                check_service_health "Frontend (Prod)" "http://localhost:80/" &
                wait
                ;;
            6)
                print_success "Goodbye!"
                exit 0
                ;;
            *)
                print_error "Invalid option. Please select 1-6."
                ;;
        esac
        
        echo ""
        read -p "Press Enter to continue..."
    done
}

# Run main function
main "$@"