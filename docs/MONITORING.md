# ConsultantOS Monitoring Guide

## Overview

This guide provides comprehensive monitoring setup instructions for ConsultantOS, including metrics collection, alerting, dashboards, and on-call procedures.

**Version:** 0.3.0
**Last Updated:** November 2024

---

## Table of Contents

1. [Monitoring Architecture](#monitoring-architecture)
2. [Metrics Collection](#metrics-collection)
3. [Alert Configuration](#alert-configuration)
4. [Dashboard Layouts](#dashboard-layouts)
5. [Log Aggregation](#log-aggregation)
6. [On-Call Procedures](#on-call-procedures)

---

## Monitoring Architecture

### Components

```
┌─────────────────────────────────────────────────────────────┐
│                     ConsultantOS Application                │
│  ┌────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │ Structured │  │  Prometheus  │  │  Health Check    │   │
│  │   Logging  │  │   Metrics    │  │   Endpoints      │   │
│  └────────────┘  └──────────────┘  └──────────────────┘   │
└─────────────────────────────────────────────────────────────┘
         │                  │                   │
         ▼                  ▼                   ▼
┌─────────────────┐  ┌──────────────┐  ┌──────────────┐
│  Cloud Logging  │  │  Prometheus  │  │  Uptime      │
│   (Stackdriver) │  │   Server     │  │  Monitoring  │
└─────────────────┘  └──────────────┘  └──────────────┘
         │                  │                   │
         └──────────────────┴───────────────────┘
                            │
                            ▼
                  ┌──────────────────┐
                  │     Grafana      │
                  │   Dashboards     │
                  └──────────────────┘
                            │
                            ▼
                  ┌──────────────────┐
                  │  Alert Manager   │
                  │   (PagerDuty)    │
                  └──────────────────┘
```

### Observability Stack

**Metrics:** Prometheus + Grafana
**Logs:** Cloud Logging (Stackdriver)
**Traces:** OpenTelemetry (optional)
**Alerting:** Prometheus Alertmanager + PagerDuty
**Uptime Monitoring:** Google Cloud Monitoring

---

## Metrics Collection

### Prometheus Setup

**1. Scrape Configuration**

Add to `prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'consultantos'
    metrics_path: '/health/metrics'
    static_configs:
      - targets: ['consultantos-service:8080']

    # For Cloud Run (with authentication)
    bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token

    relabel_configs:
      - source_labels: [__address__]
        target_label: instance
      - source_labels: [__meta_kubernetes_pod_name]
        target_label: pod
```

**2. Deploy Prometheus (Kubernetes)**

```bash
# Create namespace
kubectl create namespace monitoring

# Deploy Prometheus
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
  namespace: monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      containers:
      - name: prometheus
        image: prom/prometheus:latest
        args:
          - '--config.file=/etc/prometheus/prometheus.yml'
          - '--storage.tsdb.path=/prometheus'
          - '--storage.tsdb.retention.time=30d'
        ports:
        - containerPort: 9090
        volumeMounts:
        - name: config
          mountPath: /etc/prometheus
        - name: storage
          mountPath: /prometheus
      volumes:
      - name: config
        configMap:
          name: prometheus-config
      - name: storage
        emptyDir: {}
EOF

# Expose Prometheus
kubectl expose deployment prometheus \
  --port=9090 \
  --type=LoadBalancer \
  --namespace monitoring
```

**3. Verify Metrics Collection**

```bash
# Check metrics endpoint
curl http://consultantos-service:8080/health/metrics

# Query Prometheus
curl http://prometheus:9090/api/v1/query?query=consultantos_requests_total
```

---

### Key Metrics to Track

#### Request Metrics

| Metric | Type | Description | Alert Threshold |
|--------|------|-------------|-----------------|
| `consultantos_requests_total` | Counter | Total requests | - |
| `consultantos_requests_success` | Counter | Successful requests | < 95% success rate |
| `consultantos_requests_failed` | Counter | Failed requests | > 5% error rate |

**PromQL Queries:**
```promql
# Request rate (requests per second)
rate(consultantos_requests_total[5m])

# Success rate (percentage)
(consultantos_requests_success / consultantos_requests_total) * 100

# Error rate (percentage)
(consultantos_requests_failed / consultantos_requests_total) * 100
```

#### Performance Metrics

| Metric | Type | Description | Alert Threshold |
|--------|------|-------------|-----------------|
| `consultantos_execution_duration_seconds` | Histogram | Request duration | p95 > 60s |
| `consultantos_cache_hits` | Counter | Cache hits | - |
| `consultantos_cache_misses` | Counter | Cache misses | Hit rate < 60% |

**PromQL Queries:**
```promql
# P95 latency
histogram_quantile(0.95,
  rate(consultantos_execution_duration_seconds_bucket[5m]))

# P99 latency
histogram_quantile(0.99,
  rate(consultantos_execution_duration_seconds_bucket[5m]))

# Cache hit rate
consultantos_cache_hits / (consultantos_cache_hits + consultantos_cache_misses)

# Average execution time by operation
avg(consultantos_execution_duration_seconds) by (operation)
```

#### Error Metrics

| Metric | Type | Description | Alert Threshold |
|--------|------|-------------|-----------------|
| `consultantos_errors_total` | Counter | Errors by type | > 10 errors/minute |

**PromQL Queries:**
```promql
# Error rate by type
rate(consultantos_errors_total[5m])

# Top error types
topk(5, sum(rate(consultantos_errors_total[5m])) by (error_type))
```

#### Resource Metrics

| Metric | Type | Description | Alert Threshold |
|--------|------|-------------|-----------------|
| `consultantos_jobs_total` | Gauge | Jobs by status | pending > 100 |
| `consultantos_api_calls_total` | Counter | External API calls | failure rate > 10% |
| `consultantos_api_cost_total` | Counter | API costs | > $100/day |

**PromQL Queries:**
```promql
# Job queue depth
consultantos_jobs_total{status="pending"}

# API success rate by service
(consultantos_api_calls_total{status="success"} /
 consultantos_api_calls_total) by (service)

# Daily API cost
increase(consultantos_api_cost_total[24h])
```

---

## Alert Configuration

### Alert Rules

Create `alert_rules.yml`:

```yaml
groups:
  - name: consultantos_alerts
    interval: 30s
    rules:

      # High Error Rate
      - alert: HighErrorRate
        expr: |
          (consultantos_requests_failed / consultantos_requests_total) > 0.05
        for: 5m
        labels:
          severity: critical
          component: api
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }} (threshold: 5%)"

      # High Latency
      - alert: HighLatency
        expr: |
          histogram_quantile(0.95,
            rate(consultantos_execution_duration_seconds_bucket[5m])) > 60
        for: 10m
        labels:
          severity: warning
          component: performance
        annotations:
          summary: "High P95 latency detected"
          description: "P95 latency is {{ $value }}s (threshold: 60s)"

      # Low Cache Hit Rate
      - alert: LowCacheHitRate
        expr: |
          (consultantos_cache_hits /
           (consultantos_cache_hits + consultantos_cache_misses)) < 0.6
        for: 15m
        labels:
          severity: warning
          component: cache
        annotations:
          summary: "Cache hit rate below target"
          description: "Cache hit rate is {{ $value | humanizePercentage }} (target: 60%)"

      # Job Queue Backup
      - alert: JobQueueBackup
        expr: consultantos_jobs_total{status="pending"} > 100
        for: 5m
        labels:
          severity: warning
          component: worker
        annotations:
          summary: "Job queue backing up"
          description: "{{ $value }} jobs pending (threshold: 100)"

      # API Failure Rate
      - alert: APIFailureRate
        expr: |
          (consultantos_api_calls_total{status="failed"} /
           consultantos_api_calls_total) by (service) > 0.1
        for: 5m
        labels:
          severity: critical
          component: external_api
        annotations:
          summary: "High API failure rate for {{ $labels.service }}"
          description: "Failure rate is {{ $value | humanizePercentage }} (threshold: 10%)"

      # Service Down
      - alert: ServiceDown
        expr: up{job="consultantos"} == 0
        for: 2m
        labels:
          severity: critical
          component: availability
        annotations:
          summary: "ConsultantOS service is down"
          description: "Service has been down for 2 minutes"

      # High API Costs
      - alert: HighAPICosts
        expr: increase(consultantos_api_cost_total[1h]) > 10
        for: 1h
        labels:
          severity: warning
          component: cost
        annotations:
          summary: "High API costs detected"
          description: "API costs are ${{ $value }}/hour (threshold: $10/hour)"
```

### Alertmanager Configuration

Create `alertmanager.yml`:

```yaml
global:
  resolve_timeout: 5m
  slack_api_url: 'YOUR_SLACK_WEBHOOK'

route:
  group_by: ['alertname', 'component']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  receiver: 'team-pagerduty'

  routes:
    # Critical alerts to PagerDuty
    - match:
        severity: critical
      receiver: 'team-pagerduty'
      continue: true

    # Warnings to Slack
    - match:
        severity: warning
      receiver: 'team-slack'

    # Cost alerts to email
    - match:
        component: cost
      receiver: 'finance-email'

receivers:
  - name: 'team-pagerduty'
    pagerduty_configs:
      - service_key: 'YOUR_PAGERDUTY_KEY'
        description: '{{ .GroupLabels.alertname }}: {{ .Annotations.summary }}'

  - name: 'team-slack'
    slack_configs:
      - channel: '#consultantos-alerts'
        title: '{{ .GroupLabels.alertname }}'
        text: '{{ .Annotations.description }}'

  - name: 'finance-email'
    email_configs:
      - to: 'finance@example.com'
        from: 'alerts@consultantos.com'
        subject: 'ConsultantOS Cost Alert'
```

---

## Dashboard Layouts

### Grafana Dashboard Setup

**1. Install Grafana**

```bash
# Deploy Grafana (Kubernetes)
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: grafana
  namespace: monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: grafana
  template:
    metadata:
      labels:
        app: grafana
    spec:
      containers:
      - name: grafana
        image: grafana/grafana:latest
        ports:
        - containerPort: 3000
        env:
        - name: GF_SECURITY_ADMIN_PASSWORD
          value: "admin"
EOF

# Expose Grafana
kubectl expose deployment grafana \
  --port=3000 \
  --type=LoadBalancer \
  --namespace monitoring
```

**2. Add Prometheus Data Source**

1. Access Grafana UI: `http://grafana:3000`
2. Login: admin/admin
3. Configuration → Data Sources → Add Prometheus
4. URL: `http://prometheus:9090`
5. Save & Test

### Dashboard Panels

#### **Dashboard 1: Service Overview**

**Panels:**

1. **Request Rate** (Graph)
   ```promql
   rate(consultantos_requests_total[5m])
   ```

2. **Success Rate** (Gauge)
   ```promql
   (consultantos_requests_success / consultantos_requests_total) * 100
   ```

3. **Error Rate** (Graph)
   ```promql
   rate(consultantos_requests_failed[5m])
   ```

4. **Active Jobs** (Stat)
   ```promql
   consultantos_jobs_total{status="processing"}
   ```

#### **Dashboard 2: Performance Metrics**

**Panels:**

1. **Latency Percentiles** (Graph)
   ```promql
   histogram_quantile(0.50, rate(consultantos_execution_duration_seconds_bucket[5m]))
   histogram_quantile(0.95, rate(consultantos_execution_duration_seconds_bucket[5m]))
   histogram_quantile(0.99, rate(consultantos_execution_duration_seconds_bucket[5m]))
   ```

2. **Cache Performance** (Graph)
   ```promql
   rate(consultantos_cache_hits[5m])
   rate(consultantos_cache_misses[5m])
   ```

3. **Cache Hit Rate** (Gauge)
   ```promql
   consultantos_cache_hits / (consultantos_cache_hits + consultantos_cache_misses)
   ```

#### **Dashboard 3: Error Analysis**

**Panels:**

1. **Errors by Type** (Bar Chart)
   ```promql
   sum(consultantos_errors_total) by (error_type)
   ```

2. **Error Rate Trend** (Graph)
   ```promql
   rate(consultantos_errors_total[5m])
   ```

3. **API Failure Rate** (Table)
   ```promql
   (consultantos_api_calls_total{status="failed"} / consultantos_api_calls_total) by (service)
   ```

#### **Dashboard 4: Cost Tracking**

**Panels:**

1. **Daily API Costs** (Graph)
   ```promql
   increase(consultantos_api_cost_total[24h])
   ```

2. **Cost by Service** (Pie Chart)
   ```promql
   sum(consultantos_api_cost_total) by (service)
   ```

3. **Cost Trend** (Graph)
   ```promql
   rate(consultantos_api_cost_total[1h]) * 24
   ```

---

## Log Aggregation

### Structured Logging Format

All logs include:
- `timestamp` - ISO 8601 format
- `level` - DEBUG, INFO, WARNING, ERROR, CRITICAL
- `request_id` - Unique request identifier
- `event` - Event name (snake_case)
- Additional context fields

**Example Log Entry:**
```json
{
  "timestamp": "2024-11-08T12:00:00.000Z",
  "level": "INFO",
  "logger": "consultantos.api",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "event": "analysis_request_received",
  "company": "Tesla",
  "frameworks": ["porter", "swot"],
  "user_ip": "192.168.1.1"
}
```

### Log Queries (Cloud Logging)

**Find logs by request ID:**
```
jsonPayload.request_id="550e8400-e29b-41d4-a716-446655440000"
```

**Find errors in last hour:**
```
severity>=ERROR
timestamp>="2024-11-08T11:00:00Z"
```

**Find slow requests:**
```
jsonPayload.event="analysis_completed"
jsonPayload.execution_time_seconds>60
```

**Find API failures:**
```
jsonPayload.event="agent_execution_failed"
jsonPayload.agent_name="research_agent"
```

### Log Export to BigQuery

```bash
# Create log sink
gcloud logging sinks create consultantos-logs \
  bigquery.googleapis.com/projects/$GCP_PROJECT_ID/datasets/consultantos_logs \
  --log-filter='resource.type="cloud_run_revision" AND resource.labels.service_name="consultantos"'
```

---

## On-Call Procedures

### Alert Response Playbook

#### **Critical Alert: Service Down**

**Severity:** P1 (Immediate Response)
**SLA:** Acknowledge within 5 minutes

**Steps:**
1. Check service status: `curl https://consultantos-service/health/live`
2. Review recent deployments: `gcloud run revisions list`
3. Check logs for errors: `gcloud run logs read consultantos --limit 100`
4. Rollback if needed (see RUNBOOK.md)
5. Page backup on-call if not resolved in 15 minutes

#### **Critical Alert: High Error Rate**

**Severity:** P1 (Immediate Response)
**SLA:** Acknowledge within 5 minutes

**Steps:**
1. Check error types: `curl https://consultantos-service/health/detailed`
2. Search logs by error type: Filter by `error_type` in Cloud Logging
3. Identify root cause (API rate limits, database issues, etc.)
4. Apply appropriate mitigation from RUNBOOK.md
5. Update incident channel with status

#### **Warning Alert: High Latency**

**Severity:** P2 (1 hour response)
**SLA:** Acknowledge within 30 minutes

**Steps:**
1. Check performance metrics dashboard
2. Identify slow operations: Review execution_duration_seconds by operation
3. Check cache hit rate
4. Scale resources if needed
5. Schedule post-mortem if pattern continues

#### **Warning Alert: Low Cache Hit Rate**

**Severity:** P3 (Business hours)
**SLA:** Acknowledge within 2 hours

**Steps:**
1. Check cache statistics: `/health/detailed`
2. Review cache TTL settings
3. Identify cache misses pattern
4. Consider cache warming for common queries
5. Document findings for optimization sprint

---

## Monitoring Best Practices

### Alert Tuning

1. **Avoid Alert Fatigue**
   - Set appropriate thresholds
   - Use `for:` duration to avoid transient spikes
   - Group related alerts

2. **Alert Quality Metrics**
   - Target: <5% false positive rate
   - Track alert response times
   - Regular review of alert usefulness

3. **Escalation Paths**
   - Critical → PagerDuty → On-call
   - Warning → Slack → Team channel
   - Info → Dashboard → Weekly review

### Dashboard Maintenance

1. **Weekly Review**
   - Check for missing data
   - Validate alert thresholds
   - Update dashboards based on feedback

2. **Monthly Optimization**
   - Archive unused panels
   - Add new metrics as needed
   - Review dashboard performance

---

**Document Version:** 1.0
**Maintained By:** Platform Team
**Next Review Date:** February 2025
