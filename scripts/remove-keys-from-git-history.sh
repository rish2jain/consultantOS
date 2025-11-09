#!/bin/bash
# Script to remove exposed API keys from git history
# WARNING: This rewrites git history. Coordinate with your team before running.

set -e

# Note: Using perl -pi for cross-platform in-place editing (works on both macOS and Linux)

echo "⚠️  WARNING: This script will rewrite git history!"
echo "   Make sure you have:"
echo "   1. Backed up your repository"
echo "   2. Coordinated with your team"
echo "   3. Revoked the exposed keys"
echo ""
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Aborted."
    exit 1
fi

# Exposed keys to remove - set via environment variables for security
# The actual keys should be passed as environment variables to avoid storing them in the script
GEMINI_KEY="${GEMINI_KEY_TO_REMOVE:-}"
TAVILY_KEY="${TAVILY_KEY_TO_REMOVE:-}"

# If not set, prompt for them (non-echoed)
if [ -z "$GEMINI_KEY" ]; then
    echo "Enter the Gemini API key to remove from history (input will be hidden):"
    read -s GEMINI_KEY
    echo ""
fi

if [ -z "$TAVILY_KEY" ]; then
    echo "Enter the Tavily API key to remove from history (input will be hidden):"
    read -s TAVILY_KEY
    echo ""
fi

if [ -z "$GEMINI_KEY" ] || [ -z "$TAVILY_KEY" ]; then
    echo "❌ ERROR: Both keys are required"
    exit 1
fi

echo ""
echo "🔍 Checking if keys exist in current codebase..."
if git grep -q "$GEMINI_KEY" 2>/dev/null || git grep -q "$TAVILY_KEY" 2>/dev/null; then
    echo "   ⚠️  Keys found in current codebase. Removing from tracked files first..."
    # This shouldn't happen if we already removed them, but just in case
    # Use perl for cross-platform compatibility instead of sed
    git grep -l "$GEMINI_KEY" | xargs -I {} perl -pi -e "s/$GEMINI_KEY/***REMOVED***/g" {} 2>/dev/null || true
    git grep -l "$TAVILY_KEY" | xargs -I {} perl -pi -e "s/$TAVILY_KEY/***REMOVED***/g" {} 2>/dev/null || true
fi

echo ""
echo "🧹 Removing keys from git history..."

# Check if git filter-repo is available (recommended tool)
if command -v git-filter-repo &> /dev/null; then
    echo "   Using git filter-repo (recommended)..."
    
    # Create replacement file
    REPLACEMENT_FILE=$(mktemp)
    cat > "$REPLACEMENT_FILE" << EOF
$GEMINI_KEY===>***REMOVED***
$TAVILY_KEY===>***REMOVED***
EOF
    
    # Use filter-repo to replace keys
    git filter-repo --replace-text "$REPLACEMENT_FILE" --force
    
    # Clean up
    rm "$REPLACEMENT_FILE"
else
    echo "   Using git filter-branch (git filter-repo not found)..."
    echo "   ⚠️  Consider installing git-filter-repo for better performance:"
    echo "      brew install git-filter-repo  # macOS"
    echo "      pip install git-filter-repo   # Linux/Windows"
    echo ""
    
    # Set environment variable to suppress warning
    export FILTER_BRANCH_SQUELCH_WARNING=1
    
    # Remove keys from all commits using filter-branch
    # Escape special characters in keys for sed/perl
    GEMINI_ESCAPED=$(printf '%s\n' "$GEMINI_KEY" | sed 's/[[\.*^$()+?{|]/\\&/g')
    TAVILY_ESCAPED=$(printf '%s\n' "$TAVILY_KEY" | sed 's/[[\.*^$()+?{|]/\\&/g')
    
    git filter-branch --force --index-filter \
        "git rm --cached --ignore-unmatch .env claudedocs/SECURITY_AUDIT_REPORT.md 2>/dev/null || true; \
         git ls-files | xargs perl -pi -e 's/$GEMINI_ESCAPED/***REMOVED***/g' 2>/dev/null || true; \
         git ls-files | xargs perl -pi -e 's/$TAVILY_ESCAPED/***REMOVED***/g' 2>/dev/null || true; \
         git add -A" \
        --prune-empty --tag-name-filter cat -- --all
fi

# Clean up backup refs
echo "   Cleaning up backup references..."
git for-each-ref --format="%(refname)" refs/original/ | xargs -n 1 git update-ref -d 2>/dev/null || true

# Expire reflog and garbage collect
echo "   Running garbage collection..."
git reflog expire --expire=now --all
git gc --prune=now --aggressive

echo ""
echo "✅ Git history cleanup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Verify keys are removed:"
echo "      git log --all --full-history --source -- '*SECURITY_AUDIT_REPORT.md' | grep -i 'AIzaSy\|tvly-dev'"
echo ""
echo "   2. Force push to remote (CAUTION - coordinate with team first!):"
echo "      git push origin --force --all"
echo "      git push origin --force --tags"
echo ""
echo "   3. Notify team members to re-clone the repository"
echo ""

