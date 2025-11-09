"""
API endpoints for continuous intelligence monitoring.

Provides RESTful interface for managing monitors, viewing alerts,
and controlling the continuous intelligence platform.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional

from consultantos.models.monitoring import (
    Alert,
    AlertFeedbackRequest,
    AlertListResponse,
    Monitor,
    MonitorCreateRequest,
    MonitoringStats,
    MonitorListResponse,
    MonitorStatus,
    MonitorUpdateRequest,
)
from consultantos.monitoring.intelligence_monitor import IntelligenceMonitor
from consultantos.auth import get_current_user_id
from consultantos.utils.sanitize import sanitize_string
import logging
logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/monitors",
    tags=["monitoring"],
    responses={404: {"description": "Not found"}},
)


def get_intelligence_monitor() -> IntelligenceMonitor:
    """
    Dependency injection for IntelligenceMonitor.

    Override this in tests or configure with production dependencies.
    """
    from consultantos.orchestrator.analysis_orchestrator import get_orchestrator
    from consultantos.database import get_database_service
    from consultantos.cache import get_cache_service

    return IntelligenceMonitor(
        orchestrator=get_orchestrator(),
        db_service=get_database_service(),
        cache_service=get_cache_service(),
    )


@router.post("", response_model=Monitor, status_code=201)
async def create_monitor(
    request: MonitorCreateRequest,
    user_id: str = Depends(get_current_user_id),
    monitor_service: IntelligenceMonitor = Depends(get_intelligence_monitor),
) -> Monitor:
    """
    Create new monitoring instance.

    Creates continuous monitoring for a company with specified configuration.
    Runs initial baseline analysis automatically.

    Args:
        request: Monitor creation request
        user_id: Authenticated user ID
        monitor_service: Intelligence monitor service

    Returns:
        Created monitor instance

    Raises:
        HTTPException: 400 if inputs invalid or duplicate exists
        HTTPException: 500 if creation fails
    """
    try:
        # Sanitize inputs
        company = sanitize_string(request.company)
        industry = sanitize_string(request.industry)

        monitor = await monitor_service.create_monitor(
            user_id=user_id,
            company=company,
            industry=industry,
            config=request.config,
        )

        logger.info(
            "monitor_created_via_api",
            monitor_id=monitor.id,
            company=company,
            user_id=user_id,
        )

        return monitor

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(
            "monitor_creation_failed",
            company=request.company,
            user_id=user_id,
            error=str(e),
        )
        raise HTTPException(status_code=500, detail="Failed to create monitor")


@router.get("", response_model=MonitorListResponse)
async def list_monitors(
    user_id: str = Depends(get_current_user_id),
    status: Optional[MonitorStatus] = Query(None, description="Filter by status"),
    monitor_service: IntelligenceMonitor = Depends(get_intelligence_monitor),
) -> MonitorListResponse:
    """
    List all monitors for authenticated user.

    Args:
        user_id: Authenticated user ID
        status: Optional status filter
        monitor_service: Intelligence monitor service

    Returns:
        List of monitors with summary stats
    """
    try:
        monitors = await monitor_service.db.get_user_monitors(user_id, status=status)

        active_count = sum(1 for m in monitors if m.status == MonitorStatus.ACTIVE)

        return MonitorListResponse(
            monitors=monitors,
            total=len(monitors),
            active_count=active_count,
        )

    except Exception as e:
        logger.error(
            "list_monitors_failed",
            user_id=user_id,
            error=str(e),
        )
        raise HTTPException(status_code=500, detail="Failed to list monitors")


@router.get("/{monitor_id}", response_model=Monitor)
async def get_monitor(
    monitor_id: str,
    user_id: str = Depends(get_current_user_id),
    monitor_service: IntelligenceMonitor = Depends(get_intelligence_monitor),
) -> Monitor:
    """
    Get monitor details.

    Args:
        monitor_id: Monitor ID
        user_id: Authenticated user ID
        monitor_service: Intelligence monitor service

    Returns:
        Monitor details

    Raises:
        HTTPException: 404 if not found or unauthorized
    """
    try:
        monitor = await monitor_service.db.get_monitor(monitor_id)

        if not monitor:
            raise HTTPException(status_code=404, detail="Monitor not found")

        # Verify ownership
        if monitor.user_id != user_id:
            raise HTTPException(status_code=404, detail="Monitor not found")

        return monitor

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "get_monitor_failed",
            monitor_id=monitor_id,
            error=str(e),
        )
        raise HTTPException(status_code=500, detail="Failed to get monitor")


@router.put("/{monitor_id}", response_model=Monitor)
async def update_monitor(
    monitor_id: str,
    request: MonitorUpdateRequest,
    user_id: str = Depends(get_current_user_id),
    monitor_service: IntelligenceMonitor = Depends(get_intelligence_monitor),
) -> Monitor:
    """
    Update monitor configuration or status.

    Args:
        monitor_id: Monitor ID
        request: Update request
        user_id: Authenticated user ID
        monitor_service: Intelligence monitor service

    Returns:
        Updated monitor

    Raises:
        HTTPException: 404 if not found or unauthorized
        HTTPException: 400 if invalid update
    """
    try:
        # Verify ownership
        monitor = await monitor_service.db.get_monitor(monitor_id)
        if not monitor or monitor.user_id != user_id:
            raise HTTPException(status_code=404, detail="Monitor not found")

        # Update monitor
        updated = await monitor_service.update_monitor(
            monitor_id=monitor_id,
            config=request.config,
            status=request.status,
        )

        logger.info(
            "monitor_updated",
            monitor_id=monitor_id,
            user_id=user_id,
        )

        return updated

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(
            "update_monitor_failed",
            monitor_id=monitor_id,
            error=str(e),
        )
        raise HTTPException(status_code=500, detail="Failed to update monitor")


@router.delete("/{monitor_id}", status_code=204)
async def delete_monitor(
    monitor_id: str,
    user_id: str = Depends(get_current_user_id),
    monitor_service: IntelligenceMonitor = Depends(get_intelligence_monitor),
) -> None:
    """
    Delete monitor (soft delete).

    Args:
        monitor_id: Monitor ID
        user_id: Authenticated user ID
        monitor_service: Intelligence monitor service

    Raises:
        HTTPException: 404 if not found or unauthorized
    """
    try:
        # Verify ownership
        monitor = await monitor_service.db.get_monitor(monitor_id)
        if not monitor or monitor.user_id != user_id:
            raise HTTPException(status_code=404, detail="Monitor not found")

        await monitor_service.delete_monitor(monitor_id)

        logger.info(
            "monitor_deleted",
            monitor_id=monitor_id,
            user_id=user_id,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "delete_monitor_failed",
            monitor_id=monitor_id,
            error=str(e),
        )
        raise HTTPException(status_code=500, detail="Failed to delete monitor")


@router.post("/{monitor_id}/check", response_model=List[Alert])
async def check_monitor_now(
    monitor_id: str,
    user_id: str = Depends(get_current_user_id),
    monitor_service: IntelligenceMonitor = Depends(get_intelligence_monitor),
) -> List[Alert]:
    """
    Trigger immediate monitor check (manual refresh).

    Args:
        monitor_id: Monitor ID
        user_id: Authenticated user ID
        monitor_service: Intelligence monitor service

    Returns:
        List of generated alerts

    Raises:
        HTTPException: 404 if not found or unauthorized
        HTTPException: 500 if check fails
    """
    try:
        # Verify ownership
        monitor = await monitor_service.db.get_monitor(monitor_id)
        if not monitor or monitor.user_id != user_id:
            raise HTTPException(status_code=404, detail="Monitor not found")

        # Run check
        alerts = await monitor_service.check_for_updates(monitor_id)

        logger.info(
            "manual_monitor_check",
            monitor_id=monitor_id,
            alerts_generated=len(alerts),
        )

        return alerts

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "manual_check_failed",
            monitor_id=monitor_id,
            error=str(e),
        )
        raise HTTPException(status_code=500, detail="Failed to check monitor")


@router.get("/{monitor_id}/alerts", response_model=AlertListResponse)
async def get_monitor_alerts(
    monitor_id: str,
    user_id: str = Depends(get_current_user_id),
    limit: int = Query(50, ge=1, le=100, description="Max alerts to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    monitor_service: IntelligenceMonitor = Depends(get_intelligence_monitor),
) -> AlertListResponse:
    """
    Get alerts for monitor.

    Args:
        monitor_id: Monitor ID
        user_id: Authenticated user ID
        limit: Maximum alerts to return
        offset: Pagination offset
        monitor_service: Intelligence monitor service

    Returns:
        List of alerts with pagination

    Raises:
        HTTPException: 404 if monitor not found or unauthorized
    """
    try:
        # Verify ownership
        monitor = await monitor_service.db.get_monitor(monitor_id)
        if not monitor or monitor.user_id != user_id:
            raise HTTPException(status_code=404, detail="Monitor not found")

        # Get alerts
        alerts = await monitor_service.db.get_monitor_alerts(
            monitor_id, limit=limit, offset=offset
        )

        unread_count = sum(1 for a in alerts if not a.read)

        return AlertListResponse(
            alerts=alerts,
            total=len(alerts),
            unread_count=unread_count,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "get_alerts_failed",
            monitor_id=monitor_id,
            error=str(e),
        )
        raise HTTPException(status_code=500, detail="Failed to get alerts")


@router.post("/alerts/{alert_id}/read", response_model=Alert)
async def mark_alert_read(
    alert_id: str,
    user_id: str = Depends(get_current_user_id),
    monitor_service: IntelligenceMonitor = Depends(get_intelligence_monitor),
) -> Alert:
    """
    Mark alert as read.

    Args:
        alert_id: Alert ID
        user_id: Authenticated user ID
        monitor_service: Intelligence monitor service

    Returns:
        Updated alert

    Raises:
        HTTPException: 404 if not found or unauthorized
    """
    try:
        alert = await monitor_service.db.get_alert(alert_id)
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")

        # Verify ownership via monitor
        monitor = await monitor_service.db.get_monitor(alert.monitor_id)
        if not monitor or monitor.user_id != user_id:
            raise HTTPException(status_code=404, detail="Alert not found")

        # Mark as read
        from datetime import datetime

        alert.read = True
        alert.read_at = datetime.utcnow()

        await monitor_service.db.update_alert(alert)

        return alert

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "mark_read_failed",
            alert_id=alert_id,
            error=str(e),
        )
        raise HTTPException(status_code=500, detail="Failed to mark alert as read")


@router.post("/alerts/{alert_id}/feedback")
async def submit_alert_feedback(
    alert_id: str,
    feedback: AlertFeedbackRequest,
    user_id: str = Depends(get_current_user_id),
    monitor_service: IntelligenceMonitor = Depends(get_intelligence_monitor),
) -> dict:
    """
    Submit feedback on alert quality.

    Helps improve alert relevance and confidence scoring.

    Args:
        alert_id: Alert ID
        feedback: Feedback data
        user_id: Authenticated user ID
        monitor_service: Intelligence monitor service

    Returns:
        Success response

    Raises:
        HTTPException: 404 if not found or unauthorized
    """
    try:
        alert = await monitor_service.db.get_alert(alert_id)
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")

        # Verify ownership
        monitor = await monitor_service.db.get_monitor(alert.monitor_id)
        if not monitor or monitor.user_id != user_id:
            raise HTTPException(status_code=404, detail="Alert not found")

        # Store feedback
        alert.user_feedback = feedback.feedback
        alert.action_taken = feedback.action_taken

        await monitor_service.db.update_alert(alert)

        logger.info(
            "alert_feedback_received",
            alert_id=alert_id,
            feedback=feedback.feedback,
        )

        return {"status": "success", "message": "Feedback recorded"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "feedback_submission_failed",
            alert_id=alert_id,
            error=str(e),
        )
        raise HTTPException(status_code=500, detail="Failed to submit feedback")


@router.get("/stats/dashboard", response_model=MonitoringStats)
async def get_dashboard_stats(
    user_id: str = Depends(get_current_user_id),
    monitor_service: IntelligenceMonitor = Depends(get_intelligence_monitor),
) -> MonitoringStats:
    """
    Get monitoring statistics for dashboard.

    Args:
        user_id: Authenticated user ID
        monitor_service: Intelligence monitor service

    Returns:
        Dashboard statistics
    """
    try:
        stats = await monitor_service.db.get_monitoring_stats(user_id)
        return stats

    except Exception as e:
        logger.error(
            "get_stats_failed",
            user_id=user_id,
            error=str(e),
        )
        raise HTTPException(status_code=500, detail="Failed to get statistics")
