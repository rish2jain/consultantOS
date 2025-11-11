"""
Pydantic models for continuous intelligence monitoring system.

Implements the data structures for monitoring companies, detecting changes,
and managing alerts in the continuous intelligence platform.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class MonitoringFrequency(str, Enum):
    """Monitoring check frequency options"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class MonitorStatus(str, Enum):
    """Monitor lifecycle status"""
    ACTIVE = "active"
    PAUSED = "paused"
    DELETED = "deleted"
    ERROR = "error"


class NotificationChannel(str, Enum):
    """Notification delivery channels"""
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    IN_APP = "in_app"


class ChangeType(str, Enum):
    """Types of detected changes"""
    COMPETITIVE_LANDSCAPE = "competitive_landscape"
    MARKET_TREND = "market_trend"
    FINANCIAL_METRIC = "financial_metric"
    STRATEGIC_SHIFT = "strategic_shift"
    REGULATORY = "regulatory"
    TECHNOLOGY = "technology"
    LEADERSHIP = "leadership"


class MonitoringConfig(BaseModel):
    """Configuration for a monitoring instance"""

    frequency: MonitoringFrequency = Field(
        default=MonitoringFrequency.DAILY,
        description="How often to check for updates"
    )

    frameworks: List[str] = Field(
        default=["porter", "swot"],
        description="Business frameworks to apply in analysis"
    )

    alert_threshold: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Minimum confidence score to trigger alert (0.0-1.0)"
    )

    notification_channels: List[NotificationChannel] = Field(
        default=[NotificationChannel.EMAIL, NotificationChannel.IN_APP],
        description="Channels for alert delivery"
    )

    notification_preferences: Optional[dict] = Field(
        default=None,
        description="Channel-specific notification settings (e.g., email, Slack webhook, etc.)"
    )

    keywords: Optional[List[str]] = Field(
        default=None,
        description="Optional keywords to monitor for mentions"
    )

    competitors: Optional[List[str]] = Field(
        default=None,
        description="Optional competitor companies to track"
    )

    @field_validator("frameworks")
    @classmethod
    def validate_frameworks(cls, v: List[str]) -> List[str]:
        """Validate framework names"""
        valid_frameworks = {
            "porter", "swot", "pestel", "blue_ocean",
            "ansoff", "bcg_matrix", "value_chain"
        }
        invalid = set(v) - valid_frameworks
        if invalid:
            raise ValueError(f"Invalid frameworks: {invalid}")
        return v


class Change(BaseModel):
    """Represents a detected change in monitored data"""

    change_type: ChangeType = Field(
        description="Category of change detected"
    )

    title: str = Field(
        description="Brief description of change"
    )

    description: str = Field(
        description="Detailed explanation of change"
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence score for this change detection"
    )

    source_urls: List[str] = Field(
        default_factory=list,
        description="URLs where change was detected"
    )

    detected_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When change was detected"
    )

    previous_value: Optional[str] = Field(
        default=None,
        description="Previous state (if applicable)"
    )

    current_value: Optional[str] = Field(
        default=None,
        description="Current state (if applicable)"
    )


class AnomalyScoreModel(BaseModel):
    """Anomaly detection result (embedded in Alert)"""

    metric_name: str
    anomaly_type: str  # point, contextual, trend_reversal, volatility_spike
    severity: float = Field(ge=0.0, le=10.0)
    confidence: float = Field(ge=0.0, le=1.0)
    explanation: str
    statistical_details: dict = Field(default_factory=dict)
    forecast_value: Optional[float] = None
    actual_value: Optional[float] = None
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None


class AlertPriorityModel(BaseModel):
    """Alert priority score (embedded in Alert)"""

    priority_score: float = Field(ge=0.0, le=10.0)
    urgency_level: str  # critical, high, medium, low
    should_notify: bool
    reasoning: List[str] = Field(default_factory=list)
    throttle_until: Optional[datetime] = None


class Alert(BaseModel):
    """Alert notification for material changes"""

    id: str = Field(
        description="Unique alert identifier"
    )

    monitor_id: str = Field(
        description="ID of monitor that generated this alert"
    )

    title: str = Field(
        description="Alert headline"
    )

    summary: str = Field(
        description="Executive summary of changes"
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Overall confidence score for alert"
    )

    changes_detected: List[Change] = Field(
        description="List of specific changes detected"
    )

    # Statistical anomaly scores
    anomaly_scores: List[AnomalyScoreModel] = Field(
        default_factory=list,
        description="Statistical anomaly detection results"
    )

    # Priority scoring
    priority: Optional[AlertPriorityModel] = Field(
        default=None,
        description="Alert priority and notification recommendation"
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Alert creation timestamp"
    )

    read: bool = Field(
        default=False,
        description="Whether user has read this alert"
    )

    read_at: Optional[datetime] = Field(
        default=None,
        description="When alert was marked as read"
    )

    user_feedback: Optional[str] = Field(
        default=None,
        description="User feedback on alert quality"
    )

    action_taken: Optional[str] = Field(
        default=None,
        description="Action user took based on alert"
    )

    # Root cause analysis
    root_cause_analysis: Optional[dict] = Field(
        default=None,
        description="Enhanced root cause analysis with actionable insights"
    )


class Monitor(BaseModel):
    """Continuous monitoring instance for a company"""

    id: str = Field(
        description="Unique monitor identifier"
    )

    user_id: str = Field(
        description="Owner user ID"
    )

    company: str = Field(
        description="Company being monitored"
    )

    industry: str = Field(
        description="Industry sector"
    )

    config: MonitoringConfig = Field(
        description="Monitoring configuration"
    )

    status: MonitorStatus = Field(
        default=MonitorStatus.ACTIVE,
        description="Current monitor status"
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Monitor creation timestamp"
    )

    last_check: Optional[datetime] = Field(
        default=None,
        description="Last monitoring check timestamp"
    )

    next_check: Optional[datetime] = Field(
        default=None,
        description="Scheduled next check timestamp"
    )

    last_alert_id: Optional[str] = Field(
        default=None,
        description="ID of most recent alert"
    )

    total_alerts: int = Field(
        default=0,
        description="Total alerts generated"
    )

    error_count: int = Field(
        default=0,
        description="Consecutive error count"
    )

    last_error: Optional[str] = Field(
        default=None,
        description="Most recent error message"
    )


class MonitorCreateRequest(BaseModel):
    """Request to create new monitor"""

    company: str = Field(
        min_length=1,
        max_length=200,
        description="Company name to monitor"
    )

    industry: str = Field(
        min_length=1,
        max_length=200,
        description="Industry sector"
    )

    config: MonitoringConfig = Field(
        default_factory=MonitoringConfig,
        description="Optional monitoring configuration"
    )


class MonitorUpdateRequest(BaseModel):
    """Request to update monitor configuration"""

    config: Optional[MonitoringConfig] = Field(
        default=None,
        description="Updated configuration"
    )

    status: Optional[MonitorStatus] = Field(
        default=None,
        description="Updated status"
    )


class MonitorListResponse(BaseModel):
    """Response with list of monitors"""

    monitors: List[Monitor] = Field(
        description="List of user's monitors"
    )

    total: int = Field(
        description="Total number of monitors"
    )

    active_count: int = Field(
        description="Number of active monitors"
    )


class AlertListResponse(BaseModel):
    """Response with list of alerts"""

    alerts: List[Alert] = Field(
        description="List of alerts"
    )

    total: int = Field(
        description="Total number of alerts"
    )

    unread_count: int = Field(
        description="Number of unread alerts"
    )


class AlertFeedbackRequest(BaseModel):
    """User feedback on alert quality"""

    feedback: str = Field(
        description="Feedback text: 'helpful', 'not_helpful', 'false_positive', etc."
    )

    action_taken: Optional[str] = Field(
        default=None,
        description="Action taken based on alert"
    )

    notes: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Additional notes"
    )


class MonitorAnalysisSnapshot(BaseModel):
    """Snapshot of analysis results for change detection"""

    monitor_id: str
    timestamp: datetime
    company: str
    industry: str

    # Key metrics for change detection
    competitive_forces: dict = Field(
        default_factory=dict,
        description="Porter's 5 Forces analysis snapshot"
    )

    market_trends: List[str] = Field(
        default_factory=list,
        description="Key market trends"
    )

    financial_metrics: dict = Field(
        default_factory=dict,
        description="Financial indicators"
    )

    strategic_position: dict = Field(
        default_factory=dict,
        description="SWOT or strategic framework results"
    )

    news_sentiment: Optional[float] = Field(
        default=None,
        description="Aggregated news sentiment score"
    )

    competitor_mentions: dict = Field(
        default_factory=dict,
        description="Competitor activity tracking"
    )


class MonitoringStats(BaseModel):
    """Statistics for monitoring dashboard"""

    total_monitors: int
    active_monitors: int
    paused_monitors: int
    total_alerts_24h: int
    unread_alerts: int
    avg_alert_confidence: float
    top_change_types: List[tuple[str, int]]  # (change_type, count)


class NotificationPreferencesUpdate(BaseModel):
    """Request to update notification preferences"""

    notification_channels: Optional[List[NotificationChannel]] = Field(
        default=None,
        description="Updated list of notification channels"
    )

    notification_preferences: Optional[dict] = Field(
        default=None,
        description="""Channel-specific settings. Example:
        {
            "email": "user@example.com",
            "slack_channel": "#alerts",
            "slack_user_id": "U123456",
            "webhook_url": "https://hooks.example.com/...",
            "webhook_headers": {"Authorization": "Bearer token"},
            "webhook_timeout": 10
        }"""
    )


class NotificationHistoryItem(BaseModel):
    """Single notification delivery record"""

    alert_id: str = Field(description="Alert identifier")
    channel: str = Field(description="Channel name")
    status: str = Field(description="Delivery status (sent, failed, pending)")
    delivered_at: Optional[datetime] = Field(default=None, description="Delivery timestamp")
    error_message: Optional[str] = Field(default=None, description="Error details if failed")
    retry_count: int = Field(default=0, description="Number of retry attempts")


class NotificationHistoryResponse(BaseModel):
    """Response with notification delivery history"""

    monitor_id: str = Field(description="Monitor identifier")
    deliveries: List[NotificationHistoryItem] = Field(
        description="List of delivery records"
    )
    total: int = Field(description="Total delivery attempts")
    success_count: int = Field(description="Successful deliveries")
    failure_count: int = Field(description="Failed deliveries")


class TestNotificationRequest(BaseModel):
    """Request to send test notifications"""

    channels: Optional[List[NotificationChannel]] = Field(
        default=None,
        description="Specific channels to test (defaults to all configured)"
    )


class TestNotificationResponse(BaseModel):
    """Response from test notification"""

    results: dict = Field(
        description="Delivery results by channel"
    )
    success: bool = Field(
        description="True if all channels succeeded"
    )
