"""
Health check endpoints for Kubernetes-style probes
"""
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from consultantos import config, database, storage
import logging

logger = logging.getLogger(__name__)

from consultantos.cache import get_cache_stats

router = APIRouter(prefix="/health", tags=["health"])

# Startup flag
_startup_complete: bool = False


def mark_startup_complete():
    """Mark application startup as complete"""
    global _startup_complete
    _startup_complete = True


@router.get("/live")
async def liveness_probe():
    """
    Liveness probe - Is the application running?

    Returns 200 if the application is alive and responsive.
    Kubernetes will restart the pod if this fails.

    **Example Response:**
    ```json
    {
        "status": "alive",
        "timestamp": "2024-01-01T12:00:00"
    }
    ```
    """
    return {
        "status": "alive",
        "timestamp": datetime.now().isoformat()
    }


@router.get("/ready")
async def readiness_probe():
    """
    Readiness probe - Can the application serve traffic?

    Checks:
    - Database connectivity
    - Cache availability
    - Gemini API configuration

    Returns 200 if ready to serve traffic, 503 if not ready.
    Kubernetes will remove pod from service if this fails.

    **Example Response:**
    ```json
    {
        "status": "ready",
        "timestamp": "2024-01-01T12:00:00",
        "checks": {
            "database": "healthy",
            "cache": "healthy",
            "gemini_api": "configured"
        }
    }
    ```
    """
    checks = {}
    is_ready = True

    # Check database connectivity
    try:
        db_service = database.get_db_service()
        # Try to access the database
        _ = db_service.db
        checks["database"] = "healthy"
    except Exception as e:
        logger.warning(f"Database readiness check failed: {e}")
        checks["database"] = "unhealthy"
        is_ready = False

    # Check cache availability
    try:
        cache_stats = get_cache_stats()
        if cache_stats.get("disk_cache", {}).get("available"):
            checks["cache"] = "healthy"
        else:
            checks["cache"] = "degraded"
            # Cache degradation is not critical for readiness
    except Exception as e:
        logger.warning(f"Cache readiness check failed: {e}")
        checks["cache"] = "unhealthy"
        # Cache is optional, don't fail readiness

    # Check Gemini API configuration
    try:
        settings = config.settings
        if settings.gemini_api_key and settings.gemini_api_key != "test-key-placeholder":
            checks["gemini_api"] = "configured"
        else:
            checks["gemini_api"] = "not_configured"
            is_ready = False
    except Exception as e:
        logger.warning(f"Gemini API check failed: {e}")
        checks["gemini_api"] = "error"
        is_ready = False

    # Check storage (optional, degraded state is acceptable)
    try:
        storage_service = storage.get_storage_service()
        checks["storage"] = "available"
    except Exception as e:
        logger.warning(f"Storage readiness check failed: {e}")
        checks["storage"] = "unavailable"
        # Storage is optional for some operations

    if is_ready:
        return {
            "status": "ready",
            "timestamp": datetime.now().isoformat(),
            "checks": checks
        }
    else:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "not_ready",
                "timestamp": datetime.now().isoformat(),
                "checks": checks
            }
        )


@router.get("/startup")
async def startup_probe():
    """
    Startup probe - Has initialization completed?

    Returns 200 once application has completed startup initialization.
    Kubernetes will wait for this before checking readiness.

    **Example Response:**
    ```json
    {
        "status": "started",
        "timestamp": "2024-01-01T12:00:00",
        "startup_complete": true
    }
    ```
    """
    if _startup_complete:
        return {
            "status": "started",
            "timestamp": datetime.now().isoformat(),
            "startup_complete": True
        }
    else:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "starting",
                "timestamp": datetime.now().isoformat(),
                "startup_complete": False
            }
        )


@router.get("/detailed")
async def detailed_health_check():
    """
    Detailed health check with comprehensive status information

    Includes:
    - All probe statuses
    - Performance metrics
    - Resource utilization
    - System diagnostics

    **Example Response:**
    ```json
    {
        "status": "healthy",
        "timestamp": "2024-01-01T12:00:00",
        "probes": {
            "liveness": "pass",
            "readiness": "pass",
            "startup": "pass"
        },
        "metrics": {
            "total_requests": 1000,
            "cache_hit_rate": 0.75,
            "error_rate": 0.02
        },
        "system": {
            "version": "0.3.0",
            "environment": "production",
            "uptime_seconds": 3600
        }
    }
    ```
    """
    # Run all probe checks
    probes = {
        "liveness": "pass",
        "readiness": "unknown",
        "startup": "pass" if _startup_complete else "fail"
    }

    # Check readiness
    try:
        await readiness_probe()
        probes["readiness"] = "pass"
    except HTTPException:
        probes["readiness"] = "fail"

    # Get metrics summary
    metrics_summary = metrics.get_summary()

    # System information
    settings = config.settings
    system_info = {
        "version": "0.3.0",
        "environment": settings.environment,
        "log_level": settings.log_level
    }

    # Determine overall status
    overall_status = "healthy"
    if probes["readiness"] == "fail":
        overall_status = "degraded"
    if probes["liveness"] == "fail":
        overall_status = "unhealthy"

    return {
        "status": overall_status,
        "timestamp": datetime.now().isoformat(),
        "probes": probes,
        "metrics": metrics_summary,
        "system": system_info
    }


@router.get("/metrics")
async def prometheus_metrics():
    """
    Prometheus-compatible metrics endpoint

    Returns metrics in Prometheus exposition format for scraping.

    **Example Response:**
    ```
    # TYPE consultantos_requests_total counter
    # HELP consultantos_requests_total Total number of requests
    consultantos_requests_total 1000
    # TYPE consultantos_cache_hits counter
    # HELP consultantos_cache_hits Number of cache hits
    consultantos_cache_hits 750
    ```
    """
    from fastapi.responses import PlainTextResponse
    
    prometheus_output = metrics.get_prometheus_metrics()
    return PlainTextResponse(content=prometheus_output, media_type="text/plain; version=0.0.4")