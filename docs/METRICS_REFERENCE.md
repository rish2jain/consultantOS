# ConsultantOS Metrics Reference

Complete reference for all metrics collected by ConsultantOS observability system.

## API Metrics

### `consultantos_api_requests_total`
**Type**: Counter
**Labels**: `method`, `endpoint`, `status`
**Description**: Total API requests received
**Example**: `consultantos_api_requests_total{method="GET",endpoint="/analyze",status="200"}`

### `consultantos_api_request_duration_seconds`
**Type**: Histogram
**Labels**: `method`, `endpoint`
**Buckets**: 0.001s, 0.005s, 0.01s, 0.025s, 0.05s, 0.1s, 0.25s, 0.5s, 1s, 2.5s, 5s, 10s
**Description**: API request latency in seconds
**Example**:
```
histogram_quantile(0.95, rate(consultantos_api_request_duration_seconds_bucket[5m]))
```

### `consultantos_api_request_size_bytes`
**Type**: Summary
**Labels**: `method`, `endpoint`
**Description**: API request payload size in bytes
**Example**: `rate(consultantos_api_request_size_bytes_sum[5m])`

### `consultantos_api_response_size_bytes`
**Type**: Summary
**Labels**: `method`, `endpoint`
**Description**: API response payload size in bytes
**Example**: `rate(consultantos_api_response_size_bytes_sum[5m])`

## Agent Metrics

### `consultantos_agent_execution_duration_seconds`
**Type**: Histogram
**Labels**: `agent_name`, `status`
**Buckets**: 0.5s, 1s, 2s, 5s, 10s, 30s, 60s, 120s, 300s
**Description**: Time taken to execute agent in seconds
**Status values**: `success`, `failure`
**Example**:
```
histogram_quantile(0.95, rate(consultantos_agent_execution_duration_seconds_bucket{agent_name="research_agent"}[5m]))
```

### `consultantos_agent_executions_total`
**Type**: Counter
**Labels**: `agent_name`, `status`
**Description**: Total agent executions
**Status values**: `success`, `failure`
**Example**: `rate(consultantos_agent_executions_total[1m])`

### `consultantos_agent_success_rate`
**Type**: Gauge
**Labels**: `agent_name`
**Range**: 0-1
**Description**: Agent success rate (ratio of successful executions)
**Example**: `consultantos_agent_success_rate{agent_name="research_agent"}`

## Monitoring System Metrics

### `consultantos_monitor_checks_total`
**Type**: Counter
**Labels**: `monitor_id`, `status`
**Description**: Total monitoring checks executed
**Status values**: `success`, `failure`
**Example**: `rate(consultantos_monitor_checks_total{monitor_id="monitor_123"}[5m])`

### `consultantos_monitor_check_duration_seconds`
**Type**: Histogram
**Labels**: `monitor_id`
**Buckets**: 1s, 5s, 10s, 30s, 60s, 120s, 300s, 600s
**Description**: Time taken to execute monitoring check
**Example**: `histogram_quantile(0.95, rate(consultantos_monitor_check_duration_seconds_bucket[5m]))`

### `consultantos_alerts_generated_total`
**Type**: Counter
**Labels**: `monitor_id`, `alert_type`, `severity`
**Description**: Total alerts generated
**Severity values**: `critical`, `warning`, `info`
**Example**: `rate(consultantos_alerts_generated_total{severity="critical"}[1h])`

### `consultantos_alert_quality_score`
**Type**: Gauge
**Labels**: `monitor_id`
**Range**: 0-1
**Description**: Alert quality score based on user feedback
**Calculation**: (true_positives) / (true_positives + false_positives)
**Example**: `consultantos_alert_quality_score{monitor_id="monitor_123"}`

### `consultantos_change_detection_accuracy`
**Type**: Gauge
**Labels**: `monitor_id`
**Range**: 0-1
**Description**: Accuracy of change detection algorithm
**Calculation**: (correctly detected changes) / (total changes)
**Example**: `consultantos_change_detection_accuracy{monitor_id="monitor_123"}`

## Cache Metrics

### `consultantos_cache_hits_total`
**Type**: Counter
**Labels**: `cache_type`
**Description**: Total cache hits
**Cache types**: `disk`, `semantic`
**Example**: `rate(consultantos_cache_hits_total[1m])`

### `consultantos_cache_misses_total`
**Type**: Counter
**Labels**: `cache_type`
**Description**: Total cache misses
**Cache types**: `disk`, `semantic`
**Example**: `rate(consultantos_cache_misses_total[1m])`

### `consultantos_cache_hit_rate`
**Type**: Gauge
**Labels**: `cache_type`
**Range**: 0-1
**Description**: Cache hit rate (hits / (hits + misses))
**Example**: `consultantos_cache_hit_rate{cache_type="disk"}`

### `consultantos_cache_size_bytes`
**Type**: Gauge
**Labels**: `cache_type`
**Description**: Current cache size in bytes
**Example**: `consultantos_cache_size_bytes{cache_type="disk"}`

## Data Source Metrics

### `consultantos_data_source_requests_total`
**Type**: Counter
**Labels**: `source_name`, `status`
**Description**: Total requests to data source
**Status values**: `success`, `failure`
**Source names**: `tavily`, `yfinance`, `trends`, `sec_edgar`, `finnhub`, `finviz`, `alpha_vantage`
**Example**: `rate(consultantos_data_source_requests_total{source_name="tavily"}[5m])`

### `consultantos_data_source_request_duration_seconds`
**Type**: Histogram
**Labels**: `source_name`
**Buckets**: 0.1s, 0.5s, 1s, 2s, 5s, 10s, 30s
**Description**: Time taken for data source request
**Example**:
```
histogram_quantile(0.95, rate(consultantos_data_source_request_duration_seconds_bucket{source_name="yfinance"}[5m]))
```

### `consultantos_data_source_reliability`
**Type**: Gauge
**Labels**: `source_name`
**Range**: 0-1
**Description**: Data source reliability score
**Calculation**: (successful_requests) / (total_requests)
**Example**: `consultantos_data_source_reliability{source_name="tavily"}`

### `consultantos_data_source_errors_total`
**Type**: Counter
**Labels**: `source_name`, `error_type`
**Description**: Total data source errors
**Common error types**: `timeout`, `rate_limit`, `auth_error`, `parse_error`, `connection_error`
**Example**: `rate(consultantos_data_source_errors_total{source_name="tavily",error_type="rate_limit"}[1h])`

## Job Queue Metrics

### `consultantos_jobs_total`
**Type**: Counter
**Labels**: `job_type`, `status`
**Description**: Total jobs processed
**Status values**: `success`, `failure`
**Job types**: `analysis`, `monitoring_check`, `report_generation`, `cleanup`
**Example**: `rate(consultantos_jobs_total{job_type="analysis"}[5m])`

### `consultantos_job_processing_duration_seconds`
**Type**: Histogram
**Labels**: `job_type`
**Buckets**: 1s, 5s, 10s, 30s, 60s, 300s
**Description**: Time taken to process job
**Example**: `histogram_quantile(0.95, rate(consultantos_job_processing_duration_seconds_bucket{job_type="analysis"}[5m]))`

### `consultantos_queue_size`
**Type**: Gauge
**Labels**: `queue_name`
**Description**: Current size of job queue
**Queue names**: `default`, `priority`, `background`
**Example**: `consultantos_queue_size{queue_name="default"}`

## Error Metrics

### `consultantos_errors_total`
**Type**: Counter
**Labels**: `error_type`, `component`
**Description**: Total errors encountered
**Components**: `api`, `agents`, `monitoring`, `data_sources`, `jobs`, `database`, `storage`
**Common error types**: `RequestError`, `TimeoutError`, `ValidationError`, `DatabaseError`, `StorageError`, `ConfigError`
**Example**: `rate(consultantos_errors_total{component="api"}[5m])`

## System Metrics

### `consultantos_active_requests`
**Type**: Gauge
**Description**: Number of active HTTP requests being processed
**Example**: `consultantos_active_requests`

### `consultantos_uptime_seconds`
**Type**: Gauge
**Description**: Application uptime in seconds
**Example**: `consultantos_uptime_seconds`

## Standard Prometheus Metrics

The following standard metrics are automatically exported by Prometheus:

### `up`
**Type**: Gauge
**Labels**: `job`, `instance`
**Range**: 0-1
**Description**: Whether the scrape was successful
**Example**: `up{job="consultantos-api"}`

### `scrape_duration_seconds`
**Type**: Gauge
**Labels**: `job`, `instance`
**Description**: Duration of the scrape in seconds

### `scrape_samples_post_metric_relabeling`
**Type**: Gauge
**Labels**: `job`, `instance`
**Description**: Number of samples after metric relabeling

## Query Examples

### SLA Monitoring

**99% uptime SLO**:
```
(sum(rate(consultantos_api_requests_total[5m])) - sum(rate(consultantos_api_requests_total{status=~"5.."}[5m]))) / sum(rate(consultantos_api_requests_total[5m])) > 0.99
```

**2 second p95 latency SLO**:
```
histogram_quantile(0.95, rate(consultantos_api_request_duration_seconds_bucket[5m])) < 2
```

### Agent Performance

**Total agent execution count last hour**:
```
sum(increase(consultantos_agent_executions_total[1h])) by (agent_name)
```

**Agent failure rate**:
```
rate(consultantos_agent_executions_total{status="failure"}[5m]) / rate(consultantos_agent_executions_total[5m])
```

### Data Source Health

**Data source uptime**:
```
consultantos_data_source_reliability{source_name="tavily"}
```

**API rate limits**:
```
rate(consultantos_data_source_errors_total{error_type="rate_limit"}[1h])
```

### Cache Performance

**Cache hit rate over time**:
```
consultantos_cache_hit_rate{cache_type="disk"}
```

**Cache size trend**:
```
consultantos_cache_size_bytes{cache_type="disk"}
```

### Monitoring System Health

**Monitor check success rate**:
```
(sum(rate(consultantos_monitor_checks_total{status="success"}[5m]))) / (sum(rate(consultantos_monitor_checks_total[5m])))
```

**Alert generation volume**:
```
rate(consultantos_alerts_generated_total[1m])
```

## Metric Cardinality

High-cardinality labels can cause performance issues. Current metric design limits cardinality:

| Metric | Label | Estimated Cardinality |
|--------|-------|----------------------|
| api_requests_total | endpoint | 20-50 |
| api_requests_total | method | 7 (GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS) |
| api_requests_total | status | 12 (various HTTP statuses) |
| agent_executions_total | agent_name | 5-10 |
| data_source_requests_total | source_name | 7 |
| monitor_checks_total | monitor_id | unbounded (user-created) |
| errors_total | component | 7 |

## Recording Rules

Suggested Prometheus recording rules for common queries:

```yaml
groups:
  - name: consultantos_rules
    interval: 15s
    rules:
      - record: api:success_rate
        expr: (sum(rate(consultantos_api_requests_total{status=~"2.."}[5m])) / sum(rate(consultantos_api_requests_total[5m])))

      - record: api:error_rate
        expr: (sum(rate(consultantos_api_requests_total{status=~"5.."}[5m])) / sum(rate(consultantos_api_requests_total[5m])))

      - record: api:p95_latency
        expr: histogram_quantile(0.95, rate(consultantos_api_request_duration_seconds_bucket[5m]))

      - record: agent:execution_rate
        expr: rate(consultantos_agent_executions_total[5m])

      - record: data_source:reliability
        expr: (sum(rate(consultantos_data_source_requests_total{status="success"}[5m])) by (source_name)) / (sum(rate(consultantos_data_source_requests_total[5m])) by (source_name))
```

## Retention and Storage

### Storage Requirements

- **Daily rate**: ~10-20MB per day for typical production load
- **Monthly**: ~300-600MB
- **Yearly**: ~3.6-7.2GB

Adjust retention policy based on storage capacity:

```yaml
# In prometheus.yml
--storage.tsdb.retention.time=15d  # Default: 15 days
```

### Purging Old Data

To manually purge old data:

1. Stop Prometheus
2. `promtool tsdb prune --retention 7d` (keep 7 days, delete older)
3. Restart Prometheus

## Integration Examples

### With External Systems

**Push to CloudMonitoring**:
```bash
docker run -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus \
  --config.file=/etc/prometheus/prometheus.yml \
  --storage.tsdb.path=/prometheus \
  --remote_write.url=https://monitoring.googleapis.com/...
```

**Scrape from Kubernetes**:
```yaml
- job_name: 'kubernetes-pods'
  kubernetes_sd_configs:
    - role: pod
  relabel_configs:
    - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
      action: keep
      regex: true
```

## Performance Tuning

### Reducing Memory Usage

1. Lower scrape frequency: `scrape_interval: 30s` (instead of 15s)
2. Reduce retention: `--storage.tsdb.retention.time=7d`
3. Remove unused metrics: Use metric relabeling to drop unused metrics
4. Increase heap size: Set `--query.max-samples` appropriately

### Improving Query Performance

1. Use recording rules for frequent queries
2. Limit query range for dashboards: 1h instead of 7d
3. Use aggregation: `sum by (job)` instead of per-instance
4. Cache results at application level
