#!/bin/bash
# Script to remove exposed API keys from git history
# WARNING: This rewrites git history. Coordinate with your team before running.

set -e

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

# Strategy: Remove files that contained keys and use pattern matching
# Since we don't have the exact keys, we'll:
# 1. Remove the files that contained them from history
# 2. Use pattern matching to find and remove API key patterns

echo ""
echo "📋 Strategy: Since exact keys are not available, we will:"
echo "   1. Remove files that contained keys (.env, SECURITY_AUDIT_REPORT.md)"
echo "   2. Search for and remove common API key patterns"
echo ""
read -p "Continue with file removal and pattern matching? (yes/no): " strategy_confirm

if [ "$strategy_confirm" != "yes" ]; then
    echo "Aborted."
    exit 1
fi

echo ""
echo "🧹 Removing sensitive files and patterns from git history..."

# Check if git filter-repo is available (recommended tool)
if command -v git-filter-repo &> /dev/null; then
    echo "   Using git filter-repo (recommended)..."
    
    # Step 1: Remove files that contained keys
    echo "   Step 1: Removing files that contained keys..."
    git filter-repo --path .env --invert-paths --force
    git filter-repo --path claudedocs/SECURITY_AUDIT_REPORT.md --invert-paths --force
    
    # Step 2: Remove API key patterns using replacement patterns
    echo "   Step 2: Removing API key patterns..."
    REPLACEMENT_FILE=$(mktemp)
    cat > "$REPLACEMENT_FILE" << 'EOF'
***REMOVED***
***REMOVED***==>***REMOVED***
***REMOVED***
***REMOVED***==>***REMOVED***
EOF
    
    # Use filter-repo to replace patterns
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
    
    # Remove sensitive files from all commits using filter-branch
    # Note: For blob-level key replacements, use the separate BFG script (scripts/remove-keys-bfg.sh)
    # with --replace-text instead of attempting inline perl in filter-branch
    git filter-branch --force --index-filter \
        "git rm --cached --ignore-unmatch .env && \
         git rm --cached --ignore-unmatch claudedocs/SECURITY_AUDIT_REPORT.md" \
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

