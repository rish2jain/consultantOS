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

# Exposed keys to remove
GEMINI_KEY="***REMOVED***"
TAVILY_KEY="***REMOVED***"

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

# Method 1: Using git filter-branch (built-in, slower but reliable)
echo "   Using git filter-branch..."

# Remove keys from all commits
# Note: Using perl for cross-platform compatibility in filter-branch
git filter-branch --force --index-filter \
    "git rm --cached --ignore-unmatch .env claudedocs/SECURITY_AUDIT_REPORT.md 2>/dev/null || true; \
     git ls-files | xargs perl -pi -e 's/$GEMINI_KEY/***REMOVED***/g' 2>/dev/null || true; \
     git ls-files | xargs perl -pi -e 's/$TAVILY_KEY/***REMOVED***/g' 2>/dev/null || true; \
     git add -A" \
    --prune-empty --tag-name-filter cat -- --all

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

