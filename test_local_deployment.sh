#!/bin/bash
# Quick local deployment test script
# This script runs basic validation before deployment

set -e

echo "=========================================="
echo "ConsultantOS Local Deployment Test"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo -n "Checking Python version... "
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
if [[ $(echo "$PYTHON_VERSION 3.11" | awk '{print ($1 >= $2)}') == 1 ]]; then
    echo -e "${GREEN}✓ Python $PYTHON_VERSION${NC}"
else
    echo -e "${RED}✗ Python $PYTHON_VERSION (requires 3.11+)${NC}"
    exit 1
fi

# Check if Docker is available
echo -n "Checking Docker... "
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✓ Docker available${NC}"
else
    echo -e "${YELLOW}⚠ Docker not found (skipping Docker tests)${NC}"
    SKIP_DOCKER=true
fi

# Check if required files exist
echo -n "Checking Dockerfile... "
if [ -f "Dockerfile" ]; then
    echo -e "${GREEN}✓ Found${NC}"
else
    echo -e "${RED}✗ Not found${NC}"
    exit 1
fi

echo -n "Checking requirements.txt... "
if [ -f "requirements.txt" ]; then
    echo -e "${GREEN}✓ Found${NC}"
else
    echo -e "${RED}✗ Not found${NC}"
    exit 1
fi

# Run Python test script
echo ""
echo "Running comprehensive tests..."
echo ""

if [ "$SKIP_DOCKER" = true ]; then
    python3 test_local_deployment.py --skip-docker
else
    python3 test_local_deployment.py
fi

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo -e "${GREEN}=========================================="
    echo "All tests passed! Ready for deployment."
    echo "==========================================${NC}"
else
    echo ""
    echo -e "${RED}=========================================="
    echo "Some tests failed. Fix issues before deploying."
    echo "==========================================${NC}"
fi

exit $EXIT_CODE


