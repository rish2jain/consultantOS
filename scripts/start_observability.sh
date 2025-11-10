#!/bin/bash

##############################################################################
# ConsultantOS Observability Stack Startup Script
#
# This script starts the complete observability stack with Prometheus, Grafana,
# and AlertManager for monitoring and alerting.
#
# Usage:
#   ./scripts/start_observability.sh [up|down|logs|restart]
#
# Options:
#   up       - Start the observability stack (default)
#   down     - Stop and remove the observability stack
#   logs     - View logs from all services
#   restart  - Restart the observability stack
#
##############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Docker compose file
COMPOSE_FILE="$PROJECT_DIR/docker-compose.observability.yml"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed${NC}"
    exit 1
fi

# Function to print section headers
print_header() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}\n"
}

# Function to print success messages
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print error messages
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Function to print warning messages
print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Function to start the stack
start_stack() {
    print_header "Starting ConsultantOS Observability Stack"

    # Check if required directories and files exist
    if [ ! -f "$COMPOSE_FILE" ]; then
        print_error "Docker Compose file not found: $COMPOSE_FILE"
        exit 1
    fi

    # Start services
    print_warning "Starting services..."
    docker-compose -f "$COMPOSE_FILE" up -d

    # Wait for services to be ready
    print_warning "Waiting for services to be ready..."
    sleep 5

    # Check service status
    print_warning "Checking service health..."

    # Prometheus
    if curl -s http://localhost:9090/-/healthy > /dev/null 2>&1; then
        print_success "Prometheus is running on http://localhost:9090"
    else
        print_warning "Prometheus health check pending..."
    fi

    # Grafana
    if curl -s http://localhost:3001/api/health > /dev/null 2>&1; then
        print_success "Grafana is running on http://localhost:3001"
        echo -e "  ${YELLOW}Default credentials: admin/admin${NC}"
    else
        print_warning "Grafana health check pending..."
    fi

    # AlertManager
    if curl -s http://localhost:9093/-/healthy > /dev/null 2>&1; then
        print_success "AlertManager is running on http://localhost:9093"
    else
        print_warning "AlertManager health check pending..."
    fi

    print_header "Observability Stack Started"
    echo -e "${GREEN}Services are starting up. Please wait a moment for full initialization.${NC}\n"

    echo "Available services:"
    echo -e "  ${BLUE}Prometheus${NC}   : http://localhost:9090"
    echo -e "  ${BLUE}Grafana${NC}      : http://localhost:3001 (admin/admin)"
    echo -e "  ${BLUE}AlertManager${NC} : http://localhost:9093"
    echo ""
    echo "Quick start:"
    echo "  1. Open Grafana at http://localhost:3001"
    echo "  2. Log in with admin/admin"
    echo "  3. Dashboards should be auto-provisioned in the 'ConsultantOS' folder"
    echo "  4. View metrics from Prometheus data source"
    echo ""
    echo "To view logs:"
    echo "  docker-compose -f $COMPOSE_FILE logs -f [service-name]"
    echo ""
}

# Function to stop the stack
stop_stack() {
    print_header "Stopping ConsultantOS Observability Stack"

    docker-compose -f "$COMPOSE_FILE" down

    print_success "Observability stack stopped"
}

# Function to view logs
view_logs() {
    print_header "ConsultantOS Observability Stack Logs"

    if [ $# -gt 1 ]; then
        docker-compose -f "$COMPOSE_FILE" logs -f "$2"
    else
        docker-compose -f "$COMPOSE_FILE" logs -f
    fi
}

# Function to restart the stack
restart_stack() {
    print_header "Restarting ConsultantOS Observability Stack"

    docker-compose -f "$COMPOSE_FILE" restart

    print_success "Observability stack restarted"
    sleep 3

    print_header "Stack Status After Restart"
    docker-compose -f "$COMPOSE_FILE" ps
}

# Function to show status
show_status() {
    print_header "ConsultantOS Observability Stack Status"

    docker-compose -f "$COMPOSE_FILE" ps

    echo ""
    echo "Health checks:"

    if curl -s http://localhost:9090/-/healthy > /dev/null 2>&1; then
        print_success "Prometheus is healthy"
    else
        print_error "Prometheus is not responding"
    fi

    if curl -s http://localhost:3001/api/health > /dev/null 2>&1; then
        print_success "Grafana is healthy"
    else
        print_error "Grafana is not responding"
    fi

    if curl -s http://localhost:9093/-/healthy > /dev/null 2>&1; then
        print_success "AlertManager is healthy"
    else
        print_error "AlertManager is not responding"
    fi
}

# Function to validate configuration
validate_config() {
    print_header "Validating Configuration"

    # Check Prometheus config
    if [ -f "$PROJECT_DIR/prometheus/prometheus.yml" ]; then
        print_success "Prometheus config found"
    else
        print_warning "Prometheus config not found at $PROJECT_DIR/prometheus/prometheus.yml"
    fi

    # Check Prometheus alerts
    if [ -f "$PROJECT_DIR/prometheus/alerts.yml" ]; then
        print_success "Prometheus alerts found"
    else
        print_warning "Prometheus alerts not found at $PROJECT_DIR/prometheus/alerts.yml"
    fi

    # Check Grafana dashboards
    dashboard_count=$(find "$PROJECT_DIR/grafana/dashboards" -name "*.json" 2>/dev/null | wc -l)
    if [ "$dashboard_count" -gt 0 ]; then
        print_success "Found $dashboard_count Grafana dashboards"
    else
        print_warning "No Grafana dashboards found"
    fi

    # Check AlertManager config
    if [ -f "$PROJECT_DIR/alertmanager/config.yml" ]; then
        print_success "AlertManager config found"
    else
        print_warning "AlertManager config not found at $PROJECT_DIR/alertmanager/config.yml"
    fi
}

# Main script logic
case "${1:-up}" in
    up)
        start_stack
        ;;
    down)
        stop_stack
        ;;
    logs)
        view_logs "$@"
        ;;
    restart)
        restart_stack
        ;;
    status)
        show_status
        ;;
    validate)
        validate_config
        ;;
    *)
        echo "Usage: $0 {up|down|logs|restart|status|validate}"
        echo ""
        echo "Commands:"
        echo "  up       - Start the observability stack"
        echo "  down     - Stop the observability stack"
        echo "  logs     - View stack logs"
        echo "  restart  - Restart the observability stack"
        echo "  status   - Show stack status"
        echo "  validate - Validate configuration files"
        exit 1
        ;;
esac
