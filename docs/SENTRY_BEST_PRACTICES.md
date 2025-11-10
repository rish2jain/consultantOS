# Sentry Best Practices for ConsultantOS

Production-ready patterns for error handling, performance monitoring, and security.

## Table of Contents

- [Error Handling Patterns](#error-handling-patterns)
- [Performance Monitoring](#performance-monitoring)
- [Security & Privacy](#security--privacy)
- [Alert Management](#alert-management)
- [Team Workflows](#team-workflows)
- [Cost Optimization](#cost-optimization)

## Error Handling Patterns

### Agent Error Handling

**Pattern**: Wrap agent execution with context

```python
from consultantos.observability import SentryIntegration

class CustomAgent(BaseAgent):
    async def _execute_internal(self, input_data):
        # Set agent context (inherited from BaseAgent.execute())
        # BaseAgent already wraps execution with Sentry transaction

        try:
            # Add operation-specific breadcrumbs
            SentryIntegration.add_breadcrumb(
                message=f"Fetching data from {data_source}",
                category="data_fetch",
                level="info",
                data={"source": data_source, "company": input_data["company"]}
            )

            result = await fetch_data(input_data)

            return {"success": True, "data": result}

        except ExternalAPIError as e:
            # Log specific external API failures
            SentryIntegration.add_breadcrumb(
                message=f"External API failed: {data_source}",
                category="data_fetch",
                level="error",
                data={"error": str(e), "source": data_source}
            )
            # Exception will be captured by BaseAgent
            raise
```

### API Error Handling

**Pattern**: Enrich errors with request context

```python
from fastapi import Request
from consultantos.observability import SentryIntegration

@app.get("/analyze/{report_id}")
async def get_report(report_id: str, request: Request):
    try:
        # Set user context if authenticated
        if request.state.user:
            SentryIntegration.set_user_context(
                user_id=request.state.user.id,
                tier=request.state.user.tier
            )

        # Add breadcrumb for operation start
        SentryIntegration.add_breadcrumb(
            message=f"Fetching report {report_id}",
            category="api",
            level="info",
            data={"report_id": report_id}
        )

        report = await db.get_report(report_id)

        if not report:
            # Log 404 as breadcrumb, not error
            SentryIntegration.add_breadcrumb(
                message=f"Report not found: {report_id}",
                category="api",
                level="warning"
            )
            raise HTTPException(status_code=404, detail="Report not found")

        return report

    except HTTPException:
        # Don't capture expected HTTPExceptions in Sentry
        raise
    except Exception as e:
        # Unexpected errors are captured by global exception handler
        raise
```

### Monitor Error Handling

**Pattern**: Track error counts and pause on repeated failures

```python
# Already implemented in IntelligenceMonitor.check_for_updates()

try:
    # Monitor check logic
    ...
except Exception as e:
    # Increment error count
    monitor.error_count += 1
    monitor.last_error = str(e)

    # Pause after 5 consecutive failures
    if monitor.error_count >= 5:
        monitor.status = MonitorStatus.ERROR

        # Send critical alert to Sentry
        SentryIntegration.capture_message(
            f"Monitor paused: {monitor.id} ({monitor.company})",
            level="error"
        )

    # Capture error with context
    SentryIntegration.capture_exception(
        e,
        tag_monitor_id=monitor.id,
        tag_company=monitor.company,
        tag_error_count=monitor.error_count
    )

    raise
```

## Performance Monitoring

### Transaction Best Practices

**DO**: Use transactions for critical paths

```python
# Good: Track critical operations
transaction = SentryIntegration.start_transaction(
    name="generate_strategic_report",
    op="analysis"
)
transaction.__enter__()

try:
    report = await orchestrator.run_full_analysis(request)
    transaction.set_measurement("agents_executed", 5)
    transaction.set_measurement("total_execution_time", elapsed_time, "second")
    transaction.__exit__(None, None, None)
except Exception as e:
    transaction.__exit__(type(e), e, None)
    raise
```

**DON'T**: Create transactions for trivial operations

```python
# Bad: Excessive transactions for simple operations
transaction = SentryIntegration.start_transaction(
    name="get_user_name",  # Too granular
    op="database"
)
```

### Performance Targets

| Operation | Target (p95) | Action if Exceeded |
|-----------|--------------|-------------------|
| API Request | < 2s | Add caching, optimize queries |
| Agent Execution | < 5s | Review data source timeouts |
| Monitor Check | < 10s | Reduce analysis depth |
| PDF Generation | < 3s | Optimize chart rendering |

### Sampling Strategy

**Development**: 100% sampling for debugging

```bash
SENTRY_ENVIRONMENT=development
SENTRY_TRACES_SAMPLE_RATE=1.0
```

**Staging**: 30% sampling for realistic testing

```bash
SENTRY_ENVIRONMENT=staging
SENTRY_TRACES_SAMPLE_RATE=0.3
```

**Production**: 10% sampling for cost efficiency

```bash
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1
```

**High-Traffic Production**: 5% or lower

```bash
# > 10,000 requests/day
SENTRY_TRACES_SAMPLE_RATE=0.05
```

## Security & Privacy

### PII Protection

**Always sanitize before logging**:

```python
# Good: Sanitize before breadcrumb
SentryIntegration.add_breadcrumb(
    message=f"User registered: {user.id}",  # ID only, no email
    category="auth",
    data={"user_id": user.id, "tier": user.tier}
)

# Bad: PII in breadcrumb
SentryIntegration.add_breadcrumb(
    message=f"User registered: {user.email}",  # Email leaked!
    category="auth"
)
```

**Verify automatic sanitization**:

```python
# Test PII patterns
from consultantos.observability.sentry_integration import PII_PATTERNS

test_string = "User email: user@example.com, API key: sk_test_123"
for pattern_name, pattern in PII_PATTERNS.items():
    if pattern.search(test_string):
        print(f"Detected {pattern_name} in: {test_string}")
```

**Custom PII patterns** (add to `sentry_integration.py`):

```python
# Add company-specific patterns
PII_PATTERNS["internal_id"] = re.compile(r"\bID-\d{6,}\b")
PII_PATTERNS["ssn"] = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
```

### Sensitive Data Handling

**Never log**:
- User passwords (even hashed)
- Full API keys
- Credit card numbers
- Session tokens
- OAuth secrets

**Safe to log**:
- User IDs (UUID, hash)
- Company names (public)
- Error types
- Performance metrics
- Feature flags

### Security Incidents

**Suspected data leak**:

1. **Immediate**: Disable Sentry capture
   ```bash
   # Emergency shutdown
   unset SENTRY_DSN
   systemctl restart consultantos
   ```

2. **Investigation**: Review events in Sentry UI
   - Search for PII patterns
   - Check breadcrumbs for leaks
   - Verify sanitization worked

3. **Remediation**: Delete leaked events
   - Sentry UI → Issue → Delete & Discard
   - Update PII patterns
   - Add regression test

4. **Prevention**: Add test coverage
   ```python
   def test_no_pii_in_events():
       """Verify no PII in captured events"""
       # Trigger error with PII data
       integration = SentryIntegration()
       event = {
           "message": "Error for user@example.com",
           "extra": {"email": "test@test.com"}
       }
       hint = {}

       # Process through before_send
       result = integration._before_send(event, hint)

       # Verify PII was sanitized
       assert "user@example.com" not in str(result)
       assert result["extra"]["email"] == "[REDACTED]"
   ```

## Alert Management

### Alert Fatigue Prevention

**Problem**: Too many alerts = ignored alerts

**Solution**: Tiered alerting

```yaml
# Critical (immediate action)
- Agent timeout rate > 5% in 5 minutes
- Monitor system down > 10 minutes
- Error rate > 20/minute

# Warning (review within 1 hour)
- Error rate > 5/minute
- P95 latency > 3 seconds
- Monitor failure rate > 2%

# Info (daily review)
- New error types
- Performance regressions
- Unusual traffic patterns
```

### Alert Channels

**PagerDuty/SMS**: Critical production issues
- System outages
- Data corruption
- Security incidents

**Slack**: Warnings and operational issues
- Performance degradation
- High error rates
- Monitor failures

**Email**: Info and daily summaries
- New error types
- Weekly performance reports
- Release health

### On-Call Best Practices

1. **Document runbooks** for common alerts
2. **Set quiet hours** (10pm-6am) for non-critical alerts
3. **Escalate** after 15 minutes if no response
4. **Post-mortem** all critical incidents
5. **Review alerts weekly** to tune thresholds

## Team Workflows

### Development Workflow

**Before committing**:
```bash
# Test error capture locally
pytest tests/test_sentry_integration.py -v

# Verify no PII leaks
grep -r "email" tests/test_sentry_integration.py
```

**Before deploying**:
```bash
# Set release version
export SENTRY_RELEASE=$(git rev-parse --short HEAD)

# Deploy with release tracking
gcloud run deploy --set-env-vars SENTRY_RELEASE=$SENTRY_RELEASE
```

**After deploying**:
1. Monitor Sentry for new errors
2. Check release health dashboard
3. Verify performance metrics stable

### Code Review Checklist

**Error Handling**:
- [ ] Exceptions have context (breadcrumbs)
- [ ] No PII in error messages
- [ ] Appropriate error level (error vs warning)
- [ ] Custom tags for grouping

**Performance**:
- [ ] Transactions for critical paths only
- [ ] Measurements added for key metrics
- [ ] No nested transactions (causes overhead)

**Testing**:
- [ ] Tests for new error paths
- [ ] PII sanitization verified
- [ ] Alert thresholds reviewed

### Incident Response

**1. Triage** (0-5 minutes):
- Assess impact (users affected, revenue lost)
- Identify root cause (Sentry issue → stack trace)
- Communicate to stakeholders

**2. Mitigation** (5-30 minutes):
- Apply hotfix or rollback
- Verify fix in Sentry (error rate drops)
- Monitor for regressions

**3. Resolution** (30-60 minutes):
- Document root cause
- Create follow-up tasks
- Update runbook

**4. Post-Mortem** (within 24 hours):
- Timeline of events
- Action items (prevent recurrence)
- Lessons learned

## Cost Optimization

### Sentry Quota Management

**Understand pricing**:
- Events: Errors, transactions, replays
- Data retention: 90 days default
- On-demand pricing: $0.000045 per event

**Optimize quota usage**:

```python
# 1. Sample aggressively in production
SENTRY_TRACES_SAMPLE_RATE=0.05  # 5% = 20x reduction

# 2. Filter noisy errors
def before_send(event, hint):
    # Ignore expected errors
    if "UserCancelled" in str(hint.get("exc_info")):
        return None  # Don't send to Sentry
    return event

# 3. Rate limit per error type
SENTRY_MAX_EVENTS_PER_ISSUE = 50  # Cap at 50 events per unique error
```

### Cost Projections

| Traffic | Sampling | Events/Month | Cost/Month |
|---------|----------|--------------|------------|
| 1M requests | 100% | 1M | $45 |
| 1M requests | 10% | 100K | $4.50 |
| 10M requests | 10% | 1M | $45 |
| 10M requests | 5% | 500K | $22.50 |

**Recommendation**: Start with 10% sampling, adjust based on budget and value.

### Monitoring Quota Usage

**Sentry UI**: Settings → Quota → Usage Stats

**Alerts for quota**:
- 80% quota used (warning)
- 90% quota used (critical)
- Quota exceeded (emergency)

**Auto-scaling sampling**:

```python
# Adjust sampling based on quota usage
current_usage = get_sentry_quota_usage()

if current_usage > 0.8:
    # Reduce sampling temporarily
    settings.sentry_traces_sample_rate = 0.05
elif current_usage < 0.5:
    # Increase sampling for better visibility
    settings.sentry_traces_sample_rate = 0.15
```

## Appendix

### Custom Tags Reference

| Tag | Values | Usage |
|-----|--------|-------|
| `agent_name` | ResearchAgent, FinancialAgent, etc. | Agent execution errors |
| `monitor_id` | UUID | Monitor-related errors |
| `company` | Company name | Business context |
| `industry` | Industry sector | Business context |
| `endpoint` | API path | API endpoint errors |
| `method` | GET, POST, etc. | HTTP method |
| `error_type` | ValueError, TimeoutError, etc. | Error classification |
| `environment` | dev, staging, prod | Deployment environment |

### Useful Sentry Queries

**Find timeouts**:
```
error.type:TimeoutError environment:production
```

**Agent failures by company**:
```
tags.agent_name:FinancialAgent tags.company:Tesla
```

**High-impact errors** (>100 users affected):
```
event.count:>100 environment:production
```

**Performance regressions** (p95 > 3s):
```
transaction.duration:>3000 transaction.op:agent.execution
```
