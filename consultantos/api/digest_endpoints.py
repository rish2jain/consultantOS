"""
API endpoints for email digest preferences and alerts
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from datetime import datetime
import uuid

from consultantos.models import (
    DigestPreferences,
    DigestContent,
    Alert,
    CreateAlertRequest,
)
from consultantos.auth import get_current_user
from consultantos.database import get_db_service
from consultantos.notifications.digest import DigestGenerator
import logging

router = APIRouter(prefix="/digest", tags=["digest"])
logger = logging.getLogger(__name__)


# ===== Digest Preferences =====

@router.get("/preferences", response_model=DigestPreferences)
async def get_digest_preferences(
    user_id: str = Depends(get_current_user),
    db = Depends(get_db_service)
) -> DigestPreferences:
    """
    Get user's digest preferences

    Args:
        user_id: Authenticated user ID
        db: Database service

    Returns:
        Digest preferences
    """
    try:
        prefs = await db.get_digest_preferences(user_id)

        if not prefs:
            # Create default preferences
            prefs = DigestPreferences(user_id=user_id)
            await db.save_digest_preferences(prefs)

        return prefs

    except Exception as e:
        logger.error("get_preferences_failed", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get preferences")


@router.put("/preferences", response_model=DigestPreferences)
async def update_digest_preferences(
    prefs: DigestPreferences,
    user_id: str = Depends(get_current_user),
    db = Depends(get_db_service)
) -> DigestPreferences:
    """
    Update digest preferences

    Args:
        prefs: New preferences
        user_id: Authenticated user ID
        db: Database service

    Returns:
        Updated preferences
    """
    try:
        # Ensure user_id matches
        prefs.user_id = user_id

        # Save
        await db.save_digest_preferences(prefs)

        logger.info("preferences_updated", user_id=user_id, enabled=prefs.enabled)

        return prefs

    except Exception as e:
        logger.error("update_preferences_failed", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to update preferences")


# ===== Digest Preview & Generation =====

@router.get("/preview", response_model=DigestContent)
async def preview_digest(
    user_id: str = Depends(get_current_user),
    db = Depends(get_db_service)
) -> DigestContent:
    """
    Preview what would be in the next digest

    Args:
        user_id: Authenticated user ID
        db: Database service

    Returns:
        Digest content preview
    """
    try:
        generator = DigestGenerator(db)
        digest = await generator.generate_weekly_digest(user_id)

        logger.info("digest_previewed", user_id=user_id)

        return digest

    except Exception as e:
        logger.error("preview_digest_failed", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to preview digest")


@router.post("/send-now", status_code=202)
async def send_digest_now(
    user_id: str = Depends(get_current_user),
    db = Depends(get_db_service)
) -> dict:
    """
    Send digest immediately (on-demand)

    Args:
        user_id: Authenticated user ID
        db: Database service

    Returns:
        Status message
    """
    try:
        generator = DigestGenerator(db)
        await generator.send_digest(user_id)

        logger.info("digest_sent_manual", user_id=user_id)

        return {"message": "Digest sent successfully"}

    except Exception as e:
        logger.error("send_digest_now_failed", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to send digest")


# ===== Alerts =====

@router.get("/alerts", response_model=List[Alert])
async def list_alerts(
    unread_only: bool = True,
    user_id: str = Depends(get_current_user),
    db = Depends(get_db_service)
) -> List[Alert]:
    """
    List user's alerts

    Args:
        unread_only: Only show unread alerts
        user_id: Authenticated user ID
        db: Database service

    Returns:
        List of alerts
    """
    try:
        alerts = await db.list_alerts(user_id, unread_only=unread_only)

        logger.info("alerts_listed", user_id=user_id, count=len(alerts))

        return alerts

    except Exception as e:
        logger.error("list_alerts_failed", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to list alerts")


@router.post("/alerts", response_model=Alert, status_code=201)
async def create_alert(
    request: CreateAlertRequest,
    user_id: str = Depends(get_current_user),
    db = Depends(get_db_service)
) -> Alert:
    """
    Create a custom alert

    Args:
        request: Alert configuration
        user_id: Authenticated user ID
        db: Database service

    Returns:
        Created alert
    """
    try:
        # Create alert
        alert = Alert(
            id=str(uuid.uuid4()),
            user_id=user_id,
            company=request.company,
            alert_type=request.alert_type,
            severity="medium",  # Default
            message=f"Custom alert for {request.company}",
            details=request.conditions,
        )

        await db.create_alert(alert)

        logger.info("alert_created", user_id=user_id, company=request.company)

        return alert

    except Exception as e:
        logger.error("create_alert_failed", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create alert")


@router.patch("/alerts/{alert_id}/mark-read", status_code=200)
async def mark_alert_read(
    alert_id: str,
    user_id: str = Depends(get_current_user),
    db = Depends(get_db_service)
) -> dict:
    """
    Mark alert as read

    Args:
        alert_id: Alert ID
        user_id: Authenticated user ID
        db: Database service

    Returns:
        Success message
    """
    try:
        # Get alert
        alert = await db.get_alert(alert_id)

        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")

        # Verify ownership
        if alert.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")

        # Mark as read
        alert.read = True
        await db.update_alert(alert)

        logger.info("alert_marked_read", user_id=user_id, alert_id=alert_id)

        return {"message": "Alert marked as read"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error("mark_alert_read_failed", alert_id=alert_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to mark alert as read")


@router.delete("/alerts/{alert_id}", status_code=204)
async def delete_alert(
    alert_id: str,
    user_id: str = Depends(get_current_user),
    db = Depends(get_db_service)
):
    """
    Delete an alert

    Args:
        alert_id: Alert ID
        user_id: Authenticated user ID
        db: Database service
    """
    try:
        # Get alert
        alert = await db.get_alert(alert_id)

        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")

        # Verify ownership
        if alert.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")

        # Delete
        await db.delete_alert(alert_id)

        logger.info("alert_deleted", user_id=user_id, alert_id=alert_id)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("delete_alert_failed", alert_id=alert_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to delete alert")
