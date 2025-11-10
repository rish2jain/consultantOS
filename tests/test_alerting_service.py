"""
Tests for multi-channel alerting service.

Tests channels, retry logic, rate limiting, and delivery tracking.
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from consultantos.services.alerting import (
    AlertingService,
    AlertChannel,
    AlertDeliveryResult,
    DeliveryStatus,
)
from consultantos.services.alerting.email_channel import EmailAlertChannel
from consultantos.services.alerting.slack_channel import SlackAlertChannel
from consultantos.services.alerting.webhook_channel import WebhookAlertChannel
from consultantos.services.alerting.inapp_channel import InAppAlertChannel


# ==================== Fixtures ====================

@pytest.fixture
def mock_db():
    """Mock database service"""
    db = AsyncMock()
    db.set_document = AsyncMock()
    db.list_documents = AsyncMock(return_value=[])
    return db


@pytest.fixture
def alerting_config():
    """Test alerting service configuration"""
    return {
        "slack": {
            "bot_token": "xoxb-test-token",
            "webhook_url": "https://hooks.slack.com/test"
        },
        "max_alerts_per_monitor_per_day": 5,
        "max_retries": 3
    }


@pytest.fixture
def alerting_service(alerting_config, mock_db):
    """AlertingService instance with mocked dependencies"""
    with patch("consultantos.services.alerting.service.get_db_service", return_value=mock_db):
        service = AlertingService(alerting_config)
        return service


@pytest.fixture
def sample_alert_data():
    """Sample alert data for testing"""
    return {
        "alert_id": "alert_123",
        "monitor_id": "monitor_456",
        "user_id": "user_789",
        "title": "Market Share Decline Detected",
        "summary": "Competitor X gained 5% market share in Q4",
        "confidence": 0.85,
        "changes": [
            {
                "change_type": "competitive_landscape",
                "title": "Market share shift",
                "description": "Competitor X launched new product",
                "confidence": 0.85,
                "detected_at": datetime.utcnow()
            }
        ],
        "notification_channels": ["email", "slack"],
        "user_preferences": {
            "email": "user@example.com",
            "slack_channel": "#alerts"
        }
    }


# ==================== Email Channel Tests ====================

@pytest.mark.asyncio
async def test_email_channel_success():
    """Test successful email delivery"""
    with patch("consultantos.services.alerting.email_channel.get_email_service") as mock_email:
        email_service = MagicMock()
        email_service.send_email = MagicMock(return_value=True)
        mock_email.return_value = email_service

        channel = EmailAlertChannel({})
        result = await channel.send_alert(
            alert_id="alert_123",
            monitor_id="monitor_456",
            title="Test Alert",
            summary="Test summary",
            confidence=0.8,
            changes=[],
            user_preferences={"email": "test@example.com"}
        )

        assert result.status == DeliveryStatus.SENT
        assert result.channel == "email"
        assert result.delivered_at is not None
        email_service.send_email.assert_called_once()


@pytest.mark.asyncio
async def test_email_channel_missing_address():
    """Test email delivery fails without email address"""
    channel = EmailAlertChannel({})
    result = await channel.send_alert(
        alert_id="alert_123",
        monitor_id="monitor_456",
        title="Test Alert",
        summary="Test summary",
        confidence=0.8,
        changes=[],
        user_preferences={}  # No email
    )

    assert result.status == DeliveryStatus.FAILED
    assert "No email address" in result.error_message


@pytest.mark.asyncio
async def test_email_channel_html_escaping():
    """Test HTML escaping in email templates"""
    with patch("consultantos.services.alerting.email_channel.get_email_service") as mock_email:
        email_service = MagicMock()
        email_service.send_email = MagicMock(return_value=True)
        mock_email.return_value = email_service

        channel = EmailAlertChannel({})

        # Try to inject XSS
        result = await channel.send_alert(
            alert_id="alert_123",
            monitor_id="monitor_456",
            title="<script>alert('xss')</script>",
            summary="<img src=x onerror=alert(1)>",
            confidence=0.8,
            changes=[],
            user_preferences={"email": "test@example.com"}
        )

        assert result.status == DeliveryStatus.SENT

        # Check that HTML was escaped
        call_args = email_service.send_email.call_args
        html_body = call_args.kwargs.get("html_body", "")
        assert "<script>" not in html_body
        assert "&lt;script&gt;" in html_body


# ==================== Slack Channel Tests ====================

@pytest.mark.asyncio
async def test_slack_channel_bot_token_success():
    """Test successful Slack delivery via bot token"""
    with patch("consultantos.services.alerting.slack_channel.AsyncWebClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.chat_postMessage = AsyncMock(return_value={
            "ok": True,
            "ts": "1234567890.123456"
        })
        mock_client_class.return_value = mock_client

        channel = SlackAlertChannel({"bot_token": "xoxb-test-token"})
        result = await channel.send_alert(
            alert_id="alert_123",
            monitor_id="monitor_456",
            title="Test Alert",
            summary="Test summary",
            confidence=0.8,
            changes=[],
            user_preferences={"slack_channel": "#alerts"}
        )

        assert result.status == DeliveryStatus.SENT
        assert result.channel == "slack"
        mock_client.chat_postMessage.assert_called_once()


@pytest.mark.asyncio
async def test_slack_channel_webhook_success():
    """Test successful Slack delivery via webhook"""
    with patch("aiohttp.ClientSession") as mock_session_class:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value="ok")

        mock_session = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.post = AsyncMock(return_value=mock_response)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session_class.return_value = mock_session

        channel = SlackAlertChannel({"webhook_url": "https://hooks.slack.com/test"})
        result = await channel.send_alert(
            alert_id="alert_123",
            monitor_id="monitor_456",
            title="Test Alert",
            summary="Test summary",
            confidence=0.8,
            changes=[],
            user_preferences={"slack_channel": "#alerts"}
        )

        assert result.status == DeliveryStatus.SENT


@pytest.mark.asyncio
async def test_slack_channel_block_formatting():
    """Test Slack Block Kit formatting"""
    with patch("consultantos.services.alerting.slack_channel.AsyncWebClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.chat_postMessage = AsyncMock(return_value={"ok": True})
        mock_client_class.return_value = mock_client

        channel = SlackAlertChannel({"bot_token": "xoxb-test-token"})
        result = await channel.send_alert(
            alert_id="alert_123",
            monitor_id="monitor_456",
            title="Market Share Decline",
            summary="Competitor gained 5% market share",
            confidence=0.85,
            changes=[
                {
                    "change_type": "competitive_landscape",
                    "title": "New competitor product",
                    "description": "Competitor X launched product Y",
                    "confidence": 0.9
                }
            ],
            user_preferences={"slack_channel": "#alerts"}
        )

        assert result.status == DeliveryStatus.SENT

        # Check that blocks were created
        call_args = mock_client.chat_postMessage.call_args
        blocks = call_args.kwargs.get("blocks", [])
        assert len(blocks) > 0
        assert any("Market Share Decline" in str(block) for block in blocks)


# ==================== Webhook Channel Tests ====================

@pytest.mark.asyncio
async def test_webhook_channel_success():
    """Test successful webhook delivery"""
    with patch("aiohttp.ClientSession") as mock_session_class:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value="success")

        mock_session = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.post = AsyncMock(return_value=mock_response)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session_class.return_value = mock_session

        channel = WebhookAlertChannel({})
        result = await channel.send_alert(
            alert_id="alert_123",
            monitor_id="monitor_456",
            title="Test Alert",
            summary="Test summary",
            confidence=0.8,
            changes=[],
            user_preferences={"webhook_url": "https://example.com/webhook"}
        )

        assert result.status == DeliveryStatus.SENT
        assert result.channel == "webhook"


@pytest.mark.asyncio
async def test_webhook_channel_custom_headers():
    """Test webhook with custom headers"""
    with patch("aiohttp.ClientSession") as mock_session_class:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value="success")

        mock_session = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.post = AsyncMock(return_value=mock_response)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session_class.return_value = mock_session

        channel = WebhookAlertChannel({})
        result = await channel.send_alert(
            alert_id="alert_123",
            monitor_id="monitor_456",
            title="Test Alert",
            summary="Test summary",
            confidence=0.8,
            changes=[],
            user_preferences={
                "webhook_url": "https://example.com/webhook",
                "webhook_headers": {"Authorization": "Bearer secret-token"}
            }
        )

        assert result.status == DeliveryStatus.SENT

        # Check headers were passed
        call_args = mock_session.post.call_args
        headers = call_args.kwargs.get("headers", {})
        assert "Authorization" in headers
        assert headers["Authorization"] == "Bearer secret-token"


# ==================== In-App Channel Tests ====================

@pytest.mark.asyncio
async def test_inapp_channel_success(mock_db):
    """Test successful in-app notification storage"""
    with patch("consultantos.services.alerting.inapp_channel.get_db_service", return_value=mock_db):
        channel = InAppAlertChannel({})
        result = await channel.send_alert(
            alert_id="alert_123",
            monitor_id="monitor_456",
            title="Test Alert",
            summary="Test summary",
            confidence=0.8,
            changes=[],
            user_preferences={"user_id": "user_789"}
        )

        assert result.status == DeliveryStatus.SENT
        assert result.channel == "in_app"
        mock_db.set_document.assert_called_once()

        # Check correct Firestore path
        call_args = mock_db.set_document.call_args
        collection_path = call_args.args[0]
        assert "users/user_789/notifications" in collection_path


# ==================== AlertingService Tests ====================

@pytest.mark.asyncio
async def test_alerting_service_multi_channel_delivery(alerting_service, sample_alert_data):
    """Test parallel delivery to multiple channels"""
    # Mock all channels to return success
    for channel in alerting_service.channels.values():
        channel.send_alert = AsyncMock(return_value=AlertDeliveryResult(
            channel=channel.__class__.__name__.replace("AlertChannel", "").lower(),
            status=DeliveryStatus.SENT,
            delivered_at=datetime.utcnow()
        ))

    results = await alerting_service.send_alert(**sample_alert_data)

    # Check both channels were called
    assert "email" in results
    assert "slack" in results
    assert results["email"].status == DeliveryStatus.SENT
    assert results["slack"].status == DeliveryStatus.SENT


@pytest.mark.asyncio
async def test_alerting_service_retry_logic(alerting_service, sample_alert_data):
    """Test exponential backoff retry"""
    # Mock channel to fail twice, then succeed
    mock_channel = alerting_service.channels["email"]
    call_count = 0

    async def mock_send(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            return AlertDeliveryResult(
                channel="email",
                status=DeliveryStatus.FAILED,
                error_message="Temporary failure"
            )
        return AlertDeliveryResult(
            channel="email",
            status=DeliveryStatus.SENT,
            delivered_at=datetime.utcnow()
        )

    mock_channel.send_alert = mock_send

    # Only test email channel
    sample_alert_data["notification_channels"] = ["email"]
    results = await alerting_service.send_alert(**sample_alert_data)

    # Should succeed after retries
    assert results["email"].status == DeliveryStatus.SENT
    assert call_count == 3  # Failed twice, succeeded on third attempt


@pytest.mark.asyncio
async def test_alerting_service_rate_limiting(alerting_service, sample_alert_data):
    """Test rate limiting (max 5 alerts/monitor/day)"""
    # Mock successful delivery
    for channel in alerting_service.channels.values():
        channel.send_alert = AsyncMock(return_value=AlertDeliveryResult(
            channel=channel.__class__.__name__.replace("AlertChannel", "").lower(),
            status=DeliveryStatus.SENT,
            delivered_at=datetime.utcnow()
        ))

    # Send 5 alerts (should all succeed)
    for i in range(5):
        results = await alerting_service.send_alert(**sample_alert_data)
        assert all(r.status == DeliveryStatus.SENT for r in results.values())

    # 6th alert should be rate limited
    results = await alerting_service.send_alert(**sample_alert_data)
    assert all(r.status == DeliveryStatus.RATE_LIMITED for r in results.values())


@pytest.mark.asyncio
async def test_alerting_service_graceful_degradation(alerting_service, sample_alert_data):
    """Test that one channel failure doesn't block others"""
    # Email fails, Slack succeeds
    alerting_service.channels["email"].send_alert = AsyncMock(
        return_value=AlertDeliveryResult(
            channel="email",
            status=DeliveryStatus.FAILED,
            error_message="SMTP server down"
        )
    )

    alerting_service.channels["slack"].send_alert = AsyncMock(
        return_value=AlertDeliveryResult(
            channel="slack",
            status=DeliveryStatus.SENT,
            delivered_at=datetime.utcnow()
        )
    )

    results = await alerting_service.send_alert(**sample_alert_data)

    # Slack should succeed even though email failed
    assert results["email"].status == DeliveryStatus.FAILED
    assert results["slack"].status == DeliveryStatus.SENT


@pytest.mark.asyncio
async def test_alerting_service_test_notification(alerting_service):
    """Test sending test notifications"""
    # Mock all channels
    for channel in alerting_service.channels.values():
        channel.test_delivery = AsyncMock(return_value=AlertDeliveryResult(
            channel=channel.__class__.__name__.replace("AlertChannel", "").lower(),
            status=DeliveryStatus.SENT,
            delivered_at=datetime.utcnow()
        ))

    results = await alerting_service.test_notification(
        user_id="user_789",
        notification_channels=["email", "slack"],
        user_preferences={
            "email": "test@example.com",
            "slack_channel": "#alerts"
        }
    )

    assert "email" in results
    assert "slack" in results
    assert results["email"].status == DeliveryStatus.SENT
    assert results["slack"].status == DeliveryStatus.SENT


@pytest.mark.asyncio
async def test_alerting_service_delivery_tracking(alerting_service, sample_alert_data, mock_db):
    """Test that delivery status is tracked in Firestore"""
    # Mock successful delivery
    for channel in alerting_service.channels.values():
        channel.send_alert = AsyncMock(return_value=AlertDeliveryResult(
            channel=channel.__class__.__name__.replace("AlertChannel", "").lower(),
            status=DeliveryStatus.SENT,
            delivered_at=datetime.utcnow()
        ))

    await alerting_service.send_alert(**sample_alert_data)

    # Check delivery was tracked
    mock_db.set_document.assert_called()
    call_args = mock_db.set_document.call_args
    collection_path = call_args.args[0]
    assert "alert_deliveries" in collection_path
