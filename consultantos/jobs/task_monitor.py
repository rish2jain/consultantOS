"""
Task monitoring and metrics for Celery tasks.

Provides:
- Task success/failure rate tracking
- Dead letter queue monitoring
- Task execution metrics
- Prometheus integration
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import defaultdict
import logging

try:
    from prometheus_client import Counter, Histogram, Gauge
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

logger = logging.getLogger(__name__)


# ============================================================================
# Prometheus Metrics
# ============================================================================

if PROMETHEUS_AVAILABLE:
    # Task execution counters
    task_total = Counter(
        "celery_task_total",
        "Total tasks executed",
        ["task_name", "status"]  # status: success, failure, retry
    )

    task_duration = Histogram(
        "celery_task_duration_seconds",
        "Task execution duration",
        ["task_name"],
        buckets=[0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0, 300.0, 600.0]
    )

    task_retries = Counter(
        "celery_task_retries_total",
        "Total task retries",
        ["task_name"]
    )

    dead_letter_queue_size = Gauge(
        "celery_dead_letter_queue_size",
        "Number of tasks in dead letter queue",
        ["queue_name"]
    )

    active_tasks = Gauge(
        "celery_active_tasks",
        "Number of currently active tasks",
        ["queue_name"]
    )


# ============================================================================
# Task Statistics Tracker
# ============================================================================


@dataclass
class TaskStats:
    """Statistics for a specific task type"""
    task_name: str
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    retry_count: int = 0
    avg_duration_seconds: float = 0.0
    last_execution: Optional[datetime] = None
    last_failure: Optional[datetime] = None


class TaskMonitor:
    """
    Monitor Celery task execution and health.

    Tracks task metrics and integrates with Prometheus.
    """

    def __init__(self):
        """Initialize task monitor"""
        self.stats: Dict[str, TaskStats] = defaultdict(
            lambda: TaskStats(task_name="")
        )
        self.enabled = PROMETHEUS_AVAILABLE
        if not self.enabled:
            logger.warning("Prometheus not available, metrics disabled")

    def record_task_start(self, task_name: str, task_id: str) -> None:
        """
        Record task start.

        Args:
            task_name: Name of the task
            task_id: Task identifier
        """
        logger.debug(
            f"Task started: {task_name}",
            extra={"task_name": task_name, "task_id": task_id}
        )

    def record_task_success(
        self,
        task_name: str,
        task_id: str,
        duration_seconds: float
    ) -> None:
        """
        Record successful task execution.

        Args:
            task_name: Name of the task
            task_id: Task identifier
            duration_seconds: Execution duration
        """
        # Update internal stats
        stats = self.stats[task_name]
        stats.task_name = task_name
        stats.total_executions += 1
        stats.successful_executions += 1
        stats.last_execution = datetime.utcnow()

        # Update average duration
        if stats.avg_duration_seconds == 0:
            stats.avg_duration_seconds = duration_seconds
        else:
            # Exponential moving average
            alpha = 0.3
            stats.avg_duration_seconds = (
                alpha * duration_seconds +
                (1 - alpha) * stats.avg_duration_seconds
            )

        # Update Prometheus metrics
        if self.enabled:
            task_total.labels(task_name=task_name, status="success").inc()
            task_duration.labels(task_name=task_name).observe(duration_seconds)

        logger.info(
            f"Task completed successfully: {task_name}",
            extra={
                "task_name": task_name,
                "task_id": task_id,
                "duration_seconds": duration_seconds,
            }
        )

    def record_task_failure(
        self,
        task_name: str,
        task_id: str,
        error: str,
        duration_seconds: float
    ) -> None:
        """
        Record task failure.

        Args:
            task_name: Name of the task
            task_id: Task identifier
            error: Error message
            duration_seconds: Execution duration before failure
        """
        # Update internal stats
        stats = self.stats[task_name]
        stats.task_name = task_name
        stats.total_executions += 1
        stats.failed_executions += 1
        stats.last_execution = datetime.utcnow()
        stats.last_failure = datetime.utcnow()

        # Update Prometheus metrics
        if self.enabled:
            task_total.labels(task_name=task_name, status="failure").inc()
            task_duration.labels(task_name=task_name).observe(duration_seconds)

        logger.error(
            f"Task failed: {task_name}",
            extra={
                "task_name": task_name,
                "task_id": task_id,
                "error": error,
                "duration_seconds": duration_seconds,
            }
        )

    def record_task_retry(
        self,
        task_name: str,
        task_id: str,
        retry_count: int,
        error: str
    ) -> None:
        """
        Record task retry.

        Args:
            task_name: Name of the task
            task_id: Task identifier
            retry_count: Current retry attempt number
            error: Error that triggered retry
        """
        # Update internal stats
        stats = self.stats[task_name]
        stats.task_name = task_name
        stats.retry_count += 1

        # Update Prometheus metrics
        if self.enabled:
            task_retries.labels(task_name=task_name).inc()

        logger.warning(
            f"Task retry: {task_name}",
            extra={
                "task_name": task_name,
                "task_id": task_id,
                "retry_count": retry_count,
                "error": error,
            }
        )

    def get_task_stats(self, task_name: str) -> Optional[TaskStats]:
        """
        Get statistics for a specific task.

        Args:
            task_name: Name of the task

        Returns:
            TaskStats or None if task not tracked
        """
        return self.stats.get(task_name)

    def get_all_stats(self) -> Dict[str, TaskStats]:
        """
        Get statistics for all tasks.

        Returns:
            Dict mapping task names to TaskStats
        """
        return dict(self.stats)

    def get_success_rate(self, task_name: str) -> float:
        """
        Calculate success rate for a task.

        Args:
            task_name: Name of the task

        Returns:
            Success rate as percentage (0-100)
        """
        stats = self.stats.get(task_name)
        if not stats or stats.total_executions == 0:
            return 0.0

        return (stats.successful_executions / stats.total_executions) * 100

    def get_failure_rate(self, task_name: str) -> float:
        """
        Calculate failure rate for a task.

        Args:
            task_name: Name of the task

        Returns:
            Failure rate as percentage (0-100)
        """
        return 100 - self.get_success_rate(task_name)


# ============================================================================
# Dead Letter Queue Monitor
# ============================================================================


class DeadLetterQueueMonitor:
    """
    Monitor dead letter queues for permanently failed tasks.

    Provides visibility into tasks that exhausted all retries.
    """

    def __init__(self):
        """Initialize DLQ monitor"""
        self.enabled = PROMETHEUS_AVAILABLE

    def get_dead_letter_queue_size(self, queue_name: str) -> int:
        """
        Get number of tasks in dead letter queue.

        Args:
            queue_name: Name of the dead letter queue

        Returns:
            Number of tasks in queue
        """
        try:
            from consultantos.jobs.celery_app import app

            # Get queue size from Celery
            with app.connection_or_acquire() as conn:
                queue = conn.default_channel.queue_declare(
                    queue=queue_name,
                    passive=True
                )
                message_count = queue.message_count

            # Update Prometheus metric
            if self.enabled:
                dead_letter_queue_size.labels(queue_name=queue_name).set(message_count)

            return message_count

        except Exception as e:
            logger.error(
                f"Failed to get DLQ size for {queue_name}: {str(e)}",
                extra={"queue_name": queue_name, "error": str(e)}
            )
            return 0

    def get_all_dead_letter_queues(self) -> Dict[str, int]:
        """
        Get sizes of all dead letter queues.

        Returns:
            Dict mapping queue names to message counts
        """
        dlq_names = [
            "critical.dead",
            "high.dead",
            "normal.dead",
            "low.dead",
        ]

        return {
            queue_name: self.get_dead_letter_queue_size(queue_name)
            for queue_name in dlq_names
        }

    def inspect_dead_letter_queue(
        self,
        queue_name: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Inspect messages in dead letter queue.

        Args:
            queue_name: Name of the dead letter queue
            limit: Maximum number of messages to retrieve

        Returns:
            List of failed task details
        """
        try:
            from consultantos.jobs.celery_app import app

            failed_tasks = []

            with app.connection_or_acquire() as conn:
                channel = conn.default_channel

                for _ in range(limit):
                    # Get message without removing from queue
                    message = channel.basic_get(queue=queue_name)

                    if message is None:
                        break

                    # Extract task details
                    task_info = {
                        "task_id": message.properties.get("task_id"),
                        "task_name": message.properties.get("task"),
                        "args": message.body.get("args"),
                        "kwargs": message.body.get("kwargs"),
                        "exception": message.properties.get("exception"),
                        "failed_at": message.properties.get("timestamp"),
                    }

                    failed_tasks.append(task_info)

            return failed_tasks

        except Exception as e:
            logger.error(
                f"Failed to inspect DLQ {queue_name}: {str(e)}",
                extra={"queue_name": queue_name, "error": str(e)}
            )
            return []

    def purge_dead_letter_queue(self, queue_name: str) -> int:
        """
        Purge all messages from dead letter queue.

        WARNING: This permanently deletes failed tasks.

        Args:
            queue_name: Name of the dead letter queue

        Returns:
            Number of messages purged
        """
        try:
            from consultantos.jobs.celery_app import app

            with app.connection_or_acquire() as conn:
                channel = conn.default_channel
                result = channel.queue_purge(queue=queue_name)

            logger.warning(
                f"Purged dead letter queue: {queue_name}",
                extra={"queue_name": queue_name, "messages_purged": result}
            )

            return result

        except Exception as e:
            logger.error(
                f"Failed to purge DLQ {queue_name}: {str(e)}",
                extra={"queue_name": queue_name, "error": str(e)}
            )
            return 0


# ============================================================================
# Global Instances
# ============================================================================

# Singleton instances
_task_monitor: Optional[TaskMonitor] = None
_dlq_monitor: Optional[DeadLetterQueueMonitor] = None


def get_task_monitor() -> TaskMonitor:
    """
    Get or create task monitor instance.

    Returns:
        TaskMonitor singleton
    """
    global _task_monitor
    if _task_monitor is None:
        _task_monitor = TaskMonitor()
    return _task_monitor


def get_dlq_monitor() -> DeadLetterQueueMonitor:
    """
    Get or create dead letter queue monitor instance.

    Returns:
        DeadLetterQueueMonitor singleton
    """
    global _dlq_monitor
    if _dlq_monitor is None:
        _dlq_monitor = DeadLetterQueueMonitor()
    return _dlq_monitor


# ============================================================================
# Celery Signal Handlers
# ============================================================================

def setup_celery_monitoring():
    """
    Setup Celery signal handlers for automatic monitoring.

    Call this during application initialization.
    """
    from celery import signals

    task_monitor = get_task_monitor()

    @signals.task_prerun.connect
    def task_prerun_handler(sender=None, task_id=None, task=None, **kwargs):
        """Handle task start"""
        task_monitor.record_task_start(task.name, task_id)

    @signals.task_postrun.connect
    def task_postrun_handler(
        sender=None,
        task_id=None,
        task=None,
        retval=None,
        state=None,
        **kwargs
    ):
        """Handle task completion"""
        # Calculate duration (if available in kwargs)
        duration = kwargs.get("runtime", 0.0)

        if state == "SUCCESS":
            task_monitor.record_task_success(task.name, task_id, duration)
        elif state == "FAILURE":
            error = kwargs.get("exception", "Unknown error")
            task_monitor.record_task_failure(task.name, task_id, str(error), duration)

    @signals.task_retry.connect
    def task_retry_handler(
        sender=None,
        task_id=None,
        reason=None,
        einfo=None,
        **kwargs
    ):
        """Handle task retry"""
        retry_count = kwargs.get("retries", 0)
        task_monitor.record_task_retry(sender.name, task_id, retry_count, str(reason))

    logger.info("Celery monitoring signals configured")
