# Celery Operations Guide

## Overview

This guide covers day-to-day operations for the Celery + Redis task queue system.

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   FastAPI   │────▶│    Redis    │────▶│   Celery    │
│  (Enqueue)  │     │  (Broker)   │     │   Worker    │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   Celery    │
                    │    Beat     │
                    │ (Scheduler) │
                    └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   Flower    │
                    │ (Monitoring)│
                    └─────────────┘
```

## Task Types and Priorities

### Priority Levels

| Priority | Queue | Use Case | Rate Limit |
|----------|-------|----------|------------|
| 10 | `critical` | User-triggered checks | No limit |
| 8  | `high` | Alert delivery | 30/min |
| 5  | `normal` | Scheduled monitor checks | 10/min |
| 2-3 | `low` | Background maintenance | No limit |

### Task Categories

**Monitor Checking** (Normal Priority):
- `check_monitor_task` - Scheduled monitor checks
- `check_scheduled_monitors_task` - Batch scheduled checks
- Rate limit: 10/minute

**Alert Processing** (High Priority):
- `process_alert_task` - Send alerts via email/Slack
- `send_alert_webhook` - Webhook delivery
- Rate limit: 30/minute

**Analysis** (Normal Priority):
- `run_analysis_task` - Full competitive analysis
- Rate limit: 5/minute

**Maintenance** (Low Priority):
- `aggregate_snapshots_task` - Daily at 2 AM
- `cleanup_old_data_task` - Daily at 3 AM
- `train_anomaly_model_task` - Weekly on Sunday at 4 AM

## Starting and Stopping Services

### Local Development

**Start all services**:

```bash
# Using Docker Compose (recommended)
docker-compose -f docker-compose.celery.yml up -d

# Or start individually
./scripts/start_celery_worker.sh &
./scripts/start_celery_beat.sh &
celery -A consultantos.jobs.celery_app flower --port=5555 &
```

**Stop services**:

```bash
# Docker Compose
docker-compose -f docker-compose.celery.yml down

# Or stop individual processes
pkill -f "celery.*worker"
pkill -f "celery.*beat"
pkill -f "celery.*flower"
```

**Restart worker** (reload code changes):

```bash
# Docker Compose
docker-compose -f docker-compose.celery.yml restart celery-worker

# Direct execution
pkill -HUP -f "celery.*worker"  # Graceful restart
```

### Production (Cloud Run)

**Deploy worker**:

```bash
gcloud run deploy consultantos-worker \
  --source . \
  --region us-central1 \
  --set-env-vars "REDIS_URL=${REDIS_URL}"
```

**Scale workers**:

```bash
# Auto-scale based on load
gcloud run services update consultantos-worker \
  --min-instances=1 \
  --max-instances=10 \
  --cpu=2 \
  --memory=2Gi
```

## Monitoring

### Flower UI

Access: http://localhost:5555

**Key Metrics**:
- Active tasks: Currently executing
- Scheduled tasks: Queued for execution
- Completed tasks: Successfully finished
- Failed tasks: Errors encountered
- Workers: Active worker instances

**Views**:
- **Tasks**: Real-time task execution
- **Workers**: Worker status and configuration
- **Broker**: Queue depths and message rates
- **Monitor**: Live task timeline

### Prometheus Metrics

Available metrics:

```
# Task execution counters
celery_task_total{task_name="...",status="success|failure|retry"}

# Task duration histogram
celery_task_duration_seconds{task_name="..."}

# Retry counters
celery_task_retries_total{task_name="..."}

# Dead letter queue size
celery_dead_letter_queue_size{queue_name="..."}

# Active tasks gauge
celery_active_tasks{queue_name="..."}
```

**Query examples**:

```promql
# Task success rate
sum(rate(celery_task_total{status="success"}[5m])) / sum(rate(celery_task_total[5m]))

# Average task duration
avg(celery_task_duration_seconds)

# Dead letter queue alerts
celery_dead_letter_queue_size > 10
```

### CLI Inspection

**Check worker status**:

```bash
celery -A consultantos.jobs.celery_app inspect active
celery -A consultantos.jobs.celery_app inspect stats
celery -A consultantos.jobs.celery_app inspect registered
```

**Check queues**:

```bash
celery -A consultantos.jobs.celery_app inspect active_queues
celery -A consultantos.jobs.celery_app inspect reserved
```

**Check scheduled tasks**:

```bash
celery -A consultantos.jobs.celery_app inspect scheduled
```

## Dead Letter Queue Management

### Inspect Dead Letter Queue

**Using Python**:

```python
from consultantos.jobs.task_monitor import get_dlq_monitor

dlq_monitor = get_dlq_monitor()

# Get queue sizes
queue_sizes = dlq_monitor.get_all_dead_letter_queues()
print(f"Dead letter queues: {queue_sizes}")

# Inspect failed tasks
failed_tasks = dlq_monitor.inspect_dead_letter_queue("critical.dead", limit=10)
for task in failed_tasks:
    print(f"Task ID: {task['task_id']}")
    print(f"Task Name: {task['task_name']}")
    print(f"Exception: {task['exception']}")
    print(f"Failed At: {task['failed_at']}")
    print("---")
```

**Using Flower UI**:
1. Navigate to http://localhost:5555
2. Go to "Broker" tab
3. View dead letter queues (`.dead` suffix)

### Retry Failed Tasks

**Option 1: Requeue manually**:

```python
from consultantos.jobs.tasks import check_monitor_task

# Requeue failed monitor check
check_monitor_task.apply_async(
    args=["monitor_123"],
    priority=5,
    queue="normal",
)
```

**Option 2: Bulk requeue** (for systematic issues):

```python
from consultantos.jobs.celery_app import app

# Get failed tasks from DLQ
failed_tasks = dlq_monitor.inspect_dead_letter_queue("normal.dead", limit=100)

# Requeue each task
for task in failed_tasks:
    # Extract task details and requeue
    task_name = task["task_name"]
    args = task["args"]
    kwargs = task["kwargs"]

    # Send to original queue
    app.send_task(
        task_name,
        args=args,
        kwargs=kwargs,
        queue="normal",
        priority=5,
    )
```

### Purge Dead Letter Queue

**WARNING**: This permanently deletes failed tasks.

```python
from consultantos.jobs.task_monitor import get_dlq_monitor

dlq_monitor = get_dlq_monitor()

# Purge specific queue
purged_count = dlq_monitor.purge_dead_letter_queue("critical.dead")
print(f"Purged {purged_count} messages")
```

## Task Management

### Queue a Task Manually

```python
from consultantos.jobs.tasks import (
    check_monitor_task,
    process_alert_task,
    run_analysis_task,
)

# Queue monitor check
result = check_monitor_task.apply_async(
    args=["monitor_123"],
    priority=5,
    queue="normal",
)

# Queue with custom countdown (delay)
result = check_monitor_task.apply_async(
    args=["monitor_123"],
    countdown=300,  # Delay 5 minutes
    priority=5,
    queue="normal",
)

# Queue with ETA (specific time)
from datetime import datetime, timedelta
eta = datetime.utcnow() + timedelta(hours=1)

result = check_monitor_task.apply_async(
    args=["monitor_123"],
    eta=eta,
    priority=5,
    queue="normal",
)
```

### Cancel a Task

```python
from celery.result import AsyncResult

# Get task result
result = AsyncResult("task_id")

# Cancel task (if not started)
result.revoke(terminate=False)

# Terminate running task (use with caution)
result.revoke(terminate=True)
```

### View Task Status

```python
from celery.result import AsyncResult

result = AsyncResult("task_id")

# Check status
print(f"Status: {result.status}")  # PENDING, STARTED, SUCCESS, FAILURE

# Get result (blocks until complete)
try:
    task_result = result.get(timeout=60)
    print(f"Result: {task_result}")
except Exception as e:
    print(f"Error: {e}")

# Check if successful
if result.successful():
    print(f"Task succeeded: {result.result}")
elif result.failed():
    print(f"Task failed: {result.info}")
```

## Performance Tuning

### Worker Concurrency

**Adjust worker concurrency**:

```bash
# Low traffic (1-2 concurrent tasks)
CONCURRENCY=2 ./scripts/start_celery_worker.sh

# Medium traffic (4-8 concurrent tasks)
CONCURRENCY=4 ./scripts/start_celery_worker.sh

# High traffic (8-16 concurrent tasks)
CONCURRENCY=8 ./scripts/start_celery_worker.sh
```

**Guidelines**:
- CPU-bound tasks: `concurrency = CPU cores`
- I/O-bound tasks: `concurrency = CPU cores * 2-4`
- Memory-constrained: Lower concurrency to reduce memory usage

### Rate Limiting

**Adjust task rate limits** (in `celery_app.py`):

```python
task_annotations={
    "consultantos.jobs.tasks.check_monitor_task": {
        "rate_limit": "20/m",  # Increase to 20 per minute
    },
}
```

**Monitor rate limit impact**:

```bash
# Check task execution rate
celery -A consultantos.jobs.celery_app inspect stats
```

### Queue Management

**Purge queue** (clear all pending tasks):

```bash
celery -A consultantos.jobs.celery_app purge
```

**Migrate queue**:

```python
# Move tasks from one queue to another
from consultantos.jobs.celery_app import app

# Example: Move low-priority tasks to high-priority
# (Not recommended in production - for emergency use only)
```

## Troubleshooting

### Worker Not Processing Tasks

**Check worker is running**:

```bash
celery -A consultantos.jobs.celery_app inspect active
```

**Check worker logs**:

```bash
# Docker Compose
docker-compose -f docker-compose.celery.yml logs celery-worker

# System logs
tail -f /var/log/celery/worker.log
```

**Common causes**:
- Redis connection failed
- Worker crashed (check logs)
- Task routing misconfigured
- Rate limit reached

### Tasks Failing Repeatedly

**Check task logs in Flower**:
1. Navigate to http://localhost:5555/tasks
2. Filter by status: FAILURE
3. Inspect exception details

**Common causes**:
- Database connection timeout
- External API unavailable
- Invalid task arguments
- Memory/resource limits exceeded

**Solutions**:
- Increase retry backoff: Edit `RetryTask` configuration
- Add circuit breaker: Prevent cascading failures
- Scale resources: Add more workers or increase memory

### High Memory Usage

**Check worker memory**:

```bash
# Docker Compose
docker stats consultantos-celery-worker

# System
ps aux | grep celery
```

**Reduce memory usage**:

```python
# In celery_app.py
worker_max_tasks_per_child=500  # Restart worker more frequently
```

**Monitor memory over time**:

```bash
# Enable memory profiling
celery -A consultantos.jobs.celery_app worker --loglevel=info --autoscale=10,3
```

### Redis Connection Issues

**Test Redis connection**:

```bash
redis-cli -h localhost -p 6379 ping
```

**Check Redis memory**:

```bash
redis-cli info memory
```

**Clear Redis (development only)**:

```bash
redis-cli FLUSHALL
```

## Scheduled Tasks (Beat)

### View Beat Schedule

```bash
celery -A consultantos.jobs.celery_app inspect scheduled
```

### Trigger Scheduled Task Manually

```python
from consultantos.jobs.tasks import aggregate_snapshots_task

# Run now instead of waiting for schedule
aggregate_snapshots_task.apply_async()
```

### Disable Scheduled Task

Edit `celery_app.py`:

```python
beat_schedule={
    # Comment out to disable
    # "aggregate-daily-snapshots": {
    #     "task": "consultantos.jobs.tasks.aggregate_snapshots_task",
    #     "schedule": crontab(hour=2, minute=0),
    # },
}
```

Restart Beat:

```bash
docker-compose -f docker-compose.celery.yml restart celery-beat
```

## Logging

### Configure Log Level

```bash
# Development (verbose)
LOG_LEVEL=debug ./scripts/start_celery_worker.sh

# Production (standard)
LOG_LEVEL=info ./scripts/start_celery_worker.sh

# Production (minimal)
LOG_LEVEL=warning ./scripts/start_celery_worker.sh
```

### View Logs

**Docker Compose**:

```bash
# All services
docker-compose -f docker-compose.celery.yml logs -f

# Specific service
docker-compose -f docker-compose.celery.yml logs -f celery-worker
```

**Direct execution**:

```bash
# Worker logs
tail -f /var/log/celery/worker.log

# Beat logs
tail -f /var/log/celery/beat.log
```

## Security

### Secure Redis

**Production Redis configuration**:

```bash
# Require password
redis-cli CONFIG SET requirepass "your_secure_password"

# Update .env
REDIS_URL=redis://:your_secure_password@localhost:6379/0
```

**Network isolation**:
- Use VPC for Cloud Memorystore
- Restrict Redis port (6379) to internal network only
- Enable SSL/TLS for Redis connections

### Task Authorization

**Verify task origin**:

```python
# In task execution
@app.task(bind=True)
def secure_task(self, data):
    # Verify task was queued by authorized service
    # Check task.request.origin, task.request.hostname
    pass
```

## Backup and Recovery

### Backup Redis Data

```bash
# Create snapshot
redis-cli BGSAVE

# Backup RDB file
cp /var/lib/redis/dump.rdb /backup/redis-$(date +%Y%m%d).rdb
```

### Restore Redis Data

```bash
# Stop Redis
systemctl stop redis

# Restore RDB file
cp /backup/redis-20250101.rdb /var/lib/redis/dump.rdb

# Start Redis
systemctl start redis
```

## Maintenance Windows

### Graceful Worker Shutdown

```bash
# Send SIGTERM for graceful shutdown
pkill -TERM -f "celery.*worker"

# Wait for tasks to complete (up to 30 seconds)
# Then force shutdown if needed
```

### Update Code Without Downtime

1. Deploy new worker instances
2. Wait for new workers to start processing
3. Gracefully shutdown old workers
4. Old workers complete in-flight tasks before shutting down

## Alerts and Notifications

### Setup Prometheus Alerts

```yaml
# prometheus_alerts.yml
groups:
  - name: celery_alerts
    rules:
      - alert: HighTaskFailureRate
        expr: rate(celery_task_total{status="failure"}[5m]) > 0.1
        annotations:
          summary: "High task failure rate"

      - alert: DeadLetterQueueGrowth
        expr: celery_dead_letter_queue_size > 100
        annotations:
          summary: "Dead letter queue growing"

      - alert: WorkerDown
        expr: up{job="celery-worker"} == 0
        annotations:
          summary: "Celery worker is down"
```

### Email Notifications

Configure in Flower:

```bash
celery -A consultantos.jobs.celery_app flower \
  --url-prefix=flower \
  --basic_auth=admin:password \
  --broker_api=redis://localhost:6379/0
```

## Best Practices

1. **Monitor dead letter queue daily**: Review and address failed tasks
2. **Set resource limits**: Prevent runaway tasks from consuming all resources
3. **Use rate limiting**: Protect external APIs and databases
4. **Enable graceful shutdown**: Allow tasks to complete before restart
5. **Log task metadata**: Include monitor_id, user_id for troubleshooting
6. **Test retry logic**: Ensure tasks are idempotent and safely retryable
7. **Scale horizontally**: Add workers rather than increasing concurrency
8. **Monitor memory usage**: Restart workers periodically to prevent leaks
9. **Backup Redis regularly**: Enable RDB snapshots for recovery
10. **Review metrics weekly**: Identify trends and optimize configuration
