#!/bin/bash
# Quick validation script - runs in seconds
# Use this before every commit/deployment

set -e

echo "🔍 Quick Validation Check..."
echo ""

# Check Python
python3 --version > /dev/null 2>&1 || { echo "❌ Python not found"; exit 1; }
echo "✅ Python OK"

# Check critical imports
python3 -c "import fastapi, uvicorn, pydantic" 2>/dev/null || { echo "❌ Missing critical imports"; exit 1; }
echo "✅ Critical imports OK"

# Check Dockerfile exists
[ -f "Dockerfile" ] || { echo "❌ Dockerfile not found"; exit 1; }
echo "✅ Dockerfile exists"

# Check requirements.txt exists
[ -f "requirements.txt" ] || { echo "❌ requirements.txt not found"; exit 1; }
echo "✅ requirements.txt exists"

# Check Dockerfile healthcheck doesn't use requests
if grep -q "requests.get" Dockerfile 2>/dev/null; then
    echo "⚠️  WARNING: Dockerfile healthcheck uses 'requests' (should use urllib)"
else
    echo "✅ Dockerfile healthcheck OK"
fi

# Check main.py can be imported
python3 -c "from consultantos.api.main import app" 2>/dev/null || { echo "❌ Cannot import main app"; exit 1; }
echo "✅ Main app imports OK"

echo ""
echo "✅ Quick validation passed!"
echo "Run './test_local_deployment.sh' for full testing"


