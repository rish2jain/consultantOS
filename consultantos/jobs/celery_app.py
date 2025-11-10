"""
Celery application configuration for distributed task processing.

Provides production-grade task queue with:
- Redis broker/backend
- Retry policies with exponential backoff
- Priority-based task routing
- Rate limiting per task type
- Dead letter queue for failed tasks
"""

import os
from celery import Celery
from celery.schedules import crontab
from kombu import Exchange, Queue
from consultantos.config import settings

# Redis connection URL from environment or config
REDIS_URL = os.getenv(
    "REDIS_URL",
    os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
)

# Create Celery app
app = Celery(
    "consultantos",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        "consultantos.jobs.tasks",
    ]
)

# Celery Configuration
app.conf.update(
    # Broker settings
    broker_connection_retry_on_startup=True,
    broker_connection_retry=True,
    broker_connection_max_retries=10,

    # Result backend settings
    result_backend=REDIS_URL,
    result_expires=3600,  # Results expire after 1 hour
    result_extended=True,  # Store task arguments in result

    # Task serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,

    # Task execution
    task_acks_late=True,  # Acknowledge tasks after execution
    task_reject_on_worker_lost=True,  # Requeue if worker dies
    worker_prefetch_multiplier=1,  # Fair task distribution

    # Task routing - Priority queues
    task_routes={
        # Critical priority - User-triggered checks
        "consultantos.jobs.tasks.check_monitor_user_triggered": {
            "queue": "critical",
            "priority": 10,
        },

        # High priority - Alert delivery
        "consultantos.jobs.tasks.process_alert_task": {
            "queue": "high",
            "priority": 8,
        },
        "consultantos.jobs.tasks.send_alert_webhook": {
            "queue": "high",
            "priority": 8,
        },

        # Normal priority - Scheduled monitor checks
        "consultantos.jobs.tasks.check_monitor_task": {
            "queue": "normal",
            "priority": 5,
        },
        "consultantos.jobs.tasks.run_analysis_task": {
            "queue": "normal",
            "priority": 5,
        },

        # Low priority - Background maintenance
        "consultantos.jobs.tasks.aggregate_snapshots_task": {
            "queue": "low",
            "priority": 2,
        },
        "consultantos.jobs.tasks.cleanup_old_data_task": {
            "queue": "low",
            "priority": 1,
        },
        "consultantos.jobs.tasks.train_anomaly_model_task": {
            "queue": "low",
            "priority": 3,
        },
    },

    # Task rate limits
    task_annotations={
        "consultantos.jobs.tasks.check_monitor_task": {
            "rate_limit": "10/m",  # Max 10 monitor checks per minute
        },
        "consultantos.jobs.tasks.process_alert_task": {
            "rate_limit": "30/m",  # Max 30 alerts per minute
        },
        "consultantos.jobs.tasks.send_alert_webhook": {
            "rate_limit": "20/m",  # Max 20 webhook deliveries per minute
        },
        "consultantos.jobs.tasks.run_analysis_task": {
            "rate_limit": "5/m",  # Max 5 analyses per minute
        },
    },

    # Default retry policy
    task_default_retry_delay=60,  # Wait 1 minute before first retry
    task_max_retries=3,  # Max 3 retry attempts

    # Worker settings
    worker_max_tasks_per_child=1000,  # Restart worker after 1000 tasks (prevent memory leaks)
    worker_disable_rate_limits=False,  # Enable rate limiting

    # Beat scheduler settings (for periodic tasks)
    beat_schedule={
        "check-scheduled-monitors": {
            "task": "consultantos.jobs.tasks.check_scheduled_monitors_task",
            "schedule": 60.0,  # Every 60 seconds
            "options": {"queue": "normal", "priority": 5},
        },
        "aggregate-daily-snapshots": {
            "task": "consultantos.jobs.tasks.aggregate_snapshots_task",
            "schedule": crontab(hour=2, minute=0),  # Daily at 2 AM
            "options": {"queue": "low", "priority": 2},
        },
        "cleanup-old-data": {
            "task": "consultantos.jobs.tasks.cleanup_old_data_task",
            "schedule": crontab(hour=3, minute=0),  # Daily at 3 AM
            "options": {"queue": "low", "priority": 1},
        },
        "train-anomaly-models": {
            "task": "consultantos.jobs.tasks.train_anomaly_model_task",
            "schedule": crontab(hour=4, minute=0, day_of_week=0),  # Weekly on Sunday at 4 AM
            "options": {"queue": "low", "priority": 3},
        },
    },
)

# Define priority queues with dead letter exchange
default_exchange = Exchange("default", type="direct")
dead_letter_exchange = Exchange("dead_letter", type="direct")

app.conf.task_queues = (
    # Critical priority queue
    Queue(
        "critical",
        exchange=default_exchange,
        routing_key="critical",
        queue_arguments={
            "x-max-priority": 10,
            "x-dead-letter-exchange": "dead_letter",
            "x-dead-letter-routing-key": "critical.dead",
        },
    ),

    # High priority queue
    Queue(
        "high",
        exchange=default_exchange,
        routing_key="high",
        queue_arguments={
            "x-max-priority": 10,
            "x-dead-letter-exchange": "dead_letter",
            "x-dead-letter-routing-key": "high.dead",
        },
    ),

    # Normal priority queue (default)
    Queue(
        "normal",
        exchange=default_exchange,
        routing_key="normal",
        queue_arguments={
            "x-max-priority": 10,
            "x-dead-letter-exchange": "dead_letter",
            "x-dead-letter-routing-key": "normal.dead",
        },
    ),

    # Low priority queue
    Queue(
        "low",
        exchange=default_exchange,
        routing_key="low",
        queue_arguments={
            "x-max-priority": 10,
            "x-dead-letter-exchange": "dead_letter",
            "x-dead-letter-routing-key": "low.dead",
        },
    ),

    # Dead letter queues (for failed tasks)
    Queue(
        "critical.dead",
        exchange=dead_letter_exchange,
        routing_key="critical.dead",
    ),
    Queue(
        "high.dead",
        exchange=dead_letter_exchange,
        routing_key="high.dead",
    ),
    Queue(
        "normal.dead",
        exchange=dead_letter_exchange,
        routing_key="normal.dead",
    ),
    Queue(
        "low.dead",
        exchange=dead_letter_exchange,
        routing_key="low.dead",
    ),
)

# Default queue
app.conf.task_default_queue = "normal"
app.conf.task_default_exchange = "default"
app.conf.task_default_routing_key = "normal"


# Celery signals for monitoring
@app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery setup"""
    print(f"Request: {self.request!r}")


if __name__ == "__main__":
    app.start()
