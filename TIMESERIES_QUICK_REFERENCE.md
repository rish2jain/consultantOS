# Time-Series Optimization Quick Reference

Fast reference for common time-series operations in ConsultantOS monitoring.

## Setup (One-Time)

```bash
# 1. Deploy Firestore indexes
firebase deploy --only firestore:indexes

# 2. Run migration (dry-run first)
python scripts/migrate_timeseries.py --all --days 90 --dry-run
python scripts/migrate_timeseries.py --all --days 90
```

## Common Operations

### Get Historical Snapshots

```python
# Last 7 days
snapshots = await monitor_system.timeseries_optimizer.get_snapshots_in_range(
    monitor_id="monitor-123",
    start_time=datetime.utcnow() - timedelta(days=7),
    end_time=datetime.utcnow(),
    limit=100,  # Optional pagination
)

# Latest snapshot
latest = await monitor_system.timeseries_optimizer.get_latest_snapshot("monitor-123")
```

### Get Aggregated Analytics

```python
from consultantos.monitoring.snapshot_aggregator import AggregationPeriod

# Get daily aggregation
daily = await monitor_system.snapshot_aggregator.get_aggregation(
    monitor_id="monitor-123",
    period=AggregationPeriod.DAILY,
    start_time=datetime(2025, 11, 9),
)

# Access metrics
revenue_stats = daily.metrics_summary["revenue"]
# → {min: 80B, max: 85B, avg: 82.5B, stddev: 1.2B, count: 24}

# Check trends
revenue_trend = daily.trends["revenue"]  # "up", "down", or "stable"

# Get significant changes
for change in daily.significant_changes:
    print(f"{change['metric']} changed by {change['change_pct']}%")
```

### Get 30-Day Trends

```python
# All metrics
trend_data = await monitor_system.timeseries_optimizer.get_trend_data(
    monitor_id="monitor-123",
    days=30,
)

# Specific metric
revenue_trend = await monitor_system.timeseries_optimizer.get_trend_data(
    monitor_id="monitor-123",
    days=30,
    metric_name="revenue",
)

# Extract values for plotting
timestamps = [point["timestamp"] for point in trend_data]
values = [point["value"] for point in trend_data]
```

### Compare to Last Week/Month

```python
# Get snapshot from 7 days ago (±6 hours tolerance)
last_week = await monitor_system.timeseries_optimizer.get_snapshot_at_time(
    monitor_id="monitor-123",
    target_time=datetime.utcnow() - timedelta(days=7),
    tolerance_hours=6,
)

# Get snapshot from 30 days ago
last_month = await monitor_system.timeseries_optimizer.get_snapshot_at_time(
    monitor_id="monitor-123",
    target_time=datetime.utcnow() - timedelta(days=30),
    tolerance_hours=24,
)

# Compare metrics
revenue_change = (
    (current.financial_metrics["revenue"] - last_month.financial_metrics["revenue"])
    / last_month.financial_metrics["revenue"]
    * 100
)
print(f"Revenue changed {revenue_change:.1f}% vs last month")
```

### Cleanup Old Data

```python
# Dry run (preview)
count = await monitor_system.timeseries_optimizer.cleanup_old_snapshots(
    monitor_id="monitor-123",
    retention_days=90,
    dry_run=True,
)
print(f"Would delete {count} snapshots")

# Actual cleanup
deleted = await monitor_system.timeseries_optimizer.cleanup_old_snapshots(
    monitor_id="monitor-123",
    retention_days=90,
    dry_run=False,
)
print(f"Deleted {deleted} snapshots")
```

## Performance Tips

### Use Aggregations for Dashboards

❌ **Slow** (queries raw snapshots):
```python
# Don't do this for dashboard displays
snapshots = await optimizer.get_snapshots_in_range(monitor_id, start, end)
revenue_avg = sum(s.financial_metrics["revenue"] for s in snapshots) / len(snapshots)
```

✅ **Fast** (uses pre-aggregated data):
```python
# Do this instead
daily_agg = await aggregator.get_aggregation(monitor_id, AggregationPeriod.DAILY, start)
revenue_avg = daily_agg.metrics_summary["revenue"]["avg"]
```

### Pagination for Large Queries

❌ **Memory intensive**:
```python
# All snapshots at once
all_snapshots = await optimizer.get_snapshots_in_range(monitor_id, start, end)
```

✅ **Memory efficient**:
```python
# Paginated retrieval
snapshots_page1 = await optimizer.get_snapshots_in_range(monitor_id, start, end, limit=100)
snapshots_page2 = await optimizer.get_snapshots_in_range(monitor_id, start, end, limit=100, offset=100)
```

### Batch Writes for High Frequency

❌ **Individual writes**:
```python
for snapshot in snapshots:
    await optimizer.store_snapshot(snapshot)  # Slow
```

✅ **Batched writes**:
```python
for snapshot in snapshots:
    await optimizer.store_snapshot(snapshot, batch=True)  # Fast

# Flush at end
await optimizer.flush_pending_writes()
```

## Monitoring Stats

```python
# Get optimizer statistics
stats = monitor_system.timeseries_optimizer.get_optimizer_stats()

print(f"Pending writes: {stats['pending_writes']}")
print(f"Cache entries: {stats['cache_entries']}")
print(f"Batch size: {stats['batch_size']}")
print(f"Cache TTL: {stats['cache_ttl_seconds']}s")

# Track in production monitoring
metrics.gauge("timeseries.pending_writes", stats["pending_writes"])
metrics.gauge("timeseries.cache_hit_rate", calculate_hit_rate())
```

## Troubleshooting

### Query Slow?

```bash
# 1. Check indexes deployed
firebase deploy --only firestore:indexes

# 2. Enable debug logging
import logging
logging.getLogger("consultantos.monitoring").setLevel(logging.DEBUG)

# 3. Use pagination
snapshots = await optimizer.get_snapshots_in_range(..., limit=100)
```

### High Storage?

```python
# 1. Check compression is enabled
await optimizer.store_snapshot(snapshot, compress=True)  # Default

# 2. Implement retention
await optimizer.cleanup_old_snapshots(monitor_id, retention_days=90)

# 3. Use aggregations instead of raw snapshots
```

### Cache Not Working?

```python
# 1. Verify cache service configured
monitor_system = IntelligenceMonitor(
    ...,
    cache_service=redis_cache,  # Must be provided
)

# 2. Check cache TTL
# Default: 300 seconds (5 minutes)
# Increase if needed:
optimizer.cache_ttl = 600  # 10 minutes
```

## Performance Reference

| Operation | Expected Time | Notes |
|-----------|--------------|-------|
| Latest snapshot | ~45ms | Cached after first access |
| 7-day range (uncached) | ~120ms | 168 snapshots |
| 7-day range (cached) | ~3ms | Subsequent access |
| 30-day range | ~280ms | 720 snapshots |
| Daily aggregation | ~60ms | Pre-computed |
| Weekly aggregation | ~140ms | Pre-computed |
| Compression | >50 ops/sec | Automatic for >1KB |
| Batch write (10) | 500 ops/sec | 2ms per snapshot |

## Storage Reference

| Data Type | Size | Compressed | Savings |
|-----------|------|------------|---------|
| Small snapshot | 850 B | Not compressed | 0% |
| Medium snapshot | 2 KB | 820 B | 60% |
| Large snapshot | 5 KB | 1 KB | 80% |
| Porter analysis | 3.2 KB | 980 B | 69% |

## Retention Policies

| Monitor Frequency | Raw Snapshots | Daily Agg | Weekly Agg | Monthly Agg |
|-------------------|--------------|-----------|------------|-------------|
| Hourly | 90 days | 2 years | 2 years | 5 years |
| Daily | 180 days | 2 years | 2 years | 5 years |
| Weekly | 1 year | N/A | 2 years | 5 years |
| Monthly | 2 years | N/A | N/A | 5 years |

## Full Documentation

**Comprehensive Guide**: `docs/TIMESERIES_OPTIMIZATION.md`
**Implementation Summary**: `TIMESERIES_IMPLEMENTATION_SUMMARY.md`
