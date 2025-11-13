# ConsultantOS Cloud Deployment Plan

**Comprehensive deployment guide for Google Cloud Run Hackathon submission**

## 🎯 Deployment Objectives

### Hackathon Requirements Met:
- ✅ **Cloud Run Deployment** (MANDATORY) - Both frontend and backend
- ✅ **Multiple Cloud Run Services** (+0.4 bonus points) - Frontend + Backend
- ✅ **Google AI Models** (+0.4 bonus points) - Gemini 2.5 Flash
- ✅ **Production-Ready** - Enterprise-grade infrastructure
- ✅ **Public Repository** - GitHub with full documentation

### Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Google Cloud Run                      │
│                                                          │
│  ┌──────────────────┐      ┌──────────────────┐      │
│  │  Frontend Service │      │   Backend API    │      │
│  │  (Next.js)        │◄─────┤   (FastAPI)      │      │
│  │  Port: 8080       │      │   Port: 8080     │      │
│  │  Memory: 512Mi     │      │   Memory: 2Gi    │      │
│  │  CPU: 1           │      │   CPU: 2         │      │
│  └──────────────────┘      └────────┬─────────┘      │
│                                      │                 │
└──────────────────────────────────────┼─────────────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
            ┌───────▼──────┐  ┌────────▼────────┐  ┌─────▼──────┐
            │   Firestore  │  │  Cloud Storage  │  │  Secret    │
            │  (Database)   │  │  (Reports/PDFs)│  │  Manager   │
            └──────────────┘  └─────────────────┘  └────────────┘
```

---

## 📋 Pre-Deployment Checklist

### Prerequisites

- [ ] Google Cloud Project created with billing enabled
- [ ] `gcloud` CLI installed and authenticated
- [ ] Docker installed (for local testing)
- [ ] GitHub repository is public
- [ ] API keys secured (Gemini, Tavily)
- [ ] Domain name (optional, for custom domain)

### Required Environment Variables

**Backend:**
- `GEMINI_API_KEY` - Google Gemini API key
- `TAVILY_API_KEY` - Tavily research API key
- `GCP_PROJECT_ID` - Your GCP project ID
- `GOOGLE_APPLICATION_CREDENTIALS` - Service account JSON (optional, for local dev)

**Frontend:**
- `NEXT_PUBLIC_API_URL` - Backend API URL (set after backend deployment)

---

## 🚀 Phase 1: Initial Setup

### Step 1.1: Create GCP Project

```bash
# Set your project ID
export PROJECT_ID="consultantos-hackathon"
export REGION="us-central1"

# Create project (if new)
gcloud projects create $PROJECT_ID --name="ConsultantOS Hackathon"

# Set as active project
gcloud config set project $PROJECT_ID

# Enable billing (required)
# Go to: https://console.cloud.google.com/billing
```

### Step 1.2: Enable Required APIs

```bash
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  containerregistry.googleapis.com \
  secretmanager.googleapis.com \
  firestore.googleapis.com \
  storage-component.googleapis.com \
  logging.googleapis.com \
  monitoring.googleapis.com \
  cloudtasks.googleapis.com
```

### Step 1.3: Create Service Accounts

```bash
# Backend service account
gcloud iam service-accounts create consultantos-api-sa \
  --display-name="ConsultantOS API Service Account"

# Frontend service account (if needed)
gcloud iam service-accounts create consultantos-frontend-sa \
  --display-name="ConsultantOS Frontend Service Account"

# Grant necessary roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:consultantos-api-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/datastore.user"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:consultantos-api-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:consultantos-api-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/cloudtasks.enqueuer"
```

### Step 1.4: Store Secrets in Secret Manager

```bash
# Store Gemini API key
# SECURITY: Read from secure file or prompt interactively to avoid shell history exposure
# Option 1: Read from file (recommended)
gcloud secrets create gemini-api-key \
  --data-file=~/secrets/gemini-api-key \
  --replication-policy="automatic"

# Option 2: Interactive prompt (no echo)
read -s GEMINI_KEY
echo -n "$GEMINI_KEY" | gcloud secrets create gemini-api-key \
  --data-file=- \
  --replication-policy="automatic"
unset GEMINI_KEY

# Store Tavily API key (same approach)
gcloud secrets create tavily-api-key \
  --data-file=~/secrets/tavily-api-key \
  --replication-policy="automatic"

# Grant service account access to secrets
gcloud secrets add-iam-policy-binding gemini-api-key \
  --member="serviceAccount:consultantos-api-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding tavily-api-key \
  --member="serviceAccount:consultantos-api-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### Step 1.5: Create Firestore Database

```bash
# Create Firestore database (Native mode)
gcloud firestore databases create \
  --location=$REGION \
  --type=firestore-native
```

### Step 1.6: Create Cloud Storage Bucket

```bash
# Create bucket for reports and PDFs
gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://$PROJECT_ID-consultantos-reports

# Set lifecycle policy (optional - delete files older than 90 days)
cat > /tmp/lifecycle.json << EOF
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {"age": 90}
      }
    ]
  }
}
EOF

gsutil lifecycle set /tmp/lifecycle.json gs://$PROJECT_ID-consultantos-reports
```

---

## 🔧 Phase 2: Backend API Deployment

### Step 2.1: Update CORS Configuration

Update `consultantos/api/main.py` to allow frontend domain:

```python
# Add your frontend URL to CORS origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://consultantos-frontend-*.run.app",  # Cloud Run pattern
        "https://your-custom-domain.com",  # If using custom domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Step 2.2: Deploy Backend Using Cloud Build

```bash
# Navigate to project root
cd /Users/rish2jain/Documents/Hackathons/ConsultantOS

# Submit build with Cloud Build
gcloud builds submit --config=cloudbuild.api.yaml \
  --project=$PROJECT_ID
```

**Alternative: Direct Deployment**

```bash
# Deploy directly from source
gcloud run deploy consultantos-api \
  --source . \
  --region $REGION \
  --platform managed \
  --service-account consultantos-api-sa@$PROJECT_ID.iam.gserviceaccount.com \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --min-instances 0 \
  --max-instances 10 \
  --set-env-vars "GCP_PROJECT_ID=$PROJECT_ID,ENVIRONMENT=production" \
  --set-secrets "GEMINI_API_KEY=gemini-api-key:latest,TAVILY_API_KEY=tavily-api-key:latest" \
  --project $PROJECT_ID
```

### Step 2.3: Get Backend URL

```bash
# Get the deployed service URL
export API_URL=$(gcloud run services describe consultantos-api \
  --region $REGION \
  --format 'value(status.url)' \
  --project $PROJECT_ID)

echo "Backend API URL: $API_URL"
```

### Step 2.4: Verify Backend Deployment

```bash
# Test health endpoint
curl $API_URL/health

# Expected response:
# {"status":"healthy","version":"0.3.0",...}
```

---

## 🎨 Phase 3: Frontend Dashboard Deployment

### Step 3.1: Update Frontend Configuration

Ensure `frontend/next.config.js` is configured for standalone output:

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',  // Required for Cloud Run
  // ... other config
}

module.exports = nextConfig
```

### Step 3.2: Deploy Frontend Using Cloud Build

```bash
# Set the backend API URL
export API_URL="https://consultantos-api-xxx-uc.a.run.app"  # Use actual URL from Step 2.3

# Submit build
gcloud builds submit --config=cloudbuild.frontend.yaml \
  --substitutions=_API_URL=$API_URL,_REGION=$REGION \
  --project=$PROJECT_ID
```

**Alternative: Direct Deployment**

```bash
# Navigate to frontend directory
cd frontend

# Deploy directly
gcloud run deploy consultantos-frontend \
  --source . \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300 \
  --min-instances 0 \
  --max-instances 10 \
  --set-env-vars "NEXT_PUBLIC_API_URL=$API_URL,PORT=8080" \
  --project $PROJECT_ID
```

### Step 3.3: Get Frontend URL

```bash
# Get the deployed service URL
export FRONTEND_URL=$(gcloud run services describe consultantos-frontend \
  --region $REGION \
  --format 'value(status.url)' \
  --project $PROJECT_ID)

echo "Frontend URL: $FRONTEND_URL"
```

### Step 3.4: Update Backend CORS with Frontend URL

```bash
# Update backend CORS to include frontend URL
# Edit consultantos/api/main.py and add:
# "https://consultantos-frontend-xxx.run.app"

# Redeploy backend
gcloud run deploy consultantos-api \
  --source . \
  --region $REGION \
  --project $PROJECT_ID
```

---

## ✅ Phase 4: Verification & Testing

### Step 4.1: Test Frontend

```bash
# Open frontend in browser
open $FRONTEND_URL

# Check browser console for errors
# Verify API connectivity
```

### Step 4.2: Test Backend API

```bash
# Test health check
curl $API_URL/health

# Test analysis endpoint
curl -X POST "$API_URL/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "company": "Tesla",
    "industry": "Electric Vehicles",
    "frameworks": ["porter", "swot"]
  }'
```

### Step 4.3: End-to-End Test

1. Open frontend URL in browser
2. Create a test analysis
3. Verify results appear
4. Check all pages load correctly
5. Test authentication flow

---

## 📊 Phase 5: Monitoring & Observability

### Step 5.1: View Logs

```bash
# Backend logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=consultantos-api" \
  --limit 50 \
  --format json

# Frontend logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=consultantos-frontend" \
  --limit 50 \
  --format json
```

### Step 5.2: Set Up Monitoring Dashboards

```bash
# View metrics in Cloud Console
# Go to: https://console.cloud.google.com/monitoring

# Or use gcloud
gcloud monitoring dashboards list
```

### Step 5.3: Set Up Alerts (Optional)

```bash
# Create alert policy for high error rate
gcloud alpha monitoring policies create \
  --notification-channels=[YOUR_CHANNEL_ID] \
  --display-name="ConsultantOS High Error Rate" \
  --condition-display-name="Error Rate > 5%" \
  --condition-threshold-value=0.05 \
  --condition-threshold-duration=300s
```

---

## 🔒 Phase 6: Security Hardening

### Step 6.1: Enable Authentication (Optional)

```bash
# Require authentication for backend (if needed)
gcloud run services update consultantos-api \
  --no-allow-unauthenticated \
  --region $REGION

# Grant access to specific service accounts
gcloud run services add-iam-policy-binding consultantos-api \
  --member="serviceAccount:consultantos-frontend-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.invoker" \
  --region $REGION
```

### Step 6.2: Set Up Custom Domain (Optional)

```bash
# Map custom domain to Cloud Run service
gcloud run domain-mappings create \
  --service consultantos-frontend \
  --domain your-domain.com \
  --region $REGION

# Follow DNS instructions provided
```

### Step 6.3: Enable Rate Limiting

Rate limiting is already configured in the backend. Verify settings:

```python
# In consultantos/api/main.py
RATE_LIMIT_PER_HOUR = int(os.getenv("RATE_LIMIT_PER_HOUR", "10"))
```

---

## 💰 Phase 7: Cost Optimization

### Step 7.1: Optimize Resource Allocation

```bash
# Adjust based on actual usage
# Start with minimums, scale up as needed

# Backend (if high traffic)
gcloud run services update consultantos-api \
  --memory 2Gi \
  --cpu 2 \
  --min-instances 0 \
  --max-instances 20 \
  --region $REGION

# Frontend (if high traffic)
gcloud run services update consultantos-frontend \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --region $REGION
```

### Step 7.2: Set Budget Alerts

```bash
# Create budget alert
gcloud billing budgets create \
  --billing-account=YOUR_BILLING_ACCOUNT \
  --display-name="ConsultantOS Budget" \
  --budget-amount=100USD \
  --threshold-rule=percent=50 \
  --threshold-rule=percent=90 \
  --threshold-rule=percent=100
```

### Estimated Monthly Costs

| Service | Configuration | Estimated Cost |
|---------|--------------|----------------|
| Cloud Run (Backend) | 2Gi, 2 CPU, 0-10 instances | $20-50 |
| Cloud Run (Frontend) | 512Mi, 1 CPU, 0-10 instances | $5-15 |
| Firestore | Native mode, reads/writes | $5-20 |
| Cloud Storage | Reports storage | $1-5 |
| Secret Manager | API keys | $0.06/key/month |
| Gemini API | Token-based pricing (varies by model/usage) | $10-100 |
| Tavily API | Search queries (varies by volume) | $5-50 |
| Cloud Build | CI/CD minutes | $5-20 |
| Network Egress | Data transfer out of GCP | $5-30 |
| Cloud Logging/Monitoring | Ingestion and retention | $5-25 |
| **Total** | | **$65-315/month** |

**Note**: Cost estimates assume moderate usage (100-1000 analyses/month). Gemini API costs vary significantly based on model choice (Gemini Pro vs Ultra), token volume, and request frequency. Tavily costs scale with search query volume. Network egress depends on report size and download frequency. Adjust estimates based on your expected usage patterns.

---

## 🚀 Phase 8: CI/CD Setup (Optional)

### Step 8.1: GitHub Actions Workflow

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Cloud Run

on:
  push:
    branches: [master]
    paths:
      - 'consultantos/**'
      - 'frontend/**'
      - 'Dockerfile*'
      - 'cloudbuild*.yaml'

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - uses: google-github-actions/setup-gcloud@v1
        with:
          service_account_key: ${{ secrets.GCP_SA_KEY }}
          project_id: ${{ secrets.GCP_PROJECT_ID }}
      
      - name: Deploy Backend
        run: |
          gcloud builds submit --config=cloudbuild.api.yaml \
            --project=${{ secrets.GCP_PROJECT_ID }}
  
  deploy-frontend:
    runs-on: ubuntu-latest
    needs: deploy-backend
    steps:
      - uses: actions/checkout@v3
      
      - uses: google-github-actions/setup-gcloud@v1
        with:
          service_account_key: ${{ secrets.GCP_SA_KEY }}
          project_id: ${{ secrets.GCP_PROJECT_ID }}
      
      - name: Get Backend URL
        id: backend
        run: |
          URL=$(gcloud run services describe consultantos-api \
            --region us-central1 \
            --format 'value(status.url)' \
            --project=${{ secrets.GCP_PROJECT_ID }})
          echo "url=$URL" >> $GITHUB_OUTPUT
      
      - name: Deploy Frontend
        run: |
          gcloud builds submit --config=cloudbuild.frontend.yaml \
            --substitutions=_API_URL=${{ steps.backend.outputs.url }},_REGION=us-central1 \
            --project=${{ secrets.GCP_PROJECT_ID }}
```

### Step 8.2: Set Up GitHub Secrets

1. Go to GitHub repository → Settings → Secrets
2. Add:
   - `GCP_SA_KEY` - Service account JSON key
   - `GCP_PROJECT_ID` - Your GCP project ID

---

## 📝 Phase 9: Documentation for Submission

### Step 9.1: Update README

Ensure README includes:
- ✅ Live deployment URLs
- ✅ Architecture diagram
- ✅ Deployment instructions
- ✅ API documentation link

### Step 9.2: Create Architecture Diagram

Create `docs/ARCHITECTURE_DIAGRAM.md` with:
- Cloud Run services (frontend + backend)
- Firestore database
- Cloud Storage
- Secret Manager
- External APIs (Gemini, Tavily, etc.)

### Step 9.3: Record Demo Video

**Requirements:**
- ≤3 minutes
- Show both frontend and backend working
- Demonstrate key features
- Upload to YouTube/Vimeo (public)

**Suggested Script:**
1. Show frontend dashboard (0:00-0:30)
2. Create analysis (0:30-1:00)
3. Show results (1:00-1:30)
4. Show API documentation (1:30-2:00)
5. Show Cloud Run deployment (2:00-2:30)
6. Summary (2:30-3:00)

---

## 🐛 Troubleshooting

### Issue: Build Fails

**Solution:**
```bash
# Check build logs
gcloud builds list --limit=5
gcloud builds log BUILD_ID

# Common fixes:
# - Check Dockerfile syntax
# - Verify dependencies in requirements.txt
# - Ensure build context is correct
```

### Issue: Service Won't Start

**Solution:**
```bash
# Check logs
gcloud run services logs read consultantos-api --region $REGION

# Common issues:
# - Missing environment variables
# - Secret access denied
# - Port configuration
```

### Issue: CORS Errors

**Solution:**
```bash
# Verify CORS configuration in backend
# Ensure frontend URL is in allow_origins list
# Check browser console for exact error
```

### Issue: High Costs

**Solution:**
```bash
# Reduce min-instances to 0
gcloud run services update consultantos-api \
  --min-instances 0 \
  --region $REGION

# Set max-instances limit
gcloud run services update consultantos-api \
  --max-instances 5 \
  --region $REGION
```

---

## ✅ Final Checklist for Hackathon Submission

### Required Items:
- [ ] ✅ Backend deployed to Cloud Run
- [ ] ✅ Frontend deployed to Cloud Run
- [ ] ✅ Public GitHub repository
- [ ] ✅ Demo video (≤3 minutes, public)
- [ ] ✅ Text description (English)
- [ ] ✅ Architecture diagram
- [ ] ✅ Hosted project URL (both services)

### Bonus Points:
- [ ] ✅ Using Google AI models (Gemini) - Already done
- [ ] ✅ Multiple Cloud Run services - Frontend + Backend
- [ ] ✅ Published blog/video about project
- [ ] ✅ Social media post with #CloudRunHackathon

### Documentation:
- [ ] ✅ README with deployment instructions
- [ ] ✅ API documentation accessible
- [ ] ✅ Architecture diagram included
- [ ] ✅ Code comments and documentation

---

## 🎯 Quick Deploy Commands (Summary)

```bash
# 1. Set variables
export PROJECT_ID="consultantos-hackathon"
export REGION="us-central1"

# 2. Enable APIs
gcloud services enable run.googleapis.com cloudbuild.googleapis.com

# 3. Store secrets
echo -n "GEMINI_KEY" | gcloud secrets create gemini-api-key --data-file=-
echo -n "TAVILY_KEY" | gcloud secrets create tavily-api-key --data-file=-

# 4. Deploy backend
gcloud run deploy consultantos-api \
  --source . \
  --region $REGION \
  --set-secrets "GEMINI_API_KEY=gemini-api-key:latest,TAVILY_API_KEY=tavily-api-key:latest"

# 5. Get backend URL
export API_URL=$(gcloud run services describe consultantos-api --region $REGION --format 'value(status.url)')

# 6. Deploy frontend
gcloud run deploy consultantos-frontend \
  --source frontend \
  --region $REGION \
  --set-env-vars "NEXT_PUBLIC_API_URL=$API_URL"

# 7. Get frontend URL
export FRONTEND_URL=$(gcloud run services describe consultantos-frontend --region $REGION --format 'value(status.url)')

echo "✅ Deployment complete!"
echo "Frontend: $FRONTEND_URL"
echo "Backend: $API_URL"
```

---

## 📞 Support & Resources

- **Cloud Run Docs**: https://cloud.google.com/run/docs
- **Cloud Build Docs**: https://cloud.google.com/build/docs
- **Hackathon Rules**: `docs/HACKATHON_RULES.md`
- **Frontend Deployment**: `frontend/DEPLOYMENT.md`
- **Observability Guide**: `docs/OBSERVABILITY_CLOUD_DEPLOYMENT.md`

---

## 🎉 Success Criteria

Your deployment is successful when:
1. ✅ Both services are accessible via public URLs
2. ✅ Frontend can communicate with backend
3. ✅ Health checks return 200 OK
4. ✅ Analysis requests complete successfully
5. ✅ No errors in Cloud Run logs
6. ✅ Services auto-scale based on traffic

**Good luck with your hackathon submission! 🚀**

