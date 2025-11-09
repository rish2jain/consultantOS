"""
Background worker for continuous intelligence monitoring.

Runs scheduled checks on all active monitors, detects changes,
and sends alerts to users.
"""

import asyncio
from datetime import datetime
from typing import List

from consultantos.models.monitoring import Monitor, MonitorStatus
from consultantos.monitoring.intelligence_monitor import IntelligenceMonitor
from consultantos.database import DatabaseService
from consultantos.cache import CacheService
from consultantos.orchestrator.analysis_orchestrator import AnalysisOrchestrator
from consultantos.monitoring import logger


class MonitoringWorker:
    """
    Background worker for scheduled monitoring checks.

    Continuously polls for monitors that need checking and processes
    them in batches with concurrency control.
    """

    def __init__(
        self,
        intelligence_monitor: IntelligenceMonitor,
        check_interval: int = 60,  # seconds
        max_concurrent_checks: int = 5,
    ):
        """
        Initialize monitoring worker.

        Args:
            intelligence_monitor: Intelligence monitor service
            check_interval: Seconds between check polls
            max_concurrent_checks: Max monitors to check concurrently
        """
        self.monitor_service = intelligence_monitor
        self.check_interval = check_interval
        self.max_concurrent_checks = max_concurrent_checks
        self.is_running = False
        self.logger = logger.bind(component="monitoring_worker")

    async def start(self) -> None:
        """
        Start worker loop.

        Continuously polls for monitors needing checks and processes them.
        """
        self.is_running = True
        self.logger.info("monitoring_worker_started")

        try:
            while self.is_running:
                await self._process_scheduled_monitors()
                await asyncio.sleep(self.check_interval)

        except Exception as e:
            self.logger.error("worker_crashed", error=str(e))
            raise

    async def stop(self) -> None:
        """Stop worker gracefully."""
        self.is_running = False
        self.logger.info("monitoring_worker_stopped")

    async def _process_scheduled_monitors(self) -> None:
        """
        Find and process monitors scheduled for checking.

        Processes monitors in batches with concurrency control.
        """
        try:
            # Get monitors that need checking
            monitors = await self._get_monitors_to_check()

            if not monitors:
                self.logger.debug("no_monitors_to_check")
                return

            self.logger.info(
                "processing_scheduled_monitors",
                monitor_count=len(monitors),
            )

            # Process in batches with concurrency limit
            for i in range(0, len(monitors), self.max_concurrent_checks):
                batch = monitors[i : i + self.max_concurrent_checks]
                await self._process_batch(batch)

        except Exception as e:
            self.logger.error(
                "scheduled_check_processing_failed",
                error=str(e),
            )

    async def _get_monitors_to_check(self) -> List[Monitor]:
        """
        Get monitors that are due for checking.

        Returns:
            List of monitors scheduled for checking
        """
        try:
            # Query database for monitors where next_check <= now
            monitors = await self.monitor_service.db.get_monitors_due_for_check()

            # Filter to only active monitors
            active_monitors = [
                m for m in monitors if m.status == MonitorStatus.ACTIVE
            ]

            return active_monitors

        except Exception as e:
            self.logger.error(
                "get_monitors_to_check_failed",
                error=str(e),
            )
            return []

    async def _process_batch(self, monitors: List[Monitor]) -> None:
        """
        Process batch of monitors concurrently.

        Args:
            monitors: Batch of monitors to check
        """
        tasks = [self._check_monitor_safe(monitor) for monitor in monitors]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Log summary
        successes = sum(1 for r in results if not isinstance(r, Exception))
        failures = len(results) - successes

        self.logger.info(
            "batch_processed",
            total=len(monitors),
            successes=successes,
            failures=failures,
        )

    async def _check_monitor_safe(self, monitor: Monitor) -> None:
        """
        Check monitor with error handling.

        Args:
            monitor: Monitor to check
        """
        try:
            self.logger.info(
                "checking_monitor",
                monitor_id=monitor.id,
                company=monitor.company,
            )

            # Run monitoring check
            alerts = await self.monitor_service.check_for_updates(monitor.id)

            # Send alerts
            for alert in alerts:
                try:
                    await self.monitor_service.send_alert(alert)
                except Exception as e:
                    self.logger.error(
                        "alert_send_failed",
                        alert_id=alert.id,
                        monitor_id=monitor.id,
                        error=str(e),
                    )

            self.logger.info(
                "monitor_check_completed",
                monitor_id=monitor.id,
                alerts_generated=len(alerts),
            )

        except Exception as e:
            self.logger.error(
                "monitor_check_failed",
                monitor_id=monitor.id,
                company=monitor.company,
                error=str(e),
            )


async def run_monitoring_worker() -> None:
    """
    Main entry point for monitoring worker.

    Initializes dependencies and starts worker loop.
    """
    # Initialize dependencies
    from consultantos.orchestrator.analysis_orchestrator import get_orchestrator
    from consultantos.database import get_database_service
    from consultantos.cache import get_cache_service

    orchestrator = get_orchestrator()
    db_service = get_database_service()
    cache_service = get_cache_service()

    # Create intelligence monitor
    intelligence_monitor = IntelligenceMonitor(
        orchestrator=orchestrator,
        db_service=db_service,
        cache_service=cache_service,
    )

    # Create and start worker
    worker = MonitoringWorker(
        intelligence_monitor=intelligence_monitor,
        check_interval=60,  # Check every minute
        max_concurrent_checks=5,  # Process up to 5 monitors concurrently
    )

    logger.info("starting_monitoring_worker")

    try:
        await worker.start()
    except KeyboardInterrupt:
        logger.info("worker_interrupted")
        await worker.stop()
    except Exception as e:
        logger.error("worker_error", error=str(e))
        raise


if __name__ == "__main__":
    # Run worker directly
    asyncio.run(run_monitoring_worker())
