"""
Performance metrics collection using Prometheus.
"""
import logging
import time
from functools import wraps
from typing import Optional, Callable
from contextlib import contextmanager

try:
    from prometheus_client import (
        Counter,
        Histogram,
        Gauge,
        Summary,
        Info,
        generate_latest,
        CONTENT_TYPE_LATEST
    )
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

logger = logging.getLogger(__name__)


class PerformanceMetrics:
    """
    Centralized performance metrics using Prometheus.
    """

    def __init__(self):
        """Initialize Prometheus metrics."""
        if not PROMETHEUS_AVAILABLE:
            logger.warning("Prometheus client not available, metrics disabled")
            self.enabled = False
            return

        self.enabled = True

        # Request metrics
        self.request_count = Counter(
            'consultantos_requests_total',
            'Total number of requests',
            ['endpoint', 'method', 'status']
        )

        self.request_duration = Histogram(
            'consultantos_request_duration_seconds',
            'Request duration in seconds',
            ['endpoint', 'method'],
            buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0)
        )

        # Agent execution metrics
        self.agent_duration = Histogram(
            'consultantos_agent_duration_seconds',
            'Agent execution time in seconds',
            ['agent_name'],
            buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, 120.0)
        )

        self.agent_errors = Counter(
            'consultantos_agent_errors_total',
            'Total number of agent errors',
            ['agent_name', 'error_type']
        )

        self.agent_success = Counter(
            'consultantos_agent_success_total',
            'Total number of successful agent executions',
            ['agent_name']
        )

        # Cache metrics
        self.cache_hits = Counter(
            'consultantos_cache_hits_total',
            'Total number of cache hits',
            ['cache_level']  # l1, l2, l3, semantic
        )

        self.cache_misses = Counter(
            'consultantos_cache_misses_total',
            'Total number of cache misses'
        )

        self.cache_errors = Counter(
            'consultantos_cache_errors_total',
            'Total number of cache errors',
            ['operation']  # get, set, delete
        )

        # Database metrics
        self.db_operations = Counter(
            'consultantos_db_operations_total',
            'Total number of database operations',
            ['operation', 'collection']
        )

        self.db_duration = Histogram(
            'consultantos_db_duration_seconds',
            'Database operation duration in seconds',
            ['operation', 'collection'],
            buckets=(0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0)
        )

        self.db_batch_size = Histogram(
            'consultantos_db_batch_size',
            'Database batch operation size',
            ['operation'],
            buckets=(1, 5, 10, 50, 100, 250, 500)
        )

        # LLM metrics
        self.llm_calls = Counter(
            'consultantos_llm_calls_total',
            'Total number of LLM API calls',
            ['model', 'agent']
        )

        self.llm_duration = Histogram(
            'consultantos_llm_duration_seconds',
            'LLM API call duration in seconds',
            ['model', 'agent'],
            buckets=(0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 30.0, 60.0)
        )

        self.llm_tokens = Counter(
            'consultantos_llm_tokens_total',
            'Total number of LLM tokens used',
            ['model', 'agent', 'token_type']  # input, output
        )

        # System metrics
        self.active_requests = Gauge(
            'consultantos_active_requests',
            'Number of active requests'
        )

        self.orchestration_phases = Counter(
            'consultantos_orchestration_phases_total',
            'Orchestration phases completed',
            ['phase', 'status']  # success, partial_success, error
        )

        # Custom business metrics
        self.analyses_generated = Counter(
            'consultantos_analyses_generated_total',
            'Total number of analyses generated',
            ['frameworks']
        )

        self.reports_generated = Counter(
            'consultantos_reports_generated_total',
            'Total number of reports generated',
            ['format']  # pdf, json, excel, word
        )

        logger.info("Prometheus metrics initialized")

    @contextmanager
    def track_request(self, endpoint: str, method: str):
        """
        Context manager to track request duration and count.

        Args:
            endpoint: API endpoint name
            method: HTTP method

        Example:
            with metrics.track_request('/analyze', 'POST'):
                # ... handle request
                pass
        """
        if not self.enabled:
            yield
            return

        start_time = time.time()
        self.active_requests.inc()
        status = "success"

        try:
            yield
        except Exception as e:
            status = "error"
            raise
        finally:
            duration = time.time() - start_time
            self.active_requests.dec()
            self.request_duration.labels(endpoint=endpoint, method=method).observe(duration)
            self.request_count.labels(endpoint=endpoint, method=method, status=status).inc()

    @contextmanager
    def track_agent(self, agent_name: str):
        """
        Context manager to track agent execution.

        Args:
            agent_name: Name of the agent

        Example:
            with metrics.track_agent('research_agent'):
                result = await agent.execute()
        """
        if not self.enabled:
            yield
            return

        start_time = time.time()

        try:
            yield
            # Success
            duration = time.time() - start_time
            self.agent_duration.labels(agent_name=agent_name).observe(duration)
            self.agent_success.labels(agent_name=agent_name).inc()

        except Exception as e:
            # Error
            duration = time.time() - start_time
            self.agent_duration.labels(agent_name=agent_name).observe(duration)
            error_type = type(e).__name__
            self.agent_errors.labels(agent_name=agent_name, error_type=error_type).inc()
            raise

    @contextmanager
    def track_db_operation(self, operation: str, collection: str):
        """
        Context manager to track database operations.

        Args:
            operation: Operation type (get, set, query, batch_get, batch_write)
            collection: Collection name
        """
        if not self.enabled:
            yield
            return

        start_time = time.time()

        try:
            yield
            # Success
            duration = time.time() - start_time
            self.db_operations.labels(operation=operation, collection=collection).inc()
            self.db_duration.labels(operation=operation, collection=collection).observe(duration)

        except Exception:
            # Still track duration on error
            duration = time.time() - start_time
            self.db_duration.labels(operation=operation, collection=collection).observe(duration)
            raise

    def record_cache_hit(self, cache_level: str):
        """
        Record a cache hit.

        Args:
            cache_level: Cache level (l1, l2, l3, semantic)
        """
        if self.enabled:
            self.cache_hits.labels(cache_level=cache_level).inc()

    def record_cache_miss(self):
        """Record a cache miss."""
        if self.enabled:
            self.cache_misses.inc()

    def record_cache_error(self, operation: str):
        """
        Record a cache error.

        Args:
            operation: Operation that failed (get, set, delete)
        """
        if self.enabled:
            self.cache_errors.labels(operation=operation).inc()

    def record_llm_call(
        self,
        model: str,
        agent: str,
        duration: float,
        input_tokens: int = 0,
        output_tokens: int = 0
    ):
        """
        Record LLM API call metrics.

        Args:
            model: Model name
            agent: Agent name
            duration: Call duration in seconds
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
        """
        if not self.enabled:
            return

        self.llm_calls.labels(model=model, agent=agent).inc()
        self.llm_duration.labels(model=model, agent=agent).observe(duration)

        if input_tokens > 0:
            self.llm_tokens.labels(
                model=model,
                agent=agent,
                token_type='input'
            ).inc(input_tokens)

        if output_tokens > 0:
            self.llm_tokens.labels(
                model=model,
                agent=agent,
                token_type='output'
            ).inc(output_tokens)

    def record_batch_operation(self, operation: str, batch_size: int):
        """
        Record batch operation size.

        Args:
            operation: Operation type
            batch_size: Number of items in batch
        """
        if self.enabled:
            self.db_batch_size.labels(operation=operation).observe(batch_size)

    def record_orchestration_phase(self, phase: str, status: str):
        """
        Record orchestration phase completion.

        Args:
            phase: Phase name (phase1, phase2, phase3)
            status: Phase status (success, partial_success, error)
        """
        if self.enabled:
            self.orchestration_phases.labels(phase=phase, status=status).inc()

    def record_analysis_generated(self, frameworks: str):
        """
        Record analysis generation.

        Args:
            frameworks: Comma-separated framework names
        """
        if self.enabled:
            self.analyses_generated.labels(frameworks=frameworks).inc()

    def record_report_generated(self, format: str):
        """
        Record report generation.

        Args:
            format: Report format (pdf, json, excel, word)
        """
        if self.enabled:
            self.reports_generated.labels(format=format).inc()

    def get_metrics(self) -> bytes:
        """
        Get metrics in Prometheus format.

        Returns:
            Metrics data in Prometheus text format
        """
        if not self.enabled:
            return b""

        return generate_latest()

    def get_content_type(self) -> str:
        """Get content type for metrics endpoint."""
        return CONTENT_TYPE_LATEST


# Global metrics instance
metrics = PerformanceMetrics()


def track_performance(metric_name: str):
    """
    Decorator to track function performance.

    Args:
        metric_name: Name for the metric

    Example:
        @track_performance('my_function')
        async def my_function():
            pass
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            with metrics.track_agent(metric_name):
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                return func(*args, **kwargs)
        return wrapper
    return decorator
