"""
Alert priority scoring and deduplication system.

Combines anomaly severity, confidence, user preferences, and historical
feedback to prioritize alerts and reduce notification fatigue.
"""

import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set

from pydantic import BaseModel, Field

from consultantos.models.monitoring import Alert, Change, ChangeType, MonitoringConfig
from consultantos.monitoring.anomaly_detector import AnomalyScore

logger = logging.getLogger(__name__)


class AlertPriority(BaseModel):
    """Alert priority score with explanation"""

    priority_score: float = Field(
        ge=0.0,
        le=10.0,
        description="Overall priority (0-10, higher = more urgent)"
    )

    urgency_level: str = Field(
        description="critical, high, medium, low"
    )

    should_notify: bool = Field(
        description="Whether to send notification"
    )

    reasoning: List[str] = Field(
        description="Factors contributing to priority"
    )

    throttle_until: Optional[datetime] = Field(
        default=None,
        description="Suppress similar alerts until this time"
    )


class AlertScorer:
    """
    Alert priority scoring and intelligent throttling.

    Prevents alert fatigue through deduplication, throttling, and
    priority-based filtering.
    """

    # Priority thresholds
    CRITICAL_THRESHOLD = 8.0  # Always notify
    HIGH_THRESHOLD = 6.0  # Notify during business hours
    MEDIUM_THRESHOLD = 4.0  # Batch notifications
    LOW_THRESHOLD = 2.0  # In-app only

    # Throttling windows
    DEFAULT_THROTTLE_HOURS = 4  # Don't re-alert same issue for 4h
    CRITICAL_THROTTLE_HOURS = 1  # Critical alerts can repeat more frequently
    LOW_PRIORITY_THROTTLE_HOURS = 24  # Low priority batched daily

    # Max alerts per monitor per day
    MAX_ALERTS_PER_DAY = 5

    def __init__(self, db_service=None):
        """
        Initialize alert scorer.

        Args:
            db_service: Optional database service for feedback lookup
        """
        self.db = db_service
        self.logger = logger

        # Track recent alerts for deduplication (in-memory cache)
        # In production, use Redis or database
        self._recent_alerts: Dict[str, Set[str]] = {}  # monitor_id -> alert_hashes

    def score_alert(
        self,
        alert: Alert,
        anomaly_scores: List[AnomalyScore],
        config: MonitoringConfig,
        user_preferences: Optional[Dict] = None,
    ) -> AlertPriority:
        """
        Calculate alert priority score.

        Args:
            alert: Alert to score
            anomaly_scores: Statistical anomaly scores
            config: Monitor configuration
            user_preferences: User-specific preferences

        Returns:
            AlertPriority with score and recommendation
        """
        reasoning = []
        priority_score = 0.0

        # Factor 1: Anomaly severity (40% weight)
        if anomaly_scores:
            avg_severity = sum(a.severity for a in anomaly_scores) / len(anomaly_scores)
            severity_contribution = avg_severity * 0.4
            priority_score += severity_contribution
            reasoning.append(
                f"Anomaly severity: {avg_severity:.1f}/10 (+{severity_contribution:.1f})"
            )
        else:
            # Fallback to alert confidence if no anomaly scores
            confidence_contribution = alert.confidence * 4.0  # Scale to 0-4
            priority_score += confidence_contribution
            reasoning.append(
                f"Alert confidence: {alert.confidence:.0%} (+{confidence_contribution:.1f})"
            )

        # Factor 2: Number and diversity of changes (30% weight)
        change_diversity = len(set(c.change_type for c in alert.changes_detected))
        change_count_score = min(3.0, len(alert.changes_detected) * 0.5)  # Max 3.0
        priority_score += change_count_score
        reasoning.append(
            f"Changes: {len(alert.changes_detected)} across "
            f"{change_diversity} categories (+{change_count_score:.1f})"
        )

        # Factor 3: Change type importance (20% weight)
        critical_change_types = {
            ChangeType.FINANCIAL_METRIC,
            ChangeType.COMPETITIVE_LANDSCAPE,
            ChangeType.REGULATORY,
        }
        has_critical_changes = any(
            c.change_type in critical_change_types for c in alert.changes_detected
        )
        if has_critical_changes:
            priority_score += 2.0
            reasoning.append("Critical change type detected (+2.0)")

        # Factor 4: User preferences (10% weight)
        if user_preferences:
            # User can boost priority for specific change types
            preferred_types = set(user_preferences.get("priority_change_types", []))
            if preferred_types:
                matching_changes = sum(
                    1 for c in alert.changes_detected
                    if c.change_type.value in preferred_types
                )
                if matching_changes > 0:
                    preference_boost = min(1.0, matching_changes * 0.5)
                    priority_score += preference_boost
                    reasoning.append(f"User preference match (+{preference_boost:.1f})")

        # Apply threshold from config
        if alert.confidence < config.alert_threshold:
            priority_score *= 0.5
            reasoning.append(
                f"Below confidence threshold {config.alert_threshold:.0%} (halved)"
            )

        # Cap at 10.0
        priority_score = min(10.0, priority_score)

        # Determine urgency level
        if priority_score >= self.CRITICAL_THRESHOLD:
            urgency_level = "critical"
            should_notify = True
            throttle_hours = self.CRITICAL_THROTTLE_HOURS
        elif priority_score >= self.HIGH_THRESHOLD:
            urgency_level = "high"
            should_notify = True
            throttle_hours = self.DEFAULT_THROTTLE_HOURS
        elif priority_score >= self.MEDIUM_THRESHOLD:
            urgency_level = "medium"
            should_notify = self._should_notify_medium_priority(alert.monitor_id)
            throttle_hours = self.DEFAULT_THROTTLE_HOURS
        else:
            urgency_level = "low"
            should_notify = False  # In-app only
            throttle_hours = self.LOW_PRIORITY_THROTTLE_HOURS

        throttle_until = datetime.utcnow() + timedelta(hours=throttle_hours)

        return AlertPriority(
            priority_score=priority_score,
            urgency_level=urgency_level,
            should_notify=should_notify,
            reasoning=reasoning,
            throttle_until=throttle_until,
        )

    def should_send_alert(
        self,
        alert: Alert,
        priority: AlertPriority,
    ) -> bool:
        """
        Determine if alert should be sent (deduplication + throttling).

        Args:
            alert: Alert to check
            priority: Calculated priority

        Returns:
            True if alert should be sent
        """
        # Check deduplication
        if self._is_duplicate_alert(alert):
            self.logger.info(
                f"Alert suppressed (duplicate): monitor={alert.monitor_id}"
            )
            return False

        # Check daily limit
        if self._exceeds_daily_limit(alert.monitor_id):
            self.logger.info(
                f"Alert suppressed (daily limit): monitor={alert.monitor_id}"
            )
            return False

        # Check priority threshold
        if not priority.should_notify:
            self.logger.info(
                f"Alert suppressed (low priority): monitor={alert.monitor_id}, "
                f"score={priority.priority_score:.1f}"
            )
            return False

        # Record alert for deduplication
        self._record_alert(alert)

        return True

    def incorporate_feedback(
        self,
        alert_id: str,
        feedback: str,
    ) -> None:
        """
        Incorporate user feedback for future scoring.

        Args:
            alert_id: Alert that received feedback
            feedback: Feedback type (helpful, not_helpful, false_positive, etc.)
        """
        # In production, store feedback in database and use ML to adjust weights
        # For now, just log for analysis
        self.logger.info(
            f"Alert feedback received: alert_id={alert_id}, feedback={feedback}"
        )

        # TODO: Implement adaptive scoring based on feedback
        # - Track feedback per change_type, monitor, user
        # - Adjust weights for change types with high false positive rate
        # - Personalize scoring based on user feedback patterns

    def _is_duplicate_alert(self, alert: Alert) -> bool:
        """
        Check if similar alert recently sent.

        Uses content hash to detect duplicates.
        """
        alert_hash = self._compute_alert_hash(alert)
        monitor_id = alert.monitor_id

        # Check recent alerts for this monitor
        recent_hashes = self._recent_alerts.get(monitor_id, set())

        return alert_hash in recent_hashes

    def _compute_alert_hash(self, alert: Alert) -> str:
        """
        Compute content hash for deduplication.

        Hash based on change types and key metrics (not exact values).
        """
        # Sort changes by type for consistent hashing
        change_summary = sorted([
            f"{c.change_type.value}:{c.title}"
            for c in alert.changes_detected
        ])

        content = "|".join(change_summary)
        return hashlib.md5(content.encode()).hexdigest()

    def _record_alert(self, alert: Alert) -> None:
        """Record alert for deduplication tracking."""
        alert_hash = self._compute_alert_hash(alert)
        monitor_id = alert.monitor_id

        if monitor_id not in self._recent_alerts:
            self._recent_alerts[monitor_id] = set()

        self._recent_alerts[monitor_id].add(alert_hash)

        # Clean up old entries (in production, use TTL in Redis)
        # Keep last 20 hashes per monitor
        if len(self._recent_alerts[monitor_id]) > 20:
            self._recent_alerts[monitor_id].pop()

    def _exceeds_daily_limit(self, monitor_id: str) -> bool:
        """
        Check if monitor exceeded daily alert limit.

        In production, query database for alert count in last 24h.
        """
        # For now, use in-memory cache length as proxy
        # In production: SELECT COUNT(*) FROM alerts WHERE monitor_id = ? AND created_at > NOW() - INTERVAL 1 DAY
        alert_count = len(self._recent_alerts.get(monitor_id, set()))
        return alert_count >= self.MAX_ALERTS_PER_DAY

    def _should_notify_medium_priority(self, monitor_id: str) -> bool:
        """
        Determine if medium priority alert should trigger notification.

        Strategy: Batch medium priority alerts (notify at most every 4 hours).
        """
        # In production, check last notification time from database
        # For now, allow medium priority notifications
        return True

    def get_alert_statistics(self, monitor_id: str) -> Dict:
        """
        Get alert statistics for a monitor.

        Args:
            monitor_id: Monitor to analyze

        Returns:
            Statistics dictionary
        """
        # In production, query database for comprehensive stats
        recent_count = len(self._recent_alerts.get(monitor_id, set()))

        return {
            "recent_alert_count": recent_count,
            "daily_limit": self.MAX_ALERTS_PER_DAY,
            "remaining_quota": max(0, self.MAX_ALERTS_PER_DAY - recent_count),
            "throttle_active": recent_count >= self.MAX_ALERTS_PER_DAY,
        }

    def adjust_threshold_for_user(
        self,
        user_id: str,
        base_threshold: float,
    ) -> float:
        """
        Adjust alert threshold based on user feedback history.

        Args:
            user_id: User to personalize for
            base_threshold: Default threshold from config

        Returns:
            Personalized threshold
        """
        # In production, query feedback history
        # For now, return base threshold
        # TODO: Implement adaptive thresholding
        # - High false positive rate → increase threshold
        # - Missing important alerts → decrease threshold
        return base_threshold

    def clear_cache(self, monitor_id: Optional[str] = None) -> None:
        """
        Clear deduplication cache.

        Args:
            monitor_id: Specific monitor to clear, or None for all
        """
        if monitor_id:
            self._recent_alerts.pop(monitor_id, None)
        else:
            self._recent_alerts.clear()
