"""
Tests for Sentry integration.

Tests error tracking, performance monitoring, context enrichment,
and PII sanitization.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from consultantos.observability.sentry_integration import (
    SentryIntegration,
    setup_sentry,
    PII_PATTERNS,
)


class TestSentryIntegration:
    """Test SentryIntegration class"""

    def test_init(self):
        """Test initialization"""
        integration = SentryIntegration(
            dsn="https://test@sentry.io/12345",
            environment="test",
            traces_sample_rate=0.5,
            release="test-release",
        )

        assert integration.dsn == "https://test@sentry.io/12345"
        assert integration.environment == "test"
        assert integration.traces_sample_rate == 0.5
        assert integration.release == "test-release"
        assert integration._initialized is False

    def test_init_from_env(self, monkeypatch):
        """Test initialization from environment variables"""
        monkeypatch.setenv("SENTRY_DSN", "https://env@sentry.io/12345")
        monkeypatch.setenv("SENTRY_ENVIRONMENT", "production")
        monkeypatch.setenv("SENTRY_RELEASE", "v1.0.0")

        integration = SentryIntegration()

        assert integration.dsn == "https://env@sentry.io/12345"
        assert integration.environment == "production"
        assert integration.release == "v1.0.0"

    @patch("consultantos.observability.sentry_integration.sentry_sdk")
    def test_initialize(self, mock_sentry_sdk):
        """Test Sentry SDK initialization"""
        integration = SentryIntegration(
            dsn="https://test@sentry.io/12345",
            environment="test",
            traces_sample_rate=0.3,
        )

        integration.initialize()

        assert integration._initialized is True
        mock_sentry_sdk.init.assert_called_once()

        # Verify init was called with correct parameters
        call_args = mock_sentry_sdk.init.call_args
        assert call_args.kwargs["dsn"] == "https://test@sentry.io/12345"
        assert call_args.kwargs["environment"] == "test"
        assert call_args.kwargs["traces_sample_rate"] == 0.3
        assert call_args.kwargs["send_default_pii"] is False

    @patch("consultantos.observability.sentry_integration.sentry_sdk")
    def test_initialize_without_dsn(self, mock_sentry_sdk):
        """Test initialization without DSN (should skip)"""
        integration = SentryIntegration(dsn=None)

        integration.initialize()

        assert integration._initialized is False
        mock_sentry_sdk.init.assert_not_called()

    def test_sanitize_email(self):
        """Test email sanitization"""
        integration = SentryIntegration()

        text = "Contact us at user@example.com for support"
        sanitized = integration._sanitize_string(text)

        assert "user@example.com" not in sanitized
        assert "[EMAIL_REDACTED]" in sanitized

    def test_sanitize_api_key(self):
        """Test API key sanitization"""
        integration = SentryIntegration()

        text = 'api_key = "sk_test_1234567890"'
        sanitized = integration._sanitize_string(text)

        assert "sk_test_1234567890" not in sanitized
        assert "[API_KEY_REDACTED]" in sanitized

    def test_sanitize_dict(self):
        """Test dictionary sanitization"""
        integration = SentryIntegration()

        data = {
            "username": "john_doe",
            "email": "john@example.com",
            "password": "secret123",
            "api_key": "sk_test_abc",
            "normal_field": "safe_value",
        }

        sanitized = integration._sanitize_dict(data)

        assert sanitized["username"] == "john_doe"
        assert sanitized["email"] == "[REDACTED]"
        assert sanitized["password"] == "[REDACTED]"
        assert sanitized["api_key"] == "[REDACTED]"
        assert sanitized["normal_field"] == "safe_value"

    def test_sanitize_nested_structures(self):
        """Test sanitization of nested data structures"""
        integration = SentryIntegration()

        data = {
            "user": {
                "name": "John",
                "email": "john@example.com",
                "metadata": {
                    "api_key": "secret_key",
                    "preferences": ["option1", "option2"],
                }
            },
            "items": [
                {"name": "Item 1", "token": "secret_token"},
                {"name": "Item 2", "email": "user@test.com"},
            ]
        }

        sanitized = integration._sanitize_pii(data)

        assert sanitized["user"]["email"] == "[REDACTED]"
        assert sanitized["user"]["metadata"]["api_key"] == "[REDACTED]"
        assert sanitized["items"][0]["token"] == "[REDACTED]"
        assert sanitized["items"][1]["email"] == "[REDACTED]"
        assert sanitized["user"]["name"] == "John"
        assert sanitized["items"][0]["name"] == "Item 1"

    def test_custom_fingerprint_agent(self):
        """Test custom fingerprint for agent errors"""
        integration = SentryIntegration()

        event = {
            "tags": {"agent_name": "FinancialAgent"},
        }
        hint = {
            "exception": ValueError("Test error")
        }

        result = integration._add_custom_fingerprint(event, hint)

        assert "fingerprint" in result
        assert "ValueError" in result["fingerprint"]
        assert "agent:FinancialAgent" in result["fingerprint"]

    def test_custom_fingerprint_endpoint(self):
        """Test custom fingerprint for API endpoint errors"""
        integration = SentryIntegration()

        event = {
            "tags": {"endpoint": "/api/analyze"},
        }
        hint = {
            "exception": RuntimeError("Test error")
        }

        result = integration._add_custom_fingerprint(event, hint)

        assert "fingerprint" in result
        assert "RuntimeError" in result["fingerprint"]
        assert "endpoint:/api/analyze" in result["fingerprint"]

    @patch("consultantos.observability.sentry_integration.sentry_sdk")
    def test_set_user_context(self, mock_sentry_sdk):
        """Test setting user context"""
        SentryIntegration.set_user_context(
            user_id="user123",
            tier="pro",
            custom_field="value"
        )

        mock_sentry_sdk.set_user.assert_called_once()
        user_data = mock_sentry_sdk.set_user.call_args[0][0]

        assert user_data["id"] == "user123"
        assert user_data["tier"] == "pro"
        assert user_data["custom_field"] == "value"

    @patch("consultantos.observability.sentry_integration.sentry_sdk")
    def test_set_monitor_context(self, mock_sentry_sdk):
        """Test setting monitor context"""
        SentryIntegration.set_monitor_context(
            monitor_id="mon123",
            company="Tesla",
            industry="Automotive"
        )

        # Verify tags were set
        assert mock_sentry_sdk.set_tag.call_count >= 2

        # Verify context was set
        mock_sentry_sdk.set_context.assert_called_once()
        context_data = mock_sentry_sdk.set_context.call_args[0][1]
        assert context_data["monitor_id"] == "mon123"
        assert context_data["company"] == "Tesla"
        assert context_data["industry"] == "Automotive"

    @patch("consultantos.observability.sentry_integration.sentry_sdk")
    def test_set_agent_context(self, mock_sentry_sdk):
        """Test setting agent context"""
        SentryIntegration.set_agent_context(
            agent_name="ResearchAgent",
            data_sources=["tavily", "pytrends"],
            timeout=60
        )

        # Verify tag was set
        mock_sentry_sdk.set_tag.assert_called_once_with("agent_name", "ResearchAgent")

        # Verify context was set
        mock_sentry_sdk.set_context.assert_called_once()
        context_data = mock_sentry_sdk.set_context.call_args[0][1]
        assert context_data["agent_name"] == "ResearchAgent"
        assert context_data["data_sources"] == ["tavily", "pytrends"]
        assert context_data["timeout"] == 60

    @patch("consultantos.observability.sentry_integration.sentry_sdk")
    def test_start_transaction(self, mock_sentry_sdk):
        """Test starting performance transaction"""
        mock_transaction = Mock()
        mock_sentry_sdk.start_transaction.return_value = mock_transaction

        transaction = SentryIntegration.start_transaction(
            name="test_operation",
            op="custom.operation"
        )

        assert transaction == mock_transaction
        mock_sentry_sdk.start_transaction.assert_called_once_with(
            name="test_operation",
            op="custom.operation"
        )

    @patch("consultantos.observability.sentry_integration.sentry_sdk")
    def test_add_breadcrumb(self, mock_sentry_sdk):
        """Test adding breadcrumb"""
        SentryIntegration.add_breadcrumb(
            message="Test breadcrumb",
            category="test",
            level="info",
            data={"key": "value"}
        )

        mock_sentry_sdk.add_breadcrumb.assert_called_once_with(
            message="Test breadcrumb",
            category="test",
            level="info",
            data={"key": "value"}
        )

    @patch("consultantos.observability.sentry_integration.sentry_sdk")
    def test_capture_exception(self, mock_sentry_sdk):
        """Test capturing exception"""
        mock_sentry_sdk.capture_exception.return_value = "event123"

        error = ValueError("Test error")
        event_id = SentryIntegration.capture_exception(
            error,
            tag_custom="value"
        )

        assert event_id == "event123"
        mock_sentry_sdk.capture_exception.assert_called_once_with(error)

    @patch("consultantos.observability.sentry_integration.sentry_sdk")
    def test_capture_message(self, mock_sentry_sdk):
        """Test capturing message"""
        mock_sentry_sdk.capture_message.return_value = "msg123"

        event_id = SentryIntegration.capture_message(
            "Test message",
            level="warning"
        )

        assert event_id == "msg123"
        mock_sentry_sdk.capture_message.assert_called_once_with(
            "Test message",
            level="warning"
        )


class TestSetupSentry:
    """Test setup_sentry convenience function"""

    @patch("consultantos.observability.sentry_integration.SentryIntegration")
    def test_setup_with_dsn(self, mock_integration_class):
        """Test setup with DSN"""
        mock_instance = Mock()
        mock_instance._initialized = True
        mock_integration_class.return_value = mock_instance

        result = setup_sentry(
            dsn="https://test@sentry.io/12345",
            environment="staging",
            traces_sample_rate=0.3
        )

        assert result == mock_instance
        mock_integration_class.assert_called_once()
        mock_instance.initialize.assert_called_once()

    @patch("consultantos.observability.sentry_integration.SentryIntegration")
    def test_setup_without_dsn(self, mock_integration_class):
        """Test setup without DSN (returns None)"""
        mock_instance = Mock()
        mock_instance._initialized = False
        mock_integration_class.return_value = mock_instance

        result = setup_sentry(dsn=None)

        assert result is None

    def test_setup_sample_rate_production(self, monkeypatch):
        """Test sample rate defaults for production"""
        monkeypatch.setenv("SENTRY_ENVIRONMENT", "production")

        with patch("consultantos.observability.sentry_integration.SentryIntegration") as mock_class:
            mock_instance = Mock()
            mock_instance._initialized = True
            mock_class.return_value = mock_instance

            setup_sentry(dsn="https://test@sentry.io/12345")

            # Verify sample rate for production (default 0.1)
            call_args = mock_class.call_args
            assert call_args.kwargs["traces_sample_rate"] == 0.1

    def test_setup_sample_rate_development(self, monkeypatch):
        """Test sample rate defaults for development"""
        monkeypatch.setenv("SENTRY_ENVIRONMENT", "development")

        with patch("consultantos.observability.sentry_integration.SentryIntegration") as mock_class:
            mock_instance = Mock()
            mock_instance._initialized = True
            mock_class.return_value = mock_instance

            setup_sentry(dsn="https://test@sentry.io/12345")

            # Verify sample rate for development (default 1.0)
            call_args = mock_class.call_args
            assert call_args.kwargs["traces_sample_rate"] == 1.0


class TestPIIPatterns:
    """Test PII regex patterns"""

    def test_email_pattern(self):
        """Test email regex pattern"""
        pattern = PII_PATTERNS["email"]

        assert pattern.search("user@example.com")
        assert pattern.search("first.last@company.co.uk")
        assert pattern.search("email: user123@test-domain.com")
        assert not pattern.search("not-an-email")

    def test_api_key_pattern(self):
        """Test API key regex pattern"""
        pattern = PII_PATTERNS["api_key"]

        assert pattern.search('api_key = "sk_test_123"')
        assert pattern.search("token: abc123def")
        assert pattern.search('secret="my_secret_key"')
        assert not pattern.search("public_field: value")

    def test_credit_card_pattern(self):
        """Test credit card regex pattern"""
        pattern = PII_PATTERNS["credit_card"]

        assert pattern.search("4111 1111 1111 1111")
        assert pattern.search("4111-1111-1111-1111")
        assert pattern.search("4111111111111111")
        assert not pattern.search("123 456 789")
