# Local Dashboard Testing Guide

**Date**: 2025-11-10
**Purpose**: Test dashboard locally before deploying to Cloud Run

## Current Setup

### ✅ Backend Status
- **Local Backend**: Running on `http://localhost:8080`
- **Production Backend**: `https://consultantos-api-bdndyf33xa-uc.a.run.app` (keep running)
- **Monitoring Endpoints**: ✅ Enabled in `main.py` (line 359)
- **Dashboard Endpoints**: ✅ Registered in `main.py` (line 373)

### ✅ Frontend Status
- **Local Frontend**: Should run on `http://localhost:3000`
- **API URL**: Defaults to `http://localhost:8080` (local backend)
- **Syntax Errors**: ✅ Fixed (Reports tab JSX structure)

## Quick Test Script

Run the automated test script:

```bash
# Set your API key (if you have one)
export API_KEY="your-api-key-here"

# Run the test script
./test_dashboard_local.sh
```

This will verify:
- ✅ Backend is running
- ✅ Monitoring endpoints are registered
- ✅ Dashboard endpoints are registered
- ✅ Swagger docs are accessible

## Testing Steps

### 1. Restart Local Backend (to pick up changes)

Since we enabled monitoring endpoints, restart the backend to ensure changes are loaded:

```bash
# If running with python main.py, stop it (Ctrl+C) and restart:
python main.py

# Or if running with uvicorn directly:
# Stop current process (Ctrl+C) then:
uvicorn consultantos.api.main:app --host 0.0.0.0 --port 8080 --reload
```

**Note**: With `--reload`, the server should auto-reload, but for router changes, a manual restart is safer.

### 2. Verify Local Backend is Running

```bash
# Check health
curl http://localhost:8080/health

# Should return: {"status":"healthy",...}
```

### 3. Verify Endpoints Are Available

```bash
# Check Swagger docs (should show dashboard and monitors endpoints)
open http://localhost:8080/docs

# Or check via curl:
curl -s http://localhost:8080/docs | grep -i "dashboard\|monitor" | head -5
```

### 4. Test Endpoints (requires API key)

First, get or create an API key:

```bash
# Option 1: Use existing API key from your auth system
# Option 2: Create one via API (if auth endpoints are working)
curl -X POST "http://localhost:8080/auth/api-keys" \
  -H "X-API-Key: existing-key" \
  -d '{"user_id": "test-user", "description": "Test key"}'

# Save the API key
export API_KEY="your-api-key-here"
```

Then test endpoints:

```bash
# Test monitoring endpoints
curl -H "X-API-Key: $API_KEY" \
  "http://localhost:8080/monitors/stats/dashboard"

# Test dashboard endpoints
curl -H "X-API-Key: $API_KEY" \
  "http://localhost:8080/dashboard/overview?alert_limit=10&report_limit=5"
```

### 2. Start Frontend (if not running)

```bash
cd frontend
npm run dev
```

Frontend will be available at: `http://localhost:3000`

### 3. Configure Frontend to Use Local Backend

The frontend automatically uses `http://localhost:8080` if `NEXT_PUBLIC_API_URL` is not set.

**Verify configuration**:
- Check `frontend/app/dashboard/page.tsx` line 142: `const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';`
- This means it will use local backend by default

**To explicitly use local backend** (optional):
```bash
cd frontend
echo "NEXT_PUBLIC_API_URL=http://localhost:8080" > .env.local
```

**To use production backend** (for comparison):
```bash
cd frontend
echo "NEXT_PUBLIC_API_URL=https://consultantos-api-bdndyf33xa-uc.a.run.app" > .env.local
```

### 4. Test Dashboard Locally

1. **Open browser**: Navigate to `http://localhost:3000/dashboard`
2. **Check browser console**: Look for any errors
3. **Test each tab**:
   - Overview tab
   - Analytics tab
   - Reports tab
   - Jobs tab

### 5. Test API Endpoints Directly

```bash
# Get your API key first (from auth system or create one)
export API_KEY="your-api-key-here"

# Test dashboard overview
curl -H "X-API-Key: $API_KEY" \
  "http://localhost:8080/dashboard/overview?alert_limit=10&report_limit=5"

# Test analytics
curl -H "X-API-Key: $API_KEY" \
  "http://localhost:8080/dashboard/analytics?days=30"

# Test reports
curl -H "X-API-Key: $API_KEY" \
  "http://localhost:8080/dashboard/reports?action=list&page=1&page_size=10"

# Test jobs
curl -H "X-API-Key: $API_KEY" \
  "http://localhost:8080/dashboard/jobs?action=list&status=pending,running&limit=20"

# Test monitoring endpoints
curl -H "X-API-Key: $API_KEY" \
  "http://localhost:8080/monitors"

curl -H "X-API-Key: $API_KEY" \
  "http://localhost:8080/monitors/stats/dashboard"
```

## Expected Results

### ✅ Success Indicators

1. **Dashboard loads** without syntax errors
2. **API calls succeed** (check Network tab in DevTools)
3. **No 404 errors** for `/dashboard/*` or `/monitors/*` endpoints
4. **Data displays** (even if empty, should show empty states)
5. **Tabs switch** correctly
6. **Error handling** works (shows error messages gracefully)

### ⚠️ Common Issues

1. **404 errors**: 
   - Check that monitoring endpoints are enabled in `main.py`
   - Restart backend server after changes

2. **CORS errors**:
   - Check `main.py` CORS configuration allows `http://localhost:3000`

3. **Authentication errors**:
   - Ensure API key is set in frontend
   - Check that `getApiKey()` returns a valid key

4. **Empty data**:
   - This is normal if no monitors/reports exist
   - Create test data using API endpoints

## Creating Test Data

### Create a Monitor

```bash
curl -X POST "http://localhost:8080/monitors" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "company": "Tesla",
    "industry": "Electric Vehicles",
    "config": {
      "frequency": "daily",
      "frameworks": ["porter", "swot"],
      "alert_threshold": 0.7,
      "notification_channels": ["dashboard"]
    }
  }'
```

### Trigger a Check

```bash
# Get monitor ID from previous response
curl -X POST "http://localhost:8080/monitors/{monitor_id}/check" \
  -H "X-API-Key: $API_KEY"
```

## Verification Checklist

Before deploying to Cloud Run, verify:

- [ ] Local backend starts without errors
- [ ] Monitoring endpoints are accessible (`/monitors/*`)
- [ ] Dashboard endpoints are accessible (`/dashboard/*`)
- [ ] Frontend loads dashboard without errors
- [ ] All tabs work correctly
- [ ] API calls succeed (check Network tab)
- [ ] Error handling works (test with invalid API key)
- [ ] Empty states display correctly
- [ ] Auto-refresh works (wait 30 seconds)

## Next Steps After Local Testing

Once local testing is successful:

1. **Commit changes**:
   ```bash
   git add consultantos/api/main.py
   git commit -m "Enable monitoring endpoints for dashboard"
   ```

2. **Deploy to Cloud Run**:
   ```bash
   gcloud run deploy consultantos-api \
     --source . \
     --region us-central1 \
     --allow-unauthenticated
   ```

3. **Verify production deployment**:
   ```bash
   curl https://consultantos-api-bdndyf33xa-uc.a.run.app/dashboard/overview \
     -H "X-API-Key: YOUR_KEY"
   ```

4. **Update frontend to use production** (optional):
   ```bash
   cd frontend
   echo "NEXT_PUBLIC_API_URL=https://consultantos-api-bdndyf33xa-uc.a.run.app" > .env.local
   ```

---

**Last Updated**: 2025-11-10
**Status**: Ready for local testing

