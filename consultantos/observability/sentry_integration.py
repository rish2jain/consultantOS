"""Sentry integration for comprehensive error tracking and performance monitoring.

This module provides:
- Error capture with rich context (user, monitor, company, agent)
- Performance transaction tracking for API endpoints and agents
- Custom error fingerprinting for intelligent grouping
- Breadcrumb configuration for debugging trails
- PII sanitization to protect user privacy
- Environment-aware configuration (dev, staging, prod)
"""

import logging
import os
import re
from typing import Any, Dict, Optional

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

logger = logging.getLogger(__name__)

# PII patterns to sanitize
PII_PATTERNS = {
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
    "api_key": re.compile(r"\b(api[_-]?key|token|secret)[\"']?\s*[:=]\s*[\"']?([a-zA-Z0-9_-]+)[\"']?", re.IGNORECASE),
    "credit_card": re.compile(r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b"),
}


class SentryIntegration:
    """Central Sentry integration for ConsultantOS.

    Provides methods for:
    - Initialization with environment detection
    - Context enrichment for errors and transactions
    - Custom error fingerprinting
    - PII sanitization
    - Performance transaction management
    """

    def __init__(
        self,
        dsn: Optional[str] = None,
        environment: Optional[str] = None,
        traces_sample_rate: float = 0.1,
        release: Optional[str] = None,
        enable_profiling: bool = False,
        profiles_sample_rate: float = 0.1,
    ):
        """Initialize Sentry integration.

        Args:
            dsn: Sentry DSN for the project
            environment: Deployment environment (dev, staging, prod)
            traces_sample_rate: Sampling rate for performance transactions (0.0-1.0)
            release: Release identifier (Git SHA recommended)
            enable_profiling: Whether to enable profiling
            profiles_sample_rate: Sampling rate for profiling (0.0-1.0)
        """
        self.dsn = dsn or os.getenv("SENTRY_DSN")
        self.environment = environment or os.getenv("SENTRY_ENVIRONMENT", "development")
        self.traces_sample_rate = traces_sample_rate
        self.release = release or os.getenv("SENTRY_RELEASE", self._get_git_sha())
        self.enable_profiling = enable_profiling
        self.profiles_sample_rate = profiles_sample_rate

        # Track if initialized
        self._initialized = False

    @staticmethod
    def _get_git_sha() -> Optional[str]:
        """Get current Git SHA for release tracking."""
        try:
            import subprocess
            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None

    def initialize(self) -> None:
        """Initialize Sentry SDK with configured settings."""
        if self._initialized:
            logger.warning("Sentry already initialized")
            return

        if not self.dsn:
            logger.warning("SENTRY_DSN not configured, skipping Sentry initialization")
            return

        # Configure logging integration
        logging_integration = LoggingIntegration(
            level=logging.INFO,  # Capture info and above as breadcrumbs
            event_level=logging.ERROR  # Send errors as events
        )

        # Configure FastAPI integration
        fastapi_integration = FastApiIntegration(
            transaction_style="url",  # Group by URL pattern
            failed_request_status_codes=[500, 599],  # Only track server errors
        )

        integrations = [logging_integration, fastapi_integration]

        # Initialize Sentry
        sentry_sdk.init(
            dsn=self.dsn,
            environment=self.environment,
            release=self.release,
            traces_sample_rate=self.traces_sample_rate,
            profiles_sample_rate=self.profiles_sample_rate if self.enable_profiling else 0.0,
            integrations=integrations,
            before_send=self._before_send,
            before_breadcrumb=self._before_breadcrumb,
            # Performance monitoring settings
            enable_tracing=True,
            # Error grouping settings
            send_default_pii=False,  # Don't send PII by default
            attach_stacktrace=True,
            # Max value sizes
            max_value_length=2048,
            max_request_body_size="medium",
        )

        self._initialized = True
        logger.info(
            f"Sentry initialized: environment={self.environment}, "
            f"release={self.release}, traces_sample_rate={self.traces_sample_rate}"
        )

    def _before_send(self, event: Dict[str, Any], hint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process event before sending to Sentry (sanitize PII, add context).

        Args:
            event: Sentry event dictionary
            hint: Additional context about the event

        Returns:
            Modified event dictionary or None to drop the event
        """
        # Sanitize PII from event
        event = self._sanitize_pii(event)

        # Add custom fingerprinting
        event = self._add_custom_fingerprint(event, hint)

        # Add release context
        if self.release:
            event.setdefault("tags", {})["git_sha"] = self.release

        return event

    def _before_breadcrumb(self, crumb: Dict[str, Any], hint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process breadcrumb before adding to event trail.

        Args:
            crumb: Breadcrumb dictionary
            hint: Additional context

        Returns:
            Modified breadcrumb or None to drop it
        """
        # Sanitize PII from breadcrumbs
        if "message" in crumb:
            crumb["message"] = self._sanitize_string(crumb["message"])

        if "data" in crumb:
            crumb["data"] = self._sanitize_dict(crumb["data"])

        return crumb

    def _sanitize_pii(self, data: Any) -> Any:
        """Recursively sanitize PII from data structures.

        Args:
            data: Data to sanitize (dict, list, string, etc.)

        Returns:
            Sanitized data
        """
        if isinstance(data, dict):
            return self._sanitize_dict(data)
        elif isinstance(data, list):
            return [self._sanitize_pii(item) for item in data]
        elif isinstance(data, str):
            return self._sanitize_string(data)
        return data

    def _sanitize_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize PII from dictionary.

        Args:
            data: Dictionary to sanitize

        Returns:
            Sanitized dictionary
        """
        sanitized = {}
        for key, value in data.items():
            # Redact known sensitive keys
            if key.lower() in {"email", "password", "api_key", "token", "secret", "credit_card"}:
                sanitized[key] = "[REDACTED]"
            else:
                sanitized[key] = self._sanitize_pii(value)
        return sanitized

    def _sanitize_string(self, text: str) -> str:
        """Sanitize PII from string using regex patterns.

        Args:
            text: String to sanitize

        Returns:
            Sanitized string
        """
        for pattern_name, pattern in PII_PATTERNS.items():
            text = pattern.sub(f"[{pattern_name.upper()}_REDACTED]", text)
        return text

    def _add_custom_fingerprint(self, event: Dict[str, Any], hint: Dict[str, Any]) -> Dict[str, Any]:
        """Add custom fingerprint for intelligent error grouping.

        Groups errors by:
        - Error type + agent name (for agent errors)
        - Error type + endpoint (for API errors)
        - Error type + monitor ID (for monitoring errors)

        Args:
            event: Sentry event
            hint: Event hint with exception info

        Returns:
            Event with custom fingerprint
        """
        fingerprint = []

        # Get exception info
        if "exception" in hint and hint["exception"]:
            exc = hint["exception"]
            error_type = type(exc).__name__
            fingerprint.append(error_type)

        # Add context-specific grouping
        tags = event.get("tags", {})

        # Group by agent name
        if "agent_name" in tags:
            fingerprint.append(f"agent:{tags['agent_name']}")
        # Group by endpoint
        elif "endpoint" in tags:
            fingerprint.append(f"endpoint:{tags['endpoint']}")
        # Group by monitor ID
        elif "monitor_id" in tags:
            fingerprint.append(f"monitor:{tags['monitor_id']}")

        if fingerprint:
            event["fingerprint"] = fingerprint

        return event

    @staticmethod
    def set_user_context(user_id: str, tier: Optional[str] = None, **kwargs) -> None:
        """Set user context for error tracking.

        Args:
            user_id: User identifier (no email or PII)
            tier: User subscription tier
            **kwargs: Additional user metadata (sanitized)
        """
        user_data = {
            "id": user_id,
        }
        if tier:
            user_data["tier"] = tier

        # Add sanitized extra data
        for key, value in kwargs.items():
            if key not in {"email", "password"}:
                user_data[key] = value

        sentry_sdk.set_user(user_data)

    @staticmethod
    def set_monitor_context(monitor_id: str, company: str, industry: Optional[str] = None) -> None:
        """Set monitor context for error tracking.

        Args:
            monitor_id: Intelligence monitor ID
            company: Company being monitored
            industry: Industry sector
        """
        sentry_sdk.set_tag("monitor_id", monitor_id)
        sentry_sdk.set_tag("company", company)
        if industry:
            sentry_sdk.set_tag("industry", industry)

        sentry_sdk.set_context("monitor", {
            "monitor_id": monitor_id,
            "company": company,
            "industry": industry,
        })

    @staticmethod
    def set_agent_context(agent_name: str, data_sources: Optional[list] = None, **kwargs) -> None:
        """Set agent context for error tracking.

        Args:
            agent_name: Name of the agent (ResearchAgent, FinancialAgent, etc.)
            data_sources: List of data sources used by agent
            **kwargs: Additional agent metadata
        """
        sentry_sdk.set_tag("agent_name", agent_name)

        context = {
            "agent_name": agent_name,
        }
        if data_sources:
            context["data_sources"] = data_sources
        context.update(kwargs)

        sentry_sdk.set_context("agent", context)

    @staticmethod
    def start_transaction(name: str, op: str = "function", **kwargs) -> sentry_sdk.tracing.Transaction:
        """Start a performance transaction.

        Args:
            name: Transaction name (e.g., "FinancialAgent.execute")
            op: Operation type (function, http.request, db.query, etc.)
            **kwargs: Additional transaction data

        Returns:
            Sentry transaction object
        """
        transaction = sentry_sdk.start_transaction(
            name=name,
            op=op,
            **kwargs
        )
        return transaction

    @staticmethod
    def add_breadcrumb(message: str, category: str = "default", level: str = "info", data: Optional[Dict] = None) -> None:
        """Add breadcrumb for debugging trail.

        Args:
            message: Breadcrumb message
            category: Breadcrumb category (agent, monitor, api, etc.)
            level: Severity level (debug, info, warning, error)
            data: Additional structured data
        """
        sentry_sdk.add_breadcrumb(
            message=message,
            category=category,
            level=level,
            data=data or {}
        )

    @staticmethod
    def capture_exception(error: Exception, **kwargs) -> str:
        """Capture exception with additional context.

        Args:
            error: Exception to capture
            **kwargs: Additional context (tags, extra data)

        Returns:
            Sentry event ID
        """
        # Add any extra tags
        for key, value in kwargs.items():
            if key.startswith("tag_"):
                sentry_sdk.set_tag(key[4:], value)
            elif key.startswith("extra_"):
                sentry_sdk.set_extra(key[6:], value)

        event_id = sentry_sdk.capture_exception(error)
        return event_id

    @staticmethod
    def capture_message(message: str, level: str = "info", **kwargs) -> str:
        """Capture message event.

        Args:
            message: Message to capture
            level: Severity level
            **kwargs: Additional context

        Returns:
            Sentry event ID
        """
        return sentry_sdk.capture_message(message, level=level)


def setup_sentry(
    dsn: Optional[str] = None,
    environment: Optional[str] = None,
    traces_sample_rate: Optional[float] = None,
    release: Optional[str] = None,
) -> Optional[SentryIntegration]:
    """Convenience function to set up Sentry integration.

    Args:
        dsn: Sentry DSN
        environment: Deployment environment
        traces_sample_rate: Performance sampling rate
        release: Release identifier

    Returns:
        Initialized SentryIntegration instance or None if DSN not configured
    """
    # Get sample rate from environment with defaults by environment
    if traces_sample_rate is None:
        env = environment or os.getenv("SENTRY_ENVIRONMENT", "development")
        if env == "production":
            traces_sample_rate = float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1"))
        elif env == "staging":
            traces_sample_rate = float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.3"))
        else:  # development
            traces_sample_rate = float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "1.0"))

    integration = SentryIntegration(
        dsn=dsn,
        environment=environment,
        traces_sample_rate=traces_sample_rate,
        release=release,
    )

    integration.initialize()

    if integration._initialized:
        return integration
    return None
