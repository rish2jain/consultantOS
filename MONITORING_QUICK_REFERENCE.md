# ConsultantOS Monitoring Quick Reference

## Health Endpoints

| Endpoint | Use Case | Expected Response |
|----------|----------|-------------------|
| `GET /health/live` | Kubernetes liveness probe | `{"status": "alive"}` |
| `GET /health/ready` | Kubernetes readiness probe | `{"status": "ready", "checks": {...}}` |
| `GET /health/startup` | Kubernetes startup probe | `{"status": "started"}` |
| `GET /health/detailed` | Full diagnostics | Comprehensive system status |
| `GET /health/metrics` | Prometheus scraping | Prometheus text format |

## Quick Health Check

```bash
# Check if service is running
curl http://localhost:8080/health/live

# Check if ready to serve traffic
curl http://localhost:8080/health/ready

# Get detailed status
curl http://localhost:8080/health/detailed | jq

# View Prometheus metrics
curl http://localhost:8080/health/metrics
```

## Key Metrics

```promql
# Request rate (req/sec)
rate(consultantos_requests_total[5m])

# Success rate (%)
(consultantos_requests_success / consultantos_requests_total) * 100

# Error rate (%)
(consultantos_requests_failed / consultantos_requests_total) * 100

# P95 latency (seconds)
histogram_quantile(0.95, rate(consultantos_execution_duration_seconds_bucket[5m]))

# Cache hit rate (%)
consultantos_cache_hits / (consultantos_cache_hits + consultantos_cache_misses)

# Job queue depth
consultantos_jobs_total{status="pending"}
```

## Alert Thresholds

| Alert | Threshold | Severity |
|-------|-----------|----------|
| Error Rate | >5% | Critical |
| P95 Latency | >60s | Warning |
| Cache Hit Rate | <60% | Warning |
| Job Queue | >100 pending | Warning |
| API Failure | >10% | Critical |

## Common Issues

### Readiness Probe Failing
```bash
# Check detailed status
curl http://localhost:8080/health/detailed

# Check logs
gcloud run logs read consultantos --limit 50

# Common fix: verify API keys
gcloud run services describe consultantos --format='value(spec.template.spec.containers[0].env)'
```

### High Latency
```bash
# Check metrics
curl http://localhost:8080/health/metrics | grep execution_duration

# Check cache performance
curl http://localhost:8080/health/detailed | jq '.metrics.cache_hit_rate'

# Scale up if needed
gcloud run services update consultantos --memory 4Gi --cpu 4
```

### Job Queue Backup
```bash
# Check queue status
curl http://localhost:8080/health/metrics | grep jobs_total

# List pending jobs
curl http://localhost:8080/jobs?status=pending

# Restart worker
gcloud run services update consultantos --region us-central1
```

## Request Tracing

Every request includes `X-Request-ID` header:

```bash
# Auto-generated ID
curl -i http://localhost:8080/health/live | grep X-Request-ID

# Custom ID for correlation
curl -H "X-Request-ID: my-trace-id" http://localhost:8080/analyze

# Find all logs for a request
gcloud logging read 'jsonPayload.request_id="my-trace-id"'
```

## Deployment Commands

```bash
# Deploy to Cloud Run
gcloud run deploy consultantos \
  --source . \
  --region us-central1 \
  --memory 2Gi \
  --cpu 2 \
  --set-env-vars "GEMINI_API_KEY=$GEMINI_API_KEY"

# Verify deployment
SERVICE_URL=$(gcloud run services describe consultantos --region us-central1 --format 'value(status.url)')
curl "${SERVICE_URL}/health/ready"

# Rollback if needed
gcloud run services update-traffic consultantos --to-revisions PREVIOUS_REVISION=100
```

## Documentation

- **Full Runbook:** `docs/RUNBOOK.md`
- **Monitoring Guide:** `docs/MONITORING.md`
- **Test Suite:** `test_health_endpoints.py`

## Emergency Contacts

**On-Call:** Check PagerDuty
**Slack:** #consultantos-alerts
**Logs:** Cloud Logging console

---

**Last Updated:** November 8, 2024
**Version:** 0.3.0
