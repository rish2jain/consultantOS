"""
Continuous intelligence monitoring system.

Tracks companies over time, detects material changes, and generates
context-aware alerts for users.
"""

import asyncio
import hashlib
from datetime import datetime, timedelta
from typing import Any, List, Optional, Protocol, TYPE_CHECKING
from uuid import uuid4

if TYPE_CHECKING:
    from consultantos.orchestrator import AnalysisOrchestrator


class CacheProtocol(Protocol):
    """Protocol for cache service interface"""
    async def get(self, key: str) -> Any:
        """Get value from cache"""
        ...
    
    async def set(self, key: str, value: Any, ttl: int) -> None:
        """Set value in cache with TTL"""
        ...

from consultantos.models.monitoring import (
    Alert,
    Change,
    ChangeType,
    Monitor,
    MonitorAnalysisSnapshot,
    MonitoringConfig,
    MonitoringFrequency,
    MonitorStatus,
)
from consultantos.database import DatabaseService
from consultantos.utils.validators import AnalysisRequestValidator

# Import logger from the monitoring module (not package)
import logging
logger = logging.getLogger(__name__)


class IntelligenceMonitor:
    """
    Continuous intelligence monitoring system.

    Manages ongoing monitoring of companies/industries with automated
    change detection and intelligent alerting.
    """

    def __init__(
        self,
        orchestrator: "AnalysisOrchestrator",
        db_service: DatabaseService,
        cache_service: Optional[CacheProtocol] = None,
    ):
        """
        Initialize intelligence monitor.

        Args:
            orchestrator: Analysis orchestrator for running analyses
            db_service: Database service for persistence
            cache_service: Optional cache for snapshot storage
        """
        self.orchestrator = orchestrator
        self.db = db_service
        self.cache = cache_service
        self.logger = logger  # Standard logging, no .bind() method

    async def create_monitor(
        self,
        user_id: str,
        company: str,
        industry: str,
        config: Optional[MonitoringConfig] = None,
    ) -> Monitor:
        """
        Create new monitoring instance.

        Args:
            user_id: User creating the monitor
            company: Company to monitor
            industry: Industry sector
            config: Optional monitoring configuration

        Returns:
            Created Monitor instance

        Raises:
            ValueError: If inputs invalid or duplicate monitor exists
        """
        # Validate inputs
        company = company.strip()
        industry = industry.strip()

        if not company or not industry:
            raise ValueError("Company and industry required")

        # Check for duplicate active monitor
        existing = await self.db.get_monitor_by_company(user_id, company)
        if existing and existing.status == MonitorStatus.ACTIVE:
            raise ValueError(f"Active monitor already exists for {company}")

        # Create monitor
        monitor_id = str(uuid4())
        config = config or MonitoringConfig()

        monitor = Monitor(
            id=monitor_id,
            user_id=user_id,
            company=company,
            industry=industry,
            config=config,
            status=MonitorStatus.ACTIVE,
            created_at=datetime.utcnow(),
            next_check=self._calculate_next_check(config.frequency),
        )

        # Persist to database
        await self.db.create_monitor(monitor)

        # Run initial analysis to establish baseline
        try:
            await self._run_baseline_analysis(monitor)
        except Exception as e:
            self.logger.error(
                f"baseline_analysis_failed: monitor_id={monitor_id}, company={company}, error={str(e)}",
                exc_info=True
            )
            # Don't fail monitor creation, just log error
            monitor.error_count = 1
            monitor.last_error = f"Baseline analysis failed: {str(e)}"
            await self.db.update_monitor(monitor)

        self.logger.info(
            f"monitor_created: monitor_id={monitor_id}, company={company}, user_id={user_id}"
        )

        return monitor

    async def check_for_updates(self, monitor_id: str) -> List[Alert]:
        """
        Check monitor for material changes and generate alerts.

        Args:
            monitor_id: Monitor to check

        Returns:
            List of generated alerts (may be empty)

        Raises:
            ValueError: If monitor not found
        """
        # Fetch monitor
        monitor = await self.db.get_monitor(monitor_id)
        if not monitor:
            raise ValueError(f"Monitor {monitor_id} not found")

        if monitor.status != MonitorStatus.ACTIVE:
            self.logger.info(
                f"monitor_not_active: monitor_id={monitor_id}, status={monitor.status}"
            )
            return []

        self.logger.info(
            f"checking_monitor: monitor_id={monitor_id}, company={monitor.company}"
        )

        try:
            # Get previous snapshot
            previous_snapshot = await self._get_latest_snapshot(monitor_id)

            # Run new analysis
            new_snapshot = await self._run_analysis_snapshot(monitor)

            # Detect changes
            changes = await self._detect_changes(previous_snapshot, new_snapshot)

            # Filter by confidence threshold
            significant_changes = [
                c for c in changes if c.confidence >= monitor.config.alert_threshold
            ]

            # Generate alerts if material changes detected
            alerts = []
            if significant_changes:
                alert = await self._create_alert(monitor, significant_changes)
                alerts.append(alert)

                # Update monitor stats
                monitor.total_alerts += 1
                monitor.last_alert_id = alert.id

            # Update monitor status
            monitor.last_check = datetime.utcnow()
            monitor.next_check = self._calculate_next_check(monitor.config.frequency)
            monitor.error_count = 0  # Reset on success
            monitor.last_error = None

            await self.db.update_monitor(monitor)

            self.logger.info(
                f"monitor_check_completed: monitor_id={monitor_id}, changes_detected={len(changes)}, alerts_generated={len(alerts)}"
            )

            return alerts

        except Exception as e:
            # Handle errors gracefully
            monitor.error_count += 1
            monitor.last_error = str(e)

            # Pause monitor after 5 consecutive failures
            if monitor.error_count >= 5:
                monitor.status = MonitorStatus.ERROR
                self.logger.error(
                    f"monitor_paused_due_to_errors: monitor_id={monitor_id}, error_count={monitor.error_count}"
                )

            await self.db.update_monitor(monitor)

            self.logger.error(
                f"monitor_check_failed: monitor_id={monitor_id}, error={str(e)}",
                exc_info=True
            )

            raise

    async def send_alert(self, alert: Alert) -> None:
        """
        Send alert to user via configured channels.

        Args:
            alert: Alert to send

        Raises:
            ValueError: If alert or monitor not found
        """
        # Fetch monitor for notification settings
        monitor = await self.db.get_monitor(alert.monitor_id)
        if not monitor:
            raise ValueError(f"Monitor {alert.monitor_id} not found")

        # Send to each configured channel
        for channel in monitor.config.notification_channels:
            try:
                if channel.value == "email":
                    await self._send_email_alert(monitor, alert)
                elif channel.value == "in_app":
                    # In-app notifications handled by database storage
                    pass
                elif channel.value == "slack":
                    await self._send_slack_alert(monitor, alert)
                elif channel.value == "webhook":
                    await self._send_webhook_alert(monitor, alert)

                self.logger.info(
                    f"alert_sent: alert_id={alert.id}, channel={channel.value}"
                )

            except Exception as e:
                self.logger.error(
                    f"alert_delivery_failed: alert_id={alert.id}, channel={channel.value}, error={str(e)}",
                    exc_info=True
                )

    async def update_monitor(
        self,
        monitor_id: str,
        config: Optional[MonitoringConfig] = None,
        status: Optional[MonitorStatus] = None,
    ) -> Monitor:
        """
        Update monitor configuration or status.

        Args:
            monitor_id: Monitor to update
            config: Optional new configuration
            status: Optional new status

        Returns:
            Updated monitor

        Raises:
            ValueError: If monitor not found
        """
        monitor = await self.db.get_monitor(monitor_id)
        if not monitor:
            raise ValueError(f"Monitor {monitor_id} not found")

        if config:
            monitor.config = config
            # Recalculate next check if frequency changed
            monitor.next_check = self._calculate_next_check(config.frequency)

        if status:
            monitor.status = status

        await self.db.update_monitor(monitor)

        self.logger.info(
            f"monitor_updated: monitor_id={monitor_id}, config_updated={config is not None}, status_updated={status is not None}"
        )

        return monitor

    async def delete_monitor(self, monitor_id: str) -> None:
        """
        Soft-delete monitor (mark as deleted).

        Args:
            monitor_id: Monitor to delete

        Raises:
            ValueError: If monitor not found
        """
        monitor = await self.db.get_monitor(monitor_id)
        if not monitor:
            raise ValueError(f"Monitor {monitor_id} not found")

        monitor.status = MonitorStatus.DELETED
        await self.db.update_monitor(monitor)

        self.logger.info(f"monitor_deleted: monitor_id={monitor_id}")

    # Private helper methods

    async def _run_baseline_analysis(self, monitor: Monitor) -> None:
        """Run initial analysis to establish baseline snapshot."""
        snapshot = await self._run_analysis_snapshot(monitor)
        await self._store_snapshot(snapshot)

    async def _run_analysis_snapshot(self, monitor: Monitor) -> MonitorAnalysisSnapshot:
        """
        Run analysis and create snapshot for change detection.

        Args:
            monitor: Monitor configuration

        Returns:
            Analysis snapshot with key metrics
        """
        # Run orchestrator analysis
        result = await self.orchestrator.analyze(
            company=monitor.company,
            industry=monitor.industry,
            frameworks=monitor.config.frameworks,
            depth="standard",
        )

        # Extract key metrics for change detection
        snapshot = MonitorAnalysisSnapshot(
            monitor_id=monitor.id,
            timestamp=datetime.utcnow(),
            company=monitor.company,
            industry=monitor.industry,
        )

        # Extract competitive forces (Porter)
        if "porter" in monitor.config.frameworks and result.get("framework_analysis"):
            porter_data = result["framework_analysis"].get("porter", {})
            snapshot.competitive_forces = {
                "competitive_rivalry": porter_data.get("competitive_rivalry", ""),
                "supplier_power": porter_data.get("supplier_power", ""),
                "buyer_power": porter_data.get("buyer_power", ""),
                "threat_of_substitutes": porter_data.get("threat_of_substitutes", ""),
                "threat_of_new_entrants": porter_data.get("threat_of_new_entrants", ""),
            }

        # Extract market trends
        if result.get("market_analysis"):
            snapshot.market_trends = result["market_analysis"].get("trends", [])

        # Extract financial metrics
        if result.get("financial_analysis"):
            snapshot.financial_metrics = result["financial_analysis"].get("metrics", {})

        # Extract strategic position (SWOT)
        if "swot" in monitor.config.frameworks and result.get("framework_analysis"):
            snapshot.strategic_position = result["framework_analysis"].get("swot", {})

        return snapshot

    async def _detect_changes(
        self,
        previous: Optional[MonitorAnalysisSnapshot],
        current: MonitorAnalysisSnapshot,
    ) -> List[Change]:
        """
        Detect material changes between snapshots.

        Args:
            previous: Previous snapshot (None for first check)
            current: Current snapshot

        Returns:
            List of detected changes
        """
        if not previous:
            return []  # No baseline to compare

        changes = []

        # Compare competitive forces
        force_changes = self._compare_competitive_forces(
            previous.competitive_forces,
            current.competitive_forces,
        )
        changes.extend(force_changes)

        # Compare market trends
        trend_changes = self._compare_market_trends(
            previous.market_trends,
            current.market_trends,
        )
        changes.extend(trend_changes)

        # Compare financial metrics
        financial_changes = self._compare_financial_metrics(
            previous.financial_metrics,
            current.financial_metrics,
        )
        changes.extend(financial_changes)

        return changes

    def _compare_competitive_forces(
        self, previous: dict, current: dict
    ) -> List[Change]:
        """Detect changes in competitive forces."""
        changes = []

        for force_name, current_value in current.items():
            previous_value = previous.get(force_name, "")

            # Simple text similarity check (can be enhanced with embeddings)
            if previous_value and self._text_changed(previous_value, current_value):
                changes.append(
                    Change(
                        change_type=ChangeType.COMPETITIVE_LANDSCAPE,
                        title=f"Change in {force_name.replace('_', ' ').title()}",
                        description=f"Competitive force '{force_name}' has changed",
                        confidence=0.8,  # Can be enhanced with semantic similarity
                        previous_value=previous_value[:200],
                        current_value=current_value[:200],
                    )
                )

        return changes

    def _compare_market_trends(
        self, previous: List[str], current: List[str]
    ) -> List[Change]:
        """Detect changes in market trends."""
        changes = []

        # Find new trends
        previous_set = set(previous)
        current_set = set(current)

        new_trends = current_set - previous_set
        disappeared_trends = previous_set - current_set

        if new_trends:
            changes.append(
                Change(
                    change_type=ChangeType.MARKET_TREND,
                    title="New Market Trends Detected",
                    description=f"New trends: {', '.join(list(new_trends)[:3])}",
                    confidence=0.75,
                    current_value=", ".join(new_trends),
                )
            )

        if disappeared_trends:
            changes.append(
                Change(
                    change_type=ChangeType.MARKET_TREND,
                    title="Market Trends No Longer Detected",
                    description=f"Trends declined: {', '.join(list(disappeared_trends)[:3])}",
                    confidence=0.7,
                    previous_value=", ".join(disappeared_trends),
                )
            )

        return changes

    def _compare_financial_metrics(
        self, previous: dict, current: dict
    ) -> List[Change]:
        """Detect changes in financial metrics."""
        changes = []

        for metric_name, current_value in current.items():
            previous_value = previous.get(metric_name)

            if previous_value is None:
                continue

            # Detect significant percentage changes
            try:
                if isinstance(current_value, (int, float)) and isinstance(
                    previous_value, (int, float)
                ):
                    pct_change = abs((current_value - previous_value) / previous_value)

                    if pct_change > 0.1:  # 10% threshold
                        changes.append(
                            Change(
                                change_type=ChangeType.FINANCIAL_METRIC,
                                title=f"Significant Change in {metric_name}",
                                description=f"{metric_name} changed by {pct_change:.1%}",
                                confidence=0.9,
                                previous_value=str(previous_value),
                                current_value=str(current_value),
                            )
                        )
            except (TypeError, ZeroDivisionError):
                pass

        return changes

    def _text_changed(self, previous: str, current: str) -> bool:
        """
        Check if text has materially changed.

        Simple hash-based comparison. Can be enhanced with semantic
        similarity using embeddings.
        """
        if not previous or not current:
            return False

        # Normalize and hash
        prev_hash = hashlib.md5(previous.strip().lower().encode()).hexdigest()
        curr_hash = hashlib.md5(current.strip().lower().encode()).hexdigest()

        return prev_hash != curr_hash

    async def _create_alert(
        self, monitor: Monitor, changes: List[Change]
    ) -> Alert:
        """Create alert from detected changes."""
        alert_id = str(uuid4())

        # Calculate overall confidence (weighted average)
        avg_confidence = sum(c.confidence for c in changes) / len(changes)

        # Generate summary
        change_types = set(c.change_type.value for c in changes)
        summary = f"Detected {len(changes)} changes in {monitor.company}: {', '.join(change_types)}"

        alert = Alert(
            id=alert_id,
            monitor_id=monitor.id,
            title=f"Changes Detected: {monitor.company}",
            summary=summary,
            confidence=avg_confidence,
            changes_detected=changes,
            created_at=datetime.utcnow(),
            read=False,
        )

        # Persist alert
        await self.db.create_alert(alert)

        return alert

    async def _get_latest_snapshot(
        self, monitor_id: str
    ) -> Optional[MonitorAnalysisSnapshot]:
        """Get most recent snapshot for monitor."""
        if self.cache:
            cache_key = f"snapshot:{monitor_id}:latest"
            snapshot = await self.cache.get(cache_key)
            if snapshot:
                return snapshot

        # Fallback to database
        return await self.db.get_latest_snapshot(monitor_id)

    async def _store_snapshot(self, snapshot: MonitorAnalysisSnapshot) -> None:
        """Store snapshot for future comparison."""
        # Store in database
        await self.db.create_snapshot(snapshot)

        # Cache latest snapshot
        if self.cache:
            cache_key = f"snapshot:{snapshot.monitor_id}:latest"
            await self.cache.set(cache_key, snapshot, ttl=86400)  # 24h

    def _calculate_next_check(self, frequency: MonitoringFrequency) -> datetime:
        """Calculate next scheduled check time."""
        now = datetime.utcnow()

        if frequency == MonitoringFrequency.HOURLY:
            return now + timedelta(hours=1)
        elif frequency == MonitoringFrequency.DAILY:
            return now + timedelta(days=1)
        elif frequency == MonitoringFrequency.WEEKLY:
            return now + timedelta(weeks=1)
        elif frequency == MonitoringFrequency.MONTHLY:
            return now + timedelta(days=30)

        return now + timedelta(days=1)  # Default daily

    async def _send_email_alert(self, monitor: Monitor, alert: Alert) -> None:
        """Send email notification."""
        # Import here to avoid circular dependency
        from consultantos.services.email_service import send_alert_email

        await send_alert_email(
            user_id=monitor.user_id,
            company=monitor.company,
            alert=alert,
        )

    async def _send_slack_alert(self, monitor: Monitor, alert: Alert) -> None:
        """Send Slack notification (placeholder)."""
        # TODO: Implement Slack webhook integration
        pass

    async def _send_webhook_alert(self, monitor: Monitor, alert: Alert) -> None:
        """Send webhook notification (placeholder)."""
        # TODO: Implement webhook delivery
        pass
