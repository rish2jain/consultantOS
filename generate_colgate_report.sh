#!/bin/bash

# Script to generate Colgate Palmolive report
# This will guide you through setting up API keys if needed

API_URL="http://localhost:8080"

echo "🚀 Colgate Palmolive Analysis Generator"
echo "========================================"
echo ""

# Check if API keys are set
if [ -z "$TAVILY_API_KEY" ] || [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️  API Keys Not Set"
    echo ""
    echo "To generate a real analysis, you need:"
    echo "1. GEMINI_API_KEY - Get from: https://makersuite.google.com/app/apikey"
    echo "2. TAVILY_API_KEY - Get from: https://tavily.com"
    echo ""
    read -p "Do you have API keys ready? (y/n): " has_keys
    
    if [ "$has_keys" = "y" ] || [ "$has_keys" = "Y" ]; then
        read -s -p "Enter your GEMINI_API_KEY: " gemini_key
        echo
        read -s -p "Enter your TAVILY_API_KEY: " tavily_key
        echo
        
        export GEMINI_API_KEY="$gemini_key"
        export TAVILY_API_KEY="$tavily_key"
        
        echo ""
        echo "✅ API keys set! Please restart the backend server:"
        echo "   1. Stop the current server (Ctrl+C)"
        echo "   2. Run: python main.py"
        echo "   3. Then run this script again"
        exit 0
    else
        echo ""
        echo "📝 To get API keys:"
        echo "   - Gemini: https://makersuite.google.com/app/apikey"
        echo "   - Tavily: https://tavily.com"
        echo ""
        echo "Then set them:"
        echo "   export GEMINI_API_KEY='your_key'"
        echo "   export TAVILY_API_KEY='your_key'"
        exit 1
    fi
fi

# Get API key for authentication
echo "🔐 Logging in..."
API_KEY=$(curl -s -X POST "$API_URL/users/login" \
    -H "Content-Type: application/json" \
    -d '{"email": "test@consultantos.com", "password": "TestPassword123!"}' \
    | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null)

if [ -z "$API_KEY" ]; then
    echo "❌ Failed to get API key. Please check your login credentials."
    exit 1
fi

echo "✅ Logged in successfully"
echo ""

# Generate analysis
echo "📊 Generating analysis for Colgate Palmolive..."
echo "⏳ This may take 30-60 seconds..."
echo ""

RESPONSE=$(curl -s -X POST "$API_URL/analyze" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $API_KEY" \
    -d '{
        "company": "Colgate Palmolive",
        "industry": "Consumer Goods",
        "frameworks": ["porter", "swot", "pestel"],
        "depth": "standard"
    }' \
    --max-time 180)

# Check if successful
if echo "$RESPONSE" | grep -q "report_id\|status.*success"; then
    echo "✅ Analysis generated successfully!"
    echo ""
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
    echo ""
    echo "🌐 View in dashboard: http://localhost:3000"
else
    echo "❌ Analysis failed:"
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
    echo ""
    echo "💡 Make sure:"
    echo "   1. API keys are set correctly"
    echo "   2. Backend server is running"
    echo "   3. You have internet connectivity"
fi

