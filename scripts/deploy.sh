#!/bin/bash

#===============================================================================
# AI Security Lab v4.0 - Deployment Script
# Production deployment automation
#===============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker/compose/docker-compose.prod.yml"
ENV_FILE=".env.production"
BACKUP_DIR="backups"

#===============================================================================
# Helper Functions
#===============================================================================

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

check_requirements() {
    print_header "Checking Requirements"
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi
    print_success "Docker is installed"
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed"
        exit 1
    fi
    print_success "Docker Compose is installed"
    
    # Check environment file
    if [ ! -f "$ENV_FILE" ]; then
        print_warning "Environment file not found: $ENV_FILE"
        print_info "Creating from template..."
        cp .env.example $ENV_FILE
        print_warning "Please edit $ENV_FILE with your production values"
        exit 1
    fi
    print_success "Environment file exists"
    
    echo ""
}

#===============================================================================
# Deployment Functions
#===============================================================================

start_services() {
    print_header "Starting Services"
    
    print_info "Building and starting containers..."
    docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE up -d --build
    
    print_success "Services started"
    echo ""
    
    print_info "Waiting for services to be healthy..."
    sleep 10
    
    show_status
}

stop_services() {
    print_header "Stopping Services"
    
    docker-compose -f $COMPOSE_FILE down
    
    print_success "Services stopped"
    echo ""
}

restart_services() {
    print_header "Restarting Services"
    
    stop_services
    sleep 5
    start_services
}

show_status() {
    print_header "Service Status"
    
    docker-compose -f $COMPOSE_FILE ps
    
    echo ""
    print_info "Health Checks:"
    
    # Check AI Orchestrator
    if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        print_success "AI Orchestrator: Healthy"
    else
        print_error "AI Orchestrator: Unhealthy"
    fi
    
    # Check Dashboard
    if curl -sf http://localhost:3000 > /dev/null 2>&1; then
        print_success "Dashboard: Healthy"
    else
        print_error "Dashboard: Unhealthy"
    fi
    
    # Check TimescaleDB
    if docker exec ai-security-timescaledb pg_isready -U security > /dev/null 2>&1; then
        print_success "TimescaleDB: Healthy"
    else
        print_error "TimescaleDB: Unhealthy"
    fi
    
    echo ""
}

show_logs() {
    print_header "Service Logs"
    
    if [ -z "$1" ]; then
        docker-compose -f $COMPOSE_FILE logs --tail=100 -f
    else
        docker-compose -f $COMPOSE_FILE logs --tail=100 -f $1
    fi
}

run_migrations() {
    print_header "Running Database Migrations"
    
    print_info "Waiting for database to be ready..."
    sleep 5
    
    docker exec ai-security-orchestrator python scripts/migrate.py
    
    print_success "Migrations completed"
    echo ""
}

scale_service() {
    local service=$1
    local replicas=$2
    
    print_header "Scaling Service: $service"
    
    docker-compose -f $COMPOSE_FILE up -d --scale $service=$replicas
    
    print_success "Service scaled to $replicas replicas"
    echo ""
}

#===============================================================================
# Backup Functions
#===============================================================================

backup_database() {
    print_header "Backing Up Database"
    
    mkdir -p $BACKUP_DIR
    
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="$BACKUP_DIR/database_$timestamp.sql"
    
    print_info "Creating backup: $backup_file"
    
    docker exec ai-security-timescaledb pg_dump -U security security_events > $backup_file
    
    # Compress backup
    gzip $backup_file
    
    print_success "Database backed up to: ${backup_file}.gz"
    
    # Keep only last 7 backups
    ls -t $BACKUP_DIR/database_*.sql.gz | tail -n +8 | xargs -r rm
    
    print_info "Old backups cleaned up"
    echo ""
}

restore_database() {
    local backup_file=$1
    
    if [ -z "$backup_file" ]; then
        print_error "Please specify backup file"
        echo "Usage: $0 restore <backup_file>"
        exit 1
    fi
    
    if [ ! -f "$backup_file" ]; then
        print_error "Backup file not found: $backup_file"
        exit 1
    fi
    
    print_header "Restoring Database"
    print_warning "This will overwrite the current database!"
    
    read -p "Are you sure? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        print_info "Restore cancelled"
        exit 0
    fi
    
    print_info "Restoring from: $backup_file"
    
    # Decompress if needed
    if [[ $backup_file == *.gz ]]; then
        gunzip -c $backup_file | docker exec -i ai-security-timescaledb psql -U security security_events
    else
        docker exec -i ai-security-timescaledb psql -U security security_events < $backup_file
    fi
    
    print_success "Database restored"
    echo ""
}

#===============================================================================
# Maintenance Functions
#===============================================================================

cleanup() {
    print_header "Cleaning Up"
    
    print_info "Removing stopped containers..."
    docker-compose -f $COMPOSE_FILE rm -f
    
    print_info "Pruning Docker system..."
    docker system prune -f
    
    print_success "Cleanup completed"
    echo ""
}

update_services() {
    print_header "Updating Services"
    
    print_info "Pulling latest images..."
    docker-compose -f $COMPOSE_FILE pull
    
    print_info "Rebuilding services..."
    docker-compose -f $COMPOSE_FILE build --no-cache
    
    print_info "Restarting services..."
    docker-compose -f $COMPOSE_FILE up -d
    
    print_success "Services updated"
    echo ""
}

#===============================================================================
# Main Script
#===============================================================================

main() {
    case "$1" in
        start)
            check_requirements
            start_services
            ;;
        stop)
            stop_services
            ;;
        restart)
            restart_services
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs "$2"
            ;;
        migrate)
            run_migrations
            ;;
        backup)
            backup_database
            ;;
        restore)
            restore_database "$2"
            ;;
        scale)
            scale_service "$2" "$3"
            ;;
        cleanup)
            cleanup
            ;;
        update)
            update_services
            ;;
        *)
            echo "AI Security Lab v4.0 - Deployment Script"
            echo ""
            echo "Usage: $0 {command} [options]"
            echo ""
            echo "Commands:"
            echo "  start            Start all services"
            echo "  stop             Stop all services"
            echo "  restart          Restart all services"
            echo "  status           Show service status"
            echo "  logs [service]   Show logs (optional: specific service)"
            echo "  migrate          Run database migrations"
            echo "  backup           Backup database"
            echo "  restore <file>   Restore database from backup"
            echo "  scale <service> <n>  Scale service to n replicas"
            echo "  cleanup          Clean up unused resources"
            echo "  update           Update services to latest versions"
            echo ""
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
