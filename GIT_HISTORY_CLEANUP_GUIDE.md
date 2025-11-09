# Git History Cleanup Guide - Removing Exposed API Keys

## ⚠️ CRITICAL WARNING

**This process rewrites git history and will affect all team members.**

**Before proceeding:**
1. ✅ **Revoke the exposed keys** (already done or in progress)
2. ✅ **Backup your repository** (create a full backup)
3. ✅ **Coordinate with your team** (everyone needs to re-clone after cleanup)
4. ✅ **Ensure you have admin access** to the repository

---

## Quick Start

### Option 1: Automated Script (Recommended)

```bash
# Run the automated cleanup script
./scripts/remove-keys-from-git-history.sh
```

This script will:
- Check for keys in current codebase
- Remove keys from all git history
- Clean up backup references
- Run garbage collection

### Option 2: BFG Repo-Cleaner (Faster, but requires installation)

```bash
# Install BFG (macOS)
brew install bfg

# Run BFG cleanup script
./scripts/remove-keys-bfg.sh
```

---

## Manual Process

If you prefer to do it manually or the scripts don't work:

### Step 1: Verify Keys Are Removed from Current Codebase

```bash
# Check if keys exist in current files
git grep "***REMOVED***" || echo "✅ Not found"
git grep "***REMOVED***" || echo "✅ Not found"
```

### Step 2: Remove from Git History

#### Method A: Using git filter-branch

```bash
# Remove keys from all commits
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env claudedocs/SECURITY_AUDIT_REPORT.md 2>/dev/null || true" \
  --prune-empty --tag-name-filter cat -- --all

# Clean up backup refs
git for-each-ref --format="%(refname)" refs/original/ | xargs -n 1 git update-ref -d

# Expire reflog and garbage collect
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

#### Method B: Using BFG Repo-Cleaner (Faster)

```bash
# 1. Create replacement file
cat > /tmp/replacements.txt << EOF
***REMOVED***===>***REMOVED***
***REMOVED***===>***REMOVED***
EOF

# 2. Clone a fresh mirror
git clone --mirror . /tmp/repo-cleanup.git
cd /tmp/repo-cleanup.git

# 3. Run BFG
bfg --replace-text /tmp/replacements.txt

# 4. Clean up
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 5. Update original repo
cd /path/to/original/repo
git remote set-url origin /tmp/repo-cleanup.git
git fetch
git reset --hard origin/main  # or origin/master
```

### Step 3: Verify Cleanup

```bash
# Check git history for keys
git log --all --full-history --source -- '*SECURITY_AUDIT_REPORT.md' | grep -i "AIzaSy\|tvly-dev" || echo "✅ Keys removed from history"

# Search entire history
git log --all -S "***REMOVED***" || echo "✅ Not found in history"
git log --all -S "***REMOVED***" || echo "✅ Not found in history"
```

### Step 4: Force Push (Coordinate with Team!)

```bash
# ⚠️ WARNING: This rewrites remote history
# Make sure all team members are aware and have backed up their work

git push origin --force --all
git push origin --force --tags
```

### Step 5: Notify Team Members

**Important:** All team members must:

1. **Backup their local changes** (if any)
2. **Delete their local repository**
3. **Re-clone the repository**:
   ```bash
   cd ..
   rm -rf ConsultantOS
   git clone <repository-url> ConsultantOS
   ```

**DO NOT** try to pull or merge - the history has changed!

---

## Alternative: GitHub Support

If the repository is already public and you want help:

1. **Contact GitHub Support**: https://support.github.com/contact
2. **Report exposed credentials**: They can help remove sensitive data
3. **Consider making repo private** temporarily:
   - Settings → General → Danger Zone → Change visibility

---

## Verification Checklist

After cleanup, verify:

- [ ] Keys not found in current codebase: `git grep "***REMOVED***"`
- [ ] Keys not found in git history: `git log --all -S "***REMOVED***"`
- [ ] `.env` is in `.gitignore`: `grep "^\.env$" .gitignore`
- [ ] Team members notified and re-cloned
- [ ] Remote repository updated
- [ ] New keys stored in Secret Manager
- [ ] Cloud Run deployment updated to use secrets

---

## Prevention for Future

### Pre-commit Hook

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Prevent committing API keys

if git diff --cached | grep -E "(AIzaSy|tvly-|sk-|pk_)"; then
    echo "❌ ERROR: Potential API key detected in commit!"
    echo "Please remove API keys before committing."
    exit 1
fi
```

Make executable:
```bash
chmod +x .git/hooks/pre-commit
```

### GitHub Secret Scanning

GitHub automatically scans for exposed secrets. Enable it:
- Settings → Security → Secret scanning → Enable

### GitGuardian (Optional)

Consider using GitGuardian for continuous secret scanning:
- https://www.gitguardian.com/

---

## Troubleshooting

### "fatal: refusing to merge unrelated histories"

If team members get this error after cleanup:
```bash
# They need to re-clone, not pull
cd ..
rm -rf ConsultantOS
git clone <repository-url> ConsultantOS
```

### "Updates were rejected because the remote contains work"

If you can't force push:
```bash
# Check if you have write access
git remote -v

# If you're a collaborator, you may need admin to force push
# Or use GitHub's web interface to delete and recreate the branch
```

### Keys still visible in GitHub

If keys are still visible on GitHub after cleanup:
1. The cleanup may not have worked - verify locally first
2. GitHub may cache - wait a few minutes and refresh
3. Contact GitHub support if persistent

---

## Summary

**What we're doing:**
- Removing exposed API keys from entire git history
- Ensuring they can't be recovered from git logs
- Preventing future exposure

**What this means:**
- Git history will be rewritten
- All team members must re-clone
- Commit SHAs will change
- Force push required

**Timeline:**
- Cleanup: 10-30 minutes
- Team coordination: 1-2 hours
- Verification: 30 minutes

---

**Last Updated**: After security notification
**Status**: Ready to execute after key revocation

