"""
Email alert channel with HTML templates and chart integration.
"""

import html
from datetime import datetime
from typing import Dict, Any
from .base_channel import AlertChannel, AlertDeliveryResult, DeliveryStatus
from consultantos.services.email_service import get_email_service


class EmailAlertChannel(AlertChannel):
    """
    Email delivery channel for alerts with rich HTML formatting.

    Supports:
    - HTML templates with change summaries
    - Embedded charts (optional)
    - Plain text fallback
    - XSS protection via HTML escaping
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
        """Send alert via email"""
        try:
            email_service = get_email_service()

            # Get user email from preferences
            to_email = user_preferences.get("email")
            if not to_email:
                return AlertDeliveryResult(
                    channel="email",
                    status=DeliveryStatus.FAILED,
                    error_message="No email address in user preferences"
                )

            # Build email content
            subject = f"🔔 Alert: {title}"
            plain_body = self._build_plain_text(
                title, summary, confidence, changes, monitor_id, alert_id
            )
            html_body = self._build_html_template(
                title, summary, confidence, changes, monitor_id, alert_id
            )

            # Send email
            success = email_service.send_email(
                to=to_email,
                subject=subject,
                body=plain_body,
                html_body=html_body
            )

            if success:
                return AlertDeliveryResult(
                    channel="email",
                    status=DeliveryStatus.SENT,
                    delivered_at=datetime.utcnow(),
                    metadata={"email": to_email}
                )
            else:
                return AlertDeliveryResult(
                    channel="email",
                    status=DeliveryStatus.FAILED,
                    error_message="Email service returned failure"
                )

        except Exception as e:
            self.logger.error(f"Email alert delivery failed: {e}", exc_info=True)
            return AlertDeliveryResult(
                channel="email",
                status=DeliveryStatus.FAILED,
                error_message=str(e)
            )

    async def test_delivery(
        self,
        user_preferences: Dict[str, Any]
    ) -> AlertDeliveryResult:
        """Send test email notification"""
        try:
            email_service = get_email_service()

            to_email = user_preferences.get("email")
            if not to_email:
                return AlertDeliveryResult(
                    channel="email",
                    status=DeliveryStatus.FAILED,
                    error_message="No email address in user preferences"
                )

            subject = "🧪 Test Alert - ConsultantOS"
            body = """
This is a test alert from ConsultantOS monitoring system.

If you received this, your email notifications are configured correctly!
            """

            html_body = """
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #2563eb;">🧪 Test Alert</h2>
                <p>This is a test alert from <strong>ConsultantOS</strong> monitoring system.</p>
                <p style="color: #059669;">✅ If you received this, your email notifications are configured correctly!</p>
            </body>
            </html>
            """

            success = email_service.send_email(to_email, subject, body, html_body)

            if success:
                return AlertDeliveryResult(
                    channel="email",
                    status=DeliveryStatus.SENT,
                    delivered_at=datetime.utcnow(),
                    metadata={"email": to_email}
                )
            else:
                return AlertDeliveryResult(
                    channel="email",
                    status=DeliveryStatus.FAILED,
                    error_message="Email service returned failure"
                )

        except Exception as e:
            self.logger.error(f"Test email delivery failed: {e}", exc_info=True)
            return AlertDeliveryResult(
                channel="email",
                status=DeliveryStatus.FAILED,
                error_message=str(e)
            )

    def _build_plain_text(
        self,
        title: str,
        summary: str,
        confidence: float,
        changes: list,
        monitor_id: str,
        alert_id: str
    ) -> str:
        """Build plain text email body"""
        change_lines = []
        for i, change in enumerate(changes[:5], 1):  # Limit to 5 changes
            change_lines.append(
                f"{i}. {change.get('title', 'Change detected')} "
                f"(Confidence: {self._format_confidence(change.get('confidence', 0.0))})"
            )

        return f"""
ConsultantOS Alert Notification
================================

{title}

Confidence: {self._format_confidence(confidence)}

Summary:
{summary}

Detected Changes:
{chr(10).join(change_lines)}

Monitor ID: {monitor_id}
Alert ID: {alert_id}

---
This is an automated alert from ConsultantOS continuous monitoring.
        """.strip()

    def _build_html_template(
        self,
        title: str,
        summary: str,
        confidence: float,
        changes: list,
        monitor_id: str,
        alert_id: str
    ) -> str:
        """Build rich HTML email template"""
        # Escape all user-provided content
        safe_title = html.escape(title, quote=True)
        safe_summary = html.escape(summary, quote=True)
        safe_monitor_id = html.escape(monitor_id, quote=True)
        safe_alert_id = html.escape(alert_id, quote=True)

        # Build changes HTML
        changes_html = []
        for change in changes[:5]:  # Limit to 5 changes
            change_type = html.escape(change.get("change_type", "unknown"), quote=True)
            change_title = html.escape(change.get("title", "Change detected"), quote=True)
            change_desc = html.escape(
                self._truncate_text(change.get("description", ""), 150),
                quote=True
            )
            change_confidence = change.get("confidence", 0.0)

            # Color code by confidence
            confidence_color = self._get_confidence_color(change_confidence)

            changes_html.append(f"""
                <div style="border-left: 4px solid {confidence_color}; padding-left: 12px; margin-bottom: 16px;">
                    <div style="font-weight: bold; color: #374151; margin-bottom: 4px;">
                        {change_title}
                    </div>
                    <div style="color: #6b7280; font-size: 14px; margin-bottom: 4px;">
                        {change_desc}
                    </div>
                    <div style="font-size: 12px; color: #9ca3af;">
                        <span style="background: #f3f4f6; padding: 2px 8px; border-radius: 4px;">
                            {change_type}
                        </span>
                        <span style="margin-left: 8px;">
                            Confidence: {self._format_confidence(change_confidence)}
                        </span>
                    </div>
                </div>
            """)

        overall_color = self._get_confidence_color(confidence)

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.6; color: #1f2937; max-width: 600px; margin: 0 auto; padding: 20px;">

            <!-- Header -->
            <div style="background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
                        color: white; padding: 24px; border-radius: 8px; margin-bottom: 24px;">
                <h1 style="margin: 0; font-size: 24px; font-weight: 600;">
                    🔔 ConsultantOS Alert
                </h1>
            </div>

            <!-- Alert Title -->
            <div style="margin-bottom: 24px;">
                <h2 style="color: #111827; font-size: 20px; margin: 0 0 8px 0;">
                    {safe_title}
                </h2>
                <div style="display: inline-block; background: {overall_color}; color: white;
                           padding: 4px 12px; border-radius: 12px; font-size: 14px; font-weight: 600;">
                    Confidence: {self._format_confidence(confidence)}
                </div>
            </div>

            <!-- Summary -->
            <div style="background: #f9fafb; border-left: 4px solid #2563eb;
                        padding: 16px; border-radius: 4px; margin-bottom: 24px;">
                <div style="font-weight: 600; color: #374151; margin-bottom: 8px;">
                    Executive Summary
                </div>
                <div style="color: #4b5563;">
                    {safe_summary}
                </div>
            </div>

            <!-- Changes Detected -->
            <div style="margin-bottom: 24px;">
                <h3 style="color: #111827; font-size: 18px; margin: 0 0 16px 0;">
                    Detected Changes
                </h3>
                {''.join(changes_html)}
            </div>

            <!-- Footer -->
            <div style="border-top: 1px solid #e5e7eb; padding-top: 16px;
                        margin-top: 24px; font-size: 12px; color: #6b7280;">
                <div style="margin-bottom: 8px;">
                    <strong>Monitor ID:</strong> {safe_monitor_id}<br>
                    <strong>Alert ID:</strong> {safe_alert_id}
                </div>
                <div style="color: #9ca3af;">
                    This is an automated alert from ConsultantOS continuous monitoring.
                </div>
            </div>
        </body>
        </html>
        """

    def _get_confidence_color(self, confidence: float) -> str:
        """Get color based on confidence score"""
        if confidence >= 0.8:
            return "#dc2626"  # Red - high confidence
        elif confidence >= 0.6:
            return "#ea580c"  # Orange - medium confidence
        else:
            return "#ca8a04"  # Yellow - lower confidence
