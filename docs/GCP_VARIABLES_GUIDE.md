# Google Cloud Optional Variables - Purpose and Usage

## Overview

ConsultantOS uses **optional** Google Cloud Platform (GCP) variables to enable production-grade features like persistent storage, database, and secret management. The application works **without these variables** using local fallbacks, but they enable enhanced functionality in production.

## Optional Variables

### 1. `GCP_PROJECT_ID`

**Purpose**: Identifies your Google Cloud Project for GCP services.

**What it enables**:
- **Firestore Database**: Persistent storage for reports, user data, API keys, and metadata
- **Cloud Storage**: PDF report storage and retrieval
- **Secret Manager**: Secure API key storage (alternative to environment variables)
- **Cloud Logging**: Centralized logging and monitoring

**Usage in code**:
```python
# database.py - Firestore client initialization
_db_client = firestore.Client(project=settings.gcp_project_id)

# storage.py - Cloud Storage client initialization  
self._client = storage.Client(project=settings.gcp_project_id)

# config.py - Secret Manager access
project_id = os.getenv("GCP_PROJECT_ID") or os.getenv("GOOGLE_CLOUD_PROJECT")
```

**Fallback behavior**:
- If not set: Uses in-memory database and local file storage
- Reports are lost on server restart
- No persistent user data or API keys

**How to set**:
```bash
export GCP_PROJECT_ID=your-project-id
# or in .env file:
GCP_PROJECT_ID=your-project-id
```

---

### 2. `GOOGLE_APPLICATION_CREDENTIALS`

**Purpose**: Path to service account JSON key file for **local development** authentication.

**What it enables**:
- Authenticates your local development environment to GCP services
- Required when running locally and accessing Firestore/Cloud Storage
- Not needed in Cloud Run (uses default service account automatically)

**Usage**:
```bash
# Local development
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json

# Or in .env file:
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
```

**When it's needed**:
- ✅ **Local development** accessing Firestore/Cloud Storage
- ❌ **Not needed** in Cloud Run (automatic authentication)
- ❌ **Not needed** if using local fallbacks only

**How to get credentials**:
1. Go to [GCP Console](https://console.cloud.google.com/)
2. Navigate to **IAM & Admin** → **Service Accounts**
3. Create or select a service account
4. Create a key (JSON format)
5. Download and save securely
6. Set the path in `GOOGLE_APPLICATION_CREDENTIALS`

**Security Note**: 
- Never commit service account keys to git
- Add `*.json` to `.gitignore`
- Use Secret Manager in production instead

---

## What Each Variable Enables

### Without GCP Variables (Local Development)

| Feature | Status | Storage Location |
|---------|--------|------------------|
| Reports | ✅ Works | Local filesystem (temporary) |
| Database | ✅ Works | In-memory (lost on restart) |
| User Data | ✅ Works | In-memory (lost on restart) |
| API Keys | ✅ Works | In-memory (lost on restart) |
| PDF Storage | ✅ Works | Local directory |
| Persistence | ❌ No | Data lost on restart |

### With `GCP_PROJECT_ID` Only (Cloud Run)

| Feature | Status | Storage Location |
|---------|--------|------------------|
| Reports | ✅ Works | Cloud Storage (persistent) |
| Database | ✅ Works | Firestore (persistent) |
| User Data | ✅ Works | Firestore (persistent) |
| API Keys | ✅ Works | Firestore (persistent) |
| PDF Storage | ✅ Works | Cloud Storage (persistent) |
| Persistence | ✅ Yes | All data persists |

### With Both Variables (Local + GCP)

| Feature | Status | Storage Location |
|---------|--------|------------------|
| Reports | ✅ Works | Cloud Storage (persistent) |
| Database | ✅ Works | Firestore (persistent) |
| User Data | ✅ Works | Firestore (persistent) |
| API Keys | ✅ Works | Firestore (persistent) |
| PDF Storage | ✅ Works | Cloud Storage (persistent) |
| Persistence | ✅ Yes | All data persists |
| Local Dev | ✅ Yes | Can test GCP features locally |

---

## Service-Specific Usage

### Firestore Database (`database.py`)

**Without GCP**:
```python
# Uses in-memory database
# Data lost on server restart
```

**With `GCP_PROJECT_ID`**:
```python
# Uses Firestore
# Persistent storage across restarts
# Supports user data, reports, API keys
```

### Cloud Storage (`storage.py`)

**Without GCP**:
```python
# Uses LocalFileStorageService
# Stores PDFs in local directory
# Files lost if server directory is deleted
```

**With `GCP_PROJECT_ID`**:
```python
# Uses Cloud Storage
# PDFs stored in GCS bucket
# Accessible via signed URLs
# Survives server restarts
```

### Secret Manager (`config.py`)

**Without GCP**:
```python
# Uses environment variables only
# Secrets in .env file or environment
```

**With `GCP_PROJECT_ID`**:
```python
# Tries Secret Manager first
# Falls back to environment variables
# More secure for production
```

### Cloud Logging (`monitoring.py`)

**Without GCP**:
```python
# Uses standard Python logging
# Logs to stdout/stderr
```

**With `GCP_PROJECT_ID`**:
```python
# Uses Cloud Logging
# Centralized log management
# Better for production monitoring
```

---

## Setup Scenarios

### Scenario 1: Local Development (No GCP)

**Use case**: Quick testing, development, hackathon demo

**Setup**:
```bash
# Only required variables
export GEMINI_API_KEY=your-key
export TAVILY_API_KEY=your-key

# No GCP variables needed
# Uses local fallbacks
```

**Limitations**:
- Data lost on restart
- No persistent storage
- No user data persistence

### Scenario 2: Local Development with GCP

**Use case**: Testing GCP features locally before deployment

**Setup**:
```bash
export GEMINI_API_KEY=your-key
export TAVILY_API_KEY=your-key
export GCP_PROJECT_ID=your-project-id
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
```

**Benefits**:
- Test Firestore/Cloud Storage locally
- Persistent data during development
- Same behavior as production

### Scenario 3: Cloud Run Deployment

**Use case**: Production deployment

**Setup**:
```bash
# In Cloud Run, GCP_PROJECT_ID is auto-set
# GOOGLE_APPLICATION_CREDENTIALS not needed
# Uses default service account

# Set via Cloud Run:
gcloud run deploy consultantos \
  --set-env-vars "GCP_PROJECT_ID=$PROJECT_ID" \
  --set-secrets "GEMINI_API_KEY=gemini-api-key:latest"
```

**Benefits**:
- Full GCP integration
- Persistent storage
- Production-ready

---

## Code Examples

### Checking if GCP is Available

```python
from consultantos.config import settings

if settings.gcp_project_id:
    # GCP features enabled
    print("Using Firestore and Cloud Storage")
else:
    # Using local fallbacks
    print("Using in-memory database and local storage")
```

### Conditional GCP Usage

```python
# storage.py example
if STORAGE_AVAILABLE and settings.gcp_project_id:
    # Use Cloud Storage
    self._client = storage.Client(project=settings.gcp_project_id)
else:
    # Use local file storage
    self._client = LocalFileStorageService()
```

---

## Migration Path

### From Local to GCP

1. **Set up GCP project**:
   ```bash
   gcloud projects create consultantos-prod
   gcloud config set project consultantos-prod
   ```

2. **Enable APIs**:
   ```bash
   gcloud services enable firestore.googleapis.com
   gcloud services enable storage-component.googleapis.com
   gcloud services enable secretmanager.googleapis.com
   ```

3. **Create Firestore database**:
   ```bash
   gcloud firestore databases create --location=us-central1
   ```

4. **Set environment variable**:
   ```bash
   export GCP_PROJECT_ID=consultantos-prod
   ```

5. **Restart server** - automatically uses GCP services

---

## Summary

| Variable | Required? | Purpose | When Needed |
|----------|-----------|---------|-------------|
| `GCP_PROJECT_ID` | Optional | Enable GCP services | Production or local GCP testing |
| `GOOGLE_APPLICATION_CREDENTIALS` | Optional | Local GCP auth | Local dev with GCP services |

**Key Points**:
- ✅ Application works **without** these variables (uses local fallbacks)
- ✅ These variables enable **production-grade** features
- ✅ `GCP_PROJECT_ID` enables Firestore, Cloud Storage, Secret Manager
- ✅ `GOOGLE_APPLICATION_CREDENTIALS` only needed for local GCP access
- ✅ In Cloud Run, authentication is automatic (no credentials file needed)

---

**For more details**, see:
- [SETUP.md](../SETUP.md) - General setup instructions
- [FIRESTORE_SETUP_COMPLETE.md](../FIRESTORE_SETUP_COMPLETE.md) - Firestore setup
- [DEPLOYMENT_GUIDE.md](../DEPLOYMENT_GUIDE.md) - Cloud Run deployment

