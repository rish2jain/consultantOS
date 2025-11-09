#!/bin/bash

# E2E Test Runner Script
# Checks if services are running and executes Puppeteer tests

set -e

FRONTEND_URL="${FRONTEND_URL:-http://localhost:3000}"
BACKEND_URL="${BACKEND_URL:-http://localhost:8080}"

echo "🚀 ConsultantOS E2E Test Suite"
echo "================================"
echo ""

# Check if backend is running
echo "Checking backend ($BACKEND_URL)..."
if curl -s -f "$BACKEND_URL/health" > /dev/null 2>&1; then
  echo "✅ Backend is running"
else
  echo "❌ Backend is not running at $BACKEND_URL"
  echo "   Please start it with: python main.py"
  exit 1
fi

# Check if frontend is running
echo "Checking frontend ($FRONTEND_URL)..."
if curl -s -f "$FRONTEND_URL" > /dev/null 2>&1; then
  echo "✅ Frontend is running"
else
  echo "❌ Frontend is not running at $FRONTEND_URL"
  echo "   Please start it with: cd frontend && npm run dev"
  exit 1
fi

echo ""
echo "Running tests..."
echo ""

# Run Jest tests
npm test -- --config jest.e2e.config.js --testPathPattern=tests/e2e

echo ""
echo "✅ Tests completed!"

