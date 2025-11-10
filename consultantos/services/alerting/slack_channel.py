"""
Slack alert channel with Block Kit rich formatting.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError
from .base_channel import AlertChannel, AlertDeliveryResult, DeliveryStatus


class SlackAlertChannel(AlertChannel):
    """
    Slack delivery channel for alerts with rich Block Kit formatting.

    Supports:
    - Rich message blocks with formatted changes
    - Color-coded confidence indicators
    - Interactive buttons (future: mark as read, provide feedback)
    - Both bot token and webhook URL delivery methods
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Slack channel.

        Config should contain either:
        - bot_token: Slack bot token for Web API
        - webhook_url: Incoming webhook URL (simpler, limited features)
        """
        super().__init__(config)
        self.bot_token = config.get("bot_token")
        self.webhook_url = config.get("webhook_url")

        if self.bot_token:
            self.client = AsyncWebClient(token=self.bot_token)
        else:
            self.client = None

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
        """Send alert to Slack"""
        try:
            # Get Slack channel/user from preferences
            slack_target = user_preferences.get("slack_channel") or user_preferences.get("slack_user_id")
            if not slack_target:
                return AlertDeliveryResult(
                    channel="slack",
                    status=DeliveryStatus.FAILED,
                    error_message="No Slack channel or user ID in preferences"
                )

            # Build Slack blocks
            blocks = self._build_slack_blocks(
                title, summary, confidence, changes, monitor_id, alert_id
            )

            # Send via bot token or webhook
            if self.client:
                result = await self._send_via_bot(slack_target, blocks)
            elif self.webhook_url:
                result = await self._send_via_webhook(blocks)
            else:
                return AlertDeliveryResult(
                    channel="slack",
                    status=DeliveryStatus.FAILED,
                    error_message="No Slack bot token or webhook URL configured"
                )

            return result

        except Exception as e:
            self.logger.error(f"Slack alert delivery failed: {e}", exc_info=True)
            return AlertDeliveryResult(
                channel="slack",
                status=DeliveryStatus.FAILED,
                error_message=str(e)
            )

    async def test_delivery(
        self,
        user_preferences: Dict[str, Any]
    ) -> AlertDeliveryResult:
        """Send test Slack message"""
        try:
            slack_target = user_preferences.get("slack_channel") or user_preferences.get("slack_user_id")
            if not slack_target:
                return AlertDeliveryResult(
                    channel="slack",
                    status=DeliveryStatus.FAILED,
                    error_message="No Slack channel or user ID in preferences"
                )

            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🧪 Test Alert - ConsultantOS"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "This is a test alert from *ConsultantOS* monitoring system.\n\n✅ If you received this, your Slack notifications are configured correctly!"
                    }
                }
            ]

            if self.client:
                result = await self._send_via_bot(slack_target, blocks)
            elif self.webhook_url:
                result = await self._send_via_webhook(blocks)
            else:
                return AlertDeliveryResult(
                    channel="slack",
                    status=DeliveryStatus.FAILED,
                    error_message="No Slack bot token or webhook URL configured"
                )

            return result

        except Exception as e:
            self.logger.error(f"Test Slack delivery failed: {e}", exc_info=True)
            return AlertDeliveryResult(
                channel="slack",
                status=DeliveryStatus.FAILED,
                error_message=str(e)
            )

    async def _send_via_bot(
        self,
        channel: str,
        blocks: List[Dict[str, Any]]
    ) -> AlertDeliveryResult:
        """Send message via Slack Web API (bot token)"""
        try:
            response = await self.client.chat_postMessage(
                channel=channel,
                blocks=blocks,
                text="ConsultantOS Alert"  # Fallback text for notifications
            )

            if response["ok"]:
                return AlertDeliveryResult(
                    channel="slack",
                    status=DeliveryStatus.SENT,
                    delivered_at=datetime.utcnow(),
                    metadata={
                        "channel": channel,
                        "message_ts": response.get("ts"),
                        "message_id": response.get("message", {}).get("ts")
                    }
                )
            else:
                return AlertDeliveryResult(
                    channel="slack",
                    status=DeliveryStatus.FAILED,
                    error_message=f"Slack API returned not OK: {response.get('error')}"
                )

        except SlackApiError as e:
            self.logger.error(f"Slack API error: {e.response['error']}")
            return AlertDeliveryResult(
                channel="slack",
                status=DeliveryStatus.FAILED,
                error_message=f"Slack API error: {e.response['error']}"
            )

    async def _send_via_webhook(
        self,
        blocks: List[Dict[str, Any]]
    ) -> AlertDeliveryResult:
        """Send message via incoming webhook"""
        import aiohttp

        try:
            payload = {
                "blocks": blocks,
                "text": "ConsultantOS Alert"
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=payload) as response:
                    if response.status == 200:
                        return AlertDeliveryResult(
                            channel="slack",
                            status=DeliveryStatus.SENT,
                            delivered_at=datetime.utcnow(),
                            metadata={"webhook_url": self.webhook_url[:50] + "..."}
                        )
                    else:
                        error_text = await response.text()
                        return AlertDeliveryResult(
                            channel="slack",
                            status=DeliveryStatus.FAILED,
                            error_message=f"Webhook returned {response.status}: {error_text}"
                        )

        except Exception as e:
            self.logger.error(f"Slack webhook error: {e}")
            return AlertDeliveryResult(
                channel="slack",
                status=DeliveryStatus.FAILED,
                error_message=f"Webhook error: {str(e)}"
            )

    def _build_slack_blocks(
        self,
        title: str,
        summary: str,
        confidence: float,
        changes: list,
        monitor_id: str,
        alert_id: str
    ) -> List[Dict[str, Any]]:
        """Build Slack Block Kit message blocks"""
        # Get color based on confidence
        color = self._get_slack_color(confidence)

        blocks = [
            # Header
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🔔 {self._truncate_text(title, 150)}"
                }
            },
            # Confidence badge
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Confidence:* `{self._format_confidence(confidence)}` {self._get_confidence_emoji(confidence)}"
                }
            },
            # Summary
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Executive Summary*\n{self._truncate_text(summary, 500)}"
                }
            },
            {"type": "divider"}
        ]

        # Add changes (limit to 3 for Slack message length)
        for i, change in enumerate(changes[:3], 1):
            change_title = change.get("title", "Change detected")
            change_desc = self._truncate_text(change.get("description", ""), 200)
            change_type = change.get("change_type", "unknown").replace("_", " ").title()
            change_confidence = change.get("confidence", 0.0)

            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{i}. {change_title}*\n{change_desc}\n`{change_type}` • Confidence: {self._format_confidence(change_confidence)}"
                }
            })

        if len(changes) > 3:
            blocks.append({
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"_+ {len(changes) - 3} more changes detected_"
                    }
                ]
            })

        # Footer with metadata
        blocks.extend([
            {"type": "divider"},
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Monitor ID: `{monitor_id}` • Alert ID: `{alert_id}`"
                    }
                ]
            }
        ])

        return blocks

    def _get_slack_color(self, confidence: float) -> str:
        """Get Slack attachment color based on confidence"""
        if confidence >= 0.8:
            return "danger"  # Red
        elif confidence >= 0.6:
            return "warning"  # Orange
        else:
            return "#fbbf24"  # Yellow

    def _get_confidence_emoji(self, confidence: float) -> str:
        """Get emoji indicator for confidence level"""
        if confidence >= 0.8:
            return "🔴"
        elif confidence >= 0.6:
            return "🟠"
        else:
            return "🟡"
