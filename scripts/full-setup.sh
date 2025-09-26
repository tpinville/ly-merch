#!/bin/bash

# =================================
# LY-Merch Full Setup Script
# Complete database build and data import from scratch
# =================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Helper functions
log_header() {
    echo ""
    echo -e "${BOLD}${PURPLE}=================================${NC}"
    echo -e "${BOLD}${PURPLE} $1${NC}"
    echo -e "${BOLD}${PURPLE}=================================${NC}"
}

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

log_step() {
    echo -e "${CYAN}🔄 $1${NC}"
}

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DATA_FILE="$PROJECT_ROOT/data/alls.json"

# Default values
CLEAN_VOLUMES=true
IMPORT_DATA=true
START_FRONTEND=true
RUN_TESTS=false
VERBOSE=false

# Parse command line arguments
usage() {
    echo "LY-Merch Full Setup Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --no-clean-volumes    Don't remove existing Docker volumes"
    echo "  --no-import-data      Don't import data from alls.json"
    echo "  --no-frontend         Don't start frontend service"
    echo "  --run-tests           Run API tests after setup"
    echo "  -v, --verbose         Enable verbose output"
    echo "  -h, --help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                           # Full setup with all defaults"
    echo "  $0 --no-frontend --run-tests # Setup without frontend, run tests"
    echo "  $0 --no-clean-volumes        # Setup without removing existing data"
}

while [[ $# -gt 0 ]]; do
    case $1 in
        --no-clean-volumes)
            CLEAN_VOLUMES=false
            shift
            ;;
        --no-import-data)
            IMPORT_DATA=false
            shift
            ;;
        --no-frontend)
            START_FRONTEND=false
            shift
            ;;
        --run-tests)
            RUN_TESTS=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Main setup function
main() {
    log_header "LY-MERCH FULL SETUP"
    echo -e "${BOLD}Complete database build and data import from scratch${NC}"
    echo ""
    echo "Configuration:"
    echo "  Clean Volumes: $CLEAN_VOLUMES"
    echo "  Import Data: $IMPORT_DATA"
    echo "  Start Frontend: $START_FRONTEND"
    echo "  Run Tests: $RUN_TESTS"
    echo "  Verbose: $VERBOSE"
    echo ""

    # Change to project root
    cd "$PROJECT_ROOT"

    # Step 1: Prerequisites check
    check_prerequisites

    # Step 2: Stop existing services and clean up
    cleanup_existing_services

    # Step 3: Start database service
    start_database_service

    # Step 4: Start API service and create tables
    start_api_service

    # Step 5: Import data
    if [ "$IMPORT_DATA" = true ]; then
        import_sample_data
    else
        log_warning "Skipping data import as requested"
    fi

    # Step 6: Start frontend (optional)
    if [ "$START_FRONTEND" = true ]; then
        start_frontend_service
    else
        log_warning "Skipping frontend startup as requested"
    fi

    # Step 7: Verification
    verify_setup

    # Step 8: Run tests (optional)
    if [ "$RUN_TESTS" = true ]; then
        run_api_tests
    fi

    # Step 9: Final summary
    show_final_summary
}

check_prerequisites() {
    log_header "CHECKING PREREQUISITES"

    local missing_deps=()

    log_step "Checking required tools..."

    if ! command -v docker >/dev/null 2>&1; then
        missing_deps+=("docker")
    fi

    if ! command -v docker-compose >/dev/null 2>&1; then
        missing_deps+=("docker-compose")
    fi

    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_error "Missing required dependencies: ${missing_deps[*]}"
        echo ""
        echo "Please install the missing dependencies:"
        echo "  Docker: https://docs.docker.com/get-docker/"
        echo "  Docker Compose: https://docs.docker.com/compose/install/"
        exit 1
    fi

    log_success "All prerequisites installed"

    # Check if .env file exists
    if [ ! -f .env ]; then
        log_warning ".env file not found"
        if [ -f .env.example ]; then
            log_step "Creating .env from .env.example..."
            cp .env.example .env
            log_success "Created .env file from template"
            log_warning "Please review and update .env file if needed"
        else
            log_error ".env.example file not found. Cannot create .env file."
            exit 1
        fi
    else
        log_success ".env file exists"
    fi

    # Check data file
    if [ "$IMPORT_DATA" = true ]; then
        if [ ! -f "$DATA_FILE" ]; then
            log_error "Data file not found: $DATA_FILE"
            echo "Please ensure the alls.json file exists in the data/ directory"
            exit 1
        fi
        log_success "Data file found: $(basename "$DATA_FILE")"
    fi
}

cleanup_existing_services() {
    log_header "CLEANING UP EXISTING SERVICES"

    log_step "Stopping all Docker Compose services..."
    docker-compose down || true
    log_success "Services stopped"

    if [ "$CLEAN_VOLUMES" = true ]; then
        log_step "Removing Docker volumes..."

        # List and remove ly-merch volumes
        local volumes=$(docker volume ls -q | grep "ly-merch" || true)
        if [ -n "$volumes" ]; then
            echo "$volumes" | xargs docker volume rm || true
            log_success "Removed Docker volumes: $volumes"
        else
            log_info "No ly-merch volumes found to remove"
        fi

        # Clean up any orphaned containers
        log_step "Cleaning up orphaned containers..."
        docker-compose down --remove-orphans || true
        log_success "Cleanup completed"
    else
        log_warning "Skipping volume cleanup as requested"
    fi

    # Clean up any dangling images (optional)
    if [ "$VERBOSE" = true ]; then
        log_step "Cleaning up dangling images..."
        docker image prune -f || true
        log_success "Dangling images removed"
    fi
}

start_database_service() {
    log_header "STARTING DATABASE SERVICE"

    log_step "Starting MySQL database..."
    docker-compose up -d db

    log_step "Waiting for database to be healthy..."
    local attempts=0
    local max_attempts=60

    while [ $attempts -lt $max_attempts ]; do
        if docker-compose ps db | grep -q "healthy"; then
            log_success "Database is healthy and ready"
            return 0
        fi

        attempts=$((attempts + 1))
        echo -n "."
        sleep 2
    done

    echo ""
    log_error "Database failed to become healthy within $((max_attempts * 2)) seconds"
    log_info "Checking database logs..."
    docker-compose logs db | tail -20
    exit 1
}

start_api_service() {
    log_header "STARTING API SERVICE"

    log_step "Starting FastAPI service..."
    docker-compose up -d api

    log_step "Waiting for API to be ready..."
    local attempts=0
    local max_attempts=30

    while [ $attempts -lt $max_attempts ]; do
        if curl -f -s http://localhost:8001/health >/dev/null 2>&1; then
            log_success "API is responding"
            break
        fi

        attempts=$((attempts + 1))
        echo -n "."
        sleep 2
    done

    echo ""

    if [ $attempts -eq $max_attempts ]; then
        log_error "API failed to start within $((max_attempts * 2)) seconds"
        log_info "Checking API logs..."
        docker-compose logs api | tail -20
        exit 1
    fi

    log_step "Creating database tables..."
    docker-compose exec -T api python -c "
from app.database import engine, create_tables, test_connection
from app.models import Base
from sqlalchemy import text

print('🔧 Testing database connection...')
if not test_connection():
    print('❌ Database connection failed')
    exit(1)

print('✅ Database connection successful')

print('🔧 Creating tables...')
create_tables()
print('✅ Tables created successfully')

# Verify tables exist
with engine.connect() as conn:
    result = conn.execute(text('SHOW TABLES')).fetchall()
    tables = [row[0] for row in result]
    print(f'📋 Tables created: {len(tables)} tables')
    if len(tables) >= 5:
        print('🎉 Database initialization complete!')
    else:
        print('❌ Expected at least 5 tables, got {len(tables)}')
        exit(1)
"

    if [ $? -ne 0 ]; then
        log_error "Failed to create database tables"
        exit 1
    fi

    log_success "Database tables created successfully"
}

import_sample_data() {
    log_header "IMPORTING SAMPLE DATA"

    log_step "Copying data file to API container..."
    docker-compose exec -T api mkdir -p /data
    docker cp "$DATA_FILE" ly-merch_api_1:/data/alls.json

    log_step "Importing data from alls.json..."
    docker-compose exec -T api python -c "
import json
import re
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db, engine
from app.models import Category, Vertical, Trend, TrendImage

def parse_json_file(filepath):
    print(f'📖 Reading {filepath}...')
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    json_objects_raw = re.split(r'}\s*{', content)
    print(f'Found {len(json_objects_raw)} JSON objects')

    if len(json_objects_raw) == 1:
        return [json.loads(content)]

    json_objects_raw[0] += '}'
    for i in range(1, len(json_objects_raw)-1):
        json_objects_raw[i] = '{' + json_objects_raw[i] + '}'
    json_objects_raw[-1] = '{' + json_objects_raw[-1]

    parsed_objects = []
    for i, obj_str in enumerate(json_objects_raw):
        try:
            obj = json.loads(obj_str)
            parsed_objects.append(obj)
        except json.JSONDecodeError as e:
            print(f'❌ Error parsing JSON object {i+1}: {e}')
            continue

    print(f'✅ Successfully parsed {len(parsed_objects)} JSON objects')
    return parsed_objects

def get_or_create_category(session, category_name):
    category = session.query(Category).filter(Category.name == category_name).first()
    if not category:
        category = Category(name=category_name, description=f'{category_name} category')
        session.add(category)
        session.flush()
    return category.id

def get_or_create_trend(session, trend_data, vertical_id):
    existing_trend = session.query(Trend).filter(Trend.trend_id == trend_data['trend_id']).first()
    if existing_trend:
        return existing_trend.id, False

    trend = Trend(
        trend_id=trend_data['trend_id'],
        vertical_id=vertical_id,
        name=trend_data['name'],
        description=trend_data.get('description', ''),
        image_hash=trend_data.get('image', '')
    )
    session.add(trend)
    session.flush()
    return trend.id, True

# Main import
print('🚀 Starting data import from alls.json')
session = None

try:
    json_objects = parse_json_file('/data/alls.json')

    if not json_objects:
        print('❌ No valid JSON objects found')
        exit(1)

    session = next(get_db())

    # Clear existing data
    print('🗑️ Clearing existing data...')
    session.execute(text('SET FOREIGN_KEY_CHECKS = 0'))
    for table in ['trend_images', 'trends', 'verticals']:
        session.execute(text(f'TRUNCATE TABLE {table}'))
    session.execute(text('SET FOREIGN_KEY_CHECKS = 1'))
    session.commit()

    total_verticals = 0
    total_trends = 0
    total_images = 0
    processed_objects = 0

    for obj_idx, json_obj in enumerate(json_objects):
        processed_objects += 1
        if processed_objects % 3 == 0 or processed_objects == len(json_objects):
            print(f'🔄 Processing JSON object {processed_objects}/{len(json_objects)}')

        verticals = json_obj.get('verticals', [])

        for vertical in verticals:
            # Extract category from vertical_id
            category_name = vertical['vertical_id'].split(':')[0]
            category_id = get_or_create_category(session, category_name)

            # Check if vertical already exists
            existing_vertical = session.query(Vertical).filter(Vertical.vertical_id == vertical['vertical_id']).first()
            if existing_vertical:
                vertical_id = existing_vertical.id
            else:
                # Insert new vertical
                db_vertical = Vertical(
                    vertical_id=vertical['vertical_id'],
                    category_id=category_id,
                    name=vertical['name'],
                    geo_zone=vertical['geo_zone']
                )
                session.add(db_vertical)
                session.flush()
                vertical_id = db_vertical.id
                total_verticals += 1

            for trend in vertical.get('trends', []):
                # Handle duplicate trends
                trend_db_id, is_new_trend = get_or_create_trend(session, trend, vertical_id)

                if is_new_trend:
                    total_trends += 1

                # Insert images (only for new trends)
                if is_new_trend:
                    pos_images = trend.get('positive_images', [])
                    neg_images = trend.get('negative_images', [])

                    for img in pos_images:
                        db_image = TrendImage(
                            trend_id=trend_db_id,
                            image_type='positive',
                            md5_hash=img['md5'],
                            description=img.get('description', '')
                        )
                        session.add(db_image)
                        total_images += 1

                    for img in neg_images:
                        db_image = TrendImage(
                            trend_id=trend_db_id,
                            image_type='negative',
                            md5_hash=img['md5'],
                            description=img.get('description', '')
                        )
                        session.add(db_image)
                        total_images += 1

    # Commit all changes
    session.commit()

    print('🎉 Import completed successfully!')
    print(f'📊 Summary:')
    print(f'  • Verticals: {total_verticals}')
    print(f'  • Trends: {total_trends}')
    print(f'  • Images: {total_images}')

    # Final verification
    print('🔍 Verifying final counts...')
    with engine.connect() as conn:
        category_count = conn.execute(text('SELECT COUNT(*) FROM categories')).scalar()
        vertical_count = conn.execute(text('SELECT COUNT(*) FROM verticals')).scalar()
        trend_count = conn.execute(text('SELECT COUNT(*) FROM trends')).scalar()
        image_count = conn.execute(text('SELECT COUNT(*) FROM trend_images')).scalar()

        print(f'  categories: {category_count}')
        print(f'  verticals: {vertical_count}')
        print(f'  trends: {trend_count}')
        print(f'  trend_images: {image_count}')

        if category_count > 0 and vertical_count > 0 and trend_count > 0:
            print('✅ Data import verification successful!')
        else:
            print('❌ Data import verification failed!')
            exit(1)

except Exception as e:
    print(f'❌ Import failed: {e}')
    if session:
        session.rollback()
    exit(1)
finally:
    if session:
        session.close()
"

    if [ $? -ne 0 ]; then
        log_error "Data import failed"
        exit 1
    fi

    log_success "Sample data imported successfully"
}

start_frontend_service() {
    log_header "STARTING FRONTEND SERVICE"

    log_step "Starting React frontend..."
    docker-compose up -d frontend

    log_step "Waiting for frontend to be ready..."
    local attempts=0
    local max_attempts=30

    while [ $attempts -lt $max_attempts ]; do
        if curl -f -s http://localhost:8080 >/dev/null 2>&1; then
            log_success "Frontend is responding"
            return 0
        fi

        attempts=$((attempts + 1))
        echo -n "."
        sleep 2
    done

    echo ""
    log_warning "Frontend may not be fully ready, but continuing..."
}

verify_setup() {
    log_header "VERIFYING SETUP"

    log_step "Checking all services..."
    docker-compose ps

    echo ""
    log_step "Testing API health..."
    local health_response=$(curl -s http://localhost:8001/health)

    if echo "$health_response" | grep -q '"status":"ok"'; then
        log_success "API health check passed"

        # Extract and display database counts
        if command -v jq >/dev/null 2>&1; then
            echo ""
            echo "Database Status:"
            echo "$health_response" | jq '.database.table_counts'
        else
            log_info "Install 'jq' for prettier JSON output"
            echo "Health Response: $health_response"
        fi
    else
        log_error "API health check failed"
        echo "Response: $health_response"
        exit 1
    fi

    echo ""
    log_step "Testing API statistics..."
    local stats_response=$(curl -s http://localhost:8001/api/v1/stats)

    if echo "$stats_response" | grep -q '"total_categories"'; then
        log_success "API statistics endpoint working"

        if command -v jq >/dev/null 2>&1; then
            echo ""
            echo "Data Summary:"
            echo "$stats_response" | jq '{
                total_categories,
                total_verticals,
                total_trends,
                total_images,
                total_products
            }'
        fi
    else
        log_error "API statistics endpoint failed"
        echo "Response: $stats_response"
        exit 1
    fi

    if [ "$START_FRONTEND" = true ]; then
        echo ""
        log_step "Testing frontend..."
        if curl -f -s http://localhost:8080 >/dev/null 2>&1; then
            log_success "Frontend is accessible"
        else
            log_warning "Frontend may not be fully ready yet"
        fi
    fi
}

run_api_tests() {
    log_header "RUNNING API TESTS"

    log_step "Running integration tests..."

    if [ -f "$SCRIPT_DIR/test-api-integration.py" ]; then
        cd "$SCRIPT_DIR"
        if python3 test-api-integration.py; then
            log_success "API integration tests passed"
        else
            log_warning "Some API tests failed, but setup is complete"
        fi
    else
        log_warning "Integration test script not found, skipping tests"
    fi
}

show_final_summary() {
    log_header "SETUP COMPLETE"

    echo -e "${BOLD}🎉 LY-Merch platform is now fully operational!${NC}"
    echo ""
    echo "Access Points:"
    echo -e "  🌐 Frontend:     ${CYAN}http://localhost:8080${NC}"
    echo -e "  🚀 API:          ${CYAN}http://localhost:8001${NC}"
    echo -e "  📚 API Docs:     ${CYAN}http://localhost:8001/docs${NC}"
    echo -e "  🔍 Health:       ${CYAN}http://localhost:8001/health${NC}"
    echo -e "  📊 Statistics:   ${CYAN}http://localhost:8001/api/v1/stats${NC}"
    echo ""
    echo "Management Commands:"
    echo "  docker-compose ps              # Check service status"
    echo "  docker-compose logs -f api     # View API logs"
    echo "  docker-compose down            # Stop all services"
    echo "  docker-compose up -d           # Start all services"
    echo ""
    echo "Next Steps:"
    echo "  1. Visit the frontend at http://localhost:8080"
    echo "  2. Explore the API documentation at http://localhost:8001/docs"
    echo "  3. Test product uploads using the bulk upload feature"
    echo "  4. Import your own CSV product data"
    echo ""

    if [ "$VERBOSE" = true ]; then
        echo "Detailed Service Information:"
        docker-compose ps
        echo ""
        echo "Recent API Logs:"
        docker-compose logs --tail=10 api
    fi

    log_success "Full setup completed successfully!"
}

# Trap cleanup on exit
cleanup_on_exit() {
    if [ $? -ne 0 ]; then
        echo ""
        log_error "Setup failed. Checking logs..."

        echo ""
        echo "Recent API logs:"
        docker-compose logs --tail=20 api || true

        echo ""
        echo "Recent DB logs:"
        docker-compose logs --tail=10 db || true

        echo ""
        echo "To manually debug:"
        echo "  docker-compose ps              # Check service status"
        echo "  docker-compose logs api        # Full API logs"
        echo "  docker-compose logs db         # Full DB logs"
        echo "  docker-compose down            # Stop and cleanup"
    fi
}

trap cleanup_on_exit EXIT

# Run main function
main "$@"