# Deployment Timeout Fix

## Problem Summary

**Error Message:**
```
ERROR: (gcloud.run.deploy) The user-provided container failed to start and listen on the port defined provided by the PORT=8080 environment variable within the allocated timeout.
```

**Root Cause:**
- Application takes ~28 seconds to initialize (heavy dependencies: LLM models, ML libraries, database clients)
- Cloud Run default startup timeout is 60 seconds, but health checks may fail during initialization
- Deployment configurations don't specify `--startup-timeout` parameter

**Evidence from Logs:**
- Container starts successfully but takes 28 seconds (from 23:21:16 to 23:21:44)
- Application eventually becomes ready and serves requests
- Deployment fails during the initial health check phase

## Solution

### Fix 1: Add Startup Timeout to Deployment

Add `--startup-timeout` parameter to give the application more time to initialize:

```bash
gcloud run deploy consultantos-api \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2 \
  --timeout 300 \
  --startup-timeout 120 \  # NEW: Allow 2 minutes for startup
  --min-instances 0 \
  --max-instances 10 \
  --set-env-vars "${ENV_VARS}"
```

### Fix 2: Update DEPLOY_NOW.sh Script

The deployment script needs to include the startup timeout:

```bash
# Deploy to Cloud Run
gcloud run deploy consultantos-api \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2 \
  --timeout 300 \
  --startup-timeout 120 \  # Add this line
  --min-instances 0 \
  --max-instances 10 \
  --set-env-vars "${ENV_VARS}"
```

### Fix 3: Update Cloud Build Configurations

For Cloud Build deployments, add startup timeout:

```yaml
# In cloudbuild.yaml or cloudbuild.api.yaml
- name: "gcr.io/google.com/cloudsdktool/cloud-sdk"
  entrypoint: gcloud
  args:
    - "run"
    - "deploy"
    - "consultantos-api"
    # ... other args ...
    - "--timeout"
    - "300"
    - "--startup-timeout"  # Add this
    - "120"                # 2 minutes
```

### Fix 4: Ensure PORT Environment Variable Support

Cloud Run sets PORT dynamically. Update Dockerfile to respect it:

```dockerfile
# Use PORT env var if set, otherwise default to 8080
CMD ["sh", "-c", "uvicorn consultantos.api.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
```

Or update main.py to read PORT:

```python
import os
port = int(os.getenv("PORT", 8080))
uvicorn.run("consultantos.api.main:app", host="0.0.0.0", port=port)
```

## Quick Fix Command

Run this to update the existing service:

```bash
gcloud run services update consultantos-api \
  --region us-central1 \
  --startup-timeout 120
```

## Verification

After deployment, check logs to verify startup time:

```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=consultantos-api" \
  --limit 20 \
  --format="table(timestamp,severity,textPayload)"
```

Look for:
- "Application startup complete" - should appear within 30-60 seconds
- "Uvicorn running on http://0.0.0.0:8080" - confirms server started
- No timeout errors

## Expected Startup Timeline

1. **0-5s**: Container starts, Python interpreter loads
2. **5-15s**: Heavy imports (transformers, torch, spacy models)
3. **15-25s**: Database clients initialize (Firestore)
4. **25-30s**: LLM clients initialize (Gemini, Instructor)
5. **30-35s**: Application startup event completes
6. **35-40s**: Health check succeeds, service ready

**Total**: ~35-40 seconds (well within 120s timeout)

## Additional Optimizations (Optional)

If startup is still too slow, consider:

1. **Lazy Loading**: Initialize LLM clients on first request instead of startup
2. **Minimal Startup**: Only load essential components at startup
3. **Warm Instances**: Set `--min-instances 1` to keep one instance warm (costs more)

## References

- [Cloud Run Startup Timeout Documentation](https://cloud.google.com/run/docs/configuring/startup-timeout)
- [Cloud Run Troubleshooting](https://cloud.google.com/run/docs/troubleshooting#container-failed-to-start)
- Local Testing Summary: `LOCAL_TEST_SUMMARY.md`
- Deployment Recommendation: `DEPLOYMENT_RECOMMENDATION.md`

