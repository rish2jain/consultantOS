#!/bin/bash
# Integration test script for dashboard agents

set -e

echo "=========================================="
echo "Dashboard Agents Integration Test Suite"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test Phase 1 agents
echo -e "${YELLOW}Testing Phase 1 Dashboard Agents...${NC}"
pytest tests/test_dashboard_agents.py -v --tb=short || {
    echo -e "${RED}Phase 1 tests failed${NC}"
    exit 1
}
echo -e "${GREEN}✓ Phase 1 agents: PASSED${NC}"
echo ""

# Test Phase 2/3 agents
echo -e "${YELLOW}Testing Phase 2/3 Dashboard Agents...${NC}"
pytest tests/test_phase2_3_agents.py -v --tb=short || {
    echo -e "${RED}Phase 2/3 tests failed${NC}"
    exit 1
}
echo -e "${GREEN}✓ Phase 2/3 agents: PASSED${NC}"
echo ""

# Test with coverage
echo -e "${YELLOW}Running coverage analysis...${NC}"
pytest tests/test_dashboard_agents.py tests/test_phase2_3_agents.py \
    --cov=consultantos.agents.dashboard_analytics_agent \
    --cov=consultantos.agents.dashboard_data_agent \
    --cov=consultantos.agents.report_management_agent \
    --cov=consultantos.agents.job_management_agent \
    --cov=consultantos.agents.notification_agent \
    --cov=consultantos.agents.version_control_agent \
    --cov=consultantos.agents.template_agent \
    --cov=consultantos.agents.visualization_agent \
    --cov=consultantos.agents.alert_feedback_agent \
    --cov-report=term-missing \
    --cov-report=html || {
    echo -e "${RED}Coverage test failed${NC}"
    exit 1
}
echo -e "${GREEN}✓ Coverage analysis: COMPLETE${NC}"
echo ""

# Collect test counts programmatically
echo -e "${YELLOW}Collecting test counts...${NC}"
PHASE1_OUTPUT=$(pytest tests/test_dashboard_agents.py --collect-only -q 2>&1)
PHASE1_COUNT=$(echo "$PHASE1_OUTPUT" | grep -c "test_" || echo "0")
if [ -z "$PHASE1_COUNT" ] || ! [ "$PHASE1_COUNT" -ge 0 ] 2>/dev/null; then
    PHASE1_COUNT=0
fi

PHASE2_OUTPUT=$(pytest tests/test_phase2_3_agents.py --collect-only -q 2>&1)
PHASE2_COUNT=$(echo "$PHASE2_OUTPUT" | grep -c "test_" || echo "0")
if [ -z "$PHASE2_COUNT" ] || ! [ "$PHASE2_COUNT" -ge 0 ] 2>/dev/null; then
    PHASE2_COUNT=0
fi

# Calculate total
TOTAL_COUNT=$((PHASE1_COUNT + PHASE2_COUNT))

# Summary
echo "=========================================="
echo -e "${GREEN}All Integration Tests Passed!${NC}"
echo "=========================================="
echo ""
echo "Test Summary:"
echo "  - Phase 1 Agents: $PHASE1_COUNT test cases"
echo "  - Phase 2/3 Agents: $PHASE2_COUNT test cases"
echo "  - Total: $TOTAL_COUNT test cases"
echo ""
echo "Coverage report generated at: htmlcov/index.html"
echo ""

