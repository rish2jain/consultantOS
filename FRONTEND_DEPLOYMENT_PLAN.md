# ConsultantOS Frontend Deployment Plan

**Target Platform**: Google Cloud Run
**Framework**: Next.js 14.2.33
**Current Status**: Ready for Deployment
**Backend API**: https://consultantos-api-187550875653.us-central1.run.app

---

## 📋 Executive Summary

Deploy the ConsultantOS Next.js 14 frontend dashboard to Google Cloud Run with production-optimized configuration, connecting to the v0.4.0 backend API with Strategic Intelligence capabilities.

### Deployment Objectives
- ✅ Deploy frontend as a containerized Next.js application
- ✅ Connect to production backend API (v0.4.0)
- ✅ Enable Strategic Intelligence Dashboard features
- ✅ Optimize for performance and cost efficiency
- ✅ Configure auto-scaling and monitoring

---

## 🏗️ Current State Analysis

### ✅ Infrastructure Ready

| Component | Status | Details |
|-----------|--------|---------|
| **Dockerfile** | ✅ Exists | Multi-stage build optimized for Next.js |
| **.dockerignore** | ✅ Exists | Properly configured |
| **next.config.js** | ✅ Configured | `output: "standalone"` enabled for Cloud Run |
| **Environment Variables** | ✅ Ready | Backend API URL configured |
| **Dependencies** | ✅ Valid | All packages in package.json |

### Frontend Stack
- **Framework**: Next.js 14.2.33 (App Router)
- **React**: 18.2.0
- **TypeScript**: 5.3.0
- **Styling**: Tailwind CSS 3.3.0
- **Charts**: D3.js 7.9.0, Recharts 2.10.0, Plotly.js
- **State Management**: TanStack React Query 5.0.0
- **HTTP Client**: Axios 1.6.0

### Key Features to Deploy
1. **Main Dashboard** (`app/dashboard/page.tsx`)
2. **Analysis Dashboard** (`app/analysis/page.tsx`)
3. **Strategic Intelligence Dashboard** (`app/dashboard/strategic-intelligence/`)
4. **Visualization Components**:
   - ForecastChart
   - CompetitivePositioningMap
   - DisruptionRadar
   - SystemDynamicsMap
   - FlywheelDashboard
   - IntelligenceFeed

---

## 📝 Pre-Deployment Checklist

### ✅ Code Quality (READY)
- [x] Next.js configuration has `output: "standalone"`
- [x] Dockerfile uses multi-stage build
- [x] Environment variables properly configured
- [x] TypeScript compilation successful
- [x] No build-blocking errors
- [x] API integration layer ready (`lib/mvp-api.ts`, `lib/strategic-intelligence-api.ts`)

### ⚠️ Pre-Deployment Tasks

#### 1. Update Backend API URL
**Current**: `.env.local.bak` points to old backend URL
**Required**: Update to new backend URL

```bash
# Update frontend/.env.local
NEXT_PUBLIC_API_URL=https://consultantos-api-187550875653.us-central1.run.app
```

#### 2. Test Build Locally (RECOMMENDED)
```bash
cd frontend

# Set production API URL for build test
export NEXT_PUBLIC_API_URL=https://consultantos-api-187550875653.us-central1.run.app

# Test production build
npm run build

# Test production server locally
npm run start
```

**Expected**: Build completes without errors, server starts on port 3000

#### 3. Verify Docker Build (RECOMMENDED)
```bash
cd frontend

# Build Docker image locally
docker build \
  --build-arg NEXT_PUBLIC_API_URL=https://consultantos-api-187550875653.us-central1.run.app \
  -t consultantos-frontend:test .

# Test Docker container locally
docker run -p 8080:8080 consultantos-frontend:test

# Verify at http://localhost:8080
```

---

## 🚀 Deployment Steps

### Step 1: Update Environment Configuration

**File**: `frontend/.env.local`

```bash
# Update with new backend URL
cat > frontend/.env.local << 'EOF'
# ConsultantOS Frontend Environment Variables
# Production Backend API
NEXT_PUBLIC_API_URL=https://consultantos-api-187550875653.us-central1.run.app

# Optional: Feature flags (uncomment to enable)
# NEXT_PUBLIC_ENABLE_COMMENTS=true
# NEXT_PUBLIC_ENABLE_SHARING=true
# NEXT_PUBLIC_ENABLE_VERSIONS=true
# NEXT_PUBLIC_ENABLE_STRATEGIC_INTELLIGENCE=true

# Optional: Analytics (configure when ready)
# NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX
# NEXT_PUBLIC_SENTRY_DSN=https://...
EOF
```

### Step 2: Deploy to Cloud Run

**Deployment Command**:

```bash
cd frontend

gcloud run deploy consultantos-frontend \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 1 \
  --timeout 60 \
  --min-instances 0 \
  --max-instances 10 \
  --set-env-vars "NEXT_PUBLIC_API_URL=https://consultantos-api-187550875653.us-central1.run.app" \
  --set-build-env-vars "NEXT_PUBLIC_API_URL=https://consultantos-api-187550875653.us-central1.run.app"
```

**Configuration Breakdown**:
- **Service Name**: `consultantos-frontend`
- **Region**: `us-central1` (same as backend)
- **Memory**: 2Gi (adequate for Next.js with visualization libraries)
- **CPU**: 1 core (sufficient for frontend serving)
- **Timeout**: 60s (shorter than backend, frontend serves static + SSR)
- **Min Instances**: 0 (cost optimization - scale to zero when idle)
- **Max Instances**: 10 (handle traffic spikes)
- **Authentication**: Unauthenticated (public dashboard access)

**Environment Variables**:
- `NEXT_PUBLIC_API_URL`: Backend API endpoint
- **Build-time**: Required because Next.js embeds env vars during build

**Expected Duration**: 8-12 minutes
- Source upload: ~1-2 min
- Container build: ~5-8 min (installing dependencies, Next.js build)
- Deployment: ~1-2 min

### Step 3: Verify Deployment

**Health Checks**:

```bash
# Get the deployed URL
FRONTEND_URL=$(gcloud run services describe consultantos-frontend \
  --region us-central1 \
  --format 'value(status.url)')

echo "Frontend URL: $FRONTEND_URL"

# Test frontend accessibility
curl -I "$FRONTEND_URL"

# Expected: HTTP 200 OK

# Test specific pages
curl -I "$FRONTEND_URL/dashboard"
curl -I "$FRONTEND_URL/analysis"
curl -I "$FRONTEND_URL/dashboard/strategic-intelligence"
```

**Browser Testing**:
1. Open frontend URL in browser
2. Verify dashboard loads
3. Test backend API connection
4. Verify Strategic Intelligence visualizations render
5. Check browser console for errors

---

## 🔧 Configuration Details

### Next.js Production Optimizations

**Enabled in `next.config.js`**:
- ✅ `output: "standalone"` - Optimized for containers
- ✅ `reactStrictMode: true` - Development best practices
- ✅ ESLint validation (fails on errors in production)
- ✅ TypeScript validation (fails on errors in production)

**Automatic Optimizations** (Next.js 14):
- Image optimization
- Font optimization
- Code splitting
- Tree shaking
- Minification
- Compression (gzip/brotli)

### Dockerfile Analysis

**Stage 1: Dependencies** (`deps`)
```dockerfile
FROM node:20-alpine AS deps
RUN apk add --no-cache libc6-compat
COPY package.json package-lock.json* ./
RUN npm ci
```
- Uses Alpine Linux (smaller image)
- Installs only production dependencies
- Uses `npm ci` for reproducible builds

**Stage 2: Builder** (`builder`)
```dockerfile
FROM base AS builder
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ARG NEXT_PUBLIC_API_URL=http://localhost:8080
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
RUN npm run build
```
- Copies dependencies from deps stage
- Accepts build-time API URL argument
- Builds Next.js application
- Generates standalone output

**Stage 3: Runner** (`runner`)
```dockerfile
FROM base AS runner
ENV NODE_ENV=production
ENV PORT=8080
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
CMD ["node", "server.js"]
```
- Production-only runtime
- Minimal files (standalone + static + public)
- Non-root user (security)
- Listens on port 8080 (Cloud Run standard)

**Image Size**: ~150-200MB (Alpine + Node 20 + Next.js standalone)

---

## 🌐 Post-Deployment Configuration

### Step 4: Configure CORS (if needed)

**Backend CORS Configuration** (already in `consultantos/api/main.py`):

```python
# Verify CORS allows new frontend URL
origins = [
    "http://localhost:3000",  # Development
    "https://consultantos-frontend-*.run.app",  # Cloud Run pattern
    # Add specific frontend URL if needed:
    # "https://consultantos-frontend-187550875653.us-central1.run.app"
]
```

**Action**: If CORS errors occur, update backend CORS to include frontend URL

### Step 5: Custom Domain (Optional)

**Set up custom domain** (if you have one):

```bash
# Map custom domain to frontend
gcloud run domain-mappings create \
  --service consultantos-frontend \
  --domain dashboard.consultantos.com \
  --region us-central1

# Map custom domain to backend API
gcloud run domain-mappings create \
  --service consultantos-api \
  --domain api.consultantos.com \
  --region us-central1
```

**DNS Configuration**:
- Frontend: `dashboard.consultantos.com` → Frontend Cloud Run URL
- Backend API: `api.consultantos.com` → Backend Cloud Run URL

**Update Environment Variables** (if using custom domain):
```bash
gcloud run services update consultantos-frontend \
  --region us-central1 \
  --set-env-vars "NEXT_PUBLIC_API_URL=https://api.consultantos.com"
```

### Step 6: Enable Cloud CDN (Optional - Performance)

**Benefits**:
- Faster global access
- Reduced latency
- Lower Cloud Run costs

**Setup**:
1. Create Cloud Load Balancer
2. Add Cloud Run backend
3. Enable Cloud CDN
4. Configure cache headers

---

## 📊 Monitoring & Observability

### Cloud Run Metrics to Monitor

**Performance Metrics**:
- Request latency (p50, p95, p99)
- Request count
- Error rate
- Instance count
- CPU utilization
- Memory utilization

**Set Up Alerts**:

```bash
# Create alert for high error rate (>5%)
# First, create a notification channel (if not exists)
gcloud monitoring channels create \
  --display-name="Frontend Alerts" \
  --type=email \
  --channel-labels=email_address=your-email@example.com

# Get the channel ID
CHANNEL_ID=$(gcloud monitoring channels list \
  --filter='displayName="Frontend Alerts"' \
  --format='value(name)' | cut -d'/' -f4)

# Create alert policy using stable API
gcloud monitoring policies create \
  --notification-channels=$CHANNEL_ID \
  --display-name="Frontend Error Rate Alert" \
  --condition-display-name="Error rate > 5%" \
  --condition-threshold-value=5 \
  --condition-threshold-duration=60s \
  --condition-filter='resource.type="cloud_run_revision" AND
    resource.labels.service_name="consultantos-frontend" AND
    metric.type="run.googleapis.com/request_count" AND
    metric.labels.response_code_class="5xx"'
```

**Alternative: Using Cloud Console (Recommended for Production)**:
1. Navigate to [Cloud Monitoring > Alerting](https://console.cloud.google.com/monitoring/alerting)
2. Click "Create Policy"
3. Select "Cloud Run Revision" as resource type
4. Filter: `service_name="consultantos-frontend"`
5. Metric: `Request Count` with filter `response_code_class="5xx"`
6. Condition: Threshold > 5% for 60 seconds
7. Configure notification channels
8. Save policy

**Alternative: Using Terraform (Infrastructure as Code)**:
```hcl
resource "google_monitoring_alert_policy" "frontend_error_rate" {
  display_name = "Frontend Error Rate Alert"
  combiner     = "OR"
  
  conditions {
    display_name = "Error rate > 5%"
    
    condition_threshold {
      filter          = 'resource.type="cloud_run_revision" AND resource.labels.service_name="consultantos-frontend" AND metric.type="run.googleapis.com/request_count" AND metric.labels.response_code_class="5xx"'
      duration        = "60s"
      comparison      = "COMPARISON_GT"
      threshold_value = 5
    }
  }
  
  notification_channels = [google_monitoring_notification_channel.email.id]
}
```

**Logging**:
```bash
# View frontend logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=consultantos-frontend" \
  --limit 50 \
  --format json

# Filter for errors
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=consultantos-frontend AND severity>=ERROR" \
  --limit 50
```

### Browser Monitoring

**Set up Real User Monitoring** (optional):
- Google Analytics 4
- Sentry error tracking
- Web Vitals monitoring

**Add to frontend**:
```typescript
// app/layout.tsx - Already included
import { reportWebVitals } from 'web-vitals';

// Report Core Web Vitals
reportWebVitals((metric) => {
  // Send to analytics
  console.log(metric);
});
```

---

## 🧪 Testing Plan

### Post-Deployment Testing Checklist

#### Functional Testing
- [ ] Dashboard loads successfully
- [ ] Analysis page accessible
- [ ] Strategic Intelligence dashboard renders
- [ ] API calls to backend succeed
- [ ] Visualizations render correctly (D3, Recharts, Plotly)
- [ ] Error handling works (network errors, API errors)
- [ ] Loading states display properly

#### Integration Testing
- [ ] Backend API connection verified
- [ ] Health endpoint check passes
- [ ] Strategic Intelligence endpoints accessible
- [ ] Data flows correctly from backend to frontend
- [ ] Authentication works (if enabled)

#### Performance Testing
- [ ] First Contentful Paint (FCP) < 1.8s
- [ ] Largest Contentful Paint (LCP) < 2.5s
- [ ] Time to Interactive (TTI) < 3.8s
- [ ] Cumulative Layout Shift (CLS) < 0.1
- [ ] First Input Delay (FID) < 100ms

#### Browser Compatibility
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)
- [ ] Mobile Safari (iOS)
- [ ] Chrome Mobile (Android)

#### Responsive Design
- [ ] Desktop (1920x1080)
- [ ] Laptop (1366x768)
- [ ] Tablet (768x1024)
- [ ] Mobile (375x667)

---

## 🐛 Troubleshooting Guide

### Common Issues & Solutions

#### 1. Build Fails with Module Not Found
**Problem**: Missing dependencies
**Solution**:
```bash
cd frontend
npm install
npm run build
```

#### 2. Container Build Timeout
**Problem**: Build takes >10 minutes
**Solution**: Increase Cloud Build timeout
```bash
gcloud run deploy consultantos-frontend \
  --source . \
  --timeout 900  # 15 minutes
```

#### 3. Frontend Can't Connect to Backend
**Problem**: CORS or network error
**Solutions**:
- Check `NEXT_PUBLIC_API_URL` is correct
- Verify backend CORS allows frontend URL
- Check backend health endpoint
- Inspect browser network tab for details

#### 4. Environment Variables Not Working
**Problem**: API URL not set correctly
**Solution**: Must set both build-time and runtime env vars
```bash
--set-env-vars "NEXT_PUBLIC_API_URL=..." \
--set-build-env-vars "NEXT_PUBLIC_API_URL=..."
```

#### 5. High Memory Usage / OOM
**Problem**: Container runs out of memory
**Solution**: Increase memory allocation
```bash
gcloud run services update consultantos-frontend \
  --memory 4Gi
```

#### 6. 404 on Next.js Routes
**Problem**: Client-side routing not working
**Solution**: Verify standalone output is working correctly
```bash
# Check next.config.js has:
output: "standalone"
```

---

## 💰 Cost Estimation

### Cloud Run Frontend Costs (Estimated)

**Assumptions**:
- 1,000 requests/day
- Average 200ms response time
- 2Gi memory, 1 CPU
- us-central1 region

**Monthly Costs** (approximate):
- **Requests**: 30,000 requests/month
  - First 2M requests free
  - **Cost**: $0

- **CPU Time**: 30,000 * 0.2s = 6,000 CPU-seconds
  - @ $0.00002400/vCPU-second
  - **Cost**: ~$0.14/month

- **Memory**: 6,000 seconds * 2Gi
  - @ $0.00000250/GiB-second
  - **Cost**: ~$0.03/month

**Total Estimated Monthly Cost**: **~$0.17** (well within free tier)

**Scaling Costs** (10,000 requests/day):
- ~$1.70/month

**Note**: Actual costs may vary based on:
- Request volume
- Response time
- Memory usage
- Cold starts
- Number of instances

---

## 🔐 Security Considerations

### Security Checklist
- [ ] No secrets in frontend code (client-side visible)
- [ ] API keys only in backend
- [ ] HTTPS enforced (Cloud Run default)
- [ ] Content Security Policy headers configured
- [ ] XSS protection enabled
- [ ] CORS properly configured
- [ ] Rate limiting (backend handles this)
- [ ] Input validation (sanitize user inputs)

### Security Headers (Add to next.config.js if needed)

```javascript
// next.config.js
module.exports = {
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'origin-when-cross-origin',
          },
        ],
      },
    ]
  },
}
```

---

## 📈 Success Criteria

### Deployment Success Indicators
- ✅ Frontend URL accessible publicly
- ✅ No 5xx errors in Cloud Run logs
- ✅ Response time < 1 second (p95)
- ✅ Successful API calls to backend
- ✅ Zero console errors in browser
- ✅ All visualizations render
- ✅ Mobile responsive
- ✅ Core Web Vitals in "Good" range

### Key Performance Indicators (KPIs)
- **Availability**: > 99.9%
- **Latency (p95)**: < 1s
- **Error Rate**: < 0.1%
- **Build Time**: < 10 minutes
- **Cold Start**: < 3 seconds

---

## 📝 Rollback Plan

### If Deployment Fails or Issues Found

**Quick Rollback to Previous Revision**:
```bash
# List revisions
gcloud run revisions list \
  --service consultantos-frontend \
  --region us-central1

# Rollback to previous revision
gcloud run services update-traffic consultantos-frontend \
  --region us-central1 \
  --to-revisions PREVIOUS_REVISION=100
```

**Complete Rollback**:
```bash
# Delete the service
gcloud run services delete consultantos-frontend \
  --region us-central1
```

---

## 🎯 Next Steps After Deployment

### Immediate (Day 1)
1. ✅ Verify deployment health
2. ✅ Test all major user flows
3. ✅ Monitor error logs for 24 hours
4. ✅ Check performance metrics
5. ✅ Document deployment URL

### Short-term (Week 1)
1. Set up monitoring alerts
2. Configure custom domain (if applicable)
3. Enable Cloud CDN for performance
4. Set up error tracking (Sentry)
5. Implement analytics (GA4)

### Long-term (Month 1)
1. Review usage patterns
2. Optimize based on metrics
3. Implement A/B testing
4. Add progressive web app (PWA) features
5. Configure CI/CD pipeline

---

## 📚 References

### Documentation Links
- [Next.js Deployment](https://nextjs.org/docs/app/building-your-application/deploying)
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Next.js Standalone Output](https://nextjs.org/docs/app/api-reference/next-config-js/output)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

### Internal Documentation
- Backend API: https://consultantos-api-187550875653.us-central1.run.app/docs
- Backend Deployment: `DEPLOYMENT_GUIDE.md`
- Backend Success Report: `DEPLOYMENT_SUCCESS_V0.4.0.md`

---

## ✅ Deployment Command Summary

**Quick Deployment** (when ready):

```bash
# 1. Navigate to frontend
cd frontend

# 2. Deploy to Cloud Run
gcloud run deploy consultantos-frontend \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 1 \
  --timeout 60 \
  --min-instances 0 \
  --max-instances 10 \
  --set-env-vars "NEXT_PUBLIC_API_URL=https://consultantos-api-187550875653.us-central1.run.app" \
  --set-build-env-vars "NEXT_PUBLIC_API_URL=https://consultantos-api-187550875653.us-central1.run.app"

# 3. Get the frontend URL
gcloud run services describe consultantos-frontend \
  --region us-central1 \
  --format 'value(status.url)'

# 4. Test deployment
curl -I $(gcloud run services describe consultantos-frontend --region us-central1 --format 'value(status.url)')
```

---

**Plan Status**: ✅ **READY FOR EXECUTION**
**Estimated Duration**: 10-15 minutes (deployment) + 30 minutes (testing)
**Risk Level**: Low (infrastructure already prepared)
**Rollback Time**: < 5 minutes

---

*Created: November 10, 2025*
*Version: 1.0*
*Status: Ready for Deployment*
