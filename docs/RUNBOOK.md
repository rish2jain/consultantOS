# ConsultantOS Operational Runbook

## Overview

This runbook provides operational procedures for deploying, managing, and troubleshooting ConsultantOS in production environments.

**Version:** 0.3.0
**Last Updated:** November 2024

---

## Table of Contents

1. [Deployment Procedures](#deployment-procedures)
2. [Health Monitoring](#health-monitoring)
3. [Common Issues and Troubleshooting](#common-issues-and-troubleshooting)
4. [Scaling Guidelines](#scaling-guidelines)
5. [Disaster Recovery](#disaster-recovery)
6. [Maintenance Procedures](#maintenance-procedures)

---

## Deployment Procedures

### Standard Deployment to Cloud Run

**Prerequisites:**
- Google Cloud SDK installed and configured
- Service account with necessary permissions
- Environment variables configured

**Deployment Steps:**

```bash
# 1. Set project ID
export GCP_PROJECT_ID="your-project-id"
gcloud config set project $GCP_PROJECT_ID

# 2. Build and deploy
gcloud run deploy consultantos \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --min-instances 1 \
  --set-env-vars "GEMINI_API_KEY=${GEMINI_API_KEY},TAVILY_API_KEY=${TAVILY_API_KEY},GCP_PROJECT_ID=${GCP_PROJECT_ID},ENVIRONMENT=production,LOG_LEVEL=INFO"

# 3. Verify deployment
gcloud run services describe consultantos --region us-central1

# 4. Test health endpoint
SERVICE_URL=$(gcloud run services describe consultantos --region us-central1 --format 'value(status.url)')
curl "${SERVICE_URL}/health/ready"
```

**Post-Deployment Verification:**

```bash
# Check all health probes
curl "${SERVICE_URL}/health/live"      # Should return 200
curl "${SERVICE_URL}/health/ready"     # Should return 200
curl "${SERVICE_URL}/health/startup"   # Should return 200
curl "${SERVICE_URL}/health/detailed"  # Should return comprehensive status

# Test analysis endpoint
curl -X POST "${SERVICE_URL}/analyze" \
  -H "Content-Type: application/json" \
  -d '{"company": "Tesla", "industry": "Electric Vehicles", "frameworks": ["porter"]}'
```

### Rollback Procedure

```bash
# List recent revisions
gcloud run revisions list --service consultantos --region us-central1

# Rollback to previous revision
gcloud run services update-traffic consultantos \
  --to-revisions REVISION_NAME=100 \
  --region us-central1
```

---

## Health Monitoring

### Health Check Endpoints

| Endpoint | Purpose | Expected Response | Kubernetes Usage |
|----------|---------|-------------------|------------------|
| `/health/live` | Liveness check | 200 if app is running | Restart pod on failure |
| `/health/ready` | Readiness check | 200 if ready to serve | Remove from service on failure |
| `/health/startup` | Startup check | 200 if initialization complete | Wait before readiness checks |
| `/health/detailed` | Comprehensive status | Full system diagnostics | Manual inspection |
| `/health/metrics` | Prometheus metrics | Text format metrics | Metrics scraping |

### Kubernetes Health Probe Configuration

```yaml
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: consultantos
    livenessProbe:
      httpGet:
        path: /health/live
        port: 8080
      initialDelaySeconds: 10
      periodSeconds: 10
      timeoutSeconds: 5
      failureThreshold: 3

    readinessProbe:
      httpGet:
        path: /health/ready
        port: 8080
      initialDelaySeconds: 5
      periodSeconds: 5
      timeoutSeconds: 5
      failureThreshold: 3

    startupProbe:
      httpGet:
        path: /health/startup
        port: 8080
      initialDelaySeconds: 0
      periodSeconds: 5
      timeoutSeconds: 5
      failureThreshold: 12
```

### Key Metrics to Monitor

**Request Metrics:**
- `consultantos_requests_total` - Total requests
- `consultantos_requests_success` - Successful requests
- `consultantos_requests_failed` - Failed requests

**Performance Metrics:**
- `consultantos_execution_duration_seconds` - Request duration
- `consultantos_cache_hits` / `consultantos_cache_misses` - Cache performance

**Error Metrics:**
- `consultantos_errors_total` - Errors by type
- `consultantos_api_calls_total` - External API success/failure

**Resource Metrics:**
- `consultantos_jobs_total` - Job queue status
- `consultantos_api_cost_total` - API costs

---

## Common Issues and Troubleshooting

### Issue: Readiness Probe Failing

**Symptoms:**
- `/health/ready` returns 503
- Pods removed from service
- Traffic not reaching application

**Diagnosis:**
```bash
# Check detailed health status
curl "${SERVICE_URL}/health/detailed"

# Check logs for database/cache errors
gcloud run logs read consultantos --region us-central1 --limit 50
```

**Common Causes:**

1. **Database Connection Issues**
   ```bash
   # Verify Firestore access
   gcloud firestore databases list

   # Check service account permissions
   gcloud projects get-iam-policy $GCP_PROJECT_ID
   ```

2. **Missing API Keys**
   ```bash
   # Check environment variables
   gcloud run services describe consultantos --region us-central1 --format 'value(spec.template.spec.containers[0].env)'

   # Update missing keys
   gcloud run services update consultantos \
     --region us-central1 \
     --update-env-vars "GEMINI_API_KEY=new-key"
   ```

3. **Cache Initialization Failure**
   - Check `/tmp` directory permissions
   - Verify sufficient memory allocation
   - Review cache configuration in logs

**Resolution:**
```bash
# Restart service
gcloud run services update consultantos --region us-central1

# If persistent, redeploy
gcloud run deploy consultantos --source . --region us-central1
```

---

### Issue: High Latency / Timeout Errors

**Symptoms:**
- Requests timing out after 300 seconds
- 504 Gateway Timeout errors
- High p95/p99 latencies

**Diagnosis:**
```bash
# Check metrics endpoint
curl "${SERVICE_URL}/health/metrics" | grep execution_duration

# Review slow requests in logs
gcloud run logs read consultantos --region us-central1 | grep "execution_time_seconds"
```

**Common Causes:**

1. **Gemini API Rate Limiting**
   - Check API quota in Google Cloud Console
   - Review `consultantos_api_calls_total{service="gemini"}` metrics
   - Implement exponential backoff (already in `utils/retry.py`)

2. **Cache Miss Storm**
   - Check cache hit rate: `consultantos_cache_hits / (consultantos_cache_hits + consultantos_cache_misses)`
   - Target: >60% cache hit rate
   - Warm cache: Pre-populate common analyses

3. **Database Slow Queries**
   - Review Firestore query performance
   - Add composite indexes if needed
   - Implement pagination for large result sets

**Resolution:**
```bash
# Increase timeout (if appropriate)
gcloud run services update consultantos \
  --region us-central1 \
  --timeout 600

# Scale up resources
gcloud run services update consultantos \
  --region us-central1 \
  --memory 4Gi \
  --cpu 4
```

---

### Issue: High Memory Usage / OOM Kills

**Symptoms:**
- Container restarts frequently
- Memory usage approaching limits
- Slow performance before crashes

**Diagnosis:**
```bash
# Check container metrics
gcloud monitoring time-series list \
  --filter='metric.type="run.googleapis.com/container/memory/utilizations"'

# Review logs for memory warnings
gcloud run logs read consultantos | grep -i "memory\|oom"
```

**Resolution:**
```bash
# Increase memory allocation
gcloud run services update consultantos \
  --region us-central1 \
  --memory 4Gi

# If persistent, investigate memory leaks
# - Review cache size limits
# - Check for unbounded data structures
# - Profile with memory profiler
```

---

### Issue: Job Queue Backup

**Symptoms:**
- Jobs stuck in "pending" status
- Long queue wait times
- Worker not processing jobs

**Diagnosis:**
```bash
# Check job queue metrics
curl "${SERVICE_URL}/health/metrics" | grep consultantos_jobs_total

# Check worker logs
gcloud run logs read consultantos | grep "worker"

# List pending jobs
curl "${SERVICE_URL}/jobs?status=pending"
```

**Resolution:**
```bash
# Restart worker by redeploying
gcloud run services update consultantos --region us-central1

# Scale up to handle backlog
gcloud run services update consultantos \
  --region us-central1 \
  --max-instances 20
```

---

## Scaling Guidelines

### Horizontal Scaling

**Auto-scaling Configuration:**
```bash
# Set min/max instances
gcloud run services update consultantos \
  --region us-central1 \
  --min-instances 2 \
  --max-instances 50

# Configure CPU-based autoscaling
gcloud run services update consultantos \
  --region us-central1 \
  --cpu-throttling \
  --concurrency 80
```

**Scaling Triggers:**
- **Low Traffic (0-100 req/hour):** 1-2 instances
- **Medium Traffic (100-1000 req/hour):** 2-5 instances
- **High Traffic (1000+ req/hour):** 5-20 instances
- **Peak Events:** 20-50 instances

### Vertical Scaling

**Resource Recommendations:**

| Load Level | Memory | CPU | Concurrency |
|------------|--------|-----|-------------|
| Development | 1Gi | 1 | 10 |
| Light Production | 2Gi | 2 | 40 |
| Standard Production | 4Gi | 2 | 80 |
| High Load | 8Gi | 4 | 100 |

```bash
# Update resources
gcloud run services update consultantos \
  --region us-central1 \
  --memory 4Gi \
  --cpu 2 \
  --concurrency 80
```

---

## Disaster Recovery

### Backup Procedures

**Database (Firestore):**
```bash
# Export Firestore data
gcloud firestore export gs://${GCP_PROJECT_ID}-backups/firestore/$(date +%Y%m%d)

# Schedule daily backups with Cloud Scheduler
gcloud scheduler jobs create http firestore-backup \
  --schedule="0 2 * * *" \
  --uri="https://firestore.googleapis.com/v1/projects/${GCP_PROJECT_ID}/databases/(default):exportDocuments" \
  --http-method=POST
```

**Cloud Storage (Reports):**
- Versioning enabled by default
- Lifecycle policy: Delete after 90 days
- Cross-region replication for critical data

### Recovery Procedures

**Complete Service Failure:**
```bash
# 1. Check service status
gcloud run services describe consultantos --region us-central1

# 2. Review recent logs
gcloud run logs read consultantos --limit 100

# 3. Rollback to last known good revision
gcloud run revisions list --service consultantos --region us-central1
gcloud run services update-traffic consultantos \
  --to-revisions PREVIOUS_REVISION=100 \
  --region us-central1

# 4. If rollback fails, redeploy from source
gcloud run deploy consultantos --source . --region us-central1
```

**Data Loss Recovery:**
```bash
# Restore Firestore from backup
gcloud firestore import gs://${GCP_PROJECT_ID}-backups/firestore/BACKUP_DATE

# Verify data integrity
# - Check report counts
# - Validate user data
# - Test critical workflows
```

---

## Maintenance Procedures

### Routine Maintenance

**Weekly:**
- Review error logs and metrics
- Check resource utilization trends
- Verify backup completion
- Update dependencies (security patches)

**Monthly:**
- Performance optimization review
- Cost analysis and optimization
- Capacity planning review
- Update runbook based on incidents

**Quarterly:**
- Disaster recovery drill
- Security audit
- Dependency upgrades (minor versions)
- Load testing

### Dependency Updates

```bash
# Update Python dependencies
pip list --outdated
pip install -U package-name
pip freeze > requirements.txt

# Test changes
pytest tests/ -v

# Deploy with canary testing
gcloud run deploy consultantos \
  --source . \
  --region us-central1 \
  --tag canary \
  --no-traffic

# Gradually shift traffic
gcloud run services update-traffic consultantos \
  --to-revisions canary=10 \
  --region us-central1
```

### Log Management

**Log Locations:**
- **Cloud Run Logs:** Cloud Logging (90-day retention)
- **Application Logs:** Structured JSON via structlog
- **Request Logs:** All requests include `request_id` for tracing

**Log Analysis:**
```bash
# Search by request ID
gcloud run logs read consultantos --filter='jsonPayload.request_id="abc123"'

# Search for errors
gcloud run logs read consultantos --filter='severity>=ERROR'

# Export logs for analysis
gcloud logging read "resource.type=cloud_run_revision" \
  --format json > logs.json
```

---

## Emergency Contacts

**On-Call Escalation:**
1. Primary On-Call Engineer
2. Platform Team Lead
3. Infrastructure Team

**External Dependencies:**
- Google Cloud Support: Cloud Console → Support
- Gemini API Status: Google AI Status Page
- Tavily API Support: support@tavily.com

---

## Appendix: Configuration Reference

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GEMINI_API_KEY` | Yes | - | Google Gemini API key |
| `TAVILY_API_KEY` | No | - | Tavily search API key |
| `GCP_PROJECT_ID` | Yes | - | Google Cloud project ID |
| `ENVIRONMENT` | No | development | Environment name |
| `LOG_LEVEL` | No | INFO | Logging level |
| `RATE_LIMIT_PER_HOUR` | No | 10 | Rate limit per IP |
| `ENABLE_METRICS` | No | true | Enable Prometheus metrics |
| `HEALTH_CHECK_TIMEOUT` | No | 5 | Health check timeout (seconds) |
| `GRACEFUL_SHUTDOWN_TIMEOUT` | No | 30 | Graceful shutdown timeout (seconds) |

### Service Account Permissions

Required IAM roles:
- `roles/datastore.user` - Firestore access
- `roles/storage.objectAdmin` - Cloud Storage access
- `roles/secretmanager.secretAccessor` - Secret Manager access
- `roles/logging.logWriter` - Cloud Logging write

---

**Document Version:** 1.0
**Maintained By:** Platform Team
**Next Review Date:** February 2025
