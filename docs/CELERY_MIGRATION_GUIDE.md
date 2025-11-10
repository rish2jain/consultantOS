# Celery Migration Guide

## Overview

This guide covers the migration from simple background worker to Celery + Redis for production-grade task queue processing.

**Migration Benefits**:
- ✅ Retry logic with exponential backoff (1min, 5min, 15min)
- ✅ Dead letter queue for failed tasks
- ✅ Priority-based task execution (4 levels)
- ✅ Rate limiting per task type
- ✅ Distributed worker execution
- ✅ Graceful shutdown and recovery
- ✅ Task monitoring via Flower UI
- ✅ Prometheus metrics integration

## Migration Steps

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

**New dependencies added**:
- `celery[redis]>=5.3.0` - Distributed task queue
- `redis>=5.0.0` - Message broker and result backend
- `flower>=2.0.0` - Celery monitoring web UI

### Step 2: Setup Redis

**Option A: Local Development (Docker)**

```bash
docker run -d \
  --name consultantos-redis \
  -p 6379:6379 \
  redis:7-alpine
```

**Option B: Local Development (Homebrew)**

```bash
brew install redis
brew services start redis
```

**Option C: Production (Cloud Memorystore)**

For Cloud Run deployment, use Google Cloud Memorystore Redis:

```bash
gcloud redis instances create consultantos-redis \
  --size=1 \
  --region=us-central1 \
  --redis-version=redis_7_0 \
  --tier=basic
```

### Step 3: Configure Environment

Update `.env` file:

```bash
# Redis connection URL
REDIS_URL=redis://localhost:6379/0

# Alternative: Separate broker and backend
# CELERY_BROKER_URL=redis://localhost:6379/0
# CELERY_RESULT_BACKEND=redis://localhost:6379/1
```

For production, use Cloud Memorystore connection string:

```bash
REDIS_URL=redis://10.0.0.3:6379/0  # Cloud Memorystore internal IP
```

### Step 4: Verify Celery Configuration

Test Celery connection:

```bash
# Test Celery ping
celery -A consultantos.jobs.celery_app inspect ping

# Check registered tasks
celery -A consultantos.jobs.celery_app inspect registered

# View queue configuration
celery -A consultantos.jobs.celery_app inspect active_queues
```

### Step 5: Start Workers

**Development Mode**:

```bash
# Start worker (terminal 1)
./scripts/start_celery_worker.sh

# Start beat scheduler (terminal 2)
./scripts/start_celery_beat.sh

# Start Flower monitoring UI (terminal 3)
celery -A consultantos.jobs.celery_app flower --port=5555
```

Access Flower UI: http://localhost:5555

**Production Mode (Docker Compose)**:

```bash
# Start all services (Redis, Worker, Beat, Flower)
docker-compose -f docker-compose.celery.yml up -d

# View logs
docker-compose -f docker-compose.celery.yml logs -f

# Stop services
docker-compose -f docker-compose.celery.yml down
```

### Step 6: Update Application Code

The MonitoringWorker now automatically uses Celery when available:

```python
from consultantos.jobs.monitoring_worker import MonitoringWorker

# Worker automatically uses Celery if available
worker = MonitoringWorker(
    use_celery=True,  # Default
    check_interval=60,
)

await worker.start()
```

For backward compatibility (fallback mode):

```python
# Disable Celery (uses old direct execution)
worker = MonitoringWorker(
    intelligence_monitor=intelligence_monitor,
    use_celery=False,
)
```

### Step 7: Test Task Execution

**Queue a test task**:

```python
from consultantos.jobs.tasks import check_monitor_task

# Queue task with normal priority
result = check_monitor_task.apply_async(
    args=["monitor_123"],
    priority=5,
    queue="normal",
)

print(f"Task ID: {result.id}")
print(f"Task Status: {result.status}")
```

**Monitor task progress**:

```python
# Check task status
result = check_monitor_task.AsyncResult("task_id")
print(f"Status: {result.status}")
print(f"Result: {result.result}")

# Wait for completion
result.get(timeout=60)
```

### Step 8: Verify Monitoring

**Check Flower UI**:
- Navigate to http://localhost:5555
- View active tasks, workers, queues
- Monitor task success/failure rates
- Inspect dead letter queue

**Check Prometheus metrics** (if enabled):
```bash
curl http://localhost:9090/metrics | grep celery
```

### Step 9: Migrate Existing Jobs

**Before (Old Worker)**:

```python
# Direct execution
from consultantos.jobs.worker import AnalysisWorker

worker = AnalysisWorker()
await worker.process_job(job_id)
```

**After (Celery)**:

```python
# Queue task
from consultantos.jobs.tasks import run_analysis_task

result = run_analysis_task.apply_async(
    args=[request_dict, user_id],
    priority=5,
    queue="normal",
)
```

### Step 10: Cloud Run Deployment

**Update Cloud Run service**:

```bash
# Deploy with Redis connection
gcloud run deploy consultantos \
  --source . \
  --region us-central1 \
  --set-env-vars "REDIS_URL=redis://MEMORYSTORE_IP:6379/0" \
  --vpc-connector=consultantos-connector  # Required for Memorystore
```

**Deploy Celery worker as separate service**:

```bash
# Create worker service
gcloud run deploy consultantos-worker \
  --source . \
  --region us-central1 \
  --set-env-vars "REDIS_URL=redis://MEMORYSTORE_IP:6379/0" \
  --command="celery" \
  --args="-A,consultantos.jobs.celery_app,worker,--loglevel=info" \
  --vpc-connector=consultantos-connector \
  --no-allow-unauthenticated
```

**Deploy Beat scheduler**:

```bash
# Create beat scheduler service
gcloud run deploy consultantos-beat \
  --source . \
  --region us-central1 \
  --set-env-vars "REDIS_URL=redis://MEMORYSTORE_IP:6379/0" \
  --command="celery" \
  --args="-A,consultantos.jobs.celery_app,beat,--loglevel=info" \
  --vpc-connector=consultantos-connector \
  --no-allow-unauthenticated
```

## Migration Checklist

- [ ] Install dependencies (`pip install -r requirements.txt`)
- [ ] Setup Redis (local or Cloud Memorystore)
- [ ] Configure `.env` with `REDIS_URL`
- [ ] Test Celery connection (`celery inspect ping`)
- [ ] Start worker (`./scripts/start_celery_worker.sh`)
- [ ] Start beat scheduler (`./scripts/start_celery_beat.sh`)
- [ ] Start Flower UI (`celery flower --port=5555`)
- [ ] Verify task execution (queue test task)
- [ ] Check Flower UI (http://localhost:5555)
- [ ] Run tests (`pytest tests/test_celery_tasks.py -v`)
- [ ] Update application code to use Celery tasks
- [ ] Deploy to production (Cloud Run + Memorystore)

## Rollback Plan

If issues occur, you can rollback to direct execution:

```python
# In MonitoringWorker initialization
worker = MonitoringWorker(
    intelligence_monitor=intelligence_monitor,
    use_celery=False,  # Disable Celery
)
```

The worker will fall back to the original direct execution mode.

## Common Issues

### Redis Connection Failed

**Issue**: `celery.exceptions.OperationalError: Error connecting to Redis`

**Solution**:
- Verify Redis is running: `redis-cli ping`
- Check `REDIS_URL` in `.env`
- For Cloud Run, verify VPC connector is configured

### Tasks Not Being Picked Up

**Issue**: Tasks queued but not executing

**Solution**:
- Check worker is running: `celery -A consultantos.jobs.celery_app inspect active`
- Verify queue routing: `celery -A consultantos.jobs.celery_app inspect active_queues`
- Check worker logs for errors

### Dead Letter Queue Growing

**Issue**: Tasks failing permanently

**Solution**:
- Check dead letter queue: See `CELERY_OPERATIONS_GUIDE.md`
- Review task failure logs in Flower UI
- Investigate root cause (database issues, API timeouts, etc.)

### High Memory Usage

**Issue**: Worker consuming too much memory

**Solution**:
- Reduce `max_tasks_per_child` (worker restarts more frequently)
- Decrease `concurrency` (fewer parallel tasks)
- Scale horizontally (more workers with lower concurrency)

## Next Steps

After successful migration:

1. **Monitor performance**: Check Flower UI for task metrics
2. **Review dead letter queue**: Inspect failed tasks for patterns
3. **Tune configuration**: Adjust concurrency, rate limits based on load
4. **Setup alerts**: Configure Prometheus alerts for task failures
5. **Read operations guide**: See `CELERY_OPERATIONS_GUIDE.md` for day-to-day operations

## Support

For issues or questions:
- Review logs: `docker-compose -f docker-compose.celery.yml logs`
- Check Flower UI: http://localhost:5555
- Inspect dead letter queue: See operations guide
- Run tests: `pytest tests/test_celery_tasks.py -v`
