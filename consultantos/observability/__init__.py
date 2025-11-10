"""
Observability and monitoring module for ConsultantOS.

Provides Prometheus metrics, Sentry error tracking, tracing, and alerting capabilities.
"""

from consultantos.observability.metrics import (
    PrometheusMetrics,
    metrics,
    AgentExecutionTimer,
    DataSourceRequestTimer,
    TimedMetric,
    REGISTRY,
)
from consultantos.observability.sentry_integration import (
    SentryIntegration,
    setup_sentry,
)

__all__ = [
    "PrometheusMetrics",
    "metrics",
    "AgentExecutionTimer",
    "DataSourceRequestTimer",
    "TimedMetric",
    "REGISTRY",
    "SentryIntegration",
    "setup_sentry",
]
