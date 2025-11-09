# ConsultantOS Deployment Fix - Implementation Guide

**Status**: Ready to implement
**Estimated Time**: 30 minutes
**Risk Level**: Low (changes are additive, no breaking changes)

---

## Quick Start (5 minutes)

If you just want to fix the deployment quickly:

```bash
cd /Users/rish2jain/Documents/Hackathons/ConsultantOS

# 1. Replace all Dockerfiles
cp Dockerfile Dockerfile.backup
cp Dockerfile.fixed Dockerfile

cp services/api_service/Dockerfile services/api_service/Dockerfile.backup
cp services/api_service/Dockerfile.fixed services/api_service/Dockerfile

cp services/agent_service/Dockerfile services/agent_service/Dockerfile.backup
cp services/agent_service/Dockerfile.fixed services/agent_service/Dockerfile

cp services/reporting_service/Dockerfile services/reporting_service/Dockerfile.backup
cp services/reporting_service/Dockerfile.fixed services/reporting_service/Dockerfile

cp services/task_handler_service/Dockerfile services/task_handler_service/Dockerfile.backup
cp services/task_handler_service/Dockerfile.fixed services/task_handler_service/Dockerfile

# 2. Replace Cloud Build configurations
cp cloudbuild.api.yaml cloudbuild.api.yaml.backup
cp cloudbuild.api.yaml.fixed cloudbuild.api.yaml

cp cloudbuild.agent.yaml cloudbuild.agent.yaml.backup
cp cloudbuild.agent.yaml.fixed cloudbuild.agent.yaml

cp cloudbuild.reporting.yaml cloudbuild.reporting.yaml.backup
cp cloudbuild.reporting.yaml.fixed cloudbuild.reporting.yaml

cp cloudbuild.task.yaml cloudbuild.task.yaml.backup
cp cloudbuild.task.yaml.fixed cloudbuild.task.yaml

# 3. Test Docker build locally
docker build -t consultantos:test .
docker run --rm consultantos:test python -c "import kaleido; import reportlab; print('✓ All critical packages available')"

# 4. Push to Cloud Build
git add Dockerfile services/*/Dockerfile cloudbuild*.yaml
git commit -m "fix: Add missing system dependencies to Dockerfiles and update Cloud Build configs with secrets"
git push origin master
```

---

## Detailed Implementation (Step-by-Step)

### Step 1: Update Root Dockerfile

**File**: `/Dockerfile`

**Changes**:
1. Add system dependencies: `build-essential`, `python3-dev`, `libffi-dev`, `libssl-dev`
2. Upgrade pip/setuptools/wheel before installing requirements
3. Add HEALTHCHECK for Cloud Run
4. Simplify and document the build process

**Current vs Fixed**:

```dockerfile
# CURRENT (❌ BROKEN)
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y gcc g++ && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["uvicorn", "consultantos.api.main:app", "--host", "0.0.0.0", "--port", "8080"]

# FIXED (✅ WORKING)
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential python3-dev gcc g++ libffi-dev libssl-dev curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONPATH="/app"
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1
EXPOSE 8080
CMD ["uvicorn", "consultantos.api.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

**Implementation**:
```bash
# Option A: Manual edit
vi /Dockerfile
# Replace entire file with content from Dockerfile.fixed

# Option B: Use provided file
cp Dockerfile Dockerfile.backup
cp Dockerfile.fixed Dockerfile
```

---

### Step 2: Update Service Dockerfiles (4 files)

All 4 service Dockerfiles need the same system dependencies:

**Files to update**:
- `services/api_service/Dockerfile`
- `services/agent_service/Dockerfile`
- `services/reporting_service/Dockerfile`
- `services/task_handler_service/Dockerfile`

**Script to update all at once**:
```bash
# Backup originals
for service in api_service agent_service reporting_service task_handler_service; do
  cp "services/$service/Dockerfile" "services/$service/Dockerfile.backup"
done

# Replace with fixed versions
cp services/api_service/Dockerfile.fixed services/api_service/Dockerfile
cp services/agent_service/Dockerfile.fixed services/agent_service/Dockerfile
cp services/reporting_service/Dockerfile.fixed services/reporting_service/Dockerfile
cp services/task_handler_service/Dockerfile.fixed services/task_handler_service/Dockerfile
```

**Key differences in service Dockerfiles**:
- Copy libs and service-specific requirements
- Set PYTHONPATH="/app"
- Still add full system dependencies
- Add HEALTHCHECK

---

### Step 3: Update Cloud Build YAML Configurations

**Files to update**:
- `cloudbuild.api.yaml`
- `cloudbuild.agent.yaml`
- `cloudbuild.reporting.yaml`
- `cloudbuild.task.yaml`

**Key changes**:

1. **Add secrets configuration** to pass API keys to Cloud Run services:
   ```yaml
   - "--set-secrets"
   - "GEMINI_API_KEY=GEMINI_API_KEY:latest,TAVILY_API_KEY=TAVILY_API_KEY:latest"
   ```

2. **Add logging configuration** for better debugging:
   ```yaml
   options:
     logging: CLOUD_LOGGING_ONLY
   ```

**Implementation**:
```bash
# Backup originals
for config in api agent reporting task; do
  cp "cloudbuild.$config.yaml" "cloudbuild.$config.yaml.backup"
done

# Apply fixes (api service shown, repeat for others)
cp cloudbuild.api.yaml.fixed cloudbuild.api.yaml
cp cloudbuild.agent.yaml.fixed cloudbuild.agent.yaml
cp cloudbuild.reporting.yaml.fixed cloudbuild.reporting.yaml
cp cloudbuild.task.yaml.fixed cloudbuild.task.yaml
```

---

### Step 4: Update requirements.txt (Optional but Recommended)

Add explicit google-api-core pinning to avoid conflicts:

**File**: `requirements.txt`

**Change to add** (after FastAPI/Pydantic section):
```txt
# Explicitly pin google-api-core to avoid conflicts across multiple google-cloud libraries
google-api-core>=1.33.0,<2.0.0

# Then keep existing google-cloud packages...
google-cloud-storage>=2.10.0
google-cloud-secret-manager>=2.16.0
# etc...
```

**To apply**:
```bash
# Edit requirements.txt manually or use sed
sed -i.bak '/^# Google Cloud/i\# Explicitly pin google-api-core to avoid conflicts across multiple google-cloud libraries\ngoogle-api-core>=1.33.0,<2.0.0\n' requirements.txt
```

---

### Step 5: Create Health Check Endpoint (Required)

The HEALTHCHECK in Dockerfile needs a `/health` endpoint in your FastAPI app.

**File**: `consultantos/api/main.py`

**Add this endpoint** (at the top level of FastAPI app):
```python
@app.get("/health")
async def health():
    """Health check endpoint for Cloud Run"""
    return {
        "status": "healthy",
        "service": "consultantos-api",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }
```

**Implementation**:
```bash
# Check if health endpoint already exists
grep -n "def health" consultantos/api/main.py

# If not found, add it using Edit tool
# Add after the FastAPI app initialization
```

---

### Step 6: Verify Secrets Exist in Secret Manager

Before deploying, ensure your secrets exist in GCP Secret Manager.

**Commands**:
```bash
# Set your GCP project
export PROJECT_ID="your-gcp-project-id"

# List existing secrets
gcloud secrets list --project=$PROJECT_ID

# Create missing secrets if needed
echo -n "your-gemini-api-key-here" | gcloud secrets create GEMINI_API_KEY \
  --replication-policy="automatic" \
  --data-file=- \
  --project=$PROJECT_ID

echo -n "your-tavily-api-key-here" | gcloud secrets create TAVILY_API_KEY \
  --replication-policy="automatic" \
  --data-file=- \
  --project=$PROJECT_ID

# Verify secrets were created
gcloud secrets list --project=$PROJECT_ID
gcloud secrets versions list GEMINI_API_KEY --project=$PROJECT_ID
gcloud secrets versions list TAVILY_API_KEY --project=$PROJECT_ID
```

**Important**: The service accounts need permission to access secrets:
```bash
# Grant Cloud Run service accounts permission to access secrets
for SERVICE_ACCOUNT in consultantos-api-sa consultantos-agent-sa consultantos-reporting-sa consultantos-task-sa; do
  gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
done
```

---

### Step 7: Test Locally (Before Cloud Push)

**Test 1: Build Docker image**
```bash
# Test root Dockerfile
docker build -t consultantos:test -f Dockerfile .

# This should complete without errors like:
# - "could not create '/usr/local/lib/python3.11/dist-packages/kaleido.so'"
# - "ffi.h: No such file or directory"
# - "error: could not create '/usr/local/lib/..."
```

**Test 2: Verify dependencies**
```bash
# Check critical packages are installed
docker run --rm consultantos:test python -c "
import sys
print('✓ Python:', sys.version.split()[0])

import fastapi
print('✓ FastAPI:', fastapi.__version__)

import pydantic
print('✓ Pydantic:', pydantic.__version__)

import kaleido
print('✓ Kaleido available')

import reportlab
print('✓ ReportLab available')

import google.cloud.storage
print('✓ Google Cloud Storage available')

print('\\n✓ All critical packages installed successfully!')
"
```

**Test 3: Run container**
```bash
# Start container
docker run -d --name test-api -p 8080:8080 consultantos:test
sleep 5

# Test health endpoint
curl http://localhost:8080/health
# Should return: {"status":"healthy","service":"consultantos-api",...}

# Check logs
docker logs test-api

# Cleanup
docker stop test-api
docker rm test-api
```

---

### Step 8: Commit and Push to Git

```bash
# Check what changed
git status

# Add all changes
git add Dockerfile services/*/Dockerfile cloudbuild*.yaml requirements.txt

# Create descriptive commit
git commit -m "fix(deployment): Add missing system dependencies and secret configuration

- Add build-essential, libffi-dev, libssl-dev to Dockerfile
- Upgrade pip/setuptools before installing requirements
- Add health check endpoint and HEALTHCHECK directive
- Configure secrets in Cloud Build YAML files
- Pin google-api-core to avoid version conflicts

Fixes deployment failures due to missing system libraries for:
- kaleido (plotly export)
- reportlab (PDF generation)
- cryptography (JWT/SSL)

This ensures Cloud Run build doesn't fail with compilation errors."

# Push to remote
git push origin master
```

---

### Step 9: Trigger Cloud Build

**Option A: Manual trigger via CLI**
```bash
gcloud builds submit \
  --config=cloudbuild.api.yaml \
  --substitutions _PROJECT_ID=$PROJECT_ID \
  .
```

**Option B: Push-triggered build (if configured)**
The build will trigger automatically when you push to master.

**Option C: Manual trigger via Cloud Console**
1. Go to Cloud Build in GCP Console
2. Click "Create Build"
3. Select your repository
4. Choose branch
5. Select `cloudbuild.api.yaml` as build config
6. Click Create

---

### Step 10: Monitor Build Progress

```bash
# Watch the build in real-time
gcloud builds log <BUILD_ID> --stream

# Or get the last build ID and watch
BUILD_ID=$(gcloud builds list --limit=1 --format='value(id)')
gcloud builds log $BUILD_ID --stream

# Look for these success indicators:
# - "Successfully built <IMAGE_ID>"
# - "Successfully pushed gcr.io/..."
# - "Creating Cloud Run service..."
# - "Cloud Run deployment succeeded"

# Look for these failure indicators (to fix):
# - "could not create '/usr/local/lib/python3.11/..."
# - "ffi.h: No such file"
# - "gcc: command not found"
# - "error: command 'x86_64-linux-gnu-gcc' failed"
```

---

### Step 11: Verify Deployment

**Test the deployed service**:
```bash
# Get the service URL
SERVICE_URL=$(gcloud run services describe consultantos-api \
  --region=us-central1 \
  --format='value(status.url)')

echo "Service URL: $SERVICE_URL"

# Test health endpoint
curl "$SERVICE_URL/health"

# Should return: {"status":"healthy",...}

# Test API is running
curl "$SERVICE_URL/docs" | head -20
# Should return Swagger UI HTML
```

**Check Cloud Run logs**:
```bash
# Get logs for the service
gcloud run logs read consultantos-api \
  --region=us-central1 \
  --limit=50

# Look for startup errors or import failures
```

**Check metrics in Cloud Console**:
1. Go to Cloud Run > consultantos-api
2. Check "Metrics" tab for:
   - Request count
   - Error rate (should be 0%)
   - Latency
   - Memory usage
3. Check "Logs" tab for any errors

---

## Troubleshooting During Deployment

### Build Failure: "ffi.h: No such file"

**Cause**: Missing libffi-dev in Docker

**Fix**:
- Verify Dockerfile has `libffi-dev` in apt-get install
- Check you're using `.fixed` Dockerfile
- Rebuild with fresh cache: `docker build --no-cache -t test .`

### Build Failure: "gcc: command not found"

**Cause**: Missing build-essential or C compiler

**Fix**:
- Add `build-essential gcc g++` to Dockerfile
- Check apt-get install includes these packages

### Build Failure: "error: could not create '/usr/local/lib/..."

**Cause**: Missing Python development headers (python3-dev)

**Fix**:
- Add `python3-dev` to Dockerfile apt-get install line

### Service Won't Start: "ModuleNotFoundError: No module named 'X'"

**Cause**: Package not installed or import error

**Fix**:
- Check requirements.txt is complete
- Verify all dependencies installed: `docker run consultantos:test python -c "import X"`
- Check for circular imports or missing dependencies

### Service Health Check Failing

**Cause**: `/health` endpoint not implemented

**Fix**:
- Add health endpoint to FastAPI app
- Verify endpoint returns JSON with 200 status
- Test locally: `curl http://localhost:8080/health`

### Secrets Not Accessible

**Cause**: Service account missing permissions

**Fix**:
```bash
# Grant secret accessor role
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:consultantos-api-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### Service Times Out During Startup

**Cause**: Long dependency install or slow image pull

**Fix**:
- Increase Cloud Run `--startup-cpu-boost`
- Increase memory allocation (currently 2Gi)
- Check if build is complete before deploying

---

## Rollback Plan (If Something Goes Wrong)

```bash
# Restore previous deployment
gcloud run deploy consultantos-api \
  --image=gcr.io/$PROJECT_ID/consultantos-api:PREVIOUS_BUILD_ID \
  --region=us-central1

# Restore previous config files
git revert <commit-hash>

# Restart from last known good state
git reset --hard <previous-commit>
git push --force origin master
```

---

## Summary of Changes

| File | Change | Reason |
|------|--------|--------|
| `Dockerfile` | Add system dependencies | Fix pip install failures |
| `services/*/Dockerfile` (4 files) | Add system dependencies | Fix service builds |
| `cloudbuild.api.yaml` | Add --set-secrets | Pass API keys to Cloud Run |
| `cloudbuild.agent.yaml` | Add --set-secrets | Pass API keys to Cloud Run |
| `cloudbuild.reporting.yaml` | Add --set-secrets | Pass API keys to Cloud Run |
| `cloudbuild.task.yaml` | Add --set-secrets | Pass API keys to Cloud Run |
| `requirements.txt` | Add google-api-core pinning | Prevent version conflicts |
| `consultantos/api/main.py` | Add /health endpoint | Support HEALTHCHECK |

**Total changes**: 10 files
**Complexity**: Low (mostly additive changes)
**Risk**: Low (no breaking changes)
**Deployment time**: 5-10 minutes

---

## Post-Deployment Verification

```bash
# All services should be running
gcloud run services list --filter="name:consultantos*"

# All services should be deployable from main branch
git log --oneline | head -1
# Should show your deployment fix commit

# All service images should exist
gcloud container images list --repository=gcr.io/$PROJECT_ID \
  --filter="name:consultantos*"

# Run smoke tests on deployed services
for SERVICE in api agent reporting task; do
  URL=$(gcloud run services describe consultantos-$SERVICE \
    --region=us-central1 --format='value(status.url)')
  echo "Testing $SERVICE at $URL/health"
  curl "$URL/health" || echo "FAILED"
done
```

---

## Success Criteria

Your deployment is successful when:

✅ All 4 Cloud Build configurations complete without errors
✅ All 4 Cloud Run services show "green" status
✅ Health check endpoints return 200 OK
✅ No import errors in Cloud Run logs
✅ API responds to requests (e.g., `/docs` returns Swagger UI)
✅ No "compilation failed" errors in build logs

If all these are true, your deployment fix is complete!
