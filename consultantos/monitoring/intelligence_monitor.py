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
    AnomalyScoreModel,
    AlertPriorityModel,
    Change,
    ChangeType,
    Monitor,
    MonitorAnalysisSnapshot,
    MonitoringConfig,
    MonitoringFrequency,
    MonitorStatus,
)
from consultantos.database import DatabaseService
from consultantos.monitoring.anomaly_detector import AnomalyDetector, AnomalyScore
from consultantos.monitoring.alert_scorer import AlertScorer
from consultantos.monitoring.timeseries_optimizer import TimeSeriesOptimizer
from consultantos.monitoring.snapshot_aggregator import SnapshotAggregator, AggregationPeriod
from consultantos.monitoring.root_cause_analyzer import RootCauseAnalyzer
from consultantos.utils.validators import AnalysisRequestValidator
from consultantos.utils.schemas import MonitorSnapshotSchema, log_validation_metrics

# Import logger from the monitoring module (not package)
import logging
logger = logging.getLogger(__name__)

# Import Sentry for error tracking and performance monitoring
try:
    from consultantos.observability import SentryIntegration
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False


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
        enable_anomaly_detection: bool = True,
    ):
        """
        Initialize intelligence monitor.

        Args:
            orchestrator: Analysis orchestrator for running analyses
            db_service: Database service for persistence
            cache_service: Optional cache for snapshot storage
            enable_anomaly_detection: Enable Prophet-based anomaly detection
        """
        self.orchestrator = orchestrator
        self.db = db_service
        self.cache = cache_service
        self.logger = logger  # Standard logging, no .bind() method

        # Initialize time-series optimization components
        self.timeseries_optimizer = TimeSeriesOptimizer(
            db_service=db_service,
            compression_threshold_bytes=1024,  # Compress snapshots >1KB
            batch_size=10,
            cache_ttl_seconds=300,  # 5 minute cache
        )

        self.snapshot_aggregator = SnapshotAggregator(
            timeseries_optimizer=self.timeseries_optimizer,
            db_service=db_service,
        )

        # Initialize anomaly detection components
        self.enable_anomaly_detection = enable_anomaly_detection
        if enable_anomaly_detection:
            self.anomaly_detector = AnomalyDetector(
                confidence_mode="balanced",
                enable_seasonality=True,
            )
            self.alert_scorer = AlertScorer(db_service=db_service)
        else:
            self.anomaly_detector = None
            self.alert_scorer = None

        # Initialize root cause analyzer (always enabled)
        self.root_cause_analyzer = RootCauseAnalyzer()

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
        # Start Sentry transaction for performance monitoring
        transaction = None
        if SENTRY_AVAILABLE:
            try:
                transaction = SentryIntegration.start_transaction(
                    name="IntelligenceMonitor.check_for_updates",
                    op="monitor.check"
                )
                transaction.__enter__()
            except Exception:
                pass

        # Fetch monitor
        monitor = await self.db.get_monitor(monitor_id)
        if not monitor:
            raise ValueError(f"Monitor {monitor_id} not found")

        if monitor.status != MonitorStatus.ACTIVE:
            self.logger.info(
                f"monitor_not_active: monitor_id={monitor_id}, status={monitor.status}"
            )
            if SENTRY_AVAILABLE and transaction:
                try:
                    transaction.__exit__(None, None, None)
                except Exception:
                    pass
            return []

        # Set monitor context for Sentry
        if SENTRY_AVAILABLE:
            try:
                SentryIntegration.set_monitor_context(
                    monitor_id=monitor_id,
                    company=monitor.company,
                    industry=monitor.industry,
                )
                SentryIntegration.add_breadcrumb(
                    message=f"Checking monitor for {monitor.company}",
                    category="monitor",
                    level="info",
                    data={
                        "frequency": monitor.config.frequency,
                        "alert_threshold": monitor.config.alert_threshold,
                    }
                )
            except Exception:
                pass

        self.logger.info(
            f"checking_monitor: monitor_id={monitor_id}, company={monitor.company}"
        )

        try:
            # Get previous snapshot
            previous_snapshot = await self._get_latest_snapshot(monitor_id)

            # Run new analysis
            new_snapshot = await self._run_analysis_snapshot(monitor)

            # Detect changes (threshold-based + anomaly detection)
            changes = await self._detect_changes(previous_snapshot, new_snapshot, monitor)

            # Run statistical anomaly detection if enabled
            anomaly_scores = []
            if self.enable_anomaly_detection and previous_snapshot:
                anomaly_scores = await self._detect_statistical_anomalies(
                    monitor, previous_snapshot, new_snapshot
                )

            # Filter by confidence threshold
            significant_changes = [
                c for c in changes if c.confidence >= monitor.config.alert_threshold
            ]

            # Generate alerts if material changes or anomalies detected
            alerts = []
            if significant_changes or anomaly_scores:
                alert = await self._create_alert(
                    monitor, significant_changes, anomaly_scores
                )

                # Score alert priority if anomaly detection enabled
                if self.enable_anomaly_detection and self.alert_scorer:
                    priority = self.alert_scorer.score_alert(
                        alert=alert,
                        anomaly_scores=anomaly_scores,
                        config=monitor.config,
                    )
                    alert.priority = AlertPriorityModel(**priority.dict())

                    # Check if alert should be sent (deduplication + throttling)
                    should_send = self.alert_scorer.should_send_alert(alert, priority)
                    if should_send:
                        alerts.append(alert)
                        # Update monitor stats
                        monitor.total_alerts += 1
                        monitor.last_alert_id = alert.id
                    else:
                        # Store alert but don't notify
                        await self.db.create_alert(alert)
                        self.logger.info(
                            f"Alert created but not sent: monitor_id={monitor.id}, "
                            f"priority={priority.priority_score:.1f}"
                        )
                else:
                    # No anomaly detection - use simple alerting
                    alerts.append(alert)
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

            # Record successful check in Sentry
            if SENTRY_AVAILABLE and transaction:
                try:
                    transaction.set_measurement("changes_detected", len(changes))
                    transaction.set_measurement("alerts_generated", len(alerts))
                    SentryIntegration.add_breadcrumb(
                        message="Monitor check completed successfully",
                        category="monitor",
                        level="info",
                        data={
                            "changes_detected": len(changes),
                            "alerts_generated": len(alerts),
                        }
                    )
                    transaction.__exit__(None, None, None)
                except Exception:
                    pass

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

            # Capture error in Sentry
            if SENTRY_AVAILABLE:
                try:
                    SentryIntegration.add_breadcrumb(
                        message="Monitor check failed",
                        category="monitor",
                        level="error",
                        data={
                            "error": str(e),
                            "error_count": monitor.error_count,
                        }
                    )
                    SentryIntegration.capture_exception(
                        e,
                        tag_monitor_id=monitor_id,
                        tag_company=monitor.company,
                        tag_error_count=monitor.error_count,
                    )
                    if transaction:
                        transaction.__exit__(type(e), e, None)
                except Exception:
                    pass

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

        # Validate snapshot before returning
        snapshot_dict = {
            "monitor_id": snapshot.monitor_id,
            "timestamp": snapshot.timestamp,
            "company": snapshot.company,
            "industry": snapshot.industry,
            "competitive_forces": snapshot.competitive_forces or {},
            "market_trends": snapshot.market_trends or [],
            "financial_metrics": snapshot.financial_metrics or {},
            "strategic_position": snapshot.strategic_position or {},
        }

        is_valid, error_msg, cleaned_snapshot = MonitorSnapshotSchema.validate_snapshot(snapshot_dict)

        # Log validation metrics
        log_validation_metrics("snapshot", is_valid, error_msg)

        if not is_valid:
            self.logger.warning(
                f"Snapshot validation failed for monitor {monitor.id}: {error_msg}. "
                "Snapshot may contain data quality issues."
            )

        return snapshot

    async def _detect_changes(
        self,
        previous: Optional[MonitorAnalysisSnapshot],
        current: MonitorAnalysisSnapshot,
        monitor: Monitor,
    ) -> List[Change]:
        """
        Detect material changes between snapshots.

        Args:
            previous: Previous snapshot (None for first check)
            current: Current snapshot
            monitor: Monitor configuration

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

    async def _detect_statistical_anomalies(
        self,
        monitor: Monitor,
        previous_snapshot: MonitorAnalysisSnapshot,
        current_snapshot: MonitorAnalysisSnapshot,
    ) -> List[AnomalyScore]:
        """
        Detect statistical anomalies using Prophet.

        Args:
            monitor: Monitor configuration
            previous_snapshot: Previous snapshot
            current_snapshot: Current snapshot

        Returns:
            List of detected anomalies
        """
        if not self.anomaly_detector:
            return []

        anomaly_scores = []

        try:
            # Fetch historical snapshots for training
            historical_snapshots = await self.db.get_snapshots_history(
                monitor_id=monitor.id,
                days_back=30,  # Last 30 days for training
            )

            if len(historical_snapshots) < AnomalyDetector.MIN_TRAINING_DAYS:
                self.logger.info(
                    f"Insufficient history for anomaly detection: "
                    f"{len(historical_snapshots)} snapshots (min: {AnomalyDetector.MIN_TRAINING_DAYS})"
                )
                return []

            # Extract and analyze financial metrics
            if current_snapshot.financial_metrics:
                financial_anomalies = await self._detect_financial_anomalies(
                    monitor, historical_snapshots, current_snapshot
                )
                anomaly_scores.extend(financial_anomalies)

            # Analyze trend reversals
            if current_snapshot.market_trends:
                trend_anomalies = await self._detect_trend_anomalies(
                    monitor, historical_snapshots, current_snapshot
                )
                anomaly_scores.extend(trend_anomalies)

            self.logger.info(
                f"Anomaly detection completed: monitor_id={monitor.id}, "
                f"anomalies_detected={len(anomaly_scores)}"
            )

        except Exception as e:
            self.logger.error(
                f"Error in anomaly detection for monitor {monitor.id}: {e}",
                exc_info=True
            )

        return anomaly_scores

    async def _detect_financial_anomalies(
        self,
        monitor: Monitor,
        historical_snapshots: List[MonitorAnalysisSnapshot],
        current_snapshot: MonitorAnalysisSnapshot,
    ) -> List[AnomalyScore]:
        """Detect anomalies in financial metrics."""
        anomalies = []

        for metric_name, current_value in current_snapshot.financial_metrics.items():
            if not isinstance(current_value, (int, float)):
                continue

            # Prepare historical data
            historical_data = [
                (snapshot.timestamp, snapshot.financial_metrics.get(metric_name, 0))
                for snapshot in historical_snapshots
                if isinstance(snapshot.financial_metrics.get(metric_name), (int, float))
            ]

            if len(historical_data) < AnomalyDetector.MIN_TRAINING_DAYS:
                continue

            # Train Prophet model
            success = self.anomaly_detector.fit_model(metric_name, historical_data)
            if not success:
                continue

            # Detect anomalies
            anomaly = self.anomaly_detector.detect_anomalies(
                metric_name=metric_name,
                current_value=float(current_value),
                timestamp=current_snapshot.timestamp,
            )

            if anomaly:
                anomalies.append(anomaly)

        return anomalies

    async def _detect_trend_anomalies(
        self,
        monitor: Monitor,
        historical_snapshots: List[MonitorAnalysisSnapshot],
        current_snapshot: MonitorAnalysisSnapshot,
    ) -> List[AnomalyScore]:
        """Detect trend reversals."""
        anomalies = []

        # For simplicity, analyze market trend count as a metric
        metric_name = "market_trends_count"

        historical_data = [
            (snapshot.timestamp, len(snapshot.market_trends or []))
            for snapshot in historical_snapshots
        ]

        if len(historical_data) < AnomalyDetector.MIN_TRAINING_DAYS:
            return []

        # Train model
        success = self.anomaly_detector.fit_model(metric_name, historical_data)
        if not success:
            return []

        # Analyze trends
        trend_analysis = self.anomaly_detector.trend_analysis(
            metric_name=metric_name,
            recent_window_days=7,
        )

        if trend_analysis and trend_analysis.reversal_detected:
            # Create anomaly score for trend reversal
            anomaly = AnomalyScore(
                metric_name="Market Trends",
                anomaly_type="trend_reversal",
                severity=min(10.0, trend_analysis.reversal_confidence * 10),
                confidence=trend_analysis.reversal_confidence,
                explanation=(
                    f"Market trend direction changed from "
                    f"{trend_analysis.historical_trend} to {trend_analysis.current_trend}"
                ),
                statistical_details={
                    "historical_trend": trend_analysis.historical_trend,
                    "current_trend": trend_analysis.current_trend,
                    "trend_strength": trend_analysis.trend_strength,
                },
            )
            anomalies.append(anomaly)

        return anomalies

    async def _create_alert(
        self,
        monitor: Monitor,
        changes: List[Change],
        anomaly_scores: Optional[List[AnomalyScore]] = None,
    ) -> Alert:
        """Create alert from detected changes and anomalies."""
        alert_id = str(uuid4())

        # Calculate overall confidence
        if changes:
            avg_confidence = sum(c.confidence for c in changes) / len(changes)
        elif anomaly_scores:
            avg_confidence = sum(a.confidence for a in anomaly_scores) / len(anomaly_scores)
        else:
            avg_confidence = 0.5

        # Generate summary
        summary_parts = []
        if changes:
            change_types = set(c.change_type.value for c in changes)
            summary_parts.append(
                f"{len(changes)} changes in {', '.join(change_types)}"
            )
        if anomaly_scores:
            summary_parts.append(f"{len(anomaly_scores)} statistical anomalies")

        summary = f"Detected {' and '.join(summary_parts)} for {monitor.company}"

        # Convert anomaly scores to models
        anomaly_models = []
        if anomaly_scores:
            for score in anomaly_scores:
                anomaly_models.append(AnomalyScoreModel(
                    metric_name=score.metric_name,
                    anomaly_type=score.anomaly_type.value,
                    severity=score.severity,
                    confidence=score.confidence,
                    explanation=score.explanation,
                    statistical_details=score.statistical_details,
                    forecast_value=score.forecast_value,
                    actual_value=score.actual_value,
                    lower_bound=score.lower_bound,
                    upper_bound=score.upper_bound,
                ))

        # Create initial alert
        alert = Alert(
            id=alert_id,
            monitor_id=monitor.id,
            title=f"Changes Detected: {monitor.company}",
            summary=summary,
            confidence=avg_confidence,
            changes_detected=changes,
            anomaly_scores=anomaly_models,
            created_at=datetime.utcnow(),
            read=False,
        )

        # Perform root cause analysis
        try:
            enhanced_explanation = self.root_cause_analyzer.analyze_alert(
                alert=alert,
                historical_data=None  # TODO: Pass historical data when available
            )

            # Convert to dict for storage
            alert.root_cause_analysis = enhanced_explanation.dict()

            # Optionally enhance alert title and summary with root cause insights
            alert.title = f"🔔 {enhanced_explanation.root_cause_analysis.severity.upper()}: {monitor.company}"
            alert.summary = enhanced_explanation.summary

        except Exception as e:
            self.logger.warning(
                f"root_cause_analysis_failed: alert_id={alert_id}, error={str(e)}"
            )
            # Continue without root cause analysis if it fails

        # Persist alert
        await self.db.create_alert(alert)

        return alert

    async def _get_latest_snapshot(
        self, monitor_id: str
    ) -> Optional[MonitorAnalysisSnapshot]:
        """Get most recent snapshot for monitor using optimized queries."""
        # Use time-series optimizer for cached retrieval
        return await self.timeseries_optimizer.get_latest_snapshot(
            monitor_id=monitor_id,
            decompress=True,
        )

    async def _store_snapshot(self, snapshot: MonitorAnalysisSnapshot) -> None:
        """Store snapshot with compression and optimization."""
        # Use time-series optimizer for compressed storage
        await self.timeseries_optimizer.store_snapshot(
            snapshot=snapshot,
            compress=True,  # Auto-compress large snapshots
            batch=False,    # Immediate write for monitoring
        )

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
        """Send Slack notification via webhook or bot token."""
        try:
            from consultantos.services.alerting.slack_channel import SlackAlertChannel
            
            # Get Slack configuration from monitor preferences
            prefs = monitor.config.notification_preferences or {}
            slack_config = prefs.get("slack", {})
            
            # Check if Slack is configured
            if not slack_config.get("webhook_url") and not slack_config.get("bot_token"):
                self.logger.warning(
                    "Slack alert skipped - no webhook URL or bot token configured",
                    extra={"monitor_id": monitor.id, "alert_id": alert.id}
                )
                return
            
            # Initialize Slack channel
            channel = SlackAlertChannel(config=slack_config)
            
            # Prepare user preferences for channel
            user_preferences = {
                "user_id": monitor.user_id,
                "slack_channel": slack_config.get("channel", "#alerts"),
                "slack_user_id": slack_config.get("user_id"),
                **slack_config
            }
            
            # Convert alert to channel format
            changes = [
                {
                    "change_type": change.change_type.value,
                    "title": change.title,
                    "description": change.description,
                    "confidence": change.confidence,
                    "detected_at": change.detected_at,
                    "previous_value": change.previous_value,
                    "current_value": change.current_value,
                    "source_urls": change.source_urls
                }
                for change in alert.changes
            ]
            
            # Send alert
            result = await channel.send_alert(
                alert_id=alert.id,
                monitor_id=monitor.id,
                title=alert.title,
                summary=alert.summary,
                confidence=alert.confidence,
                changes=changes,
                user_preferences=user_preferences
            )
            
            if result.status.value == "sent":
                self.logger.info(
                    "Slack alert sent successfully",
                    extra={
                        "monitor_id": monitor.id,
                        "alert_id": alert.id,
                        "channel": result.metadata.get("channel") if result.metadata else None
                    }
                )
            else:
                self.logger.warning(
                    "Slack alert delivery failed",
                    extra={
                        "monitor_id": monitor.id,
                        "alert_id": alert.id,
                        "error": result.error_message
                    }
                )
        except Exception as e:
            self.logger.error(
                "Failed to send Slack alert",
                extra={"monitor_id": monitor.id, "alert_id": alert.id, "error": str(e)},
                exc_info=True
            )

    async def _send_webhook_alert(self, monitor: Monitor, alert: Alert) -> None:
        """Send webhook notification to custom endpoint."""
        try:
            from consultantos.services.alerting.webhook_channel import WebhookAlertChannel
            
            # Get webhook configuration from monitor preferences
            prefs = monitor.config.notification_preferences or {}
            webhook_config = prefs.get("webhook", {})
            
            # Check if webhook URL is configured
            webhook_url = webhook_config.get("url")
            if not webhook_url:
                self.logger.warning(
                    "Webhook alert skipped - no webhook URL configured",
                    extra={"monitor_id": monitor.id, "alert_id": alert.id}
                )
                return
            
            # Initialize webhook channel
            channel = WebhookAlertChannel(config={})
            
            # Prepare user preferences for channel
            user_preferences = {
                "user_id": monitor.user_id,
                "webhook_url": webhook_url,
                "webhook_headers": webhook_config.get("headers", {}),
                "webhook_timeout": webhook_config.get("timeout", 10)
            }
            
            # Convert alert to channel format
            changes = [
                {
                    "change_type": change.change_type.value,
                    "title": change.title,
                    "description": change.description,
                    "confidence": change.confidence,
                    "detected_at": change.detected_at,
                    "previous_value": change.previous_value,
                    "current_value": change.current_value,
                    "source_urls": change.source_urls
                }
                for change in alert.changes
            ]
            
            # Send alert
            result = await channel.send_alert(
                alert_id=alert.id,
                monitor_id=monitor.id,
                title=alert.title,
                summary=alert.summary,
                confidence=alert.confidence,
                changes=changes,
                user_preferences=user_preferences
            )
            
            if result.status.value == "sent":
                self.logger.info(
                    "Webhook alert sent successfully",
                    extra={
                        "monitor_id": monitor.id,
                        "alert_id": alert.id,
                        "webhook_url": webhook_url[:50] + "..." if len(webhook_url) > 50 else webhook_url
                    }
                )
            else:
                self.logger.warning(
                    "Webhook alert delivery failed",
                    extra={
                        "monitor_id": monitor.id,
                        "alert_id": alert.id,
                        "error": result.error_message
                    }
                )
        except Exception as e:
            self.logger.error(
                "Failed to send webhook alert",
                extra={"monitor_id": monitor.id, "alert_id": alert.id, "error": str(e)},
                exc_info=True
            )
