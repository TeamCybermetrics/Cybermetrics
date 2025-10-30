#!/bin/bash

# Test runner script for Cybermetrics backend
# Usage: ./run_tests.sh [options]

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Cybermetrics Test Suite ===${NC}\n"

# Parse command line arguments
COVERAGE=false
VERBOSE=false
SPECIFIC_PATH=""
TEST_TYPE="all"

while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--coverage)
            COVERAGE=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -p|--path)
            SPECIFIC_PATH="$2"
            shift 2
            ;;
        -t|--type)
            TEST_TYPE="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: ./run_tests.sh [options]"
            echo ""
            echo "Options:"
            echo "  -c, --coverage       Run tests with coverage report"
            echo "  -v, --verbose        Run tests with verbose output"
            echo "  -p, --path PATH      Run tests for specific path"
            echo "  -t, --type TYPE      Run specific test type (unit|integration|e2e|all)"
            echo "  -h, --help           Show this help message"
            echo ""
            echo "Examples:"
            echo "  ./run_tests.sh                      # Run all tests"
            echo "  ./run_tests.sh -c                   # Run with coverage"
            echo "  ./run_tests.sh -v                   # Run with verbose output"
            echo "  ./run_tests.sh -t unit              # Run unit tests only"
            echo "  ./run_tests.sh -t integration       # Run integration tests only"
            echo "  ./run_tests.sh -t e2e               # Run E2E tests only"
            echo "  ./run_tests.sh -p domain/tests      # Run domain tests only"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

# Build pytest command
PYTEST_CMD="pytest"

if [ "$VERBOSE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -v"
fi

if [ "$COVERAGE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD --cov=. --cov-report=html --cov-report=term-missing --cov-config=pytest.ini"
fi

# Determine test paths based on type
if [ -n "$SPECIFIC_PATH" ]; then
    PYTEST_CMD="$PYTEST_CMD $SPECIFIC_PATH"
elif [ "$TEST_TYPE" = "unit" ]; then
    PYTEST_CMD="$PYTEST_CMD domain/tests services/tests models/tests middleware/tests"
elif [ "$TEST_TYPE" = "integration" ]; then
    PYTEST_CMD="$PYTEST_CMD tests/integration"
elif [ "$TEST_TYPE" = "e2e" ]; then
    PYTEST_CMD="$PYTEST_CMD tests/e2e -m e2e"
elif [ "$TEST_TYPE" = "all" ]; then
    # Run all tests
    PYTEST_CMD="$PYTEST_CMD"
else
    echo -e "${RED}Invalid test type: $TEST_TYPE${NC}"
    echo "Valid types: unit, integration, e2e, all"
    exit 1
fi

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}Error: pytest is not installed${NC}"
    echo "Install test dependencies with: pip install -r requirements.txt"
    exit 1
fi

# Run tests
echo -e "${YELLOW}Running tests...${NC}\n"
$PYTEST_CMD

# Check exit code
if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✓ All tests passed!${NC}"
    
    if [ "$COVERAGE" = true ]; then
        echo -e "${YELLOW}Coverage report generated in htmlcov/index.html${NC}"
    fi
else
    echo -e "\n${RED}✗ Some tests failed${NC}"
    exit 1
fi
