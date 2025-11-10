"""
Dashboard Builder API endpoints for ConsultantOS
Handles formulas, charts, dashboards, KPIs, and exports
"""
import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from consultantos.agents.analytics_builder_agent import AnalyticsBuilderAgent
from consultantos.models.analytics import (
    Formula,
    Chart,
    ChartType,
    Dashboard,
    KPI,
    KPIAlert,
    CreateFormulaRequest,
    CreateChartRequest,
    CreateDashboardRequest,
    UpdateDashboardRequest,
    DashboardExportRequest,
    ExportFormat,
    DashboardResponse,
    AnalyticsSummary,
)
from consultantos.analytics import (
    FormulaParser,
    ChartBuilder,
    DashboardBuilder,
    KPITracker,
    AlertEngine,
    FORMULA_TEMPLATES,
)


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dashboards", tags=["dashboards"])

# Initialize components
agent = AnalyticsBuilderAgent()
formula_parser = FormulaParser(safe_mode=True)
chart_builder = ChartBuilder()
dashboard_builder = DashboardBuilder()
kpi_tracker = KPITracker()
alert_engine = AlertEngine()

# In-memory storage (replace with database in production)
formulas: Dict[str, Formula] = {}
charts: Dict[str, Chart] = {}
dashboards: Dict[str, Dashboard] = {}
kpis: Dict[str, KPI] = {}


# Formula Endpoints
@router.post("/formulas", response_model=Formula, status_code=201)
async def create_formula(request: CreateFormulaRequest) -> Formula:
    """Create a custom formula"""
    try:
        # Extract variables
        variables = formula_parser.extract_variables(request.expression)

        formula = Formula(
            name=request.name,
            description=request.description,
            expression=request.expression,
            variables=variables,
            category=request.category,
            examples=request.examples,
        )

        formulas[formula.formula_id] = formula
        logger.info(f"Created formula: {formula.formula_id}")

        return formula

    except Exception as e:
        logger.error(f"Error creating formula: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/formulas/{formula_id}", response_model=Formula)
async def get_formula(formula_id: str) -> Formula:
    """Get a formula by ID"""
    if formula_id not in formulas:
        raise HTTPException(status_code=404, detail="Formula not found")
    return formulas[formula_id]


@router.get("/formulas", response_model=List[Formula])
async def list_formulas(category: Optional[str] = None) -> List[Formula]:
    """List all formulas, optionally filtered by category"""
    result = list(formulas.values())
    if category:
        result = [f for f in result if f.category == category]
    return result


@router.post("/formulas/{formula_id}/evaluate")
async def evaluate_formula(
    formula_id: str,
    context: Dict[str, Any],
) -> Dict[str, Any]:
    """Evaluate a formula with given context"""
    try:
        if formula_id not in formulas:
            raise HTTPException(status_code=404, detail="Formula not found")

        formula = formulas[formula_id]
        result = await formula_parser.parse_and_evaluate(
            formula.expression,
            context,
            formula.variables,
        )

        return {
            "formula_id": formula_id,
            "expression": formula.expression,
            "result": result,
            "context": context,
        }

    except Exception as e:
        logger.error(f"Error evaluating formula: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/formula-templates", response_model=Dict[str, Dict[str, Any]])
async def get_formula_templates() -> Dict[str, Dict[str, Any]]:
    """Get available formula templates"""
    return FORMULA_TEMPLATES


# Chart Endpoints
@router.post("/charts", response_model=Chart, status_code=201)
async def create_chart(request: CreateChartRequest) -> Chart:
    """Create a chart"""
    try:
        chart = Chart(
            name=request.name,
            description=request.description,
            chart_type=request.chart_type,
            data_source=request.data_source,
            config=request.config,
        )

        charts[chart.chart_id] = chart
        logger.info(f"Created chart: {chart.chart_id}")

        return chart

    except Exception as e:
        logger.error(f"Error creating chart: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/charts/{chart_id}", response_model=Chart)
async def get_chart(chart_id: str) -> Chart:
    """Get a chart by ID"""
    if chart_id not in charts:
        raise HTTPException(status_code=404, detail="Chart not found")
    return charts[chart_id]


@router.get("/charts", response_model=List[Chart])
async def list_charts(
    chart_type: Optional[ChartType] = None,
    limit: int = Query(50, ge=1, le=100),
) -> List[Chart]:
    """List all charts"""
    result = list(charts.values())
    if chart_type:
        result = [c for c in result if c.chart_type == chart_type]
    return result[:limit]


# Dashboard Endpoints
@router.post("", response_model=Dashboard, status_code=201)
async def create_dashboard(request: CreateDashboardRequest) -> Dashboard:
    """Create a dashboard"""
    try:
        dashboard = await dashboard_builder.create_dashboard(
            name=request.name,
            description=request.description,
            layout=request.layout,
            elements=request.elements,
            refresh_interval=request.refresh_interval,
            tags=request.tags,
        )

        dashboards[dashboard.dashboard_id] = dashboard
        logger.info(f"Created dashboard: {dashboard.dashboard_id}")

        return dashboard

    except Exception as e:
        logger.error(f"Error creating dashboard: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{dashboard_id}", response_model=DashboardResponse)
async def get_dashboard(dashboard_id: str) -> DashboardResponse:
    """Get a dashboard with all related data"""
    try:
        if dashboard_id not in dashboards:
            raise HTTPException(status_code=404, detail="Dashboard not found")

        dashboard = dashboards[dashboard_id]

        # Get related charts and KPIs
        dashboard_charts = [charts[cid] for cid in dashboard.charts if cid in charts]
        dashboard_kpis = [kpis[kid] for kid in dashboard.kpis if kid in kpis]
        dashboard_alerts = kpi_tracker.get_alerts(limit=10)

        return DashboardResponse(
            dashboard=dashboard,
            charts=dashboard_charts,
            kpis=dashboard_kpis,
            alerts=dashboard_alerts,
            last_refresh=dashboard.updated_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting dashboard: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[Dashboard])
async def list_dashboards(
    tag: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100),
) -> List[Dashboard]:
    """List all dashboards"""
    result = list(dashboards.values())
    if tag:
        result = [d for d in result if tag in d.tags]
    return result[:limit]


@router.put("/{dashboard_id}", response_model=Dashboard)
async def update_dashboard(
    dashboard_id: str,
    request: UpdateDashboardRequest,
) -> Dashboard:
    """Update a dashboard"""
    try:
        if dashboard_id not in dashboards:
            raise HTTPException(status_code=404, detail="Dashboard not found")

        dashboard = dashboards[dashboard_id]

        if request.name:
            dashboard.name = request.name
        if request.description:
            dashboard.description = request.description
        if request.layout:
            dashboard.layout = request.layout
        if request.elements:
            dashboard.elements = request.elements
        if request.refresh_interval:
            dashboard.refresh_interval = request.refresh_interval
        if request.tags:
            dashboard.tags = request.tags

        dashboards[dashboard_id] = dashboard
        logger.info(f"Updated dashboard: {dashboard_id}")

        return dashboard

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating dashboard: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{dashboard_id}", status_code=204)
async def delete_dashboard(dashboard_id: str) -> None:
    """Delete a dashboard"""
    if dashboard_id not in dashboards:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    del dashboards[dashboard_id]
    logger.info(f"Deleted dashboard: {dashboard_id}")


# KPI Endpoints
@router.post("/kpis", response_model=KPI, status_code=201)
async def create_kpi(
    name: str,
    formula_id: str,
    target_value: Optional[float] = None,
    alert_threshold: Optional[float] = None,
) -> KPI:
    """Create a KPI"""
    try:
        if formula_id not in formulas:
            raise HTTPException(status_code=404, detail="Formula not found")

        formula = formulas[formula_id]

        kpi = KPI(
            name=name,
            formula=formula,
            target_value=target_value,
            alert_threshold=alert_threshold,
        )

        kpis[kpi.kpi_id] = kpi
        logger.info(f"Created KPI: {kpi.kpi_id}")

        return kpi

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating KPI: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/kpis/{kpi_id}", response_model=KPI)
async def get_kpi(kpi_id: str) -> KPI:
    """Get a KPI by ID"""
    if kpi_id not in kpis:
        raise HTTPException(status_code=404, detail="KPI not found")
    return kpis[kpi_id]


@router.post("/kpis/{kpi_id}/evaluate")
async def evaluate_kpi(
    kpi_id: str,
    context: Dict[str, Any],
) -> Dict[str, Any]:
    """Evaluate a KPI"""
    try:
        if kpi_id not in kpis:
            raise HTTPException(status_code=404, detail="KPI not found")

        kpi = kpis[kpi_id]
        updated_kpi = await kpi_tracker.evaluate_kpi(kpi, context)
        alerts = await kpi_tracker.check_alerts(updated_kpi)

        kpis[kpi_id] = updated_kpi

        return {
            "kpi": updated_kpi.dict(),
            "alerts": [alert.dict() for alert in alerts],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error evaluating KPI: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/kpis/{kpi_id}/alerts", response_model=List[KPIAlert])
async def get_kpi_alerts(kpi_id: str) -> List[KPIAlert]:
    """Get alerts for a KPI"""
    if kpi_id not in kpis:
        raise HTTPException(status_code=404, detail="KPI not found")

    return kpi_tracker.get_alerts(kpi_id=kpi_id)


@router.get("/kpis/{kpi_id}/history")
async def get_kpi_history(
    kpi_id: str,
    limit: int = Query(50, ge=1, le=500),
) -> List[Dict[str, Any]]:
    """Get KPI history"""
    if kpi_id not in kpis:
        raise HTTPException(status_code=404, detail="KPI not found")

    history = kpi_tracker.get_history(kpi_id, limit=limit)
    return [h.dict() for h in history]


# Template Endpoints
@router.get("/templates/list", response_model=List[str])
async def list_dashboard_templates() -> List[str]:
    """List available dashboard templates"""
    return list(dashboard_builder.TEMPLATES.keys())


@router.get("/templates/{template_name}")
async def get_dashboard_template(template_name: str) -> Dict[str, Any]:
    """Get a dashboard template"""
    try:
        template = await dashboard_builder.get_template(template_name)
        return {
            "template_id": template.template_id,
            "name": template.name,
            "description": template.description,
            "category": template.category,
        }
    except Exception as e:
        logger.error(f"Error getting template: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/templates/{template_name}", response_model=Dashboard, status_code=201)
async def create_dashboard_from_template(
    template_name: str,
    name: str,
) -> Dashboard:
    """Create dashboard from template"""
    try:
        dashboard = await dashboard_builder.create_from_template(
            template_name=template_name,
            name=name,
        )
        dashboards[dashboard.dashboard_id] = dashboard
        logger.info(f"Created dashboard from template: {template_name}")
        return dashboard
    except Exception as e:
        logger.error(f"Error creating dashboard from template: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# Export Endpoints
@router.post("/{dashboard_id}/export", status_code=202)
async def export_dashboard(
    dashboard_id: str,
    request: DashboardExportRequest,
) -> Dict[str, Any]:
    """Export dashboard to specified format"""
    try:
        if dashboard_id not in dashboards:
            raise HTTPException(status_code=404, detail="Dashboard not found")

        result = {
            "dashboard_id": dashboard_id,
            "format": request.format.value,
            "status": "pending",
            "file_url": f"/exports/{dashboard_id}.{request.format.value}",
        }

        logger.info(f"Initiated export for dashboard: {dashboard_id}")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting dashboard: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# Summary Endpoint
@router.get("/summary", response_model=AnalyticsSummary)
async def get_analytics_summary() -> AnalyticsSummary:
    """Get analytics summary"""
    try:
        summary = await agent.create_analytics_summary(
            dashboards=list(dashboards.values()),
            charts=list(charts.values()),
            kpis=list(kpis.values()),
            formulas=list(formulas.values()),
        )
        return summary
    except Exception as e:
        logger.error(f"Error getting analytics summary: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


__all__ = ["router"]
