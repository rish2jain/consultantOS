#!/bin/bash
# Quick script to analyze UX screenshots from E2E tests

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCREENSHOTS_DIR="${SCRIPT_DIR}/e2e/screenshots"
OUTPUT_FILE="${SCRIPT_DIR}/e2e/ux-analysis-$(date +%Y%m%d-%H%M%S).json"

echo "🔍 UX Image Analyzer"
echo "==================="
echo ""

# Check if screenshots directory exists
if [ ! -d "$SCREENSHOTS_DIR" ]; then
    echo "❌ Screenshots directory not found: $SCREENSHOTS_DIR"
    echo "   Run E2E tests first to generate screenshots"
    exit 1
fi

# Check if analyzer script exists
if [ ! -f "${SCRIPT_DIR}/ux_image_analyzer.py" ]; then
    echo "❌ Analyzer script not found: ${SCRIPT_DIR}/ux_image_analyzer.py"
    exit 1
fi

# Count images
IMAGE_COUNT=$(find "$SCREENSHOTS_DIR" -type f \( -name "*.png" -o -name "*.jpg" -o -name "*.jpeg" \) | wc -l | tr -d ' ')

if [ "$IMAGE_COUNT" -eq 0 ]; then
    echo "⚠️  No images found in $SCREENSHOTS_DIR"
    exit 1
fi

echo "📸 Found $IMAGE_COUNT images to analyze"
echo "📁 Directory: $SCREENSHOTS_DIR"
echo "💾 Output: $OUTPUT_FILE"
echo ""

# Run analyzer
python3 "${SCRIPT_DIR}/ux_image_analyzer.py" \
    "$SCREENSHOTS_DIR" \
    --output "$OUTPUT_FILE" \
    --summary

echo ""
echo "✅ Analysis complete!"
echo "📄 Results saved to: $OUTPUT_FILE"

