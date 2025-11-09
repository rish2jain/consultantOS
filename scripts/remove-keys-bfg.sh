#!/bin/bash
# Alternative script using BFG Repo-Cleaner (faster than filter-branch)
# Install BFG first: brew install bfg (macOS) or download from https://rtyley.github.io/bfg-repo-cleaner/

set -e

echo "🧹 Removing exposed API keys using BFG Repo-Cleaner"
echo ""

# Check if BFG is installed
if ! command -v bfg &> /dev/null; then
    echo "❌ BFG Repo-Cleaner not found!"
    echo ""
    echo "Install BFG:"
    echo "  macOS: brew install bfg"
    echo "  Linux: Download from https://rtyley.github.io/bfg-repo-cleaner/"
    echo ""
    exit 1
fi

# Exposed keys
GEMINI_KEY="***REMOVED***"
TAVILY_KEY="***REMOVED***"

# Create replacement file
REPLACEMENT_FILE=$(mktemp)
cat > "$REPLACEMENT_FILE" << EOF
$GEMINI_KEY===>***REMOVED***
$TAVILY_KEY===>***REMOVED***
EOF

echo "⚠️  WARNING: This will rewrite git history!"
echo "   Make sure you have:"
echo "   1. Backed up your repository"
echo "   2. Coordinated with your team"
echo "   3. Revoked the exposed keys"
echo ""
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Aborted."
    rm "$REPLACEMENT_FILE"
    exit 1
fi

echo ""
echo "🔍 Running BFG to remove keys..."

# Clone a fresh copy (BFG requires this)
REPO_DIR=$(pwd)
TEMP_DIR=$(mktemp -d)
echo "   Creating temporary clone..."
git clone --mirror "$REPO_DIR" "$TEMP_DIR/repo.git"

# Run BFG
echo "   Removing keys from history..."
cd "$TEMP_DIR/repo.git"
bfg --replace-text "$REPLACEMENT_FILE"

# Clean up
echo "   Cleaning up..."
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Copy back
echo "   Updating original repository..."
cd "$REPO_DIR"
git remote set-url origin "$TEMP_DIR/repo.git"
git fetch
git reset --hard origin/main 2>/dev/null || git reset --hard origin/master 2>/dev/null || true

# Cleanup temp files
rm -rf "$TEMP_DIR"
rm "$REPLACEMENT_FILE"

echo ""
echo "✅ Git history cleanup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Verify keys are removed:"
echo "      git log --all --full-history -S '$GEMINI_KEY'"
echo ""
echo "   2. Force push to remote (CAUTION - coordinate with team first!):"
echo "      git push origin --force --all"
echo "      git push origin --force --tags"
echo ""

