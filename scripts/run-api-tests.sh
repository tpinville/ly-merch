#!/bin/bash

# =================================
# LY-Merch API Test Runner
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

# Configuration
API_DIR="$(dirname "$0")/../api"
TEST_RESULTS_DIR="$API_DIR/test-results"

# Default values
COVERAGE_MIN=80
TEST_PATTERN="test_*.py"
VERBOSE=false
COVERAGE=true
PARALLEL=false
INTEGRATION_TESTS=true
PERFORMANCE_TESTS=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        --no-coverage)
            COVERAGE=false
            shift
            ;;
        --parallel)
            PARALLEL=true
            shift
            ;;
        --no-integration)
            INTEGRATION_TESTS=false
            shift
            ;;
        --performance)
            PERFORMANCE_TESTS=true
            shift
            ;;
        --pattern)
            TEST_PATTERN="$2"
            shift 2
            ;;
        --coverage-min)
            COVERAGE_MIN="$2"
            shift 2
            ;;
        -h|--help)
            echo "LY-Merch API Test Runner"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -v, --verbose          Enable verbose output"
            echo "  --no-coverage          Disable coverage reporting"
            echo "  --parallel             Run tests in parallel"
            echo "  --no-integration       Skip integration tests"
            echo "  --performance          Include performance tests"
            echo "  --pattern PATTERN      Test file pattern (default: test_*.py)"
            echo "  --coverage-min PERCENT Minimum coverage percentage (default: 80)"
            echo "  -h, --help             Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                     Run all tests with coverage"
            echo "  $0 --parallel -v       Run tests in parallel with verbose output"
            echo "  $0 --pattern 'test_products.py'  Run only product tests"
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Check if we're in the right directory
if [ ! -f "$API_DIR/app/main.py" ]; then
    log_error "API directory not found. Please run this script from the project root."
    exit 1
fi

# Change to API directory
cd "$API_DIR"

log_info "Starting LY-Merch API tests..."

# Create test results directory
mkdir -p "$TEST_RESULTS_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    log_warning "Virtual environment not found. Creating one..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install test dependencies
log_info "Installing test dependencies..."
pip install -q -r requirements.txt
pip install -q -r requirements-test.txt

# Build pytest command
PYTEST_CMD="pytest"

# Add verbosity
if [ "$VERBOSE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -v"
else
    PYTEST_CMD="$PYTEST_CMD -q"
fi

# Add coverage
if [ "$COVERAGE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD --cov=app --cov-report=term-missing --cov-report=html:$TEST_RESULTS_DIR/htmlcov --cov-report=xml:$TEST_RESULTS_DIR/coverage.xml --cov-fail-under=$COVERAGE_MIN"
fi

# Add parallel execution
if [ "$PARALLEL" = true ]; then
    # Check if pytest-xdist is installed
    if pip list | grep -q pytest-xdist; then
        PYTEST_CMD="$PYTEST_CMD -n auto"
    else
        log_warning "pytest-xdist not installed, running tests sequentially"
    fi
fi

# Add test selection markers
TEST_MARKERS=""

if [ "$INTEGRATION_TESTS" = false ]; then
    TEST_MARKERS="not integration"
fi

if [ "$PERFORMANCE_TESTS" = true ]; then
    if [ -n "$TEST_MARKERS" ]; then
        TEST_MARKERS="$TEST_MARKERS or performance"
    else
        TEST_MARKERS="performance"
    fi
else
    if [ -n "$TEST_MARKERS" ]; then
        TEST_MARKERS="$TEST_MARKERS and not performance"
    else
        TEST_MARKERS="not performance"
    fi
fi

if [ -n "$TEST_MARKERS" ]; then
    PYTEST_CMD="$PYTEST_CMD -m \"$TEST_MARKERS\""
fi

# Add test pattern
PYTEST_CMD="$PYTEST_CMD tests/$TEST_PATTERN"

# Add additional options
PYTEST_CMD="$PYTEST_CMD --tb=short --strict-markers --junit-xml=$TEST_RESULTS_DIR/junit.xml"

log_info "Running tests with command: $PYTEST_CMD"

# Run tests
if eval "$PYTEST_CMD"; then
    log_success "All tests passed!"

    # Display coverage summary if enabled
    if [ "$COVERAGE" = true ] && [ -f "$TEST_RESULTS_DIR/coverage.xml" ]; then
        echo ""
        log_info "Coverage report generated:"
        echo "  - HTML: $TEST_RESULTS_DIR/htmlcov/index.html"
        echo "  - XML: $TEST_RESULTS_DIR/coverage.xml"
    fi

    # Display test results
    if [ -f "$TEST_RESULTS_DIR/junit.xml" ]; then
        echo "  - JUnit: $TEST_RESULTS_DIR/junit.xml"
    fi

    echo ""
    log_success "Test run completed successfully!"
    exit 0
else
    log_error "Some tests failed!"

    # Show recent failures if verbose
    if [ "$VERBOSE" = true ]; then
        echo ""
        log_info "Recent test failures (if any):"
        # This would show pytest output, which is already displayed above
    fi

    # Still generate coverage report for analysis
    if [ "$COVERAGE" = true ] && [ -f "$TEST_RESULTS_DIR/coverage.xml" ]; then
        echo ""
        log_info "Coverage report (for analysis):"
        echo "  - HTML: $TEST_RESULTS_DIR/htmlcov/index.html"
        echo "  - XML: $TEST_RESULTS_DIR/coverage.xml"
    fi

    exit 1
fi