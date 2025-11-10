"""
Monitoring and observability for ConsultantOS
"""
import json
import logging
import time
import functools
from typing import Dict, Any, Optional
from datetime import datetime
from contextlib import contextmanager
from contextvars import ContextVar

try:
    from google.cloud import logging as cloud_logging
    CLOUD_LOGGING_AVAILABLE = True
except ImportError:
    CLOUD_LOGGING_AVAILABLE = False
    cloud_logging = None

import structlog

# Request ID ContextVar (imported from main.py)
request_id_var: ContextVar[str] = ContextVar('request_id', default='')


class RequestIdFilter(logging.Filter):
    """Add request_id to all log records"""
    
    def filter(self, record):
        record.request_id = request_id_var.get('')
        return True


def get_logger(name: str) -> logging.Logger:
    """Get logger with request ID filter"""
    logger = logging.getLogger(name)
    if not any(isinstance(f, RequestIdFilter) for f in logger.filters):
        logger.addFilter(RequestIdFilter())
    return logger


# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()  # JSON for Cloud Logging
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# Initialize Cloud Logging if available
if CLOUD_LOGGING_AVAILABLE:
    try:
        logging_client = cloud_logging.Client()
        logging_client.setup_logging()
    except Exception as e:
        print(f"Warning: Cloud Logging setup failed: {e}")

logger = structlog.get_logger(__name__)


class MetricsCollector:
    """Collects and tracks application metrics"""
    
    def __init__(self):
        self.metrics: Dict[str, Any] = {
            "requests_total": 0,
            "requests_success": 0,
            "requests_failed": 0,
            "agent_executions": {},
            "cache_hits": 0,
            "cache_misses": 0,
            "execution_times": {},  # Dict[str, List[float]] - per-operation execution times
            "errors_by_type": {},
            "api_calls": {},  # Track external API calls
            "circuit_breaker_states": {},  # Track circuit breaker states
            "job_queue": {
                "pending": 0,
                "processing": 0,
                "completed": 0,
                "failed": 0
            },
            "user_activity": {},  # Track user activity
            "cost_tracking": {}  # Track API costs
        }
    
    def increment(self, metric: str, value: int = 1, labels: Optional[Dict[str, str]] = None):
        """Increment a metric"""
        if labels:
            key = f"{metric}_{json.dumps(labels, sort_keys=True)}"
        else:
            key = metric
        
        if key not in self.metrics:
            self.metrics[key] = 0
        self.metrics[key] += value
    
    def record_execution_time(self, duration: float, operation: str):
        """Record execution time for an operation"""
        if operation not in self.metrics["execution_times"]:
            self.metrics["execution_times"][operation] = []
        self.metrics["execution_times"][operation].append(duration)
    
    def record_error(self, error_type: str, error_message: str):
        """Record an error"""
        if error_type not in self.metrics["errors_by_type"]:
            self.metrics["errors_by_type"][error_type] = []
        self.metrics["errors_by_type"][error_type].append({
            "message": error_message,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics snapshot"""
        return {
            **self.metrics,
            "timestamp": datetime.now().isoformat()
        }
    
    def track_api_call(self, service: str, success: bool, duration: Optional[float] = None):
        """Track external API call"""
        if service not in self.metrics["api_calls"]:
            self.metrics["api_calls"][service] = {
                "total": 0,
                "success": 0,
                "failed": 0,
                "total_duration": 0.0
            }
        
        self.metrics["api_calls"][service]["total"] += 1
        if success:
            self.metrics["api_calls"][service]["success"] += 1
        else:
            self.metrics["api_calls"][service]["failed"] += 1
        
        if duration:
            self.metrics["api_calls"][service]["total_duration"] += duration
    
    def track_circuit_breaker_state(self, service: str, state: str):
        """Track circuit breaker state"""
        self.metrics["circuit_breaker_states"][service] = {
            "state": state,
            "timestamp": datetime.now().isoformat()
        }
    
    def track_job_status(self, status: str, increment: int = 1):
        """Track job queue status"""
        if status in self.metrics["job_queue"]:
            self.metrics["job_queue"][status] += increment
    
    def track_user_activity(self, user_id: str, action: str):
        """Track user activity"""
        if user_id not in self.metrics["user_activity"]:
            self.metrics["user_activity"][user_id] = {
                "actions": [],
                "last_activity": None
            }
        
        self.metrics["user_activity"][user_id]["actions"].append({
            "action": action,
            "timestamp": datetime.now().isoformat()
        })
        self.metrics["user_activity"][user_id]["last_activity"] = datetime.now().isoformat()
    
    def track_cost(self, service: str, cost: float, unit: str = "USD"):
        """Track API costs"""
        if service not in self.metrics["cost_tracking"]:
            self.metrics["cost_tracking"][service] = {
                "total_cost": 0.0,
                "unit": unit,
                "calls": 0
            }
        
        self.metrics["cost_tracking"][service]["total_cost"] += cost
        self.metrics["cost_tracking"][service]["calls"] += 1
    
    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary"""
        total_requests = self.metrics["requests_total"]
        success_rate = (
            self.metrics["requests_success"] / total_requests * 100
            if total_requests > 0 else 0
        )
        
        cache_hit_rate = (
            self.metrics["cache_hits"] / (self.metrics["cache_hits"] + self.metrics["cache_misses"]) * 100
            if (self.metrics["cache_hits"] + self.metrics["cache_misses"]) > 0 else 0
        )
        
        avg_execution_times = {}
        for operation, times in self.metrics["execution_times"].items():
            if isinstance(times, list) and times:
                avg_execution_times[operation] = sum(times) / len(times)
        
        # Calculate API success rates
        api_success_rates = {}
        for service, stats in self.metrics["api_calls"].items():
            if stats["total"] > 0:
                api_success_rates[service] = round(
                    stats["success"] / stats["total"] * 100, 2
                )
        
        # Calculate total costs
        total_cost = sum(
            cost["total_cost"] for cost in self.metrics["cost_tracking"].values()
        )
        
        return {
            "total_requests": total_requests,
            "success_rate": round(success_rate, 2),
            "cache_hit_rate": round(cache_hit_rate, 2),
            "average_execution_times": avg_execution_times,
            "error_count_by_type": {
                k: len(v) if isinstance(v, list) else v
                for k, v in self.metrics["errors_by_type"].items()
            },
            "api_success_rates": api_success_rates,
            "circuit_breaker_states": {
                k: v["state"] for k, v in self.metrics["circuit_breaker_states"].items()
            },
            "job_queue_status": self.metrics["job_queue"],
            "total_api_cost": round(total_cost, 4),
            "active_users": len([
                uid for uid, activity in self.metrics["user_activity"].items()
                if activity.get("last_activity")
            ])
        }
    
    def get_prometheus_metrics(self) -> str:
        """
        Export metrics in Prometheus format
        
        Returns metrics as Prometheus exposition format:
        # TYPE metric_name metric_type
        # HELP metric_name description
        metric_name{label="value"} metric_value
        """
        lines = []
        
        # Request metrics
        lines.append("# TYPE consultantos_requests_total counter")
        lines.append("# HELP consultantos_requests_total Total number of requests")
        lines.append(f"consultantos_requests_total {self.metrics['requests_total']}")
        
        lines.append("# TYPE consultantos_requests_success counter")
        lines.append("# HELP consultantos_requests_success Number of successful requests")
        lines.append(f"consultantos_requests_success {self.metrics['requests_success']}")
        
        lines.append("# TYPE consultantos_requests_failed counter")
        lines.append("# HELP consultantos_requests_failed Number of failed requests")
        lines.append(f"consultantos_requests_failed {self.metrics['requests_failed']}")
        
        # Cache metrics
        lines.append("# TYPE consultantos_cache_hits counter")
        lines.append("# HELP consultantos_cache_hits Number of cache hits")
        lines.append(f"consultantos_cache_hits {self.metrics['cache_hits']}")
        
        lines.append("# TYPE consultantos_cache_misses counter")
        lines.append("# HELP consultantos_cache_misses Number of cache misses")
        lines.append(f"consultantos_cache_misses {self.metrics['cache_misses']}")
        
        # Execution time histograms
        lines.append("# TYPE consultantos_execution_duration_seconds histogram")
        lines.append("# HELP consultantos_execution_duration_seconds Execution duration in seconds")
        for operation, times in self.metrics["execution_times"].items():
            if isinstance(times, list) and times:
                avg_time = sum(times) / len(times)
                lines.append(f'consultantos_execution_duration_seconds{{operation="{operation}"}} {avg_time}')
        
        # Error counters by type
        lines.append("# TYPE consultantos_errors_total counter")
        lines.append("# HELP consultantos_errors_total Total errors by type")
        for error_type, errors in self.metrics["errors_by_type"].items():
            count = len(errors) if isinstance(errors, list) else errors
            lines.append(f'consultantos_errors_total{{error_type="{error_type}"}} {count}')
        
        # API call metrics
        lines.append("# TYPE consultantos_api_calls_total counter")
        lines.append("# HELP consultantos_api_calls_total Total API calls by service")
        for service, stats in self.metrics["api_calls"].items():
            lines.append(f'consultantos_api_calls_total{{service="{service}",status="success"}} {stats["success"]}')
            lines.append(f'consultantos_api_calls_total{{service="{service}",status="failed"}} {stats["failed"]}')
        
        # Job queue metrics
        lines.append("# TYPE consultantos_jobs_total gauge")
        lines.append("# HELP consultantos_jobs_total Jobs by status")
        for status, count in self.metrics["job_queue"].items():
            lines.append(f'consultantos_jobs_total{{status="{status}"}} {count}')
        
        # Cost tracking
        lines.append("# TYPE consultantos_api_cost_total counter")
        lines.append("# HELP consultantos_api_cost_total Total API costs")
        for service, cost_data in self.metrics["cost_tracking"].items():
            lines.append(f'consultantos_api_cost_total{{service="{service}",unit="{cost_data["unit"]}"}} {cost_data["total_cost"]}')
        
        return "\n".join(lines)


# Global metrics collector
metrics = MetricsCollector()


def log_agent_execution(agent_name: str):
    """Decorator to log agent execution"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            report_id = kwargs.get("report_id") or args[0] if args else None
            
            logger.info(
                "agent_execution_started",
                agent_name=agent_name,
                report_id=report_id
            )
            
            try:
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                metrics.increment("agent_executions", labels={"agent": agent_name, "status": "success"})
                metrics.record_execution_time(execution_time, agent_name)
                
                logger.info(
                    "agent_execution_completed",
                    agent_name=agent_name,
                    report_id=report_id,
                    execution_time_seconds=round(execution_time, 2)
                )
                
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                error_type = type(e).__name__
                
                metrics.increment("agent_executions", labels={"agent": agent_name, "status": "failed"})
                metrics.record_error(error_type, str(e))
                
                logger.error(
                    "agent_execution_failed",
                    agent_name=agent_name,
                    report_id=report_id,
                    error_type=error_type,
                    error_message=str(e),
                    execution_time_seconds=round(execution_time, 2),
                    exc_info=True
                )
                raise
        
        return wrapper
    return decorator


@contextmanager
def track_operation(operation_name: str, **context):
    """Context manager to track operation execution"""
    start_time = time.time()
    logger.info(f"{operation_name}_started", **context)
    
    try:
        yield
        execution_time = time.time() - start_time
        metrics.record_execution_time(execution_time, operation_name)
        logger.info(
            f"{operation_name}_completed",
            execution_time_seconds=round(execution_time, 2),
            **context
        )
    except Exception as e:
        execution_time = time.time() - start_time
        error_type = type(e).__name__
        metrics.record_error(error_type, str(e))
        logger.error(
            f"{operation_name}_failed",
            error_type=error_type,
            error_message=str(e),
            execution_time_seconds=round(execution_time, 2),
            **context,
            exc_info=True
        )
        raise


def log_request(request_id: str, company: str, frameworks: list, user_ip: str):
    """Log analysis request"""
    metrics.increment("requests_total")
    logger.info(
        "analysis_request_received",
        report_id=request_id,
        company=company,
        frameworks=frameworks,
        user_ip=user_ip
    )


def log_request_success(request_id: str, execution_time: float, confidence: float):
    """Log successful analysis request"""
    try:
        metrics.increment("requests_success")
    except Exception as e:
        # Log metrics failure but don't interrupt request flow
        logger.error(f"Failed to increment metrics for request success: {e}", exc_info=True)
    
    try:
        logger.info(
            "analysis_completed",
            report_id=request_id,
            execution_time_seconds=round(execution_time, 2),
            confidence_score=confidence
        )
    except Exception as e:
        # Fallback to basic logging if structlog fails
        import logging
        basic_logger = logging.getLogger(__name__)
        basic_logger.info(
            f"analysis_completed: report_id={request_id}, "
            f"execution_time={round(execution_time, 2)}, "
            f"confidence={confidence}"
        )


def log_request_failure(request_id: str, error: Exception):
    """Log failed analysis request"""
    metrics.increment("requests_failed")
    error_type = type(error).__name__
    metrics.record_error(error_type, str(error))
    logger.error(
        "analysis_failed",
        report_id=request_id,
        error_type=error_type,
        error_message=str(error),
        exc_info=True
    )


def log_cache_hit(cache_key: str, cache_type: str = "disk"):
    """Log cache hit"""
    metrics.increment("cache_hits")
    logger.debug("cache_hit", cache_key=cache_key, cache_type=cache_type)


def log_cache_miss(cache_key: str):
    """Log cache miss"""
    metrics.increment("cache_misses")
    logger.debug("cache_miss", cache_key=cache_key)