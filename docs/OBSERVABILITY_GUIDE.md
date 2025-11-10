# ConsultantOS Observability Guide

## Overview

ConsultantOS includes a comprehensive observability stack for monitoring system health, performance, and reliability. The stack includes:

- **Prometheus**: Time-series database for metrics collection and storage
- **Grafana**: Visualization and dashboarding platform
- **AlertManager**: Alert routing and notification system
- **Custom Metrics**: Application-level instrumentation

## Quick Start

### 1. Start the Observability Stack

```bash
cd /path/to/ConsultantOS
./scripts/start_observability.sh up
```

This will start:
- Prometheus on http://localhost:9090
- Grafana on http://localhost:3001 (admin/admin)
- AlertManager on http://localhost:9093

### 2. Access Grafana

1. Open http://localhost:3001
2. Login with admin/admin
3. Navigate to the "ConsultantOS" folder
4. View available dashboards:
   - System Overview
   - Agent Performance
   - Monitoring System
   - API Performance

### 3. View Prometheus Metrics

1. Open http://localhost:9090
2. Use the Expression Browser to query metrics
3. Example queries:
   ```
   consultantos_api_requests_total
   rate(consultantos_api_requests_total[5m])
   histogram_quantile(0.95, rate(consultantos_api_request_duration_seconds_bucket[5m]))
   ```

### 4. Configure Alerts

AlertManager automatically routes alerts based on severity:
- **Critical**: Sent immediately to #consultantos-critical
- **Warning**: Batched and sent to #consultantos-warnings (30s wait)
- **Info**: Sent to #consultantos-alerts with 5m batch delay

To enable Slack notifications, set the webhook URL in `alertmanager/config.yml`.

## Architecture

### Metrics Collection

Metrics are collected at multiple levels:

#### API Level (FastAPI)
- Request count by endpoint, method, and status
- Request/response latency (p50, p95, p99)
- Request/response size
- Active request count
- Error count and rate

**File**: `consultantos/api/main.py` (metrics middleware)

#### Agent Level
- Agent execution time per agent
- Success/failure rate
- Success rate trend

**File**: `consultantos/observability/metrics.py` (timing context managers)

#### Monitoring Level
- Monitor check frequency and latency
- Alert generation rate
- Alert quality score (from user feedback)
- Change detection accuracy

#### Data Source Level
- Request count per source
- Success/failure rate
- Reliability score
- Error types

#### System Level
- Active request count
- Uptime
- Error rate by type

### Metric Types

#### Counter
Monotonically increasing value (request count, errors, alerts)
```python
metrics.api_requests_total.labels(...).inc()
```

#### Histogram
Distribution of values (latency, size)
```python
metrics.api_request_duration_seconds.labels(...).observe(duration)
```

#### Gauge
Point-in-time value (active requests, cache hit rate)
```python
metrics.cache_hit_rate.labels(...).set(0.95)
```

#### Summary
Similar to histogram but calculates percentiles on the client
```python
metrics.api_request_size_bytes.labels(...).observe(1024)
```

## Dashboards

### System Overview
- API request distribution by status
- API success rate
- Request rate over time
- API latency percentiles
- Active request count
- Error rate by type

### Agent Performance
- Agent execution distribution
- Agent success rates
- Agent execution latency (p50, p95)
- Agent execution rate
- Hour-based success rate

### Monitoring System
- Monitor check status distribution
- Alert quality score
- Monitor check latency
- Alert generation rate
- Change detection accuracy
- Monitor check rate

### API Performance
- API success rate (SLA tracking)
- p95 latency
- Request rate (RPS)
- Active requests
- Response time percentiles (p50, p95, p99)
- Request status code distribution
- Data transfer rate
- Error rate by type

## Alert Rules

Alert rules are defined in `prometheus/alerts.yml` with the following categories:

### Critical Alerts (immediate notification)
- **HighAPIErrorRate**: >5% error rate for 2 minutes
- **MonitorCheckFailure**: >10% check failure rate for 2 minutes
- **InstanceDown**: API instance down for 1 minute
- **HighErrorRateLastHour**: >10 errors/sec in last hour

### Warning Alerts (30s batch delay)
- **HighAPILatency**: p95 latency >2s for 3 minutes
- **AgentExecutionFailureRate**: >10% failure rate for 3 minutes
- **LowAgentSuccessRate**: <80% success rate for 5 minutes
- **HighMonitorCheckLatency**: p95 latency >2 minutes
- **LowAlertQuality**: Quality score <0.6 for 10 minutes
- **DataSourceReliabilityIssue**: Reliability <0.7 for 5 minutes
- **JobQueueBackup**: >100 jobs queued for 5 minutes
- **HighActiveRequests**: >100 active requests for 2 minutes

### Info Alerts (5m batch delay)
- **HighCacheMissRate**: Hit rate <50% for 5 minutes

## Integration with ConsultantOS

### Instrumenting Agents

To add metrics to an agent:

```python
from consultantos.observability import AgentExecutionTimer, metrics

async def execute(self):
    with AgentExecutionTimer("research_agent") as timer:
        # Agent logic
        result = await self._execute_internal()
    return result
```

### Instrumenting Data Sources

To add metrics to data source calls:

```python
from consultantos.observability import DataSourceRequestTimer

async def fetch_data(self, query):
    with DataSourceRequestTimer("tavily") as timer:
        result = await tavily_api.search(query)
    return result
```

### Recording Custom Metrics

```python
from consultantos.observability import metrics

# Record API request
metrics.record_api_request(
    method="GET",
    endpoint="/analyze",
    status_code=200,
    duration=0.5,
    request_size=1024,
    response_size=5120
)

# Record agent execution
metrics.record_agent_execution(
    agent_name="research_agent",
    duration=2.5,
    success=True
)

# Record monitor check
metrics.record_monitor_check(
    monitor_id="monitor_123",
    duration=10.5,
    success=True
)

# Record alert
metrics.record_alert_generated(
    monitor_id="monitor_123",
    alert_type="price_change",
    severity="warning"
)
```

## Prometheus Configuration

### Scrape Interval
- Default: 15 seconds
- ConsultantOS API: 10 seconds (more frequent)

### Data Retention
- Default: 15 days
- Configurable in `prometheus.yml`

### Alert Evaluation
- Interval: 15 seconds
- Grace period varies by alert rule

## Grafana Configuration

### Auto-provisioning
Dashboards are automatically provisioned from `grafana/dashboards/` directory.

To add a new dashboard:
1. Export dashboard JSON from Grafana or create manually
2. Save to `grafana/dashboards/` directory
3. Dashboard will be auto-loaded on next restart

### User Management
- Default admin user: admin/admin
- Disable sign-ups by default
- Configure LDAP/OAuth for enterprise auth

## Cloud Run Deployment

### Exporting Metrics to Cloud Monitoring

```bash
gcloud run deploy consultantos \
  --set-env-vars "PROMETHEUS_PUSHGATEWAY=https://monitoring.googleapis.com/v1/projects/PROJECT_ID/location/global/prometheus/api/v1/write"
```

### CloudSQL Integration

Export Prometheus metrics to CloudSQL:

```yaml
remote_write:
  - url: https://monitoring.googleapis.com/v1/projects/PROJECT_ID/location/global/prometheus/api/v1/write
    write_relabel_configs:
      - action: replace
        replacement: "consultant-os"
        target_label: project
```

## Performance Impact

The observability stack has minimal performance impact:

- **Memory overhead**: ~50-100MB (Prometheus + Grafana)
- **CPU overhead**: <5% on idle, <10% under load
- **Network overhead**: <1% of bandwidth
- **Latency impact**: <1ms per request

### Optimization Tips

1. **Reduce cardinality**: Avoid high-cardinality labels
   ```python
   # Bad: too many unique values
   metrics.api_requests_total.labels(user_id=user_id).inc()

   # Good: limited unique values
   metrics.api_requests_total.labels(endpoint=endpoint).inc()
   ```

2. **Batch metric updates**: Don't update every request
   ```python
   # Sample every 100 requests
   if request_count % 100 == 0:
       metrics.set_cache_hit_rate("disk", hit_rate)
   ```

3. **Adjust scrape intervals**: Less frequent for dev, more for prod
   ```yaml
   scrape_interval: 15s  # Production
   scrape_interval: 60s  # Development
   ```

## Troubleshooting

### Prometheus not starting

```bash
# Check logs
docker-compose -f docker-compose.observability.yml logs prometheus

# Validate config
promtool check config prometheus/prometheus.yml
```

### Grafana dashboards not appearing

```bash
# Check provisioning configuration
ls -la grafana/provisioning/dashboards/

# Verify dashboard JSON syntax
jq empty grafana/dashboards/*.json
```

### Alerts not firing

```bash
# Check alert rules
promtool check rules prometheus/alerts.yml

# Verify AlertManager is running
curl http://localhost:9093/-/healthy

# Check AlertManager config
amtool config routes
```

### High memory usage

1. Reduce data retention in Prometheus
2. Reduce scrape interval
3. Remove low-cardinality metrics
4. Increase Prometheus storage allocation

### Missing metrics

1. Verify metrics middleware is enabled in FastAPI
2. Check metrics export endpoint: http://localhost:8080/metrics
3. Verify Prometheus is scraping the endpoint
4. Check Prometheus targets: http://localhost:9090/targets

## Maintenance

### Backing up Prometheus Data

```bash
# Stop Prometheus
docker-compose -f docker-compose.observability.yml stop prometheus

# Backup data directory
tar -czf prometheus_backup.tar.gz prometheus/

# Restart
docker-compose -f docker-compose.observability.yml start prometheus
```

### Updating Grafana Dashboards

```bash
# Export current state from Grafana UI
# Edit dashboard JSON
# Restart Grafana to re-provision
docker-compose -f docker-compose.observability.yml restart grafana
```

### Cleaning up old data

Prometheus automatically cleans up data older than the retention period (default: 15 days).

To manually delete data:

```bash
# Stop Prometheus
docker-compose -f docker-compose.observability.yml stop prometheus

# Delete data directory (be careful!)
rm -rf prometheus_data/

# Restart
docker-compose -f docker-compose.observability.yml start prometheus
```

## Best Practices

1. **Alert tuning**: Start conservative, adjust thresholds based on experience
2. **Dashboard design**: Create focused dashboards for different teams
3. **Metric naming**: Use consistent, descriptive names
4. **Label strategy**: Keep labels limited and consistent
5. **SLA definition**: Define clear SLOs based on alerts
6. **Regular review**: Review dashboards and alerts monthly
7. **Documentation**: Document custom metrics and dashboards
8. **Testing**: Test alert routing and notification channels regularly

## Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [AlertManager Documentation](https://prometheus.io/docs/alerting/latest/overview/)
- [PromQL Tutorial](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Grafana Dashboard Best Practices](https://grafana.com/docs/grafana/latest/dashboards/)

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review logs: `./scripts/start_observability.sh logs [service]`
3. Check Prometheus targets: http://localhost:9090/targets
4. Verify alert rules: http://localhost:9090/alerts
