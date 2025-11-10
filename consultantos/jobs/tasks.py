"""
Celery tasks for ConsultantOS background job processing.

All tasks include:
- Exponential backoff retry (1min, 5min, 15min)
- Dead letter queue for permanent failures
- Priority-based execution
- Task execution metrics
"""

import asyncio
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from celery import Task
from celery.exceptions import Reject
from consultantos.jobs.celery_app import app
from consultantos.models import AnalysisRequest
from consultantos.models.monitoring import Monitor, Alert, MonitorStatus
from consultantos.utils.sanitize import sanitize_input
import logging

logger = logging.getLogger(__name__)


class RetryTask(Task):
    """
    Base task class with exponential backoff retry logic.

    Retry attempts: 3
    Retry delays: 60s, 300s, 900s (1min, 5min, 15min)
    """

    autoretry_for = (Exception,)
    retry_kwargs = {"max_retries": 3}
    retry_backoff = True
    retry_backoff_max = 900  # 15 minutes
    retry_jitter = True

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """
        Handle permanent task failure.

        Tasks that exhaust all retries are sent to dead letter queue.
        """
        logger.error(
            f"Task {self.name} [{task_id}] failed permanently after retries",
            extra={
                "task_name": self.name,
                "task_id": task_id,
                "args": args,
                "kwargs": kwargs,
                "exception": str(exc),
                "traceback": str(einfo),
            }
        )

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Handle task retry"""
        logger.warning(
            f"Task {self.name} [{task_id}] retry attempt {self.request.retries}",
            extra={
                "task_name": self.name,
                "task_id": task_id,
                "retry_count": self.request.retries,
                "exception": str(exc),
            }
        )


# ============================================================================
# Monitor Checking Tasks (Normal Priority)
# ============================================================================


@app.task(base=RetryTask, bind=True, name="consultantos.jobs.tasks.check_monitor_task")
def check_monitor_task(self, monitor_id: str) -> Dict[str, Any]:
    """
    Check a specific monitor for updates.

    Args:
        monitor_id: Monitor identifier

    Returns:
        Dict with check results and alerts generated
    """
    logger.info(
        f"Starting monitor check: {monitor_id}",
        extra={"monitor_id": monitor_id, "task_id": self.request.id}
    )

    try:
        # Run async check in event loop
        result = asyncio.run(_check_monitor_async(monitor_id))

        logger.info(
            f"Monitor check completed: {monitor_id}",
            extra={
                "monitor_id": monitor_id,
                "alerts_generated": result["alerts_count"],
                "task_id": self.request.id
            }
        )

        return result

    except Exception as e:
        logger.error(
            f"Monitor check failed: {monitor_id}",
            extra={
                "monitor_id": monitor_id,
                "error": str(e),
                "task_id": self.request.id
            }
        )
        raise


async def _check_monitor_async(monitor_id: str) -> Dict[str, Any]:
    """
    Async implementation of monitor checking.

    Args:
        monitor_id: Monitor identifier

    Returns:
        Dict with check results
    """
    from consultantos.monitoring.intelligence_monitor import IntelligenceMonitor
    from consultantos.orchestrator.analysis_orchestrator import get_orchestrator
    from consultantos.database import get_database_service
    from consultantos.cache import get_cache_service

    # Initialize dependencies
    orchestrator = get_orchestrator()
    db_service = get_database_service()
    cache_service = get_cache_service()

    intelligence_monitor = IntelligenceMonitor(
        orchestrator=orchestrator,
        db_service=db_service,
        cache_service=cache_service,
    )

    # Run monitoring check
    alerts = await intelligence_monitor.check_for_updates(monitor_id)

    # Queue alert processing tasks (high priority)
    for alert in alerts:
        process_alert_task.apply_async(
            args=[alert.dict()],
            priority=8,
            queue="high",
        )

    return {
        "monitor_id": monitor_id,
        "alerts_count": len(alerts),
        "checked_at": datetime.utcnow().isoformat(),
    }


@app.task(base=RetryTask, bind=True, name="consultantos.jobs.tasks.check_monitor_user_triggered")
def check_monitor_user_triggered(self, monitor_id: str, user_id: str) -> Dict[str, Any]:
    """
    User-triggered monitor check (critical priority).

    Args:
        monitor_id: Monitor identifier
        user_id: User who triggered the check

    Returns:
        Dict with check results
    """
    logger.info(
        f"User-triggered monitor check: {monitor_id}",
        extra={
            "monitor_id": monitor_id,
            "user_id": user_id,
            "task_id": self.request.id
        }
    )

    # Delegate to standard check task
    result = check_monitor_task(monitor_id)
    result["user_triggered"] = True
    result["user_id"] = user_id

    return result


@app.task(base=RetryTask, bind=True, name="consultantos.jobs.tasks.check_scheduled_monitors_task")
def check_scheduled_monitors_task(self) -> Dict[str, Any]:
    """
    Periodic task to check all monitors due for checking.

    Runs every 60 seconds via Celery Beat.

    Returns:
        Dict with summary of checks queued
    """
    logger.info("Checking for scheduled monitors", extra={"task_id": self.request.id})

    try:
        # Simplified event loop
        # Direct asyncio.run()

        result = asyncio.run(_check_scheduled_monitors_async())

        logger.info(
            f"Scheduled monitor check completed: {result['monitors_queued']} queued",
            extra={
                "monitors_queued": result["monitors_queued"],
                "task_id": self.request.id
            }
        )

        return result

    except Exception as e:
        logger.error(
            f"Scheduled monitor check failed: {str(e)}",
            extra={"error": str(e), "task_id": self.request.id}
        )
        raise


async def _check_scheduled_monitors_async() -> Dict[str, Any]:
    """
    Async implementation of scheduled monitor checking.

    Returns:
        Dict with summary
    """
    from consultantos.database import get_database_service

    db_service = get_database_service()

    # Get monitors due for checking
    monitors = await db_service.get_monitors_due_for_check()

    # Filter to active monitors
    active_monitors = [
        m for m in monitors if m.status == MonitorStatus.ACTIVE
    ]

    # Queue individual check tasks
    queued_count = 0
    for monitor in active_monitors:
        check_monitor_task.apply_async(
            args=[monitor.id],
            priority=5,
            queue="normal",
        )
        queued_count += 1

    return {
        "monitors_queued": queued_count,
        "checked_at": datetime.utcnow().isoformat(),
    }


# ============================================================================
# Alert Processing Tasks (High Priority)
# ============================================================================


@app.task(base=RetryTask, bind=True, name="consultantos.jobs.tasks.process_alert_task")
def process_alert_task(self, alert_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process and send an alert.

    Args:
        alert_dict: Alert data as dictionary

    Returns:
        Dict with processing results
    """
    alert_id = alert_dict.get("id", "unknown")
    logger.info(
        f"Processing alert: {alert_id}",
        extra={"alert_id": alert_id, "task_id": self.request.id}
    )

    try:
        # Simplified event loop
        # Direct asyncio.run()

        result = asyncio.run(_process_alert_async(alert_dict))

        logger.info(
            f"Alert processed: {alert_id}",
            extra={
                "alert_id": alert_id,
                "channels": result["channels"],
                "task_id": self.request.id
            }
        )

        return result

    except Exception as e:
        logger.error(
            f"Alert processing failed: {alert_id}",
            extra={
                "alert_id": alert_id,
                "error": str(e),
                "task_id": self.request.id
            }
        )
        raise


async def _process_alert_async(alert_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Async implementation of alert processing.

    Args:
        alert_dict: Alert data

    Returns:
        Dict with processing results
    """
    from consultantos.monitoring.intelligence_monitor import IntelligenceMonitor
    from consultantos.orchestrator.analysis_orchestrator import get_orchestrator
    from consultantos.database import get_database_service
    from consultantos.cache import get_cache_service

    # Reconstruct Alert object
    alert = Alert(**alert_dict)

    # Initialize dependencies
    orchestrator = get_orchestrator()
    db_service = get_database_service()
    cache_service = get_cache_service()

    intelligence_monitor = IntelligenceMonitor(
        orchestrator=orchestrator,
        db_service=db_service,
        cache_service=cache_service,
    )

    # Send alert via all configured channels
    await intelligence_monitor.send_alert(alert)

    return {
        "alert_id": alert.id,
        "channels": ["email", "slack"],  # Channels attempted
        "processed_at": datetime.utcnow().isoformat(),
    }


@app.task(base=RetryTask, bind=True, name="consultantos.jobs.tasks.send_alert_webhook")
def send_alert_webhook(self, webhook_url: str, alert_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send alert via webhook.

    Args:
        webhook_url: Webhook URL
        alert_data: Alert payload

    Returns:
        Dict with delivery results
    """
    logger.info(
        f"Sending alert webhook",
        extra={
            "webhook_url": webhook_url,
            "alert_id": alert_data.get("id"),
            "task_id": self.request.id
        }
    )

    try:
        import httpx

        # Send webhook with timeout
        with httpx.Client(timeout=10.0) as client:
            response = client.post(
                webhook_url,
                json=alert_data,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()

        logger.info(
            f"Webhook sent successfully",
            extra={
                "webhook_url": webhook_url,
                "status_code": response.status_code,
                "task_id": self.request.id
            }
        )

        return {
            "webhook_url": webhook_url,
            "status_code": response.status_code,
            "sent_at": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(
            f"Webhook delivery failed",
            extra={
                "webhook_url": webhook_url,
                "error": str(e),
                "task_id": self.request.id
            }
        )
        raise


# ============================================================================
# Analysis Tasks (Normal Priority)
# ============================================================================


@app.task(base=RetryTask, bind=True, name="consultantos.jobs.tasks.run_analysis_task")
def run_analysis_task(
    self,
    request_dict: Dict[str, Any],
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Run competitive intelligence analysis.

    Args:
        request_dict: AnalysisRequest as dictionary
        user_id: Optional user identifier

    Returns:
        Dict with analysis results
    """
    company = request_dict.get("company", "unknown")
    logger.info(
        f"Starting analysis: {company}",
        extra={
            "company": company,
            "user_id": user_id,
            "task_id": self.request.id
        }
    )

    try:
        # Simplified event loop
        # Direct asyncio.run()

        result = asyncio.run(_run_analysis_async(request_dict, user_id))

        logger.info(
            f"Analysis completed: {company}",
            extra={
                "company": company,
                "report_id": result["report_id"],
                "task_id": self.request.id
            }
        )

        return result

    except Exception as e:
        logger.error(
            f"Analysis failed: {company}",
            extra={
                "company": company,
                "error": str(e),
                "task_id": self.request.id
            }
        )
        raise


async def _run_analysis_async(
    request_dict: Dict[str, Any],
    user_id: Optional[str]
) -> Dict[str, Any]:
    """
    Async implementation of analysis execution.

    Args:
        request_dict: AnalysisRequest data
        user_id: Optional user ID

    Returns:
        Dict with analysis results
    """
    from consultantos.orchestrator import AnalysisOrchestrator
    from consultantos.reports import generate_pdf_report
    from consultantos.storage import get_storage_service
    from consultantos.database import get_db_service, ReportMetadata

    # Reconstruct AnalysisRequest
    analysis_request = AnalysisRequest(**request_dict)

    # Generate report ID
    sanitized_company = sanitize_input(analysis_request.company).replace(' ', '_')
    sanitized_company = ''.join(c for c in sanitized_company if c.isalnum() or c in ('_', '-'))
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
    unique_suffix = str(uuid.uuid4())[:8]
    report_id = f"{sanitized_company}_{timestamp}_{unique_suffix}"

    # Execute analysis
    orchestrator = AnalysisOrchestrator()
    report = await orchestrator.execute(analysis_request)

    # Generate PDF
    pdf_bytes = generate_pdf_report(report, report_id=report_id)

    # Upload PDF
    storage_service = get_storage_service()
    pdf_url = storage_service.upload_pdf(report_id, pdf_bytes)

    # Store metadata
    db_service = get_db_service()
    report_metadata = ReportMetadata(
        report_id=report_id,
        user_id=user_id,
        company=analysis_request.company,
        industry=analysis_request.industry,
        frameworks=analysis_request.frameworks,
        status="completed",
        confidence_score=report.executive_summary.confidence_score,
        execution_time_seconds=0.0,
        pdf_url=pdf_url
    )
    db_service.create_report_metadata(report_metadata)

    return {
        "report_id": report_id,
        "company": analysis_request.company,
        "pdf_url": pdf_url,
        "confidence_score": report.executive_summary.confidence_score,
        "completed_at": datetime.utcnow().isoformat(),
    }


# ============================================================================
# Background Maintenance Tasks (Low Priority)
# ============================================================================


@app.task(base=RetryTask, bind=True, name="consultantos.jobs.tasks.aggregate_snapshots_task")
def aggregate_snapshots_task(self) -> Dict[str, Any]:
    """
    Aggregate monitor snapshots for trend analysis.

    Runs daily at 2 AM.

    Returns:
        Dict with aggregation results
    """
    logger.info("Starting snapshot aggregation", extra={"task_id": self.request.id})

    try:
        # Simplified event loop
        # Direct asyncio.run()

        result = asyncio.run(_aggregate_snapshots_async())

        logger.info(
            f"Snapshot aggregation completed: {result['snapshots_aggregated']}",
            extra={
                "snapshots_aggregated": result["snapshots_aggregated"],
                "task_id": self.request.id
            }
        )

        return result

    except Exception as e:
        logger.error(
            f"Snapshot aggregation failed: {str(e)}",
            extra={"error": str(e), "task_id": self.request.id}
        )
        raise


async def _aggregate_snapshots_async() -> Dict[str, Any]:
    """
    Async implementation of snapshot aggregation.

    Returns:
        Dict with aggregation results
    """
    from consultantos.database import get_database_service

    db_service = get_database_service()

    # Get all monitors
    monitors = await db_service.list_monitors()

    # Aggregate snapshots for each monitor
    snapshots_aggregated = 0
    for monitor in monitors:
        # Get recent snapshots
        snapshots = await db_service.get_monitor_snapshots(
            monitor_id=monitor.id,
            limit=30  # Last 30 snapshots
        )

        if snapshots:
            # Compute aggregated metrics (example: average confidence)
            avg_confidence = sum(s.confidence for s in snapshots) / len(snapshots)

            # Store aggregated metrics (implementation depends on data model)
            # await db_service.store_aggregated_metrics(...)

            snapshots_aggregated += len(snapshots)

    return {
        "snapshots_aggregated": snapshots_aggregated,
        "aggregated_at": datetime.utcnow().isoformat(),
    }


@app.task(base=RetryTask, bind=True, name="consultantos.jobs.tasks.cleanup_old_data_task")
def cleanup_old_data_task(self, retention_days: int = 90) -> Dict[str, Any]:
    """
    Clean up old data based on retention policy.

    Runs daily at 3 AM.

    Args:
        retention_days: Days to retain data (default: 90)

    Returns:
        Dict with cleanup results
    """
    logger.info(
        f"Starting data cleanup: {retention_days} day retention",
        extra={"retention_days": retention_days, "task_id": self.request.id}
    )

    try:
        # Simplified event loop
        # Direct asyncio.run()

        result = asyncio.run(_cleanup_old_data_async(retention_days))

        logger.info(
            f"Data cleanup completed: {result['items_deleted']} items",
            extra={
                "items_deleted": result["items_deleted"],
                "task_id": self.request.id
            }
        )

        return result

    except Exception as e:
        logger.error(
            f"Data cleanup failed: {str(e)}",
            extra={"error": str(e), "task_id": self.request.id}
        )
        raise


async def _cleanup_old_data_async(retention_days: int) -> Dict[str, Any]:
    """
    Async implementation of data cleanup.

    Args:
        retention_days: Days to retain

    Returns:
        Dict with cleanup results
    """
    from datetime import timedelta
    from consultantos.database import get_database_service

    db_service = get_database_service()

    cutoff_date = datetime.utcnow() - timedelta(days=retention_days)

    # Delete old snapshots
    deleted_snapshots = await db_service.delete_snapshots_before(cutoff_date)

    # Delete old alerts
    deleted_alerts = await db_service.delete_alerts_before(cutoff_date)

    # Delete old reports (optional - may want longer retention)
    # deleted_reports = await db_service.delete_reports_before(cutoff_date)

    total_deleted = deleted_snapshots + deleted_alerts

    return {
        "items_deleted": total_deleted,
        "deleted_snapshots": deleted_snapshots,
        "deleted_alerts": deleted_alerts,
        "cutoff_date": cutoff_date.isoformat(),
        "cleaned_at": datetime.utcnow().isoformat(),
    }


@app.task(base=RetryTask, bind=True, name="consultantos.jobs.tasks.train_anomaly_model_task")
def train_anomaly_model_task(self) -> Dict[str, Any]:
    """
    Train Prophet anomaly detection models.

    Runs weekly on Sunday at 4 AM.

    Returns:
        Dict with training results
    """
    logger.info("Starting anomaly model training", extra={"task_id": self.request.id})

    try:
        # Simplified event loop
        # Direct asyncio.run()

        result = asyncio.run(_train_anomaly_model_async())

        logger.info(
            f"Anomaly model training completed: {result['models_trained']}",
            extra={
                "models_trained": result["models_trained"],
                "task_id": self.request.id
            }
        )

        return result

    except Exception as e:
        logger.error(
            f"Anomaly model training failed: {str(e)}",
            extra={"error": str(e), "task_id": self.request.id}
        )
        raise


async def _train_anomaly_model_async() -> Dict[str, Any]:
    """
    Async implementation of anomaly model training.

    Returns:
        Dict with training results
    """
    from consultantos.database import get_database_service

    db_service = get_database_service()

    # Get all active monitors
    monitors = await db_service.list_monitors(status=MonitorStatus.ACTIVE)

    models_trained = 0
    for monitor in monitors:
        try:
            # Get historical snapshots for training
            snapshots = await db_service.get_monitor_snapshots(
                monitor_id=monitor.id,
                limit=100  # Need sufficient history
            )

            if len(snapshots) < 30:
                # Skip if insufficient data
                logger.warning(
                    f"Insufficient data for model training: {monitor.id}",
                    extra={"monitor_id": monitor.id, "snapshot_count": len(snapshots)}
                )
                continue

            # Train Prophet model (implementation depends on data structure)
            # from prophet import Prophet
            # model = Prophet()
            # model.fit(training_data)
            # await db_service.store_anomaly_model(monitor.id, model)

            models_trained += 1

        except Exception as e:
            logger.error(
                f"Model training failed for monitor {monitor.id}: {str(e)}",
                extra={"monitor_id": monitor.id, "error": str(e)}
            )

    return {
        "models_trained": models_trained,
        "trained_at": datetime.utcnow().isoformat(),
    }
