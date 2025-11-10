"""
Analytics Builder Agent
Orchestrates formula creation, chart building, and dashboard design
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from consultantos.agents.base_agent import BaseAgent
from consultantos.models.analytics import (
    Formula,
    Chart,
    ChartType,
    Dashboard,
    KPI,
    CreateFormulaRequest,
    CreateChartRequest,
    CreateDashboardRequest,
    DashboardExportRequest,
    DashboardResponse,
    AnalyticsSummary,
)
from consultantos.analytics.formula_parser import FormulaParser, FORMULA_TEMPLATES
from consultantos.analytics.chart_builder import ChartBuilder
from consultantos.analytics.dashboard_builder import DashboardBuilder
from consultantos.analytics.kpi_tracker import KPITracker, AlertEngine


logger = logging.getLogger(__name__)


class AnalyticsBuilderAgent(BaseAgent):
    """
    Agent for building custom analytics, formulas, charts, and dashboards
    """

    def __init__(self, timeout: int = 120):
        """
        Initialize analytics builder agent

        Args:
            timeout: Agent timeout in seconds
        """
        super().__init__(name="AnalyticsBuilderAgent", timeout=timeout)
        self.formula_parser = FormulaParser(safe_mode=True)
        self.chart_builder = ChartBuilder()
        self.dashboard_builder = DashboardBuilder()
        self.kpi_tracker = KPITracker()
        self.alert_engine = AlertEngine()

    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute analytics builder request

        Args:
            request: Request containing action and parameters

        Returns:
            Result with created analytics components
        """
        action = request.get("action")

        if action == "create_formula":
            return await self._create_formula(request)
        elif action == "create_chart":
            return await self._create_chart(request)
        elif action == "create_dashboard":
            return await self._create_dashboard(request)
        elif action == "evaluate_kpi":
            return await self._evaluate_kpi(request)
        elif action == "export_dashboard":
            return await self._export_dashboard(request)
        elif action == "get_template":
            return await self._get_template(request)
        else:
            return {"error": f"Unknown action: {action}"}

    async def _execute_internal(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Internal execute implementation"""
        return await self.execute(request)

    async def _create_formula(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Create a custom formula"""
        try:
            formula_req = CreateFormulaRequest(**request.get("formula", {}))

            # Extract variables from expression
            variables = self.formula_parser.extract_variables(formula_req.expression)

            formula = Formula(
                name=formula_req.name,
                description=formula_req.description,
                expression=formula_req.expression,
                variables=variables,
                category=formula_req.category,
                examples=formula_req.examples,
            )

            logger.info(f"Created formula: {formula.formula_id}")

            return {
                "status": "success",
                "formula": formula.dict(),
                "message": f"Formula '{formula.name}' created successfully",
            }

        except Exception as e:
            logger.error(f"Error creating formula: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def _create_chart(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Create a chart"""
        try:
            chart_req = CreateChartRequest(**request.get("chart", {}))

            chart = Chart(
                name=chart_req.name,
                description=chart_req.description,
                chart_type=chart_req.chart_type,
                data_source=chart_req.data_source,
                config=chart_req.config,
            )

            logger.info(f"Created chart: {chart.chart_id}")

            return {
                "status": "success",
                "chart": chart.dict(use_enum_values=False),
                "message": f"Chart '{chart.name}' created successfully",
            }

        except Exception as e:
            logger.error(f"Error creating chart: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def _create_dashboard(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Create a dashboard"""
        try:
            dashboard_req = CreateDashboardRequest(**request.get("dashboard", {}))

            dashboard = await self.dashboard_builder.create_dashboard(
                name=dashboard_req.name,
                description=dashboard_req.description,
                layout=dashboard_req.layout,
                elements=dashboard_req.elements,
                refresh_interval=dashboard_req.refresh_interval,
                tags=dashboard_req.tags,
                created_by=request.get("created_by"),
            )

            logger.info(f"Created dashboard: {dashboard.dashboard_id}")

            return {
                "status": "success",
                "dashboard": dashboard.dict(use_enum_values=False),
                "message": f"Dashboard '{dashboard.name}' created successfully",
            }

        except Exception as e:
            logger.error(f"Error creating dashboard: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def _evaluate_kpi(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a KPI"""
        try:
            kpi_data = request.get("kpi", {})
            context = request.get("context", {})

            kpi = KPI(**kpi_data)
            updated_kpi = await self.kpi_tracker.evaluate_kpi(kpi, context)

            # Check for alerts
            alerts = await self.kpi_tracker.check_alerts(updated_kpi)

            # Get trend
            trend = await self.kpi_tracker.get_trend(updated_kpi.kpi_id)

            logger.info(f"Evaluated KPI: {updated_kpi.kpi_id}")

            return {
                "status": "success",
                "kpi": updated_kpi.dict(),
                "alerts": [alert.dict() for alert in alerts],
                "trend": trend,
                "message": f"KPI '{updated_kpi.name}' evaluated successfully",
            }

        except Exception as e:
            logger.error(f"Error evaluating KPI: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def _export_dashboard(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Export dashboard"""
        try:
            export_req = DashboardExportRequest(**request.get("export", {}))

            # For now, return info about export
            # In production, would generate actual file
            export_result = {
                "dashboard_id": export_req.dashboard_id,
                "format": export_req.format.value,
                "file_url": f"/exports/{export_req.dashboard_id}.{export_req.format.value}",
                "created_at": datetime.utcnow().isoformat(),
            }

            logger.info(f"Exported dashboard: {export_req.dashboard_id}")

            return {
                "status": "success",
                "export": export_result,
                "message": f"Dashboard exported as {export_req.format.value}",
            }

        except Exception as e:
            logger.error(f"Error exporting dashboard: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def _get_template(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Get dashboard template"""
        try:
            template_name = request.get("template_name")

            template = await self.dashboard_builder.get_template(template_name)

            logger.info(f"Retrieved template: {template_name}")

            return {
                "status": "success",
                "template": {
                    "name": template.name,
                    "description": template.description,
                    "category": template.category,
                    "dashboard": template.dashboard.dict(use_enum_values=False),
                },
                "message": f"Template '{template_name}' retrieved successfully",
            }

        except Exception as e:
            logger.error(f"Error getting template: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def create_analytics_summary(
        self,
        dashboards: List[Dashboard],
        charts: List[Chart],
        kpis: List[KPI],
        formulas: List[Formula],
    ) -> AnalyticsSummary:
        """
        Create analytics summary

        Args:
            dashboards: List of dashboards
            charts: List of charts
            kpis: List of KPIs
            formulas: List of formulas

        Returns:
            Analytics summary
        """
        # Get active alerts
        all_alerts = []
        for kpi in kpis:
            alerts = await self.kpi_tracker.check_alerts(kpi)
            all_alerts.extend(alerts)

        summary = AnalyticsSummary(
            total_dashboards=len(dashboards),
            total_charts=len(charts),
            total_kpis=len(kpis),
            total_formulas=len(formulas),
            active_alerts=len([a for a in all_alerts if not a.acknowledged]),
            last_updated=datetime.utcnow(),
            top_charts=charts[:5] if charts else [],
            recent_alerts=all_alerts[:10] if all_alerts else [],
        )

        return summary

    @staticmethod
    def get_formula_templates() -> Dict[str, Dict[str, Any]]:
        """Get available formula templates"""
        return FORMULA_TEMPLATES


__all__ = [
    "AnalyticsBuilderAgent",
]
