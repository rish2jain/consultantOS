"""
Multi-channel alerting service for ConsultantOS monitoring.

Provides flexible alert delivery via email, Slack, webhooks, and in-app notifications
with retry logic, rate limiting, and delivery tracking.
"""

from .service import AlertingService, get_alerting_service
from .base_channel import AlertChannel, AlertDeliveryResult, DeliveryStatus

__all__ = [
    "AlertingService",
    "get_alerting_service",
    "AlertChannel",
    "AlertDeliveryResult",
    "DeliveryStatus",
]
