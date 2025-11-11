#!/bin/bash
# Quick test script for local dashboard endpoints

set -e

API_URL="${API_URL:-http://localhost:8080}"
API_KEY="${API_KEY:-}"

echo "🧪 Testing Local Dashboard Endpoints"
echo "===================================="
echo "API URL: $API_URL"
echo ""

# Check if API key is provided
if [ -z "$API_KEY" ]; then
    echo "⚠️  Warning: API_KEY not set. Some tests will fail."
    echo "   Set it with: export API_KEY='your-key-here'"
    echo ""
fi

# Test 1: Health check
echo "1️⃣  Testing health endpoint..."
HEALTH=$(curl -s "$API_URL/health")
if echo "$HEALTH" | grep -q "healthy"; then
    echo "   ✅ Health check passed"
else
    echo "   ❌ Health check failed"
    echo "   Response: $HEALTH"
    exit 1
fi
echo ""

# Test 2: Check if monitoring endpoints are registered
echo "2️⃣  Checking monitoring endpoints..."
MONITORS_RESPONSE=$(curl -s -w "\n%{http_code}" "$API_URL/monitors" -H "X-API-Key: $API_KEY" 2>&1)
HTTP_CODE=$(echo "$MONITORS_RESPONSE" | tail -1)
if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "401" ] || [ "$HTTP_CODE" = "403" ]; then
    echo "   ✅ Monitoring endpoints are registered (HTTP $HTTP_CODE)"
else
    if [ "$HTTP_CODE" = "404" ]; then
        echo "   ❌ Monitoring endpoints NOT found (404)"
        echo "   ⚠️  Make sure monitoring_router is enabled in main.py line 359"
    else
        echo "   ⚠️  Unexpected response (HTTP $HTTP_CODE)"
    fi
fi
echo ""

# Test 3: Check if dashboard endpoints are registered
echo "3️⃣  Checking dashboard endpoints..."
DASHBOARD_RESPONSE=$(curl -s -w "\n%{http_code}" "$API_URL/dashboard/overview" -H "X-API-Key: $API_KEY" 2>&1)
HTTP_CODE=$(echo "$DASHBOARD_RESPONSE" | tail -1)
if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "401" ] || [ "$HTTP_CODE" = "403" ]; then
    echo "   ✅ Dashboard endpoints are registered (HTTP $HTTP_CODE)"
    if [ "$HTTP_CODE" = "200" ]; then
        echo "   📊 Dashboard data retrieved successfully"
    fi
else
    if [ "$HTTP_CODE" = "404" ]; then
        echo "   ❌ Dashboard endpoints NOT found (404)"
        echo "   ⚠️  Make sure dashboard_agents_router is enabled in main.py line 373"
    else
        echo "   ⚠️  Unexpected response (HTTP $HTTP_CODE)"
    fi
fi
echo ""

# Test 4: Check Swagger docs
echo "4️⃣  Checking Swagger documentation..."
if curl -s "$API_URL/docs" | grep -q "dashboard\|monitor"; then
    echo "   ✅ Swagger docs accessible and show dashboard/monitor endpoints"
    echo "   📖 View at: $API_URL/docs"
else
    echo "   ⚠️  Swagger docs may not show dashboard endpoints"
fi
echo ""

echo "===================================="
echo "✅ Local testing complete!"
echo ""
echo "Next steps:"
echo "1. If endpoints returned 404, restart the backend server"
echo "2. If endpoints returned 401/403, check your API key"
echo "3. Open http://localhost:3000/dashboard in browser"
echo "4. Check browser console for any errors"

