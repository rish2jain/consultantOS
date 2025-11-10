"""
Generic webhook alert channel for custom integrations.
"""

from datetime import datetime
from typing import Dict, Any, Optional
import aiohttp
from .base_channel import AlertChannel, AlertDeliveryResult, DeliveryStatus


class WebhookAlertChannel(AlertChannel):
    """
    Generic webhook delivery channel for custom integrations.

    Sends standardized JSON payload via HTTP POST to configured webhook URL.
    Supports:
    - Custom headers (e.g., authentication)
    - Retry on network failures
    - Timeout configuration
    - Signature verification support (future)
    """

    async def send_alert(
        self,
        alert_id: str,
        monitor_id: str,
        title: str,
        summary: str,
        confidence: float,
        changes: list,
        user_preferences: Dict[str, Any]
    ) -> AlertDeliveryResult:
        """Send alert via webhook"""
        try:
            webhook_url = user_preferences.get("webhook_url")
            if not webhook_url:
                return AlertDeliveryResult(
                    channel="webhook",
                    status=DeliveryStatus.FAILED,
                    error_message="No webhook URL in user preferences"
                )

            # Build standardized payload
            payload = self._build_webhook_payload(
                alert_id, monitor_id, title, summary, confidence, changes
            )

            # Get custom headers if provided
            custom_headers = user_preferences.get("webhook_headers", {})
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "ConsultantOS/1.0",
                **custom_headers
            }

            # Send webhook
            timeout = aiohttp.ClientTimeout(total=user_preferences.get("webhook_timeout", 10))

            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(webhook_url, json=payload, headers=headers) as response:
                    response_text = await response.text()

                    if 200 <= response.status < 300:
                        return AlertDeliveryResult(
                            channel="webhook",
                            status=DeliveryStatus.SENT,
                            delivered_at=datetime.utcnow(),
                            metadata={
                                "webhook_url": webhook_url[:50] + "...",
                                "status_code": response.status,
                                "response": response_text[:200]
                            }
                        )
                    else:
                        return AlertDeliveryResult(
                            channel="webhook",
                            status=DeliveryStatus.FAILED,
                            error_message=f"Webhook returned {response.status}: {response_text[:200]}"
                        )

        except aiohttp.ClientError as e:
            self.logger.error(f"Webhook network error: {e}")
            return AlertDeliveryResult(
                channel="webhook",
                status=DeliveryStatus.FAILED,
                error_message=f"Network error: {str(e)}"
            )
        except Exception as e:
            self.logger.error(f"Webhook delivery failed: {e}", exc_info=True)
            return AlertDeliveryResult(
                channel="webhook",
                status=DeliveryStatus.FAILED,
                error_message=str(e)
            )

    async def test_delivery(
        self,
        user_preferences: Dict[str, Any]
    ) -> AlertDeliveryResult:
        """Send test webhook"""
        try:
            webhook_url = user_preferences.get("webhook_url")
            if not webhook_url:
                return AlertDeliveryResult(
                    channel="webhook",
                    status=DeliveryStatus.FAILED,
                    error_message="No webhook URL in user preferences"
                )

            payload = {
                "event_type": "test_notification",
                "timestamp": datetime.utcnow().isoformat(),
                "message": "This is a test webhook from ConsultantOS monitoring system.",
                "status": "success"
            }

            custom_headers = user_preferences.get("webhook_headers", {})
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "ConsultantOS/1.0",
                **custom_headers
            }

            timeout = aiohttp.ClientTimeout(total=user_preferences.get("webhook_timeout", 10))

            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(webhook_url, json=payload, headers=headers) as response:
                    response_text = await response.text()

                    if 200 <= response.status < 300:
                        return AlertDeliveryResult(
                            channel="webhook",
                            status=DeliveryStatus.SENT,
                            delivered_at=datetime.utcnow(),
                            metadata={
                                "webhook_url": webhook_url[:50] + "...",
                                "status_code": response.status
                            }
                        )
                    else:
                        return AlertDeliveryResult(
                            channel="webhook",
                            status=DeliveryStatus.FAILED,
                            error_message=f"Webhook returned {response.status}: {response_text[:200]}"
                        )

        except Exception as e:
            self.logger.error(f"Test webhook delivery failed: {e}", exc_info=True)
            return AlertDeliveryResult(
                channel="webhook",
                status=DeliveryStatus.FAILED,
                error_message=str(e)
            )

    def _build_webhook_payload(
        self,
        alert_id: str,
        monitor_id: str,
        title: str,
        summary: str,
        confidence: float,
        changes: list
    ) -> Dict[str, Any]:
        """Build standardized webhook payload"""
        return {
            "event_type": "alert",
            "alert": {
                "id": alert_id,
                "monitor_id": monitor_id,
                "title": title,
                "summary": summary,
                "confidence": confidence,
                "created_at": datetime.utcnow().isoformat()
            },
            "changes": [
                {
                    "type": change.get("change_type"),
                    "title": change.get("title"),
                    "description": change.get("description"),
                    "confidence": change.get("confidence"),
                    "detected_at": change.get("detected_at", datetime.utcnow()).isoformat()
                        if isinstance(change.get("detected_at"), datetime)
                        else change.get("detected_at"),
                    "previous_value": change.get("previous_value"),
                    "current_value": change.get("current_value"),
                    "source_urls": change.get("source_urls", [])
                }
                for change in changes
            ],
            "metadata": {
                "platform": "ConsultantOS",
                "version": "1.0",
                "timestamp": datetime.utcnow().isoformat()
            }
        }
