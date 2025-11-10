# Sentry Integration Guide

Comprehensive guide to Sentry error tracking and performance monitoring in ConsultantOS.

## Table of Contents

- [Overview](#overview)
- [Setup](#setup)
- [Configuration](#configuration)
- [Features](#features)
- [Usage Examples](#usage-examples)
- [Monitoring Dashboard](#monitoring-dashboard)
- [Alerting Rules](#alerting-rules)
- [Troubleshooting](#troubleshooting)

## Overview

ConsultantOS integrates Sentry for:

- **Error Tracking**: Centralized error capture with rich context
- **Performance Monitoring**: Transaction tracing for API endpoints and agents
- **Context Enrichment**: User, monitor, agent, and company context
- **PII Sanitization**: Automatic removal of sensitive data
- **Custom Fingerprinting**: Intelligent error grouping
- **Release Tracking**: Git SHA-based deployment tracking

## Setup

### 1. Create Sentry Project

1. Sign up at [sentry.io](https://sentry.io)
2. Create a new project (Python)
3. Copy the DSN (Data Source Name)

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Installs `sentry-sdk>=1.38.0` with FastAPI integration.

### 3. Configure Environment Variables

Add to `.env` file:

```bash
# Required
SENTRY_DSN=https://your-dsn@o12345.ingest.sentry.io/67890

# Optional (with defaults)
SENTRY_ENVIRONMENT=production        # dev/staging/prod
SENTRY_TRACES_SAMPLE_RATE=0.1       # 10% sampling in production
SENTRY_RELEASE=<git-sha>            # Auto-detected if not set
```

### 4. Verify Integration

Start the application:

```bash
python main.py
```

Check logs for:
```
INFO: Sentry initialized: environment=production, release=abc1234
```

## Configuration

### Environment-Based Sampling

Sentry automatically adjusts performance sampling based on environment:

| Environment | Sample Rate | Usage |
|-------------|-------------|-------|
| `development` | 100% (1.0) | Full tracing for debugging |
| `staging` | 30% (0.3) | Balanced monitoring |
| `production` | 10% (0.1) | Low overhead, high volume |

Override with `SENTRY_TRACES_SAMPLE_RATE`:

```bash
# Custom sampling for production
SENTRY_TRACES_SAMPLE_RATE=0.05  # 5% sampling
```

### Configuration Settings

All settings in `consultantos/config.py`:

```python
class Settings(BaseSettings):
    # Sentry Configuration
    sentry_dsn: Optional[str] = None
    sentry_environment: Optional[str] = None  # Defaults to 'environment'
    sentry_traces_sample_rate: Optional[float] = None  # Auto-set by environment
    sentry_release: Optional[str] = None  # Git SHA recommended
    enable_sentry_profiling: bool = False
    sentry_profiles_sample_rate: float = 0.1
```

## Features

### 1. Error Tracking

**Automatic Capture**:
- All unhandled exceptions
- Agent execution failures
- Monitoring system errors
- API endpoint errors

**Context Enrichment**:
```python
# User context
SentryIntegration.set_user_context(
    user_id="user123",
    tier="pro"
)

# Monitor context
SentryIntegration.set_monitor_context(
    monitor_id="mon456",
    company="Tesla",
    industry="Automotive"
)

# Agent context
SentryIntegration.set_agent_context(
    agent_name="FinancialAgent",
    data_sources=["yfinance", "finnhub"],
    timeout=60
)
```

### 2. Performance Monitoring

**Agent Performance Tracking**:

All agents automatically track:
- Execution time
- Success/failure rate
- Timeout events

Example Sentry transaction:
```
Transaction: FinancialAgent.execute
Duration: 2.8s
Tags: agent_name=FinancialAgent, company=Tesla
Measurements: execution_time=2.8s
```

**API Endpoint Tracking**:

FastAPI integration automatically tracks:
- Request duration
- Status codes
- URL patterns

### 3. Custom Error Fingerprinting

Errors are intelligently grouped by:

- **Agent Errors**: `ErrorType + agent:{agent_name}`
- **API Errors**: `ErrorType + endpoint:{path}`
- **Monitor Errors**: `ErrorType + monitor:{monitor_id}`

Example:
```
Fingerprint: ["ValueError", "agent:FinancialAgent"]
Fingerprint: ["TimeoutError", "monitor:mon123"]
```

### 4. PII Sanitization

**Automatic Redaction**:
- Emails: `user@example.com` → `[EMAIL_REDACTED]`
- API Keys: `sk_test_123` → `[API_KEY_REDACTED]`
- Passwords: `password: secret` → `[REDACTED]`
- Credit Cards: `4111-1111-1111-1111` → `[CREDIT_CARD_REDACTED]`

**Sensitive Fields**:
```python
# Automatically redacted in all Sentry events
REDACTED_FIELDS = [
    "email",
    "password",
    "api_key",
    "token",
    "secret",
    "credit_card"
]
```

### 5. Breadcrumbs

Breadcrumbs provide debugging context:

```python
# Agent execution breadcrumbs
SentryIntegration.add_breadcrumb(
    message="Starting FinancialAgent execution",
    category="agent",
    level="info",
    data={"company": "Tesla", "industry": "Automotive"}
)

# Monitor check breadcrumbs
SentryIntegration.add_breadcrumb(
    message="Checking monitor for Tesla",
    category="monitor",
    level="info",
    data={"frequency": "daily", "alert_threshold": 0.7}
)
```

## Usage Examples

### Capturing Custom Errors

```python
from consultantos.observability import SentryIntegration

try:
    # Your code
    risky_operation()
except Exception as e:
    # Capture with custom tags
    SentryIntegration.capture_exception(
        e,
        tag_operation="data_fetch",
        tag_source="external_api",
        extra_request_id="req123"
    )
    raise
```

### Performance Transactions

```python
from consultantos.observability import SentryIntegration

# Start transaction
transaction = SentryIntegration.start_transaction(
    name="complex_operation",
    op="background.task"
)

try:
    transaction.__enter__()

    # Your operation
    result = perform_complex_task()

    # Record custom measurements
    transaction.set_measurement("items_processed", 150)
    transaction.set_measurement("cache_hit_rate", 0.85, "ratio")

    transaction.__exit__(None, None, None)
except Exception as e:
    transaction.__exit__(type(e), e, None)
    raise
```

### Context-Aware Logging

```python
from consultantos.observability import SentryIntegration

# Set context for entire request
SentryIntegration.set_user_context(user_id="user123", tier="enterprise")
SentryIntegration.set_monitor_context(
    monitor_id="mon456",
    company="Tesla",
    industry="Automotive"
)

# All subsequent errors will include this context
try:
    monitor.check_for_updates()
except Exception as e:
    # Error captured with user + monitor context
    SentryIntegration.capture_exception(e)
```

## Monitoring Dashboard

### Sentry Dashboard Features

1. **Error Dashboard**:
   - Error frequency trends
   - New vs. recurring errors
   - Error impact by user count
   - Stack trace browser

2. **Performance Dashboard**:
   - Transaction duration (p50, p95, p99)
   - Throughput (requests/min)
   - Apdex score
   - Slowest transactions

3. **Release Dashboard**:
   - Errors by release (Git SHA)
   - New issues in release
   - Release health score

### Key Metrics to Monitor

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Error Rate | < 1% | > 5% |
| P95 Latency | < 2s | > 3s |
| Agent Timeout Rate | < 0.1% | > 1% |
| Monitor Failure Rate | < 0.5% | > 2% |

## Alerting Rules

### Recommended Alert Configuration

**Critical Alerts** (PagerDuty/SMS):
```yaml
- name: High Error Rate
  condition: errors > 10 per minute
  action: page_on_call

- name: Agent Failures
  condition: FinancialAgent errors > 5 in 5 minutes
  action: page_on_call

- name: Monitor System Down
  condition: no monitor checks in 10 minutes
  action: page_on_call
```

**Warning Alerts** (Email/Slack):
```yaml
- name: Elevated Error Rate
  condition: errors > 5 per minute
  action: send_slack

- name: Performance Degradation
  condition: p95_latency > 3 seconds
  action: send_slack

- name: Monitor Check Failures
  condition: monitor_error_count >= 3
  action: send_email
```

**Info Alerts** (Dashboard Only):
```yaml
- name: New Error Type
  condition: first_seen_error
  action: dashboard_only

- name: Deployment Event
  condition: new_release
  action: dashboard_only
```

### Setting Up Alerts in Sentry

1. Navigate to **Alerts** → **Create Alert Rule**
2. Choose alert type:
   - **Issues**: Error frequency, new errors
   - **Metric**: Performance thresholds
   - **Change**: Release health
3. Set conditions (threshold, timeframe)
4. Configure actions (email, Slack, webhook)
5. Test alert rule

## Troubleshooting

### Common Issues

**1. Sentry Not Capturing Errors**

Check:
```bash
# Verify DSN is set
echo $SENTRY_DSN

# Check logs for initialization
grep "Sentry initialized" logs/app.log

# Test error capture
python -c "
from consultantos.observability import SentryIntegration
SentryIntegration.capture_message('Test message', level='info')
print('Test message sent to Sentry')
"
```

**2. High Performance Overhead**

Reduce sampling rate:
```bash
# Lower to 5% sampling
SENTRY_TRACES_SAMPLE_RATE=0.05
```

Or disable profiling:
```bash
# Disable profiling (keep tracing)
SENTRY_ENABLE_PROFILING=false
```

**3. PII Leaking in Events**

Verify sanitization:
```python
from consultantos.observability.sentry_integration import SentryIntegration

integration = SentryIntegration()

# Test sanitization
test_data = {"email": "user@example.com", "password": "secret"}
sanitized = integration._sanitize_dict(test_data)
print(sanitized)
# Expected: {'email': '[REDACTED]', 'password': '[REDACTED]'}
```

**4. Events Not Grouped Correctly**

Check fingerprints in Sentry UI:
- Navigate to issue → **Tags** → `fingerprint`
- Verify grouping logic matches expectations

Customize fingerprinting in `sentry_integration.py`:
```python
def _add_custom_fingerprint(self, event, hint):
    # Add custom grouping logic
    fingerprint = ["custom_group"]
    if "special_field" in event:
        fingerprint.append(event["special_field"])
    event["fingerprint"] = fingerprint
    return event
```

### Debug Mode

Enable verbose logging:
```python
import logging
logging.getLogger("sentry_sdk").setLevel(logging.DEBUG)
```

Check Sentry SDK status:
```python
import sentry_sdk
print(f"Sentry initialized: {sentry_sdk.Hub.current.client is not None}")
print(f"DSN: {sentry_sdk.Hub.current.client.dsn if sentry_sdk.Hub.current.client else 'Not set'}")
```

### Performance Testing

Verify transaction capture:
```bash
# Generate test transactions
python -c "
from consultantos.observability import SentryIntegration
import time

transaction = SentryIntegration.start_transaction(
    name='test_transaction',
    op='test'
)
transaction.__enter__()
time.sleep(0.5)  # Simulate work
transaction.__exit__(None, None, None)
print('Test transaction sent')
"
```

Check Sentry Performance dashboard after 5-10 minutes.

## Best Practices

1. **Always set context** before operations that might fail
2. **Use breadcrumbs** liberally for debugging trails
3. **Monitor Sentry quota** to avoid surprise bills
4. **Review new errors** within 24 hours of deployment
5. **Set up on-call rotation** for critical alerts
6. **Test alerts** in staging before production
7. **Document custom tags** for team consistency
8. **Review PII sanitization** regularly

## Support

- **Sentry Documentation**: https://docs.sentry.io
- **Sentry Discord**: https://discord.gg/sentry
- **Internal Issues**: See `docs/SENTRY_BEST_PRACTICES.md`
