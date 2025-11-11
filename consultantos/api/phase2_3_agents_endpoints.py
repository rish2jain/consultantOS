"""
API endpoints for Phase 2 & 3 dashboard agents
"""
from fastapi import APIRouter, Depends, HTTPException, Security, Query
from typing import List, Optional, Dict, Any
from consultantos.auth import get_current_user_id, verify_api_key
from consultantos.agents.notification_agent import NotificationAgent, NotificationListRequest, NotificationSettingsRequest, NotificationActionRequest, NotificationResponse
from consultantos.agents.version_control_agent import VersionControlAgent, VersionListRequest, VersionCreateRequest, VersionCompareRequest, VersionResponse
from consultantos.agents.template_agent import TemplateAgent, TemplateListRequest, TemplateCreateRequest, TemplateResponse
from consultantos.agents.visualization_agent import VisualizationAgent, VisualizationCreateRequest, VisualizationListRequest, VisualizationResponse
from consultantos.agents.alert_feedback_agent import AlertFeedbackAgent, AlertFeedbackSubmitRequest, AlertFeedbackListRequest, AlertFeedbackStatsRequest, AlertFeedbackResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/dashboard-agents",
    tags=["Dashboard Agents - Phase 2 & 3"],
    responses={404: {"description": "Not found"}},
)


# Dependency to get agent instances
def get_notification_agent() -> NotificationAgent:
    return NotificationAgent()

def get_version_control_agent() -> VersionControlAgent:
    return VersionControlAgent()

def get_template_agent() -> TemplateAgent:
    return TemplateAgent()

def get_visualization_agent() -> VisualizationAgent:
    return VisualizationAgent()

def get_alert_feedback_agent() -> AlertFeedbackAgent:
    return AlertFeedbackAgent()


# ============================================================================
# NOTIFICATION AGENT ENDPOINTS
# ============================================================================

@router.get("/notifications", response_model=NotificationResponse)
async def list_notifications_agent(
    user_id: str = Depends(get_current_user_id),
    limit: int = Query(50, ge=1, le=100),
    unread_only: bool = Query(False),
    type_filter: Optional[str] = Query(None),
    agent: NotificationAgent = Depends(get_notification_agent)
) -> NotificationResponse:
    """List notifications using the NotificationAgent."""
    try:
        request_data = {
            "action_type": "list",
            "user_id": user_id,
            "limit": limit,
            "unread_only": unread_only,
            "type_filter": type_filter,
        }
        result = await agent.execute(request_data)
        return NotificationResponse(**result["data"])
    except Exception as e:
        logger.error(f"Failed to list notifications via agent: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list notifications: {e}")


@router.put("/notifications/settings", response_model=NotificationResponse)
async def update_notification_settings_agent(
    request: NotificationSettingsRequest,
    user_id: str = Depends(get_current_user_id),
    agent: NotificationAgent = Depends(get_notification_agent)
) -> NotificationResponse:
    """Update notification settings using the NotificationAgent."""
    try:
        request_data = request.model_dump()
        request_data["action_type"] = "settings"
        request_data["user_id"] = user_id
        result = await agent.execute(request_data)
        return NotificationResponse(**result["data"])
    except Exception as e:
        logger.error(f"Failed to update notification settings via agent: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update settings: {e}")


@router.post("/notifications/{notification_id}/action", response_model=NotificationResponse)
async def perform_notification_action_agent(
    notification_id: str,
    action: str = Query(..., description="Action: mark_read, mark_unread, delete"),
    user_id: str = Depends(get_current_user_id),
    agent: NotificationAgent = Depends(get_notification_agent)
) -> NotificationResponse:
    """Perform an action on a notification using the NotificationAgent."""
    try:
        request_data = {
            "action_type": "action",
            "user_id": user_id,
            "notification_id": notification_id,
            "action": action,
        }
        result = await agent.execute(request_data)
        return NotificationResponse(**result["data"])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to perform notification action via agent: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to perform action: {e}")


# ============================================================================
# VERSION CONTROL AGENT ENDPOINTS
# ============================================================================

@router.get("/versions/report/{report_id}", response_model=VersionResponse)
async def get_version_history_agent(
    report_id: str,
    agent: VersionControlAgent = Depends(get_version_control_agent)
) -> VersionResponse:
    """Get version history for a report using the VersionControlAgent."""
    try:
        request_data = {
            "action_type": "list",
            "report_id": report_id,
        }
        result = await agent.execute(request_data)
        return VersionResponse(**result["data"])
    except Exception as e:
        logger.error(f"Failed to get version history via agent: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get version history: {e}")


@router.post("/versions", response_model=VersionResponse)
async def create_version_agent(
    request: VersionCreateRequest,
    user_id: str = Depends(get_current_user_id),
    agent: VersionControlAgent = Depends(get_version_control_agent)
) -> VersionResponse:
    """Create a new version using the VersionControlAgent."""
    try:
        request_data = request.model_dump()
        request_data["action_type"] = "create"
        request_data["user_id"] = user_id
        result = await agent.execute(request_data)
        return VersionResponse(**result["data"])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create version via agent: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create version: {e}")


@router.get("/versions/compare", response_model=VersionResponse)
async def compare_versions_agent(
    from_version_id: str = Query(...),
    to_version_id: str = Query(...),
    agent: VersionControlAgent = Depends(get_version_control_agent)
) -> VersionResponse:
    """Compare two versions using the VersionControlAgent."""
    try:
        request_data = {
            "action_type": "compare",
            "from_version_id": from_version_id,
            "to_version_id": to_version_id,
        }
        result = await agent.execute(request_data)
        return VersionResponse(**result["data"])
    except Exception as e:
        logger.error(f"Failed to compare versions via agent: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to compare versions: {e}")


# ============================================================================
# TEMPLATE AGENT ENDPOINTS
# ============================================================================

@router.get("/templates", response_model=TemplateResponse)
async def list_templates_agent(
    category: Optional[str] = Query(None),
    framework_type: Optional[str] = Query(None),
    visibility: Optional[str] = Query("public"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    agent: TemplateAgent = Depends(get_template_agent)
) -> TemplateResponse:
    """List templates using the TemplateAgent."""
    try:
        request_data = {
            "action_type": "list",
            "category": category,
            "framework_type": framework_type,
            "visibility": visibility,
            "page": page,
            "page_size": page_size,
        }
        result = await agent.execute(request_data)
        return TemplateResponse(**result["data"])
    except Exception as e:
        logger.error(f"Failed to list templates via agent: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list templates: {e}")


@router.post("/templates", response_model=TemplateResponse)
async def create_template_agent(
    request: TemplateCreateRequest,
    user_id: str = Depends(get_current_user_id),
    agent: TemplateAgent = Depends(get_template_agent)
) -> TemplateResponse:
    """Create a template using the TemplateAgent."""
    try:
        request_data = request.model_dump()
        request_data["action_type"] = "create"
        request_data["user_id"] = user_id
        result = await agent.execute(request_data)
        return TemplateResponse(**result["data"])
    except Exception as e:
        logger.error(f"Failed to create template via agent: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create template: {e}")


# ============================================================================
# VISUALIZATION AGENT ENDPOINTS
# ============================================================================

@router.post("/visualizations", response_model=VisualizationResponse)
async def create_visualization_agent(
    request: VisualizationCreateRequest,
    agent: VisualizationAgent = Depends(get_visualization_agent)
) -> VisualizationResponse:
    """Create a visualization using the VisualizationAgent."""
    try:
        request_data = request.model_dump()
        request_data["action_type"] = "create"
        result = await agent.execute(request_data)
        if isinstance(result, dict) and "data" in result:
            return VisualizationResponse(**result["data"])
        return VisualizationResponse(**result)
    except Exception as e:
        logger.error(f"Failed to create visualization via agent: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create visualization: {e}")


# ============================================================================
# ALERT FEEDBACK AGENT ENDPOINTS
# ============================================================================

@router.post("/alerts/feedback", response_model=AlertFeedbackResponse)
async def submit_alert_feedback_agent(
    request: AlertFeedbackSubmitRequest,
    user_id: str = Depends(get_current_user_id),
    agent: AlertFeedbackAgent = Depends(get_alert_feedback_agent)
) -> AlertFeedbackResponse:
    """Submit alert feedback using the AlertFeedbackAgent."""
    try:
        request_data = request.model_dump()
        request_data["action_type"] = "submit"
        request_data["user_id"] = user_id
        result = await agent.execute(request_data)
        return AlertFeedbackResponse(**result["data"])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to submit feedback via agent: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to submit feedback: {e}")


@router.get("/alerts/feedback/stats", response_model=AlertFeedbackResponse)
async def get_alert_feedback_stats_agent(
    user_id: str = Depends(get_current_user_id),
    monitor_id: Optional[str] = Query(None),
    agent: AlertFeedbackAgent = Depends(get_alert_feedback_agent)
) -> AlertFeedbackResponse:
    """Get alert feedback statistics using the AlertFeedbackAgent."""
    try:
        request_data = {
            "action_type": "stats",
            "user_id": user_id,
            "monitor_id": monitor_id,
        }
        result = await agent.execute(request_data)
        return AlertFeedbackResponse(**result["data"])
    except Exception as e:
        logger.error(f"Failed to get feedback stats via agent: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {e}")

