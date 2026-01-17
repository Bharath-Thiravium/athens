#!/bin/bash

# ============================================================================
# EHS Management System - Docker Setup Script
# ============================================================================
# Complete Docker environment setup without affecting existing venv
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

# Function to check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Docker and Docker Compose are installed"
}

# Function to check if Docker daemon is running
check_docker_daemon() {
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running. Please start Docker first."
        exit 1
    fi
    
    print_success "Docker daemon is running"
}

# Function to create environment file if it doesn't exist
setup_environment() {
    if [ ! -f .env ]; then
        print_warning ".env file not found. Creating from example..."
        cp .env.example .env
        print_warning "Please edit .env file with your configuration before running Docker containers"
        return 1
    fi
    
    print_success "Environment file exists"
    return 0
}

# Function to build Docker images
build_images() {
    local env_type=$1
    
    print_status "Building Docker images for $env_type environment..."
    
    if [ "$env_type" = "development" ]; then
        docker-compose -f docker-compose.dev.yml build --no-cache
    else
        docker-compose build --no-cache
    fi
    
    print_success "Docker images built successfully"
}

# Function to start services
start_services() {
    local env_type=$1
    
    print_status "Starting $env_type services..."
    
    if [ "$env_type" = "development" ]; then
        # Start development services
        docker-compose -f docker-compose.dev.yml up -d database redis
        
        # Wait for database to be ready
        print_status "Waiting for database to be ready..."
        sleep 10
        
        # Start backend and frontend
        docker-compose -f docker-compose.dev.yml up -d backend frontend
        
        # Show development tools option
        echo ""
        print_status "Development environment started successfully!"
        print_status "Services running:"
        print_status "  - Frontend: http://localhost:5173"
        print_status "  - Backend: http://localhost:8004"
        print_status "  - Database: localhost:5433"
        print_status "  - Redis: localhost:6381"
        echo ""
        print_status "To start development tools (pgAdmin, Redis Insight, MailHog):"
        print_status "  docker-compose -f docker-compose.dev.yml --profile tools up -d"
        
    else
        # Start production services
        docker-compose up -d database redis
        
        # Wait for database to be ready
        print_status "Waiting for database to be ready..."
        sleep 15
        
        # Start backend and frontend
        docker-compose up -d backend frontend
        
        # Optionally start nginx load balancer
        read -p "Do you want to start Nginx load balancer? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker-compose --profile production up -d nginx
            print_status "Nginx load balancer started on ports 80 and 443"
        fi
        
        print_success "Production environment started successfully!"
        print_status "Services running:"
        print_status "  - Frontend: http://localhost:8080"
        print_status "  - Backend: http://localhost:8005"
        print_status "  - Database: localhost:5434"
        print_status "  - Redis: localhost:6382"
    fi
}

# Function to run database migrations
run_migrations() {
    local env_type=$1
    
    print_status "Running database migrations..."
    
    if [ "$env_type" = "development" ]; then
        docker-compose -f docker-compose.dev.yml exec backend python manage.py migrate
    else
        docker-compose exec backend python manage.py migrate
    fi
    
    print_success "Database migrations completed"
}

# Function to create superuser
create_superuser() {
    local env_type=$1
    
    read -p "Do you want to create a superuser? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Creating superuser..."
        
        if [ "$env_type" = "development" ]; then
            docker-compose -f docker-compose.dev.yml exec backend python manage.py createsuperuser
        else
            docker-compose exec backend python manage.py createsuperuser
        fi
        
        print_success "Superuser created successfully"
    fi
}

# Function to show logs
show_logs() {
    local env_type=$1
    
    print_status "Showing container logs..."
    
    if [ "$env_type" = "development" ]; then
        docker-compose -f docker-compose.dev.yml logs -f
    else
        docker-compose logs -f
    fi
}

# Function to stop services
stop_services() {
    local env_type=$1
    
    print_status "Stopping $env_type services..."
    
    if [ "$env_type" = "development" ]; then
        docker-compose -f docker-compose.dev.yml down
    else
        docker-compose down
    fi
    
    print_success "Services stopped successfully"
}

# Function to clean up Docker resources
cleanup() {
    print_warning "This will remove all containers, images, and volumes. Are you sure?"
    read -p "Continue? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Cleaning up Docker resources..."
        
        # Stop all containers
        docker-compose down -v
        docker-compose -f docker-compose.dev.yml down -v
        
        # Remove images
        docker rmi $(docker images -q ehs-* 2>/dev/null) 2>/dev/null || true
        
        # Clean up unused resources
        docker system prune -f
        
        print_success "Cleanup completed"
    fi
}

# Main menu
show_menu() {
    echo ""
    echo "============================================================================"
    echo "EHS Management System - Docker Setup"
    echo "============================================================================"
    echo ""
    echo "1. Setup Development Environment"
    echo "2. Setup Production Environment"
    echo "3. Show Logs"
    echo "4. Stop Services"
    echo "5. Run Migrations"
    echo "6. Create Superuser"
    echo "7. Cleanup Docker Resources"
    echo "8. Exit"
    echo ""
}

# Main script
main() {
    print_status "EHS Management System Docker Setup"
    print_status "This script will set up Docker containers without affecting your existing venv"
    echo ""
    
    # Check prerequisites
    check_docker
    check_docker_daemon
    
    # Setup environment
    if ! setup_environment; then
        print_error "Please configure .env file before proceeding"
        exit 1
    fi
    
    while true; do
        show_menu
        read -p "Select an option (1-8): " choice
        
        case $choice in
            1)
                print_status "Setting up Development Environment..."
                build_images "development"
                start_services "development"
                sleep 5
                run_migrations "development"
                create_superuser "development"
                ;;
            2)
                print_status "Setting up Production Environment..."
                build_images "production"
                start_services "production"
                sleep 5
                run_migrations "production"
                create_superuser "production"
                ;;
            3)
                echo "Select environment:"
                echo "1. Development"
                echo "2. Production"
                read -p "Choice (1-2): " env_choice
                case $env_choice in
                    1) show_logs "development" ;;
                    2) show_logs "production" ;;
                    *) print_error "Invalid choice" ;;
                esac
                ;;
            4)
                echo "Select environment to stop:"
                echo "1. Development"
                echo "2. Production"
                echo "3. Both"
                read -p "Choice (1-3): " env_choice
                case $env_choice in
                    1) stop_services "development" ;;
                    2) stop_services "production" ;;
                    3) 
                        stop_services "development"
                        stop_services "production"
                        ;;
                    *) print_error "Invalid choice" ;;
                esac
                ;;
            5)
                echo "Select environment:"
                echo "1. Development"
                echo "2. Production"
                read -p "Choice (1-2): " env_choice
                case $env_choice in
                    1) run_migrations "development" ;;
                    2) run_migrations "production" ;;
                    *) print_error "Invalid choice" ;;
                esac
                ;;
            6)
                echo "Select environment:"
                echo "1. Development"
                echo "2. Production"
                read -p "Choice (1-2): " env_choice
                case $env_choice in
                    1) create_superuser "development" ;;
                    2) create_superuser "production" ;;
                    *) print_error "Invalid choice" ;;
                esac
                ;;
            7)
                cleanup
                ;;
            8)
                print_success "Goodbye!"
                exit 0
                ;;
            *)
                print_error "Invalid option. Please select 1-8."
                ;;
        esac
        
        echo ""
        read -p "Press Enter to continue..."
    done
}

# Run main function
main "$@"
