"""
Main alerting service with multi-channel delivery orchestration.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from collections import defaultdict

from consultantos.config import settings
from consultantos.database import get_db_service
from .base_channel import AlertChannel, AlertDeliveryResult, DeliveryStatus
from .email_channel import EmailAlertChannel
from .slack_channel import SlackAlertChannel
from .webhook_channel import WebhookAlertChannel
from .inapp_channel import InAppAlertChannel

logger = logging.getLogger(__name__)


class AlertingService:
    """
    Multi-channel alert delivery service with retry logic and rate limiting.

    Features:
    - Parallel delivery to multiple channels (<2 seconds)
    - Exponential backoff retry for failed deliveries
    - Rate limiting (max 10 alerts/monitor/day by default)
    - Delivery tracking and confirmation
    - Graceful degradation (log failures, don't block other channels)
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize alerting service.

        Args:
            config: Optional configuration dict with channel settings
        """
        self.config = config or {}
        self.db = get_db_service()

        # Initialize channels
        self.channels: Dict[str, AlertChannel] = {
            "email": EmailAlertChannel(self.config.get("email", {})),
            "slack": SlackAlertChannel(self.config.get("slack", {})),
            "webhook": WebhookAlertChannel(self.config.get("webhook", {})),
            "in_app": InAppAlertChannel(self.config.get("in_app", {}))
        }

        # Rate limiting configuration
        self.max_alerts_per_monitor_per_day = self.config.get(
            "max_alerts_per_monitor_per_day", 10
        )
        self.rate_limit_cache: Dict[str, List[datetime]] = defaultdict(list)

        # Retry configuration
        self.max_retries = self.config.get("max_retries", 3)
        self.retry_delays = [1, 2, 4]  # Exponential backoff in seconds

    async def send_alert(
        self,
        alert_id: str,
        monitor_id: str,
        user_id: str,
        title: str,
        summary: str,
        confidence: float,
        changes: list,
        notification_channels: List[str],
        user_preferences: Dict[str, Any]
    ) -> Dict[str, AlertDeliveryResult]:
        """
        Send alert to all configured channels in parallel.

        Args:
            alert_id: Unique alert identifier
            monitor_id: Monitor that generated alert
            user_id: User who owns the monitor
            title: Alert headline
            summary: Executive summary
            confidence: Confidence score (0.0-1.0)
            changes: List of detected changes
            notification_channels: List of channel names to use
            user_preferences: User-specific channel preferences

        Returns:
            Dict mapping channel names to delivery results
        """
        # Check rate limits
        if not await self._check_rate_limit(monitor_id):
            logger.warning(
                f"Rate limit exceeded for monitor {monitor_id}. "
                f"Max {self.max_alerts_per_monitor_per_day} alerts/day."
            )
            return {
                channel: AlertDeliveryResult(
                    channel=channel,
                    status=DeliveryStatus.RATE_LIMITED,
                    error_message=f"Rate limit exceeded: {self.max_alerts_per_monitor_per_day} alerts/day"
                )
                for channel in notification_channels
            }

        # Ensure user_id is in preferences
        user_preferences["user_id"] = user_id

        # Send to all channels in parallel
        tasks = []
        channel_names = []

        for channel_name in notification_channels:
            if channel_name not in self.channels:
                logger.warning(f"Unknown channel: {channel_name}")
                continue

            channel = self.channels[channel_name]
            task = self._send_with_retry(
                channel=channel,
                alert_id=alert_id,
                monitor_id=monitor_id,
                title=title,
                summary=summary,
                confidence=confidence,
                changes=changes,
                user_preferences=user_preferences
            )
            tasks.append(task)
            channel_names.append(channel_name)

        # Execute all deliveries in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Build results dict
        delivery_results = {}
        for channel_name, result in zip(channel_names, results):
            if isinstance(result, Exception):
                logger.error(f"Channel {channel_name} raised exception: {result}")
                delivery_results[channel_name] = AlertDeliveryResult(
                    channel=channel_name,
                    status=DeliveryStatus.FAILED,
                    error_message=str(result)
                )
            else:
                delivery_results[channel_name] = result

        # Track delivery in Firestore
        await self._track_delivery(alert_id, monitor_id, delivery_results)

        # Update rate limit cache
        self._update_rate_limit(monitor_id)

        return delivery_results

    async def test_notification(
        self,
        user_id: str,
        notification_channels: List[str],
        user_preferences: Dict[str, Any]
    ) -> Dict[str, AlertDeliveryResult]:
        """
        Send test notifications to all configured channels.

        Args:
            user_id: User requesting test
            notification_channels: List of channel names to test
            user_preferences: User-specific channel preferences

        Returns:
            Dict mapping channel names to test delivery results
        """
        user_preferences["user_id"] = user_id

        tasks = []
        channel_names = []

        for channel_name in notification_channels:
            if channel_name not in self.channels:
                logger.warning(f"Unknown channel: {channel_name}")
                continue

            channel = self.channels[channel_name]
            tasks.append(channel.test_delivery(user_preferences))
            channel_names.append(channel_name)

        # Execute all test deliveries in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Build results dict
        test_results = {}
        for channel_name, result in zip(channel_names, results):
            if isinstance(result, Exception):
                logger.error(f"Test for {channel_name} raised exception: {result}")
                test_results[channel_name] = AlertDeliveryResult(
                    channel=channel_name,
                    status=DeliveryStatus.FAILED,
                    error_message=str(result)
                )
            else:
                test_results[channel_name] = result

        return test_results

    async def _send_with_retry(
        self,
        channel: AlertChannel,
        alert_id: str,
        monitor_id: str,
        title: str,
        summary: str,
        confidence: float,
        changes: list,
        user_preferences: Dict[str, Any]
    ) -> AlertDeliveryResult:
        """Send alert with exponential backoff retry"""
        last_result = None

        for attempt in range(self.max_retries):
            try:
                result = await channel.send_alert(
                    alert_id=alert_id,
                    monitor_id=monitor_id,
                    title=title,
                    summary=summary,
                    confidence=confidence,
                    changes=changes,
                    user_preferences=user_preferences
                )

                # If successful, return immediately
                if result.status == DeliveryStatus.SENT:
                    if attempt > 0:
                        logger.info(
                            f"Alert {alert_id} delivered to {result.channel} "
                            f"after {attempt + 1} attempts"
                        )
                    return result

                # Store result for potential retry
                last_result = result
                last_result.retry_count = attempt + 1

                # If failed and we have retries left, wait and retry
                if attempt < self.max_retries - 1:
                    delay = self.retry_delays[min(attempt, len(self.retry_delays) - 1)]
                    logger.warning(
                        f"Alert {alert_id} to {result.channel} failed "
                        f"(attempt {attempt + 1}/{self.max_retries}). "
                        f"Retrying in {delay}s..."
                    )
                    await asyncio.sleep(delay)

            except Exception as e:
                logger.error(
                    f"Exception during alert delivery to {channel.__class__.__name__}: {e}",
                    exc_info=True
                )
                last_result = AlertDeliveryResult(
                    channel=channel.__class__.__name__.replace("AlertChannel", "").lower(),
                    status=DeliveryStatus.FAILED,
                    error_message=str(e),
                    retry_count=attempt + 1
                )

                if attempt < self.max_retries - 1:
                    delay = self.retry_delays[min(attempt, len(self.retry_delays) - 1)]
                    await asyncio.sleep(delay)

        # All retries exhausted
        logger.error(
            f"Alert {alert_id} failed to deliver to {last_result.channel} "
            f"after {self.max_retries} attempts"
        )
        return last_result

    async def _check_rate_limit(self, monitor_id: str) -> bool:
        """
        Check if monitor has exceeded rate limit.

        Args:
            monitor_id: Monitor to check

        Returns:
            True if within rate limit, False if exceeded
        """
        # Clean old entries (older than 24 hours)
        cutoff = datetime.utcnow() - timedelta(days=1)
        self.rate_limit_cache[monitor_id] = [
            ts for ts in self.rate_limit_cache[monitor_id]
            if ts > cutoff
        ]

        # Check if under limit
        return len(self.rate_limit_cache[monitor_id]) < self.max_alerts_per_monitor_per_day

    def _update_rate_limit(self, monitor_id: str) -> None:
        """Update rate limit cache after successful delivery"""
        self.rate_limit_cache[monitor_id].append(datetime.utcnow())

    async def _track_delivery(
        self,
        alert_id: str,
        monitor_id: str,
        results: Dict[str, AlertDeliveryResult]
    ) -> None:
        """
        Track alert delivery status in Firestore.

        Args:
            alert_id: Alert identifier
            monitor_id: Monitor identifier
            results: Delivery results by channel
        """
        try:
            delivery_record = {
                "alert_id": alert_id,
                "monitor_id": monitor_id,
                "timestamp": datetime.utcnow(),
                "channels": {
                    channel: {
                        "status": result.status.value,
                        "delivered_at": result.delivered_at.isoformat() if result.delivered_at else None,
                        "error_message": result.error_message,
                        "retry_count": result.retry_count,
                        "metadata": result.metadata
                    }
                    for channel, result in results.items()
                },
                "success_count": sum(
                    1 for r in results.values()
                    if r.status == DeliveryStatus.SENT
                ),
                "failure_count": sum(
                    1 for r in results.values()
                    if r.status == DeliveryStatus.FAILED
                )
            }

            await self.db.set_document(
                f"monitors/{monitor_id}/alert_deliveries",
                alert_id,
                delivery_record
            )

        except Exception as e:
            logger.error(f"Failed to track delivery for alert {alert_id}: {e}")
            # Don't fail the alert delivery if tracking fails


# Global service instance
_alerting_service: Optional[AlertingService] = None


def get_alerting_service(config: Optional[Dict[str, Any]] = None) -> AlertingService:
    """
    Get or create alerting service instance.

    Args:
        config: Optional configuration dict

    Returns:
        AlertingService instance
    """
    global _alerting_service

    if _alerting_service is None:
        # Build config from settings
        service_config = config or {
            "slack": {
                "bot_token": settings.slack_bot_token if hasattr(settings, "slack_bot_token") else None,
                "webhook_url": settings.slack_webhook_url if hasattr(settings, "slack_webhook_url") else None
            },
            "max_alerts_per_monitor_per_day": 10,
            "max_retries": 3
        }
        _alerting_service = AlertingService(service_config)

    return _alerting_service
