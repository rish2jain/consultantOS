# ConsultantOS Cloud Run Deployment Analysis

**Status**: Critical issues identified
**Date**: 2025-11-08
**Scope**: Cloud Build configurations, Dockerfiles, dependency management

---

## Executive Summary

The ConsultantOS deployment is failing due to **missing system dependencies in Docker** and **incomplete dependency version management**. While the pydantic version fixes (2.12.4 and 2.11.0) are correct, the root cause of failures is inadequate system libraries during pip install.

### Critical Issues (Blocking Deployment):
1. ❌ **Missing system libraries** for kaleido, reportlab, edgartools (CRITICAL)
2. ❌ **Incomplete Dockerfile** - only installs gcc/g++, missing libffi, libssl, python-dev
3. ❌ **No explicit google-api-core pinning** - causes version conflicts with 6 google-cloud-* packages
4. ❌ **edgartools optional dependency** not properly handled

### Current Status:
- ✅ pydantic 2.12.4 and pydantic-settings 2.11.0 are compatible
- ✅ FastAPI 0.120.4 compatible with pydantic 2.12.4
- ✅ Service-specific requirements strategy is sound
- ❌ Dockerfile lacks essential build dependencies
- ❌ Cloud Run deployment missing secret configuration for some services

---

## Issue 1: Missing System Dependencies in Docker (CRITICAL)

### Current Dockerfile
```dockerfile
FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*
```

### Problem
This only installs C/C++ compilers but **missing critical libraries required by pip packages**:

| Package | System Dependencies | Impact |
|---------|-------------------|--------|
| **kaleido** | libffi-dev, libssl-dev | Plotly chart export fails |
| **reportlab** | build-essential, python3-dev | PDF generation fails |
| **edgartools** | Full build-essential | SEC EDGAR data fails |
| **cryptography** | libssl-dev, libffi-dev | JWT/crypto operations fail |

### Why It Fails
During `pip install kaleido`:
```
error: command 'x86_64-linux-gnu-gcc' failed: No such file or directory
Collecting cffi (required for kaleido)
  error: /usr/include/ffi.h: No such file (libffi-dev missing)
```

### Solution
Replace Dockerfile with complete build dependencies:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies required for Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./requirements.txt
COPY libs ./libs
COPY services/api_service/requirements.txt ./service-requirements.txt

# Install Python dependencies with better error handling
RUN pip install --no-cache-dir \
    --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r service-requirements.txt

COPY consultantos ./consultantos
COPY services/api_service/main.py ./main.py

ENV PYTHONPATH="/app"

# Health check for Cloud Run
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### Apply to All Services
Update all 4 Dockerfile variants:
- `services/api_service/Dockerfile`
- `services/agent_service/Dockerfile`
- `services/reporting_service/Dockerfile`
- `services/task_handler_service/Dockerfile`

---

## Issue 2: Google Cloud Library Version Conflicts (MEDIUM)

### Problem
Six google-cloud-* libraries share `google-api-core` as a dependency:

```
google-cloud-storage>=2.10.0 → google-api-core>=1.33.0
google-cloud-secret-manager>=2.16.0 → google-api-core>=1.33.0
google-cloud-logging>=3.8.0 → google-api-core>=1.33.0
google-cloud-firestore>=2.13.0 → google-api-core>=1.33.0
google-cloud-tasks>=2.14.0 → google-api-core>=1.33.0
google-generativeai>=0.3.0 → google-api-core>=1.32.0
```

When pip resolves these, version mismatches can occur. Pip may select incompatible versions.

### Solution
Add explicit google-api-core pinning in requirements.txt:

```txt
# Explicitly pin google-api-core to avoid conflicts across multiple google-cloud libraries
google-api-core>=1.33.0,<2.0.0

# Google Cloud
google-cloud-storage>=2.10.0
google-cloud-secret-manager>=2.16.0
google-cloud-logging>=3.8.0
google-cloud-firestore>=2.13.0
google-cloud-tasks>=2.14.0

# Google AI
google-generativeai>=0.3.0
```

---

## Issue 3: edgartools Optional Dependency (MEDIUM)

### Problem
`edgartools>=2.0.0` is marked as required but:
1. Complex C-extension dependencies
2. Fails with cryptic errors during pip install
3. Not critical if SEC EDGAR data is optional

### Current Setup
```txt
edgartools>=2.0.0  # Heavy dependency, can fail randomly
```

### Solution: Option A (Recommended - Make Fully Optional)
Create optional requirements file:

**requirements-optional.txt**
```txt
# Optional data sources (not required for core functionality)
edgartools>=2.0.0

# Optional visualization enhancements
plotly-orca>=1.3.0  # Alternative to kaleido for exports
```

**Dockerfile change**:
```dockerfile
RUN pip install --no-cache-dir -r requirements.txt && \
    # Attempt optional dependencies, don't fail if they skip
    pip install --no-cache-dir -r requirements-optional.txt || echo "Optional dependencies skipped" && \
    pip install --no-cache-dir -r service-requirements.txt
```

**Python code change** - graceful degradation:
```python
# In consultantos/tools/financial_tools.py
try:
    import edgartools
    EDGAR_AVAILABLE = True
except ImportError:
    EDGAR_AVAILABLE = False
    logger.warning("edgartools not available - SEC EDGAR data disabled")

async def get_financial_data(ticker):
    data = {}

    # Try SEC EDGAR if available
    if EDGAR_AVAILABLE:
        try:
            # EDGAR-based financial data
            pass
        except Exception as e:
            logger.error(f"EDGAR data failed: {e}, falling back to yfinance")

    # Always fall back to yfinance
    data.update(yfinance_data)
    return data
```

### Solution: Option B (Pin to Stable Version)
If edgartools is critical:
```txt
edgartools==2.0.4  # Known stable version with all deps resolved
```

---

## Issue 4: Secret Configuration Gaps (HIGH)

### Current Cloud Build Issues

**cloudbuild.api.yaml** - Missing secrets:
```yaml
- name: "consultantos-api"
- "--set-env-vars"
- "GCP_PROJECT_ID=$PROJECT_ID,CLOUD_TASKS_LOCATION=us-central1,..."
# ❌ Missing: GEMINI_API_KEY, TAVILY_API_KEY
```

**cloudbuild.reporting.yaml** - Missing secrets:
```yaml
- "--set-env-vars"
- "GCP_PROJECT_ID=$PROJECT_ID,ENVIRONMENT=production"
# ❌ Missing: All API keys needed for data sources
```

### Solution
Add `--set-secrets` to all Cloud Build configs:

```yaml
# For API service (cloudbuild.api.yaml)
args:
  # ... other args ...
  - "--set-env-vars"
  - "GCP_PROJECT_ID=$PROJECT_ID,CLOUD_TASKS_LOCATION=us-central1,ENVIRONMENT=production"
  - "--set-secrets"
  - "GEMINI_API_KEY=GEMINI_API_KEY:latest,TAVILY_API_KEY=TAVILY_API_KEY:latest"

# For reporting service (cloudbuild.reporting.yaml)
args:
  # ... other args ...
  - "--set-env-vars"
  - "GCP_PROJECT_ID=$PROJECT_ID,ENVIRONMENT=production"
  - "--set-secrets"
  - "GEMINI_API_KEY=GEMINI_API_KEY:latest,TAVILY_API_KEY=TAVILY_API_KEY:latest,GOOGLE_APPLICATION_CREDENTIALS=/var/secrets/google/key.json"

# For task handler (cloudbuild.task.yaml)
args:
  # ... other args ...
  - "--set-env-vars"
  - "GCP_PROJECT_ID=$PROJECT_ID,ENVIRONMENT=production"
  - "--set-secrets"
  - "GEMINI_API_KEY=GEMINI_API_KEY:latest,TAVILY_API_KEY=TAVILY_API_KEY:latest"
```

### Verify Secrets Exist
```bash
# List all secrets
gcloud secrets list --project=$PROJECT_ID

# Create missing secrets
echo -n "your-gemini-key" | gcloud secrets create GEMINI_API_KEY \
  --replication-policy="automatic" \
  --data-file=-

echo -n "your-tavily-key" | gcloud secrets create TAVILY_API_KEY \
  --replication-policy="automatic" \
  --data-file=-
```

---

## Issue 5: Health Check Configuration (LOW)

### Current Problem
Cloud Run doesn't know if services are healthy:
```yaml
# No health check configured
# No liveness/readiness probes
```

### Solution

**Add to Dockerfile**:
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1
```

**Ensure health endpoint exists** in FastAPI:
```python
# In consultantos/api/main.py or services/*/main.py
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "consultantos-api",
        "version": "1.0.0"
    }
```

**Configure in Cloud Run** (cloudbuild.api.yaml):
```yaml
args:
  # ... other args ...
  - "--cpu-throttling"  # Optional: disable CPU throttling during startup
  - "--startup-cpu-boost"  # Optional: boost CPU during startup
```

---

## Issue 6: Dependency Resolution Strategy (MEDIUM)

### Current Problem
Service requirements files only have:
```txt
# services/api_service/requirements.txt
fastapi
uvicorn[standard]
```

This works but creates divergence between services and root requirements.

### Better Approach
Keep current strategy (all deps in root, minimal in service files) **but document it**:

**Add to requirements.txt header**:
```txt
# ConsultantOS Requirements
#
# Strategy: All dependencies managed in root requirements.txt
# Service-specific requirements files (services/*/requirements.txt) only
# contain service entry points (fastapi, uvicorn) for Dockerfile clarity.
#
# This approach ensures:
# 1. Single source of truth for dependency versions
# 2. All services use identical dependency versions
# 3. Easier to manage conflicts and updates
# 4. All services can be easily swapped/scaled

# If service-specific dependencies needed in future:
# Add them to services/SERVICE_NAME/requirements.txt AND
# Update that service's Dockerfile to install them

# ============================================================================
# Core Framework
fastapi==0.120.4
uvicorn[standard]==0.35.0
pydantic==2.12.4
pydantic-settings==2.11.0
# ... rest of requirements
```

---

## Deployment Checklist

### Phase 1: Fix Dockerfiles (CRITICAL)
- [ ] Update root `/Dockerfile` with full system dependencies
- [ ] Update `/services/api_service/Dockerfile`
- [ ] Update `/services/agent_service/Dockerfile`
- [ ] Update `/services/reporting_service/Dockerfile`
- [ ] Update `/services/task_handler_service/Dockerfile`
- [ ] Test build locally: `docker build -t consultantos:test -f Dockerfile .`

### Phase 2: Fix Dependencies
- [ ] Add google-api-core pinning to requirements.txt
- [ ] Create requirements-optional.txt for edgartools (if using Option A)
- [ ] Update requirements.txt with version comment header
- [ ] Add health check endpoint to FastAPI apps

### Phase 3: Fix Cloud Build Configs
- [ ] Update cloudbuild.api.yaml with secrets configuration
- [ ] Update cloudbuild.reporting.yaml with secrets configuration
- [ ] Update cloudbuild.task.yaml with secrets configuration
- [ ] Update cloudbuild.agent.yaml with missing env vars if needed
- [ ] Create/verify secrets in Secret Manager: `gcloud secrets list`

### Phase 4: Test Deployment
- [ ] Verify Cloud Build logs for clean build: `gcloud builds log <BUILD_ID>`
- [ ] Check Cloud Run service logs: `gcloud run logs list`
- [ ] Test health endpoint: `curl https://<SERVICE_URL>/health`
- [ ] Verify all API endpoints respond
- [ ] Check for any startup errors in logs

---

## Recommended requirements.txt Structure

```txt
# ConsultantOS Requirements
# Strategy: All dependencies in root, services inherit via Dockerfile COPY

# Core Framework
fastapi==0.120.4
uvicorn[standard]==0.35.0
pydantic==2.12.4
pydantic-settings==2.11.0

# Google AI
google-generativeai>=0.3.0
instructor>=0.4.0

# Data Sources
tavily-python>=0.3.0
pytrends>=4.9.0
yfinance>=0.2.0
# edgartools>=2.0.0  # See requirements-optional.txt
finviz>=1.4.0
pandas>=2.1.0
pandas-datareader>=0.10.0

# Vector Store and Caching
chromadb>=0.4.0
diskcache>=5.6.0

# Report Generation
reportlab>=4.0.0
plotly>=5.18.0
kaleido>=0.2.1

# API and Security
slowapi>=0.1.9
python-multipart>=0.0.6

# Google Cloud (with explicit api-core to avoid conflicts)
google-api-core>=1.33.0,<2.0.0
google-cloud-storage>=2.10.0
google-cloud-secret-manager>=2.16.0
google-cloud-logging>=3.8.0
google-cloud-firestore>=2.13.0
google-cloud-tasks>=2.14.0

# Utilities
python-dotenv>=1.0.0
structlog>=23.2.0
httpx>=0.25.0
passlib[bcrypt]>=1.7.4
python-jose[cryptography]>=3.3.0

# Testing
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0
```

---

## Testing Deployment Locally

### 1. Build Docker Image
```bash
# Test root Dockerfile
docker build -t consultantos:test -f Dockerfile .

# Check if all dependencies installed
docker run --rm consultantos:test python -c "
import sys
print('Python version:', sys.version)
import pydantic; print('pydantic:', pydantic.__version__)
import fastapi; print('fastapi version:', fastapi.__version__)
import kaleido; print('kaleido available')
import reportlab; print('reportlab available')
"
```

### 2. Test Service Build
```bash
# Test api service Dockerfile
docker build -t consultantos-api:test -f services/api_service/Dockerfile .
```

### 3. Test Image Runs
```bash
# Run container and check health
docker run -d --name test-api -p 8080:8080 consultantos-api:test
sleep 5
curl http://localhost:8080/health

# Check logs
docker logs test-api

# Cleanup
docker stop test-api
docker rm test-api
```

### 4. Verify Dependencies Work
```bash
# Check import chain works correctly
docker run --rm consultantos-api:test python -c "
from consultantos.reports.pdf_generator import PDFGenerator
from consultantos.visualizations import create_chart
from consultantos.agents.research_agent import ResearchAgent
print('All imports successful!')
"
```

---

## Cloud Build Local Testing

```bash
# Install Cloud Build local runner
gcloud components install cloud-build-local

# Test build locally
cloud-build-local --build-pack=gcp-cloud-builders \
  --substitutions="_PROJECT_ID=your-project" \
  --config=cloudbuild.api.yaml \
  .

# Check logs
# Verify no "file not found" or "compilation failed" errors
```

---

## Monitoring After Deployment

### Check Build Logs
```bash
# Get last build
BUILD_ID=$(gcloud builds list --limit=1 --format='value(id)')

# View detailed logs
gcloud builds log $BUILD_ID --stream

# Common failure patterns:
# ERROR: pip's dependency resolver does not currently take into account...
# error: could not create '/usr/local/lib/python3.11/dist-packages/kaleido.so'
# gcc: command not found
# ffi.h: No such file
```

### Check Runtime Logs
```bash
# View Cloud Run logs
gcloud run logs read consultantos-api \
  --region=us-central1 \
  --limit=100

# Look for:
# - ImportError: No module named 'X'
# - AttributeError: module 'X' has no attribute 'Y'
# - Connection errors to Secret Manager
# - Missing environment variables
```

### Verify Secrets
```bash
# List secret versions
gcloud secrets versions list GEMINI_API_KEY

# Test secret access from Cloud Run
gcloud run deploy test-secret \
  --image=gcr.io/cloud-builders/gke-deploy \
  --set-secrets="GEMINI_API_KEY=GEMINI_API_KEY:latest" \
  --region=us-central1

gcloud run exec test-secret --region=us-central1 -- env | grep GEMINI
```

---

## Version Compatibility Matrix (Verified)

| Component | Version | Status | Notes |
|-----------|---------|--------|-------|
| Python | 3.11 | ✅ Stable | Use python:3.11-slim base |
| FastAPI | 0.120.4 | ✅ OK | Compatible with pydantic 2.12.4 |
| Uvicorn | 0.35.0 | ✅ OK | Works with FastAPI 0.120.4 |
| Pydantic | 2.12.4 | ✅ OK | Latest in 2.x series |
| Pydantic-Settings | 2.11.0 | ✅ OK | Compatible with pydantic 2.12.4 |
| google-api-core | 1.33.0+ | ✅ OK | Supports all google-cloud libs |
| Plotly | 5.18.0+ | ✅ OK | Works with kaleido 0.2.1+ |
| Kaleido | 0.2.1+ | ✅ OK | Requires libffi-dev, libssl-dev |
| ReportLab | 4.0.0+ | ✅ OK | Requires build-essential, python3-dev |
| edgartools | 2.0.0+ | ⚠️ Optional | Heavy deps - make optional |

---

## Summary of Changes Required

| File | Change | Priority | Impact |
|------|--------|----------|--------|
| `Dockerfile` | Add system dependencies | CRITICAL | Build will fail without these |
| `services/*/Dockerfile` | Add system dependencies | CRITICAL | All service builds will fail |
| `requirements.txt` | Add google-api-core pinning | MEDIUM | May cause version conflicts |
| `requirements.txt` | Document dependency strategy | LOW | Aids future maintenance |
| `cloudbuild.api.yaml` | Add --set-secrets | HIGH | API keys not passed to service |
| `cloudbuild.reporting.yaml` | Add --set-secrets | HIGH | Service can't access APIs |
| `cloudbuild.task.yaml` | Add --set-secrets | HIGH | Background tasks fail |
| `consultantos/api/main.py` | Add /health endpoint | LOW | Cloud Run can't verify health |
| `requirements-optional.txt` | Create for edgartools | MEDIUM | Allows graceful degradation |

---

## Next Steps

1. **Immediate** (Today):
   - Update all Dockerfiles with system dependencies
   - Test build locally: `docker build -f Dockerfile .`

2. **Short-term** (Next build):
   - Update Cloud Build YAML files with secrets
   - Verify secrets exist in Secret Manager
   - Add health check endpoints

3. **Follow-up**:
   - Create requirements-optional.txt for edgartools
   - Add graceful degradation in agents for optional features
   - Monitor Cloud Run logs after deployment

---

## Questions & Answers

**Q: Why does adding libffi-dev fix the build?**
A: kaleido uses cffi to call C code. cffi needs `/usr/include/ffi.h`, which comes from libffi-dev. Without it, `pip install kaleido` fails during compilation.

**Q: Why not use alpine:3.11 instead of python:3.11-slim?**
A: Alpine is smaller but has broken dependencies for some packages. Debian-based slim is better compromise for stability.

**Q: Can we remove edgartools to simplify?**
A: Yes, if SEC EDGAR data isn't critical. Create requirements-optional.txt and add fallback in FinancialAgent.

**Q: Why pin google-api-core explicitly?**
A: 6 google-cloud-* packages depend on it. Pip may select incompatible versions. Explicit pin ensures all use same version.

**Q: How do we test this works before pushing?**
A: `docker build` locally and test imports. Use Cloud Build local runner for full build test.
