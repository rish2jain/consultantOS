#!/bin/bash
# Generate TypeScript types from FastAPI OpenAPI schema
# Usage: ./scripts/generate-api-types.sh [API_URL]

set -e

API_URL="${1:-http://localhost:8080}"
OUTPUT_DIR="frontend/lib/api-generated"
SCHEMA_FILE="openapi.json"

echo "🔍 Fetching OpenAPI schema from ${API_URL}/openapi.json..."

# Check if API is running
if ! curl -s -f "${API_URL}/openapi.json" > /dev/null 2>&1; then
    echo "❌ Error: API is not running at ${API_URL}"
    echo "   Start the backend with: python main.py"
    exit 1
fi

# Fetch OpenAPI schema
curl -s "${API_URL}/openapi.json" -o "${SCHEMA_FILE}"

if [ ! -f "${SCHEMA_FILE}" ]; then
    echo "❌ Error: Failed to fetch OpenAPI schema"
    exit 1
fi

echo "✅ Fetched OpenAPI schema"

# Check if openapi-typescript-codegen is installed
if ! command -v npx &> /dev/null; then
    echo "❌ Error: npx is not installed. Please install Node.js"
    exit 1
fi

# Install openapi-typescript-codegen if not present
if ! npm list -g openapi-typescript-codegen &> /dev/null; then
    echo "📦 Installing openapi-typescript-codegen..."
    npm install -g openapi-typescript-codegen
fi

# Generate TypeScript types
echo "🔨 Generating TypeScript types..."
npx openapi-typescript-codegen \
    --input "${SCHEMA_FILE}" \
    --output "${OUTPUT_DIR}" \
    --client axios \
    --useOptions \
    --useUnionTypes

if [ $? -eq 0 ]; then
    echo "✅ TypeScript types generated in ${OUTPUT_DIR}"
    echo ""
    echo "📝 Next steps:"
    echo "   1. Review generated types in ${OUTPUT_DIR}"
    echo "   2. Update frontend/lib/api.ts to use generated types"
    echo "   3. Add validation with Zod (see docs/QUICK_START_ZOD_VALIDATION.md)"
else
    echo "❌ Error: Failed to generate types"
    exit 1
fi

# Clean up
rm -f "${SCHEMA_FILE}"

echo ""
echo "✨ Done! Types are ready to use."

