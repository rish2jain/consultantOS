# Security Remediation Guide - Exposed API Keys

## 🚨 IMMEDIATE ACTION REQUIRED

Google has detected that your API key was publicly exposed in your GitHub repository.

**Example placeholder**: `AIzaSyXXXXXXXXXXXXXXX` (this is a placeholder, not a real key)

**Status**: ✅ Keys have been removed from the current codebase
**Remaining Risk**: ⚠️ Keys still exist in git history and must be revoked

---

## Step 1: Revoke Exposed API Keys (IMMEDIATE - Do This First)

### Revoke Gemini API Key

1. **Go to Google Cloud Console**:

   - Visit: https://console.cloud.google.com/apis/credentials
   - Select project: `gen-lang-client-0079292313` (ConsultantOS)

2. **Find and Revoke the Key**:

   - Search for your exposed API key (check your email notification or security alerts)
   - Click on the key to edit it
   - Click **"Regenerate key"** or **"Delete"** button
   - Confirm the action

3. **Alternative: Restrict the Key** (if you can't delete immediately):
   - Edit the key
   - Add **Application restrictions** (HTTP referrers, IP addresses, or Android/iOS apps)
   - Add **API restrictions** (limit to only Gemini API)
   - Save changes

### Revoke Tavily API Key

1. **Go to Tavily Dashboard**:

   - Visit: https://app.tavily.com/settings/api
   - Log in to your account

2. **Revoke the Key**:
   - Find your exposed API key (check your email notification or security alerts)
   - Click "Revoke" or "Delete"
   - Generate a new key if needed

---

## Step 2: Generate New API Keys

### Generate New Gemini API Key

1. **Google AI Studio**:

   - Visit: https://makersuite.google.com/app/apikey
   - Click "Create API Key"
   - Select your project: `gen-lang-client-0079292313`
   - Copy the new key immediately (you won't see it again)

2. **Add Restrictions** (IMPORTANT):
   - Go to Google Cloud Console → APIs & Services → Credentials
   - Click on your new API key
   - Under "Application restrictions":
     - Select "IP addresses" and add your Cloud Run service IPs
     - OR select "HTTP referrers" and add your domain
   - Under "API restrictions":
     - Select "Restrict key"
     - Choose only "Generative Language API" (Gemini)
   - Click "Save"

### Generate New Tavily API Key

1. **Tavily Dashboard**:
   - Visit: https://app.tavily.com/settings/api
   - Click "Generate New Key"
   - Copy the new key

---

## Step 3: Store Keys Securely

### Option A: Google Secret Manager (Recommended for Production)

```bash
# Set your project
export PROJECT_ID="gen-lang-client-0079292313"
gcloud config set project $PROJECT_ID

# Create secrets
echo -n "YOUR_NEW_GEMINI_KEY" | gcloud secrets create gemini-api-key \
  --data-file=- \
  --replication-policy="automatic"

echo -n "YOUR_NEW_TAVILY_KEY" | gcloud secrets create tavily-api-key \
  --data-file=- \
  --replication-policy="automatic"

# Grant Cloud Run access
gcloud secrets add-iam-policy-binding gemini-api-key \
  --member="serviceAccount:YOUR_SERVICE_ACCOUNT@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding tavily-api-key \
  --member="serviceAccount:YOUR_SERVICE_ACCOUNT@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### Option B: Environment Variables (Development Only)

Create a `.env` file (already in `.gitignore`):

```bash
# .env (DO NOT COMMIT THIS FILE)
GEMINI_API_KEY=your_new_gemini_key_here
TAVILY_API_KEY=your_new_tavily_key_here
```

**Verify `.gitignore` includes `.env`**:

```bash
grep -q "^\.env$" .gitignore && echo "✅ .env is in .gitignore" || echo "❌ Add .env to .gitignore"
```

---

## Step 4: Remove Keys from Git History

⚠️ **WARNING**: This rewrites git history. Coordinate with your team before proceeding.

### Option A: Using git filter-branch (Built-in)

```bash
# Remove .env file from all commits
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env claudedocs/SECURITY_AUDIT_REPORT.md" \
  --prune-empty --tag-name-filter cat -- --all

# Force push (CAUTION: This rewrites history)
git push origin --force --all
git push origin --force --tags
```

### Option B: Using BFG Repo-Cleaner (Recommended - Faster)

```bash
# Install BFG
brew install bfg  # macOS
# or download from: https://rtyley.github.io/bfg-repo-cleaner/

# Create a file with keys to remove
echo "***REMOVED***" > keys-to-remove.txt
echo "***REMOVED***" >> keys-to-remove.txt

# Remove keys from history
bfg --replace-text keys-to-remove.txt

# Clean up
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Force push
git push origin --force --all
```

### Option C: GitHub Support (If Already Pushed)

If the keys are already in a public repository:

1. **Contact GitHub Support**:

   - Report the exposed credentials: https://support.github.com/contact
   - They can help remove sensitive data from history

2. **Consider Making Repository Private**:
   - Settings → General → Danger Zone → Change visibility

---

## Step 5: Update Application Configuration

### Update Cloud Run Deployment

If using Cloud Run, update your deployment to use Secret Manager:

```bash
gcloud run deploy consultantos \
  --image gcr.io/$PROJECT_ID/consultantos:latest \
  --region us-central1 \
  --set-secrets="GEMINI_API_KEY=gemini-api-key:1,TAVILY_API_KEY=tavily-api-key:1" \
  --update-env-vars="GEMINI_API_KEY=,TAVILY_API_KEY="
```

**Note**: Replace `:1` with the actual secret version number from Secret Manager. To check versions:

```bash
gcloud secrets versions list gemini-api-key
gcloud secrets versions list tavily-api-key
```

### Update Local Development

Update your local `.env` file with new keys (never commit this file).

---

## Step 6: Verify Remediation

### Check Git History

```bash
# Verify keys are removed from current codebase
git grep -i "***REMOVED***" || echo "✅ Key not found in current code"
git grep -i "***REMOVED***" || echo "✅ Key not found in current code"
```

### Test Application

```bash
# Test with new keys
export GEMINI_API_KEY="your_new_key"
export TAVILY_API_KEY="your_new_key"
python -m pytest tests/ -v
```

### Monitor API Usage

1. **Google Cloud Console**:

   - APIs & Services → Dashboard
   - Monitor for unexpected usage from old keys

2. **Tavily Dashboard**:
   - Check API usage logs
   - Look for unauthorized access

---

## Step 7: Add API Key Restrictions

### Gemini API Key Restrictions

1. **Application Restrictions**:

   - **IP addresses**: Add your Cloud Run service IPs
   - **HTTP referrers**: Add your domain (e.g., `https://consultantos.app/*`)
   - **Android apps**: If using mobile app
   - **iOS apps**: If using iOS app

2. **API Restrictions**:
   - Select "Restrict key"
   - Choose only: "Generative Language API"

### Best Practices Going Forward

1. ✅ **Never commit API keys to git**
2. ✅ **Use Secret Manager for production**
3. ✅ **Add API key restrictions immediately**
4. ✅ **Rotate keys regularly (every 90 days)**
5. ✅ **Monitor API usage for anomalies**
6. ✅ **Use separate keys for dev/staging/prod**

---

## Prevention Checklist

- [x] `.env` is in `.gitignore`
- [ ] Pre-commit hook to scan for API keys
- [ ] GitHub secret scanning enabled
- [ ] Code review process checks for secrets
- [ ] Automated security scanning in CI/CD
- [ ] Documentation updated with security guidelines

### Add Pre-commit Hook

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

Make it executable:

```bash
chmod +x .git/hooks/pre-commit
```

---

## Additional Resources

- [Google Cloud: Handling Compromised Credentials](https://cloud.google.com/iam/docs/managing-service-account-keys#compromised-keys)
- [GitHub: Removing Sensitive Data](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
- [OWASP: Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)

---

## Timeline

- **Immediate (0-1 hour)**: Revoke exposed keys
- **Urgent (1-4 hours)**: Generate new keys, update configuration
- **Important (1-2 days)**: Remove from git history, add restrictions
- **Ongoing**: Monitor usage, implement prevention measures

---

**Last Updated**: After Google security notification
**Status**: Keys removed from codebase, revocation required
