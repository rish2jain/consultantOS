"""API endpoints for live dashboards and real-time updates"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from consultantos.auth import get_current_user
from consultantos.dashboards import (
    DashboardService,
    DashboardTemplate,
    LiveDashboard,
    ScenarioAssumptions,
    ScenarioForecast,
)
from consultantos.dashboards.service import get_dashboard_service
from consultantos.dashboards.templates import (
    get_template,
    get_templates_for_audience,
    get_templates_for_use_case,
    list_templates,
)
from consultantos.log_utils import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/dashboards", tags=["dashboards"])


# Request/Response Models
class CreateDashboardRequest(BaseModel):
    """Request to create a new dashboard"""
    company: str
    industry: str
    template: str
    frameworks: Optional[List[str]] = None
    depth: str = "standard"

    class Config:
        json_schema_extra = {
            "example": {
                "company": "Tesla",
                "industry": "Electric Vehicles",
                "template": "executive_summary",
                "frameworks": ["porter", "swot"],
                "depth": "standard"
            }
        }


class RunScenarioRequest(BaseModel):
    """Request to run scenario planning"""
    company: str
    industry: str
    assumptions: ScenarioAssumptions
    forecast_period: int = 12

    class Config:
        json_schema_extra = {
            "example": {
                "company": "Tesla",
                "industry": "Electric Vehicles",
                "assumptions": {
                    "market_growth_rate": 5.0,
                    "competitor_entry": False,
                    "regulatory_change": False,
                    "price_change": -10.0,
                    "cost_change": 5.0
                },
                "forecast_period": 12
            }
        }


# Dashboard Management Endpoints

@router.post("", response_model=LiveDashboard, status_code=201)
async def create_dashboard(
    request: CreateDashboardRequest,
    user_id: str = Depends(get_current_user),
    service: DashboardService = Depends(get_dashboard_service)
):
    """
    Create a new live dashboard from a template.

    The dashboard will be populated with real-time data and can be
    subscribed to for updates via WebSocket.
    """
    try:
        dashboard = await service.create_dashboard(
            company=request.company,
            industry=request.industry,
            template_id=request.template,
            user_id=user_id,
            frameworks=request.frameworks,
            depth=request.depth
        )
        return dashboard
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(
            "Failed to create dashboard",
            extra={"user_id": user_id, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Failed to create dashboard")


@router.get("/{dashboard_id}", response_model=LiveDashboard)
async def get_dashboard(
    dashboard_id: str,
    user_id: str = Depends(get_current_user),
    service: DashboardService = Depends(get_dashboard_service)
):
    """
    Get a dashboard by ID.

    Returns current state including all sections, metrics, and alerts.
    """
    dashboard = await service.get_dashboard(dashboard_id)
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    # Authorization check - verify user owns dashboard
    if dashboard.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied: You do not have permission to view this dashboard"
        )

    return dashboard


@router.post("/{dashboard_id}/refresh", response_model=LiveDashboard)
async def refresh_dashboard(
    dashboard_id: str,
    user_id: str = Depends(get_current_user),
    service: DashboardService = Depends(get_dashboard_service)
):
    """
    Force refresh dashboard data.

    Triggers immediate update of all sections and metrics from data sources.
    Connected WebSocket clients will receive the update automatically.
    """
    try:
        # Check authorization before refreshing
        dashboard = await service.get_dashboard(dashboard_id)
        if not dashboard:
            raise HTTPException(status_code=404, detail="Dashboard not found")
        
        if dashboard.user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="Access denied: You do not have permission to refresh this dashboard"
            )
        
        dashboard = await service.refresh_dashboard(dashboard_id)
        return dashboard
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(
            "Failed to refresh dashboard",
            extra={"dashboard_id": dashboard_id, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Failed to refresh dashboard")


# WebSocket Endpoint for Real-Time Updates

@router.websocket("/{dashboard_id}/ws")
async def dashboard_websocket(
    websocket: WebSocket,
    dashboard_id: str,
    service: DashboardService = Depends(get_dashboard_service)
):
    """
    WebSocket endpoint for real-time dashboard updates.

    Clients connect to this endpoint to receive live updates as data changes.
    The connection will send periodic updates based on the dashboard's
    auto_refresh_interval setting.

    Message Format:
    {
        "type": "initial" | "update" | "metric" | "alert",
        "data": { ... }
    }
    """
    try:
        await service.subscribe_to_updates(dashboard_id, websocket)
    except WebSocketDisconnect:
        logger.info(
            "WebSocket disconnected normally",
            extra={"dashboard_id": dashboard_id}
        )
    except Exception as e:
        logger.error(
            "WebSocket error",
            extra={"dashboard_id": dashboard_id, "error": str(e)}
        )


# Template Management Endpoints

@router.get("/templates/all", response_model=List[DashboardTemplate])
async def list_dashboard_templates():
    """
    List all available dashboard templates.

    Templates provide pre-configured layouts for different use cases
    and target audiences.
    """
    return list_templates()


@router.get("/templates/{template_id}", response_model=DashboardTemplate)
async def get_dashboard_template(template_id: str):
    """Get a specific dashboard template by ID"""
    try:
        return get_template(template_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/templates/audience/{audience}", response_model=List[DashboardTemplate])
async def get_templates_by_audience(audience: str):
    """
    Get dashboard templates for a specific audience.

    Audiences: executive, analyst, strategist, cfo, risk_manager, cto
    """
    templates = get_templates_for_audience(audience)
    if not templates:
        raise HTTPException(
            status_code=404,
            detail=f"No templates found for audience '{audience}'"
        )
    return templates


@router.get("/templates/use-case/{use_case}", response_model=List[DashboardTemplate])
async def get_templates_by_use_case(use_case: str):
    """
    Get dashboard templates for a specific use case.

    Use cases: quarterly_review, competitive_analysis, market_research, etc.
    """
    templates = get_templates_for_use_case(use_case)
    if not templates:
        raise HTTPException(
            status_code=404,
            detail=f"No templates found for use case '{use_case}'"
        )
    return templates


# Scenario Planning Endpoints

@router.post("/scenarios/run", response_model=ScenarioForecast)
async def run_scenario_analysis(
    request: RunScenarioRequest,
    user_id: str = Depends(get_current_user),
    service: DashboardService = Depends(get_dashboard_service)
):
    """
    Run scenario planning analysis with custom assumptions.

    Allows what-if analysis by adjusting market conditions, pricing,
    costs, and other variables to forecast outcomes.
    """
    try:
        forecast = await service.run_scenario(
            company=request.company,
            industry=request.industry,
            assumptions=request.assumptions,
            forecast_period=request.forecast_period
        )
        return forecast
    except Exception as e:
        logger.error(
            "Failed to run scenario",
            extra={"company": request.company, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Failed to run scenario analysis")


# Export Endpoints

@router.post("/{dashboard_id}/export/pdf")
async def export_dashboard_to_pdf(
    dashboard_id: str,
    user_id: str = Depends(get_current_user),
    service: DashboardService = Depends(get_dashboard_service)
):
    """
    Export dashboard to PDF (snapshot).

    Note: This creates a static snapshot of the current dashboard state.
    For latest data, use the live dashboard.

    Returns a PDF file with watermark indicating it's a snapshot.
    """
    from fastapi.responses import Response
    from datetime import datetime
    from consultantos.reports.pdf_generator import generate_pdf_report
    from consultantos import models
    
    dashboard = await service.get_dashboard(dashboard_id)
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    # Authorization check
    if dashboard.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied: You do not have permission to export this dashboard"
        )

    try:
        # Convert dashboard to StrategicReport format for PDF generation
        # Create a minimal report structure from dashboard data
        executive_summary = models.ExecutiveSummary(
            company_name=dashboard.company,
            industry=dashboard.industry,
            analysis_date=datetime.utcnow(),
            key_findings=[
                f"Dashboard snapshot generated at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}",
                f"View live dashboard for latest data: /dashboards/{dashboard_id}",
                f"Template: {dashboard.template}",
                f"Metrics: {len(dashboard.metrics)} active metrics",
                f"Alerts: {len(dashboard.alerts)} active alerts"
            ],
            confidence_score=0.85,
            methodology="Dashboard snapshot export"
        )
        
        # Build sections from dashboard sections
        sections = []
        for section in dashboard.sections:
            sections.append(models.ReportSection(
                title=section.title,
                content=f"Section type: {section.type.value}\nLast updated: {section.last_updated}",
                order=section.order
            ))
        
        # Create strategic report
        report = models.StrategicReport(
            executive_summary=executive_summary,
            sections=sections,
            frameworks={},
            metadata={
                "dashboard_id": dashboard_id,
                "export_type": "dashboard_snapshot",
                "snapshot_timestamp": datetime.utcnow().isoformat(),
                "watermark": f"Snapshot taken at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')} - View live dashboard for latest data"
            }
        )
        
        # Generate PDF
        pdf_bytes = generate_pdf_report(report, report_id=f"dashboard_{dashboard_id}")
        
        # Add watermark text to PDF (this is handled in the metadata)
        # The pdf_generator will include the watermark from metadata
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="dashboard_{dashboard_id}_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.pdf"'
            }
        )
    except Exception as e:
        logger.error(
            "Failed to export dashboard to PDF",
            extra={"dashboard_id": dashboard_id, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")


@router.post("/{dashboard_id}/export/json")
async def export_dashboard_to_json(
    dashboard_id: str,
    user_id: str = Depends(get_current_user),
    service: DashboardService = Depends(get_dashboard_service)
):
    """
    Export dashboard to JSON format.

    Useful for data integration and custom analysis.
    """
    dashboard = await service.get_dashboard(dashboard_id)
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    # Authorization check
    if dashboard.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied: You do not have permission to export this dashboard"
        )

    return dashboard.model_dump()
