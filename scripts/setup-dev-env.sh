#!/bin/bash

# =================================
# LY-Merch Development Environment Setup
# =================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    local missing_deps=()

    if ! command_exists docker; then
        missing_deps+=("docker")
    fi

    if ! command_exists docker-compose; then
        missing_deps+=("docker-compose")
    fi

    if ! command_exists python3; then
        missing_deps+=("python3")
    fi

    if ! command_exists node; then
        missing_deps+=("node")
    fi

    if ! command_exists npm; then
        missing_deps+=("npm")
    fi

    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_error "Missing required dependencies: ${missing_deps[*]}"
        echo "Please install them before running this script."
        exit 1
    fi

    log_success "All prerequisites are installed"
}

# Setup environment files
setup_environment() {
    log_info "Setting up environment files..."

    if [ ! -f .env ]; then
        cp .env.example .env
        log_success "Created .env file from template"
        log_warning "Please review and update .env file with your settings"
    else
        log_info ".env file already exists, skipping..."
    fi

    if [ ! -f docker-compose.override.yml ]; then
        cp docker-compose.override.yml.example docker-compose.override.yml
        log_success "Created docker-compose.override.yml from template"
        log_info "You can customize docker-compose.override.yml for your development needs"
    else
        log_info "docker-compose.override.yml already exists, skipping..."
    fi
}

# Setup Python environment
setup_python() {
    log_info "Setting up Python backend environment..."

    cd api

    if [ ! -d venv ]; then
        python3 -m venv venv
        log_success "Created Python virtual environment"
    fi

    source venv/bin/activate

    pip install --upgrade pip
    pip install -r requirements.txt
    log_success "Installed Python dependencies"

    # Install development dependencies
    pip install black isort flake8 pytest pytest-cov
    log_success "Installed Python development tools"

    cd ..
}

# Setup Node.js environment
setup_nodejs() {
    log_info "Setting up Node.js frontend environment..."

    cd frontend

    if [ -f package-lock.json ]; then
        npm ci
    else
        npm install
    fi
    log_success "Installed Node.js dependencies"

    cd ..
}

# Setup pre-commit hooks
setup_precommit() {
    log_info "Setting up pre-commit hooks..."

    if command_exists pre-commit; then
        pre-commit install
        pre-commit install --hook-type commit-msg
        log_success "Pre-commit hooks installed"
    else
        log_warning "pre-commit not installed, skipping hook setup"
        log_info "Install with: pip install pre-commit"
    fi
}

# Initialize database
setup_database() {
    log_info "Setting up database..."

    # Start database service
    docker-compose up -d db

    # Wait for database to be ready
    log_info "Waiting for database to be ready..."
    while ! docker-compose exec db mysqladmin ping -h localhost --silent; do
        sleep 2
        echo -n "."
    done
    echo ""
    log_success "Database is ready"

    # Import sample data
    if [ -f data/alls.json ]; then
        log_info "Importing sample data..."
        cd scripts
        ./import_data.sh
        cd ..
        log_success "Sample data imported"
    else
        log_warning "Sample data file not found, skipping data import"
    fi
}

# Test the setup
test_setup() {
    log_info "Testing setup..."

    # Start all services
    docker-compose up -d

    # Wait for services to be ready
    log_info "Waiting for services to start..."
    sleep 10

    # Test API
    if curl -f -s http://localhost:8001/health > /dev/null; then
        log_success "API is responding"
    else
        log_error "API is not responding"
        return 1
    fi

    # Test Frontend
    if curl -f -s http://localhost:8080 > /dev/null; then
        log_success "Frontend is responding"
    else
        log_error "Frontend is not responding"
        return 1
    fi

    log_success "All services are running correctly"
}

# Cleanup function
cleanup() {
    log_info "Cleaning up..."
    docker-compose down > /dev/null 2>&1 || true
}

# Main setup function
main() {
    echo "🚀 LY-Merch Development Environment Setup"
    echo "========================================"
    echo ""

    # Change to script directory
    cd "$(dirname "$0")/.."

    # Trap cleanup on exit
    trap cleanup EXIT

    check_prerequisites
    setup_environment
    setup_python
    setup_nodejs
    setup_precommit
    setup_database
    test_setup

    echo ""
    echo "🎉 Development environment setup complete!"
    echo ""
    echo "Next steps:"
    echo "1. Review and update .env file with your settings"
    echo "2. Customize docker-compose.override.yml if needed"
    echo "3. Start development with: docker-compose up"
    echo ""
    echo "Useful commands:"
    echo "  docker-compose up -d          # Start all services in background"
    echo "  docker-compose logs -f api    # View API logs"
    echo "  docker-compose down           # Stop all services"
    echo ""
    echo "Access points:"
    echo "  Frontend: http://localhost:8080"
    echo "  API: http://localhost:8001"
    echo "  API Docs: http://localhost:8001/docs"
    echo ""
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi