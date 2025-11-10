"""
Prometheus metrics and observability module for ConsultantOS.

Provides centralized metrics collection for:
- API performance (latency, error rates)
- Agent execution (timing, success rates)
- Monitoring system (check frequency, alert quality)
- Data source reliability
- Cache performance
"""

import time
import threading
from typing import Dict, Optional, Callable, Any
from datetime import datetime
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    Summary,
    CollectorRegistry,
    generate_latest,
)

# Default Prometheus registry
REGISTRY = CollectorRegistry()


class PrometheusMetrics:
    """Singleton metrics manager for ConsultantOS observability."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """Ensure singleton pattern."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize Prometheus metrics (only once)."""
        if self._initialized:
            return

        self._initialized = True

        # ========== API Metrics ==========
        # Request count by endpoint and method
        self.api_requests_total = Counter(
            name="consultantos_api_requests_total",
            documentation="Total API requests",
            labelnames=["method", "endpoint", "status"],
            registry=REGISTRY,
        )

        # Request latency in seconds
        self.api_request_duration_seconds = Histogram(
            name="consultantos_api_request_duration_seconds",
            documentation="API request latency in seconds",
            labelnames=["method", "endpoint"],
            buckets=(
                0.001,
                0.005,
                0.01,
                0.025,
                0.05,
                0.1,
                0.25,
                0.5,
                1.0,
                2.5,
                5.0,
                10.0,
            ),
            registry=REGISTRY,
        )

        # API request size
        self.api_request_size_bytes = Summary(
            name="consultantos_api_request_size_bytes",
            documentation="API request size in bytes",
            labelnames=["method", "endpoint"],
            registry=REGISTRY,
        )

        # API response size
        self.api_response_size_bytes = Summary(
            name="consultantos_api_response_size_bytes",
            documentation="API response size in bytes",
            labelnames=["method", "endpoint"],
            registry=REGISTRY,
        )

        # ========== Agent Metrics ==========
        # Agent execution time
        self.agent_execution_duration_seconds = Histogram(
            name="consultantos_agent_execution_duration_seconds",
            documentation="Agent execution time in seconds",
            labelnames=["agent_name", "status"],
            buckets=(0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0),
            registry=REGISTRY,
        )

        # Agent execution count
        self.agent_executions_total = Counter(
            name="consultantos_agent_executions_total",
            documentation="Total agent executions",
            labelnames=["agent_name", "status"],
            registry=REGISTRY,
        )

        # Agent success rate
        self.agent_success_rate = Gauge(
            name="consultantos_agent_success_rate",
            documentation="Agent success rate (0-1)",
            labelnames=["agent_name"],
            registry=REGISTRY,
        )

        # ========== Monitoring System Metrics ==========
        # Monitor check count
        self.monitor_checks_total = Counter(
            name="consultantos_monitor_checks_total",
            documentation="Total monitoring checks executed",
            labelnames=["monitor_id", "status"],
            registry=REGISTRY,
        )

        # Monitor check duration
        self.monitor_check_duration_seconds = Histogram(
            name="consultantos_monitor_check_duration_seconds",
            documentation="Monitoring check duration in seconds",
            labelnames=["monitor_id"],
            buckets=(1.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0, 600.0),
            registry=REGISTRY,
        )

        # Alert generation count
        self.alerts_generated_total = Counter(
            name="consultantos_alerts_generated_total",
            documentation="Total alerts generated",
            labelnames=["monitor_id", "alert_type", "severity"],
            registry=REGISTRY,
        )

        # Alert quality score
        self.alert_quality_score = Gauge(
            name="consultantos_alert_quality_score",
            documentation="Alert quality score based on user feedback (0-1)",
            labelnames=["monitor_id"],
            registry=REGISTRY,
        )

        # Change detection accuracy
        self.change_detection_accuracy = Gauge(
            name="consultantos_change_detection_accuracy",
            documentation="Change detection accuracy (0-1)",
            labelnames=["monitor_id"],
            registry=REGISTRY,
        )

        # ========== Cache Metrics ==========
        # Cache hits and misses
        self.cache_hits_total = Counter(
            name="consultantos_cache_hits_total",
            documentation="Total cache hits",
            labelnames=["cache_type"],
            registry=REGISTRY,
        )

        self.cache_misses_total = Counter(
            name="consultantos_cache_misses_total",
            documentation="Total cache misses",
            labelnames=["cache_type"],
            registry=REGISTRY,
        )

        # Cache hit rate
        self.cache_hit_rate = Gauge(
            name="consultantos_cache_hit_rate",
            documentation="Cache hit rate (0-1)",
            labelnames=["cache_type"],
            registry=REGISTRY,
        )

        # Cache size
        self.cache_size_bytes = Gauge(
            name="consultantos_cache_size_bytes",
            documentation="Cache size in bytes",
            labelnames=["cache_type"],
            registry=REGISTRY,
        )

        # ========== Data Source Metrics ==========
        # Data source requests
        self.data_source_requests_total = Counter(
            name="consultantos_data_source_requests_total",
            documentation="Total data source requests",
            labelnames=["source_name", "status"],
            registry=REGISTRY,
        )

        # Data source request duration
        self.data_source_request_duration_seconds = Histogram(
            name="consultantos_data_source_request_duration_seconds",
            documentation="Data source request duration in seconds",
            labelnames=["source_name"],
            buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0),
            registry=REGISTRY,
        )

        # Data source reliability
        self.data_source_reliability = Gauge(
            name="consultantos_data_source_reliability",
            documentation="Data source reliability score (0-1)",
            labelnames=["source_name"],
            registry=REGISTRY,
        )

        # Data source errors
        self.data_source_errors_total = Counter(
            name="consultantos_data_source_errors_total",
            documentation="Total data source errors",
            labelnames=["source_name", "error_type"],
            registry=REGISTRY,
        )

        # ========== Job Queue Metrics ==========
        # Job count by status
        self.jobs_total = Counter(
            name="consultantos_jobs_total",
            documentation="Total jobs processed",
            labelnames=["job_type", "status"],
            registry=REGISTRY,
        )

        # Job processing duration
        self.job_processing_duration_seconds = Histogram(
            name="consultantos_job_processing_duration_seconds",
            documentation="Job processing duration in seconds",
            labelnames=["job_type"],
            buckets=(1.0, 5.0, 10.0, 30.0, 60.0, 300.0),
            registry=REGISTRY,
        )

        # Queue size
        self.queue_size = Gauge(
            name="consultantos_queue_size",
            documentation="Current job queue size",
            labelnames=["queue_name"],
            registry=REGISTRY,
        )

        # ========== Error Metrics ==========
        # Errors by type
        self.errors_total = Counter(
            name="consultantos_errors_total",
            documentation="Total errors",
            labelnames=["error_type", "component"],
            registry=REGISTRY,
        )

        # ========== System Metrics ==========
        # Active requests
        self.active_requests = Gauge(
            name="consultantos_active_requests",
            documentation="Number of active requests",
            registry=REGISTRY,
        )

        # Uptime
        self.uptime_seconds = Gauge(
            name="consultantos_uptime_seconds",
            documentation="Application uptime in seconds",
            registry=REGISTRY,
        )

        self._start_time = time.time()

    # ===== API Metrics Methods =====

    def record_api_request(
        self,
        method: str,
        endpoint: str,
        status_code: int,
        duration: float,
        request_size: int = 0,
        response_size: int = 0,
    ) -> None:
        """Record API request metrics."""
        self.api_requests_total.labels(
            method=method, endpoint=endpoint, status=status_code
        ).inc()
        self.api_request_duration_seconds.labels(
            method=method, endpoint=endpoint
        ).observe(duration)
        if request_size > 0:
            self.api_request_size_bytes.labels(
                method=method, endpoint=endpoint
            ).observe(request_size)
        if response_size > 0:
            self.api_response_size_bytes.labels(
                method=method, endpoint=endpoint
            ).observe(response_size)

    # ===== Agent Metrics Methods =====

    def record_agent_execution(
        self, agent_name: str, duration: float, success: bool
    ) -> None:
        """Record agent execution metrics."""
        status = "success" if success else "failure"
        self.agent_execution_duration_seconds.labels(
            agent_name=agent_name, status=status
        ).observe(duration)
        self.agent_executions_total.labels(
            agent_name=agent_name, status=status
        ).inc()

    def set_agent_success_rate(self, agent_name: str, rate: float) -> None:
        """Set agent success rate."""
        self.agent_success_rate.labels(agent_name=agent_name).set(rate)

    # ===== Monitoring Metrics Methods =====

    def record_monitor_check(
        self, monitor_id: str, duration: float, success: bool
    ) -> None:
        """Record monitoring check metrics."""
        status = "success" if success else "failure"
        self.monitor_checks_total.labels(monitor_id=monitor_id, status=status).inc()
        self.monitor_check_duration_seconds.labels(monitor_id=monitor_id).observe(
            duration
        )

    def record_alert_generated(
        self, monitor_id: str, alert_type: str, severity: str
    ) -> None:
        """Record alert generation."""
        self.alerts_generated_total.labels(
            monitor_id=monitor_id, alert_type=alert_type, severity=severity
        ).inc()

    def set_alert_quality_score(self, monitor_id: str, score: float) -> None:
        """Set alert quality score (0-1)."""
        self.alert_quality_score.labels(monitor_id=monitor_id).set(score)

    def set_change_detection_accuracy(self, monitor_id: str, accuracy: float) -> None:
        """Set change detection accuracy (0-1)."""
        self.change_detection_accuracy.labels(monitor_id=monitor_id).set(accuracy)

    # ===== Cache Metrics Methods =====

    def record_cache_hit(self, cache_type: str) -> None:
        """Record cache hit."""
        self.cache_hits_total.labels(cache_type=cache_type).inc()

    def record_cache_miss(self, cache_type: str) -> None:
        """Record cache miss."""
        self.cache_misses_total.labels(cache_type=cache_type).inc()

    def set_cache_hit_rate(self, cache_type: str, rate: float) -> None:
        """Set cache hit rate (0-1)."""
        self.cache_hit_rate.labels(cache_type=cache_type).set(rate)

    def set_cache_size(self, cache_type: str, size_bytes: int) -> None:
        """Set cache size in bytes."""
        self.cache_size_bytes.labels(cache_type=cache_type).set(size_bytes)

    # ===== Data Source Metrics Methods =====

    def record_data_source_request(
        self, source_name: str, duration: float, success: bool
    ) -> None:
        """Record data source request metrics."""
        status = "success" if success else "failure"
        self.data_source_requests_total.labels(source_name=source_name, status=status).inc()
        self.data_source_request_duration_seconds.labels(
            source_name=source_name
        ).observe(duration)

    def set_data_source_reliability(self, source_name: str, reliability: float) -> None:
        """Set data source reliability (0-1)."""
        self.data_source_reliability.labels(source_name=source_name).set(reliability)

    def record_data_source_error(self, source_name: str, error_type: str) -> None:
        """Record data source error."""
        self.data_source_errors_total.labels(
            source_name=source_name, error_type=error_type
        ).inc()

    # ===== Job Queue Metrics Methods =====

    def record_job(self, job_type: str, success: bool) -> None:
        """Record job execution."""
        status = "success" if success else "failure"
        self.jobs_total.labels(job_type=job_type, status=status).inc()

    def record_job_duration(self, job_type: str, duration: float) -> None:
        """Record job processing duration."""
        self.job_processing_duration_seconds.labels(job_type=job_type).observe(duration)

    def set_queue_size(self, queue_name: str, size: int) -> None:
        """Set queue size."""
        self.queue_size.labels(queue_name=queue_name).set(size)

    # ===== Error Metrics Methods =====

    def record_error(self, error_type: str, component: str) -> None:
        """Record error."""
        self.errors_total.labels(error_type=error_type, component=component).inc()

    # ===== System Metrics Methods =====

    def increment_active_requests(self) -> None:
        """Increment active request count."""
        self.active_requests.inc()

    def decrement_active_requests(self) -> None:
        """Decrement active request count."""
        self.active_requests.dec()

    def update_uptime(self) -> None:
        """Update uptime metric."""
        uptime = time.time() - self._start_time
        self.uptime_seconds.set(uptime)

    # ===== Metrics Export =====

    def export_metrics(self) -> bytes:
        """Export metrics in Prometheus text format."""
        self.update_uptime()
        return generate_latest(REGISTRY)

    def get_metrics_dict(self) -> Dict[str, Any]:
        """Get metrics as dictionary for API responses."""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": time.time() - self._start_time,
        }


# Global metrics instance
metrics = PrometheusMetrics()


# ===== Context Managers for Timing =====


class TimedMetric:
    """Context manager for timing metrics."""

    def __init__(self, callback: Callable[[float], None]):
        """Initialize with callback function."""
        self.callback = callback
        self.start_time = None

    def __enter__(self):
        """Start timing."""
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """End timing and call callback."""
        duration = time.time() - self.start_time
        self.callback(duration)
        return False


class AgentExecutionTimer:
    """Context manager for agent execution timing."""

    def __init__(self, agent_name: str):
        """Initialize with agent name."""
        self.agent_name = agent_name
        self.start_time = None
        self.success = True

    def __enter__(self):
        """Start timing."""
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """End timing and record metrics."""
        duration = time.time() - self.start_time
        success = exc_type is None
        metrics.record_agent_execution(self.agent_name, duration, success)
        return False


class DataSourceRequestTimer:
    """Context manager for data source request timing."""

    def __init__(self, source_name: str):
        """Initialize with source name."""
        self.source_name = source_name
        self.start_time = None
        self.success = True

    def __enter__(self):
        """Start timing."""
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """End timing and record metrics."""
        duration = time.time() - self.start_time
        success = exc_type is None
        metrics.record_data_source_request(self.source_name, duration, success)
        if exc_type is not None:
            metrics.record_data_source_error(
                self.source_name, exc_type.__name__
            )
        return False


__all__ = [
    "PrometheusMetrics",
    "metrics",
    "TimedMetric",
    "AgentExecutionTimer",
    "DataSourceRequestTimer",
    "REGISTRY",
]
