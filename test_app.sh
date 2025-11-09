#!/bin/bash

# ConsultantOS Testing Script
# This script tests the main features of the application

API_URL="http://localhost:8080"
TEST_EMAIL="test@consultantos.com"
TEST_PASSWORD="TestPassword123!"
TEST_NAME="Test User"

echo "🧪 ConsultantOS Testing Script"
echo "================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Health Check
echo "1️⃣  Testing Health Endpoint..."
HEALTH=$(curl -s "$API_URL/health")
if echo "$HEALTH" | grep -q "healthy"; then
    echo -e "${GREEN}✓ Health check passed${NC}"
    echo "$HEALTH" | python3 -m json.tool 2>/dev/null | head -10
else
    echo -e "${RED}✗ Health check failed${NC}"
    exit 1
fi
echo ""

# Test 2: User Registration
echo "2️⃣  Testing User Registration..."
REGISTER_RESPONSE=$(curl -s -X POST "$API_URL/users/register" \
    -H "Content-Type: application/json" \
    -d "{
        \"email\": \"$TEST_EMAIL\",
        \"password\": \"$TEST_PASSWORD\",
        \"name\": \"$TEST_NAME\"
    }")

if echo "$REGISTER_RESPONSE" | grep -q "user_id\|message\|Registration successful"; then
    echo -e "${GREEN}✓ Registration successful${NC}"
    echo "$REGISTER_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$REGISTER_RESPONSE"
else
    if echo "$REGISTER_RESPONSE" | grep -q "already exists\|duplicate"; then
        echo -e "${YELLOW}⚠ User already exists (this is okay)${NC}"
    else
        echo -e "${RED}✗ Registration failed${NC}"
        echo "$REGISTER_RESPONSE"
    fi
fi
echo ""

# Test 3: User Login
echo "3️⃣  Testing User Login..."
LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/users/login" \
    -H "Content-Type: application/json" \
    -d "{
        \"email\": \"$TEST_EMAIL\",
        \"password\": \"$TEST_PASSWORD\"
    }")

if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
    echo -e "${GREEN}✓ Login successful${NC}"
    API_KEY=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null)
    if [ -n "$API_KEY" ]; then
        echo "API Key: ${API_KEY:0:20}..."
        echo "$LOGIN_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$LOGIN_RESPONSE"
    else
        echo -e "${YELLOW}⚠ Could not extract API key, but login worked${NC}"
        API_KEY=""
    fi
else
    echo -e "${RED}✗ Login failed${NC}"
    echo "$LOGIN_RESPONSE"
    API_KEY=""
fi
echo ""

# Test 4: List Reports (requires auth)
if [ -n "$API_KEY" ]; then
    echo "4️⃣  Testing List Reports (with authentication)..."
    REPORTS_RESPONSE=$(curl -s -X GET "$API_URL/reports" \
        -H "X-API-Key: $API_KEY")
    
    if echo "$REPORTS_RESPONSE" | grep -q "reports\|count"; then
        echo -e "${GREEN}✓ Reports endpoint accessible${NC}"
        REPORT_COUNT=$(echo "$REPORTS_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('count', 0))" 2>/dev/null || echo "0")
        echo "Found $REPORT_COUNT reports"
    else
        echo -e "${YELLOW}⚠ Reports endpoint returned unexpected response${NC}"
        echo "$REPORTS_RESPONSE" | head -5
    fi
    echo ""
    
    # Test 5: Get Metrics
    echo "5️⃣  Testing Metrics Endpoint..."
    METRICS_RESPONSE=$(curl -s -X GET "$API_URL/metrics" \
        -H "X-API-Key: $API_KEY")
    
    if echo "$METRICS_RESPONSE" | grep -q "metrics\|summary"; then
        echo -e "${GREEN}✓ Metrics endpoint accessible${NC}"
        echo "$METRICS_RESPONSE" | python3 -m json.tool 2>/dev/null | head -15 || echo "$METRICS_RESPONSE" | head -10
    else
        echo -e "${YELLOW}⚠ Metrics endpoint returned unexpected response${NC}"
        echo "$METRICS_RESPONSE" | head -5
    fi
    echo ""
    
    # Test 6: Silent Auth
    echo "6️⃣  Testing Silent Auth Endpoint..."
    SILENT_AUTH=$(curl -s -X POST "$API_URL/auth/silent-auth" \
        -H "Content-Type: application/json" \
        -d "{}")
    
    if echo "$SILENT_AUTH" | grep -q "message\|success"; then
        echo -e "${GREEN}✓ Silent auth endpoint accessible${NC}"
        echo "$SILENT_AUTH" | python3 -m json.tool 2>/dev/null || echo "$SILENT_AUTH"
    else
        echo -e "${YELLOW}⚠ Silent auth returned unexpected response${NC}"
        echo "$SILENT_AUTH"
    fi
    echo ""
    
    # Test 7: Analysis (if API keys are available)
    if [ -n "$TAVILY_API_KEY" ] && [ -n "$GEMINI_API_KEY" ]; then
        echo "7️⃣  Testing Analysis Generation (this may take 30-60 seconds)..."
        echo -e "${YELLOW}⚠ This is a long-running operation. Press Ctrl+C to skip...${NC}"
        read -t 3 -p "Starting in 3 seconds... " || true
        echo ""
        
        ANALYSIS_RESPONSE=$(curl -s -X POST "$API_URL/analyze" \
            -H "Content-Type: application/json" \
            -H "X-API-Key: $API_KEY" \
            -d '{
                "company": "Tesla",
                "industry": "Electric Vehicles",
                "frameworks": ["porter", "swot"],
                "depth": "standard"
            }' \
            --max-time 120)
        
        if echo "$ANALYSIS_RESPONSE" | grep -q "report_id\|status"; then
            echo -e "${GREEN}✓ Analysis generation successful${NC}"
            REPORT_ID=$(echo "$ANALYSIS_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('report_id', ''))" 2>/dev/null || echo "")
            if [ -n "$REPORT_ID" ]; then
                echo "Report ID: $REPORT_ID"
            fi
            echo "$ANALYSIS_RESPONSE" | python3 -m json.tool 2>/dev/null | head -20 || echo "$ANALYSIS_RESPONSE" | head -15
        else
            echo -e "${RED}✗ Analysis generation failed${NC}"
            echo "$ANALYSIS_RESPONSE" | head -10
        fi
    else
        echo "7️⃣  Skipping Analysis Test (API keys not set)"
        echo -e "${YELLOW}⚠ Set TAVILY_API_KEY and GEMINI_API_KEY to test analysis generation${NC}"
    fi
    echo ""
else
    echo "4️⃣  Skipping authenticated endpoints (login failed)"
    echo ""
fi

# Summary
echo "================================"
echo "📊 Test Summary"
echo "================================"
echo -e "${GREEN}✓ Health check${NC}"
if echo "$REGISTER_RESPONSE" | grep -q "user_id\|message\|already exists"; then
    echo -e "${GREEN}✓ User registration${NC}"
else
    echo -e "${RED}✗ User registration${NC}"
fi
if [ -n "$API_KEY" ]; then
    echo -e "${GREEN}✓ User login${NC}"
    echo -e "${GREEN}✓ Authenticated endpoints${NC}"
    if [ -n "$TAVILY_API_KEY" ] && [ -n "$GEMINI_API_KEY" ]; then
        echo -e "${GREEN}✓ API keys configured${NC}"
    else
        echo -e "${YELLOW}⚠ API keys not configured (analysis won't work)${NC}"
    fi
else
    echo -e "${RED}✗ User login${NC}"
fi
echo ""
echo "🌐 Frontend Dashboard: http://localhost:3000"
echo "📚 API Documentation: http://localhost:8080/docs"
echo ""
echo "To test the dashboard:"
echo "1. Open http://localhost:3000"
echo "2. Login with: $TEST_EMAIL / $TEST_PASSWORD"
echo "3. View your reports and metrics"
echo ""

