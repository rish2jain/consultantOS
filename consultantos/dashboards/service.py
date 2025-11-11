"""Dashboard service for real-time data management and updates"""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import WebSocket

from consultantos.dashboards.models import (
    Alert,
    AlertSeverity,
    DashboardSection,
    DashboardUpdate,
    LiveDashboard,
    Metric,
    ScenarioAssumptions,
    ScenarioForecast,
    SectionType,
    TrendDirection,
)
from consultantos.dashboards.templates import get_template
from consultantos.monitoring import get_logger
from consultantos.orchestrator.orchestrator import AnalysisOrchestrator

logger = get_logger(__name__)


class DashboardService:
    """Service for managing live dashboards with real-time updates"""

    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.dashboards: Dict[str, LiveDashboard] = {}

    async def create_dashboard(
        self,
        company: str,
        industry: str,
        template_id: str,
        user_id: str,
        frameworks: Optional[List[str]] = None,
        depth: str = "standard"
    ) -> LiveDashboard:
        """Create a new live dashboard from template"""
        template = get_template(template_id)
        dashboard_id = f"dash_{company.lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}"

        # Initialize sections from template
        sections = []
        for idx, section_config in enumerate(template.sections):
            section = DashboardSection(
                id=f"{dashboard_id}_section_{idx}",
                title=section_config["title"],
                type=SectionType(section_config["type"]),
                data={},
                last_updated=datetime.utcnow(),
                refresh_interval=template.default_refresh_interval,
                order=section_config.get("order", idx),
                size=section_config.get("size", "medium"),
                config=section_config.get("config", {})
            )
            sections.append(section)

        dashboard = LiveDashboard(
            id=dashboard_id,
            company=company,
            industry=industry,
            template=template_id,
            created_at=datetime.utcnow(),
            last_updated=datetime.utcnow(),
            user_id=user_id,
            sections=sections,
            alerts=[],
            metrics=[],
            refresh_enabled=True,
            auto_refresh_interval=template.default_refresh_interval,
            metadata={
                "frameworks": frameworks or [],
                "depth": depth
            }
        )

        # Store dashboard
        self.dashboards[dashboard_id] = dashboard

        # Perform initial data load
        await self._populate_dashboard_data(dashboard)

        logger.info(
            "Dashboard created",
            extra={
                "dashboard_id": dashboard_id,
                "company": company,
                "template": template_id,
                "user_id": user_id
            }
        )

        return dashboard

    async def get_dashboard(self, dashboard_id: str) -> Optional[LiveDashboard]:
        """Get dashboard by ID"""
        return self.dashboards.get(dashboard_id)

    async def refresh_dashboard(self, dashboard_id: str) -> LiveDashboard:
        """Force refresh of dashboard data"""
        dashboard = self.dashboards.get(dashboard_id)
        if not dashboard:
            raise ValueError(f"Dashboard {dashboard_id} not found")

        await self._populate_dashboard_data(dashboard)
        dashboard.last_updated = datetime.utcnow()

        # Notify connected clients
        await self._broadcast_update(
            dashboard_id,
            DashboardUpdate(
                dashboard_id=dashboard_id,
                update_type="full",
                timestamp=datetime.utcnow(),
                data=dashboard.model_dump()
            )
        )

        logger.info("Dashboard refreshed", extra={"dashboard_id": dashboard_id})
        return dashboard

    async def subscribe_to_updates(
        self,
        dashboard_id: str,
        websocket: WebSocket
    ):
        """Subscribe to real-time dashboard updates via WebSocket"""
        await websocket.accept()

        # Add connection to active connections
        if dashboard_id not in self.active_connections:
            self.active_connections[dashboard_id] = []
        self.active_connections[dashboard_id].append(websocket)

        logger.info(
            "WebSocket connected",
            extra={"dashboard_id": dashboard_id, "total_connections": len(self.active_connections[dashboard_id])}
        )

        try:
            # Send initial dashboard state
            dashboard = await self.get_dashboard(dashboard_id)
            if dashboard:
                await websocket.send_json({
                    "type": "initial",
                    "data": dashboard.model_dump()
                })

            # Keep connection alive and send periodic updates
            while True:
                # Check for updates every 5 seconds
                await asyncio.sleep(5)

                # Refresh dashboard if auto-refresh is enabled
                dashboard = await self.get_dashboard(dashboard_id)
                if dashboard and dashboard.refresh_enabled:
                    time_since_update = (datetime.utcnow() - dashboard.last_updated).seconds
                    if time_since_update >= dashboard.auto_refresh_interval:
                        await self.refresh_dashboard(dashboard_id)

        except Exception as e:
            logger.error(
                "WebSocket error",
                extra={"dashboard_id": dashboard_id, "error": str(e)}
            )
        finally:
            # Remove connection on disconnect
            if dashboard_id in self.active_connections:
                self.active_connections[dashboard_id].remove(websocket)
                if not self.active_connections[dashboard_id]:
                    del self.active_connections[dashboard_id]

            logger.info("WebSocket disconnected", extra={"dashboard_id": dashboard_id})

    async def run_scenario(
        self,
        company: str,
        industry: str,
        assumptions: ScenarioAssumptions,
        forecast_period: int = 12
    ) -> ScenarioForecast:
        """Run scenario planning analysis"""
        scenario_id = f"scenario_{uuid.uuid4().hex[:8]}"

        # Simplified scenario modeling (in production, use more sophisticated models)
        base_revenue = 25000000  # Example baseline
        revenue_forecast = []
        profit_forecast = []
        market_share_forecast = []

        for month in range(forecast_period):
            # Apply growth rate
            growth_factor = (1 + assumptions.market_growth_rate / 100) ** (month / 12)

            # Apply price change
            price_factor = 1 + (assumptions.price_change / 100)

            # Calculate revenue
            revenue = base_revenue * growth_factor * price_factor
            revenue_forecast.append(revenue)

            # Calculate profit (simplified)
            cost_factor = 1 + (assumptions.cost_change / 100)
            profit_margin = 0.15 / cost_factor  # Base 15% margin adjusted for costs
            profit = revenue * profit_margin
            profit_forecast.append(profit)

            # Calculate market share (simplified)
            base_share = assumptions.market_share_target or 20.0
            share_growth = assumptions.market_growth_rate / 12  # Monthly growth
            market_share = min(base_share + (share_growth * month), 100.0)
            market_share_forecast.append(market_share)

        # Calculate risk score based on assumptions
        risk_factors = []
        if assumptions.competitor_entry:
            risk_factors.append(0.3)
        if assumptions.regulatory_change:
            risk_factors.append(0.25)
        if abs(assumptions.price_change) > 15:
            risk_factors.append(0.2)
        if assumptions.market_growth_rate < 0:
            risk_factors.append(0.4)

        risk_score = min(sum(risk_factors), 1.0) if risk_factors else 0.1

        # Generate insights
        insights = []
        if assumptions.price_change < 0:
            insights.append("Price reduction expected to drive volume growth")
        if assumptions.market_growth_rate > 10:
            insights.append("High market growth creates expansion opportunities")
        if assumptions.competitor_entry:
            insights.append("Competitor entry may pressure market share and margins")
        if risk_score > 0.5:
            insights.append("High-risk scenario - consider mitigation strategies")

        forecast = ScenarioForecast(
            scenario_id=scenario_id,
            company=company,
            assumptions=assumptions,
            forecast_period=forecast_period,
            revenue_forecast=revenue_forecast,
            profit_forecast=profit_forecast,
            market_share_forecast=market_share_forecast,
            risk_score=risk_score,
            confidence=0.75 - (risk_score * 0.2),  # Higher risk = lower confidence
            key_insights=insights,
            created_at=datetime.utcnow()
        )

        logger.info(
            "Scenario forecast generated",
            extra={
                "scenario_id": scenario_id,
                "company": company,
                "risk_score": risk_score
            }
        )

        return forecast

    async def _populate_dashboard_data(self, dashboard: LiveDashboard):
        """Populate dashboard with fresh data from agents"""
        try:
            # Run analysis to get fresh data
            orchestrator = AnalysisOrchestrator()
            result = await orchestrator.orchestrate_analysis(
                company=dashboard.company,
                industry=dashboard.industry,
                frameworks=dashboard.metadata.get("frameworks", []),
                depth=dashboard.metadata.get("depth", "standard")
            )

            # Extract metrics
            dashboard.metrics = await self._extract_metrics(result)

            # Generate alerts
            dashboard.alerts = await self._generate_alerts(result)

            # Populate sections based on template
            for section in dashboard.sections:
                section.data = await self._populate_section_data(section, result)
                section.last_updated = datetime.utcnow()

        except Exception as e:
            logger.error(
                "Error populating dashboard data",
                extra={"dashboard_id": dashboard.id, "error": str(e)}
            )
            # Don't fail - partial data is better than no data
            pass

    async def _extract_metrics(self, analysis_result: Dict[str, Any]) -> List[Metric]:
        """Extract key metrics from analysis result"""
        metrics = []

        # Revenue metric (from financial data)
        if "financial" in analysis_result:
            financial = analysis_result["financial"]
            if "revenue" in financial:
                metrics.append(Metric(
                    id="metric_revenue",
                    name="Revenue",
                    value=financial["revenue"],
                    unit="$",
                    change=financial.get("revenue_growth", 0.0),
                    trend=TrendDirection.UP if financial.get("revenue_growth", 0) > 0 else TrendDirection.DOWN,
                    confidence=0.85,
                    last_updated=datetime.utcnow(),
                    source="financial_agent"
                ))

        # Market share metric
        if "market" in analysis_result:
            market = analysis_result["market"]
            if "market_share" in market:
                metrics.append(Metric(
                    id="metric_market_share",
                    name="Market Share",
                    value=market["market_share"],
                    unit="%",
                    change=market.get("market_share_change", 0.0),
                    trend=TrendDirection.UP if market.get("market_share_change", 0) > 0 else TrendDirection.DOWN,
                    confidence=0.75,
                    last_updated=datetime.utcnow(),
                    source="market_agent"
                ))

        return metrics

    async def _generate_alerts(self, analysis_result: Dict[str, Any]) -> List[Alert]:
        """Generate alerts from analysis result"""
        alerts = []

        # Check for competitive threats in Porter's analysis
        if "frameworks" in analysis_result and "porter" in analysis_result["frameworks"]:
            porter = analysis_result["frameworks"]["porter"]
            if porter.get("competitive_rivalry", 0) > 0.7:
                alerts.append(Alert(
                    id=f"alert_{uuid.uuid4().hex[:8]}",
                    title="High Competitive Rivalry",
                    message="Porter's analysis indicates intense competitive pressure",
                    severity=AlertSeverity.WARNING,
                    category="competitive",
                    source="framework_agent",
                    timestamp=datetime.utcnow()
                ))

        # Check for threats in SWOT
        if "frameworks" in analysis_result and "swot" in analysis_result["frameworks"]:
            swot = analysis_result["frameworks"]["swot"]
            if swot.get("threats") and len(swot["threats"]) > 3:
                alerts.append(Alert(
                    id=f"alert_{uuid.uuid4().hex[:8]}",
                    title="Multiple Strategic Threats",
                    message=f"SWOT analysis identified {len(swot['threats'])} threats",
                    severity=AlertSeverity.WARNING,
                    category="strategic",
                    source="framework_agent",
                    timestamp=datetime.utcnow()
                ))

        return alerts

    async def _populate_section_data(
        self,
        section: DashboardSection,
        analysis_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Populate individual section with data"""
        # Implementation depends on section type
        # This is a simplified version - expand based on needs

        if section.type == SectionType.CHART:
            return {
                "chart_type": section.config.get("chart_type", "line"),
                "data": [],  # Populate from analysis_result
                "labels": {}
            }
        elif section.type == SectionType.TABLE:
            return {
                "columns": section.config.get("columns", []),
                "rows": []  # Populate from analysis_result
            }
        elif section.type == SectionType.METRIC:
            return {
                "metrics": []  # Populate from extracted metrics
            }
        elif section.type == SectionType.ALERT:
            return {
                "alerts": []  # Populate from generated alerts
            }
        else:
            return {}

    async def _broadcast_update(
        self,
        dashboard_id: str,
        update: DashboardUpdate
    ):
        """Broadcast update to all connected clients"""
        if dashboard_id not in self.active_connections:
            return

        dead_connections = []
        for websocket in self.active_connections[dashboard_id]:
            try:
                await websocket.send_json(update.model_dump())
            except Exception as e:
                logger.error(
                    "Failed to send update to client",
                    extra={"dashboard_id": dashboard_id, "error": str(e)}
                )
                dead_connections.append(websocket)

        # Clean up dead connections
        for websocket in dead_connections:
            self.active_connections[dashboard_id].remove(websocket)


# Singleton instance
_dashboard_service = DashboardService()


def get_dashboard_service() -> DashboardService:
    """Get singleton dashboard service instance"""
    return _dashboard_service
