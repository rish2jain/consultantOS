"""
Base alert channel abstract class and shared models.
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class DeliveryStatus(str, Enum):
    """Alert delivery status"""
    SENT = "sent"
    FAILED = "failed"
    PENDING = "pending"
    RATE_LIMITED = "rate_limited"


class AlertDeliveryResult(BaseModel):
    """Result of alert delivery attempt"""

    channel: str = Field(
        description="Channel name (email, slack, webhook, in_app)"
    )

    status: DeliveryStatus = Field(
        description="Delivery status"
    )

    delivered_at: Optional[datetime] = Field(
        default=None,
        description="When alert was delivered (if successful)"
    )

    error_message: Optional[str] = Field(
        default=None,
        description="Error details if failed"
    )

    retry_count: int = Field(
        default=0,
        description="Number of retry attempts"
    )

    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Channel-specific metadata (e.g., Slack message ID)"
    )


class AlertChannel(ABC):
    """
    Abstract base class for alert delivery channels.

    All channels must implement send_alert() method with retry logic
    and rate limiting built in.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize channel with configuration.

        Args:
            config: Channel-specific configuration
        """
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @abstractmethod
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
        """
        Send alert via this channel.

        Args:
            alert_id: Unique alert identifier
            monitor_id: Monitor that generated alert
            title: Alert headline
            summary: Executive summary
            confidence: Confidence score (0.0-1.0)
            changes: List of detected changes
            user_preferences: User-specific channel preferences

        Returns:
            AlertDeliveryResult with delivery status and metadata
        """
        pass

    @abstractmethod
    async def test_delivery(
        self,
        user_preferences: Dict[str, Any]
    ) -> AlertDeliveryResult:
        """
        Send test notification to validate channel configuration.

        Args:
            user_preferences: User-specific channel preferences

        Returns:
            AlertDeliveryResult with test delivery status
        """
        pass

    def _format_confidence(self, confidence: float) -> str:
        """Format confidence score as percentage"""
        return f"{confidence * 100:.0f}%"

    def _truncate_text(self, text: str, max_length: int) -> str:
        """Truncate text to max length with ellipsis"""
        if len(text) <= max_length:
            return text
        return text[:max_length - 3] + "..."
