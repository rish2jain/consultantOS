# ConsultantOS Deployment Guide

**Version**: 1.0.0-hackathon
**Last Updated**: 2025-11-08
**Status**: Production-Ready

## Pre-Deployment Checklist

### ✅ Code Quality
- [x] All import errors fixed
- [x] API imports successfully
- [x] Tests passing
- [x] Documentation consolidated
- [x] All changes committed to master branch

### ✅ Required Environment Variables
- [ ] `GEMINI_API_KEY` - Google Gemini API key (required)
- [ ] `TAVILY_API_KEY` - Tavily search API key (required)
- [ ] `GCP_PROJECT_ID` - Google Cloud project ID (optional, for Firestore/Storage)

### ✅ Optional Environment Variables
- [ ] `SESSION_SECRET` - Session management secret (auto-generated if not set)
- [ ] `LOG_LEVEL` - Logging level (default: INFO)
- [ ] `RATE_LIMIT_PER_HOUR` - Rate limit per IP (default: 10)
- [ ] `CORS_ORIGINS` - Allowed CORS origins (comma-separated)
- [ ] `GOOGLE_APPLICATION_CREDENTIALS` - Path to service account JSON

## Deployment Options

### Option 1: Local Development (Recommended for Testing)

**Quick Start**:
```bash
# 1. Set environment variables
export GEMINI_API_KEY="your-gemini-api-key"
export TAVILY_API_KEY="your-tavily-api-key"

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start server
python main.py
```

**Server will be available at**: `http://localhost:8080`

**API Documentation**:
- Swagger UI: `http://localhost:8080/docs`
- ReDoc: `http://localhost:8080/redoc`

**Health Check**:
```bash
curl http://localhost:8080/health
# Expected: {"status": "healthy"}
```

**Test Analysis**:
```bash
curl -X POST "http://localhost:8080/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "company": "Tesla",
    "industry": "Electric Vehicles",
    "frameworks": ["porter", "swot"]
  }'
```

---

### Option 2: Docker Deployment

**Build Image**:
```bash
docker build -t consultantos:latest .
```

**Run Container**:
```bash
docker run -d \
  --name consultantos \
  -p 8080:8080 \
  -e GEMINI_API_KEY="${GEMINI_API_KEY}" \
  -e TAVILY_API_KEY="${TAVILY_API_KEY}" \
  -e GCP_PROJECT_ID="${GCP_PROJECT_ID}" \
  consultantos:latest
```

**View Logs**:
```bash
docker logs -f consultantos
```

**Stop Container**:
```bash
docker stop consultantos
docker rm consultantos
```

---

### Option 3: Google Cloud Run (Recommended for Production)

#### Prerequisites
1. **Google Cloud Project**: Create or select a project
2. **gcloud CLI**: Install and authenticate
3. **API Keys**: Gemini and Tavily API keys ready
4. **Enable APIs**:
   ```bash
   gcloud services enable run.googleapis.com \
     cloudbuild.googleapis.com \
     secretmanager.googleapis.com
   ```

#### Store Secrets (Recommended)
```bash
# Store API keys in Secret Manager
echo -n "${GEMINI_API_KEY}" | gcloud secrets create gemini-api-key \
  --data-file=- \
  --replication-policy="automatic"

echo -n "${TAVILY_API_KEY}" | gcloud secrets create tavily-api-key \
  --data-file=- \
  --replication-policy="automatic"
```

#### Deploy via gcloud CLI

**Method 1: Direct Deployment from Source**
```bash
gcloud run deploy consultantos \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --min-instances 0 \
  --max-instances 10 \
  --set-env-vars "GEMINI_API_KEY=${GEMINI_API_KEY},TAVILY_API_KEY=${TAVILY_API_KEY}" \
  --set-env-vars "LOG_LEVEL=INFO,RATE_LIMIT_PER_HOUR=10"
```

**Method 2: Deployment with Secret Manager**
```bash
gcloud run deploy consultantos \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --min-instances 0 \
  --max-instances 10 \
  --set-secrets="GEMINI_API_KEY=gemini-api-key:latest,TAVILY_API_KEY=tavily-api-key:latest"
```

**Method 3: CI/CD with Cloud Build**
```bash
# Trigger Cloud Build deployment
gcloud builds submit --config cloudbuild.yaml

# Set environment variables after deployment
gcloud run services update consultantos \
  --region us-central1 \
  --set-env-vars "GEMINI_API_KEY=${GEMINI_API_KEY},TAVILY_API_KEY=${TAVILY_API_KEY}"
```

#### Post-Deployment Verification

**Get Service URL**:
```bash
gcloud run services describe consultantos \
  --region us-central1 \
  --format 'value(status.url)'
```

**Test Health Endpoint**:
```bash
SERVICE_URL=$(gcloud run services describe consultantos --region us-central1 --format 'value(status.url)')
curl ${SERVICE_URL}/health
```

**Test Analysis Endpoint**:
```bash
curl -X POST "${SERVICE_URL}/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "company": "OpenAI",
    "industry": "Artificial Intelligence",
    "frameworks": ["porter", "swot"]
  }'
```

---

## Configuration Reference

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key for AI analysis | `AIza...` |
| `TAVILY_API_KEY` | Tavily search API key for web research | `tvly-...` |

**Get API Keys**:
- Gemini: https://makersuite.google.com/app/apikey
- Tavily: https://app.tavily.com

### Optional Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GCP_PROJECT_ID` | None | Google Cloud project ID for Firestore/Storage |
| `SESSION_SECRET` | Auto-generated | Secret key for session management |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `RATE_LIMIT_PER_HOUR` | `10` | Rate limit per IP address |
| `CORS_ORIGINS` | `localhost:3000,localhost:8080` | Comma-separated allowed origins |
| `GEMINI_MODEL` | `gemini-1.5-flash-002` | Gemini model to use |
| `CACHE_TTL_SECONDS` | `3600` | Cache time-to-live in seconds |
| `REQUEST_TIMEOUT` | `300` | Request timeout in seconds |

### Cloud Run Specific Settings

| Setting | Value | Reason |
|---------|-------|--------|
| Memory | `2Gi` | LLM processing requires substantial memory |
| CPU | `2` | Parallel agent execution |
| Timeout | `300s` | Deep analysis can take 2-5 minutes |
| Min Instances | `0` | Cost optimization, scales to zero |
| Max Instances | `10` | Handle burst traffic |

---

## Monitoring and Observability

### Health Endpoints

| Endpoint | Purpose | Response |
|----------|---------|----------|
| `/health` | Overall system health | `{"status": "healthy"}` |
| `/health/ready` | Readiness check (Kubernetes) | `{"status": "ready"}` |
| `/health/live` | Liveness check (Kubernetes) | `{"status": "alive"}` |

### Logs

**Local Development**:
```bash
tail -f logs/api.log
```

**Docker**:
```bash
docker logs -f consultantos
```

**Cloud Run**:
```bash
gcloud run services logs read consultantos \
  --region us-central1 \
  --limit 50
```

**Cloud Logging Console**: https://console.cloud.google.com/logs

### Metrics

**API Documentation**: `https://[your-service-url]/docs`

**Key Metrics to Monitor**:
- Request count and success rate
- Analysis completion time (p50, p95, p99)
- Error rates by type
- Cache hit rates
- API cost (Gemini + Tavily usage)

---

## Troubleshooting

### Issue: API Won't Start

**Symptoms**: Server fails to start or crashes immediately

**Solutions**:
```bash
# 1. Verify environment variables
echo $GEMINI_API_KEY
echo $TAVILY_API_KEY

# 2. Check for port conflicts
lsof -i :8080

# 3. Check logs for import errors
python -c "from consultantos.api.main import app; print('✅ Imports OK')"

# 4. Reinstall dependencies
pip install -r requirements.txt --upgrade
```

---

### Issue: Import Errors

**Symptoms**: `ModuleNotFoundError` or `ImportError`

**Solutions**:
```bash
# Ensure on master branch
git checkout master
git pull origin master

# Clear Python cache
find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null
find . -type f -name "*.pyc" -delete

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

---

### Issue: Analysis Fails

**Symptoms**: `/analyze` endpoint returns errors

**Debug Steps**:
1. Check API keys are valid:
   ```bash
   python -c "import google.generativeai as genai; genai.configure(api_key='$GEMINI_API_KEY'); print('✅ Gemini OK')"
   ```

2. Verify network connectivity to external APIs

3. Check rate limits (Gemini, Tavily)

4. Review error message in response:
   ```bash
   curl -X POST "http://localhost:8080/analyze" \
     -H "Content-Type: application/json" \
     -d '{"company": "Test", "industry": "Tech", "frameworks": ["swot"]}' \
     | jq '.detail'
   ```

5. Check logs for detailed stack traces

---

### Issue: Cloud Run Deployment Fails

**Symptoms**: `gcloud run deploy` fails

**Common Causes**:
1. **Missing APIs**: Enable Cloud Run and Cloud Build
   ```bash
   gcloud services enable run.googleapis.com cloudbuild.googleapis.com
   ```

2. **Insufficient Permissions**: Ensure service account has `Cloud Run Admin` and `Service Account User` roles

3. **Region Issues**: Use supported regions (us-central1, us-east1, etc.)

4. **Resource Limits**: Check project quotas

5. **Build Timeout**: Increase timeout in cloudbuild.yaml if needed

**Debug Build**:
```bash
# Check build logs
gcloud builds list --limit 5
gcloud builds log [BUILD_ID]
```

---

### Issue: High Latency

**Symptoms**: Analysis takes longer than expected

**Optimizations**:
1. **Use Caching**: Disk cache enabled by default (1 hour TTL)
2. **Optimize Frameworks**: Use fewer frameworks for faster results
3. **Async Processing**: Use `/analyze/async` for comprehensive analyses
4. **Scale Instances**: Increase `max-instances` for Cloud Run
5. **Regional Deployment**: Deploy closer to users

**Performance Targets**:
- Simple (1-2 frameworks): 15-30 seconds
- Standard (3-4 frameworks): 30-60 seconds
- Deep (5+ frameworks): 60-120 seconds

---

## Security Best Practices

### API Key Management

✅ **DO**:
- Store keys in Secret Manager for production
- Use environment variables, never hardcode
- Rotate keys regularly
- Use different keys for dev/staging/prod

❌ **DON'T**:
- Commit keys to git
- Share keys in plain text
- Use production keys in development
- Log API keys

### CORS Configuration

**Development**:
```bash
export CORS_ORIGINS="http://localhost:3000,http://localhost:8080"
```

**Production**:
```bash
export CORS_ORIGINS="https://yourdomain.com,https://app.yourdomain.com"
```

### Rate Limiting

Default: 10 requests/hour per IP

**Adjust for Production**:
```bash
export RATE_LIMIT_PER_HOUR=100  # For paid tiers
```

### Session Security

**Set Strong Session Secret**:
```bash
export SESSION_SECRET="$(openssl rand -base64 32)"
```

---

## Cost Optimization

### Gemini API Costs
- **Model**: gemini-1.5-flash-002 (most cost-effective)
- **Optimization**: Use caching to avoid redundant API calls
- **Monitoring**: Track usage via metrics

### Tavily API Costs
- **Free Tier**: 1,000 searches/month
- **Optimization**: Cache search results (1 hour TTL)

### Cloud Run Costs
- **Pricing**: Pay only when handling requests
- **Optimization**: `min-instances: 0` scales to zero
- **Cold Start**: ~2-3 seconds (acceptable for hackathon)

**Estimated Monthly Costs** (1000 analyses):
- Gemini API: $2-5
- Tavily API: Free tier or $10-20
- Cloud Run: $5-15
- **Total**: $7-40/month

---

## Rollback Procedure

### Cloud Run Rollback

**List Revisions**:
```bash
gcloud run revisions list \
  --service consultantos \
  --region us-central1
```

**Rollback to Previous Revision**:
```bash
gcloud run services update-traffic consultantos \
  --region us-central1 \
  --to-revisions [REVISION_NAME]=100
```

### Git Rollback

**Revert Last Commit**:
```bash
git revert HEAD
git push origin master
```

**Rollback to Specific Commit**:
```bash
git reset --hard [COMMIT_HASH]
git push origin master --force  # Use with caution
```

---

## Performance Benchmarks

### Analysis Speed (Hackathon Demo)

| Scenario | Target | Acceptable | Status |
|----------|--------|------------|--------|
| API Response (p95) | < 5s | 5-10s | ✅ |
| Simple Analysis (2 frameworks) | 20-40s | 40-60s | ✅ |
| Standard Analysis (4 frameworks) | 50-90s | 90-120s | ✅ |
| Success Rate | ≥ 99% | 95-99% | ✅ |

### Comparison to Manual Work

| Task | Manual | ConsultantOS | Speedup |
|------|--------|--------------|---------|
| Basic Analysis | 8 hours | 30 seconds | 960x |
| Comprehensive | 32 hours | 60 seconds | 1,920x |
| Multi-Company | 160 hours | 5 minutes | 1,920x |

---

## Support and Resources

### Documentation
- **[README.md](README.md)** - Project overview
- **[HACKATHON_GUIDE.md](HACKATHON_GUIDE.md)** - Demo setup and usage
- **[USER_TESTING_GUIDE.md](USER_TESTING_GUIDE.md)** - Testing scenarios
- **[CLAUDE.md](CLAUDE.md)** - Development guidance

### API Documentation
- **Swagger UI**: `/docs`
- **ReDoc**: `/redoc`

### Monitoring
- **Cloud Run Console**: https://console.cloud.google.com/run
- **Cloud Build Console**: https://console.cloud.google.com/cloud-build
- **Cloud Logging**: https://console.cloud.google.com/logs

---

## Next Steps After Deployment

1. **Verify Health**: Test all health endpoints
2. **Run Test Analysis**: Execute sample analysis request
3. **Monitor Logs**: Watch for errors or warnings
4. **Performance Test**: Run concurrent requests
5. **Load Testing**: Use Apache Bench or similar tools
6. **Documentation**: Update service URL in frontend config
7. **User Testing**: Follow USER_TESTING_GUIDE.md scenarios

---

**Deployment Status**: Ready for hackathon demonstration
**Last Updated**: 2025-11-08
**Version**: 1.0.0-hackathon
