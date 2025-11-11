"""
Visualization Agent for managing charts and visualizations
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from consultantos.agents.base_agent import BaseAgent
from consultantos.visualizations import (
    create_porter_radar_figure,
    create_swot_matrix_figure,
    figure_to_json,
    get_cached_figure,
    set_cached_figure,
)
import logging
import json
import hashlib

logger = logging.getLogger(__name__)


class VisualizationCreateRequest(BaseModel):
    chart_type: str = Field(..., description="Chart type (porter, swot, bar, line, pie, etc.).")
    data: Dict[str, Any] = Field(..., description="Chart data.")
    report_id: Optional[str] = Field(None, description="Associated report ID for caching.")
    title: Optional[str] = Field(None, description="Chart title.")
    config: Optional[Dict[str, Any]] = Field(None, description="Chart configuration options.")


class VisualizationListRequest(BaseModel):
    chart_type: Optional[str] = Field(None, description="Filter by chart type.")
    report_id: Optional[str] = Field(None, description="Filter by report ID.")
    limit: int = Field(50, ge=1, le=100, description="Maximum number of charts to return.")


class VisualizationResponse(BaseModel):
    charts: List[Dict[str, Any]] = Field(default_factory=list, description="List of charts.")
    chart: Optional[Dict[str, Any]] = Field(None, description="Single chart (for get/create).")
    figure: Optional[Dict[str, Any]] = Field(None, description="Chart figure JSON.")
    cached: bool = Field(False, description="Whether the chart was retrieved from cache.")
    message: Optional[str] = Field(None, description="Confirmation message for actions.")


class VisualizationAgent(BaseAgent):
    """Agent for managing charts and visualizations"""

    def __init__(self, timeout: int = 60):
        super().__init__(name="VisualizationAgent", timeout=timeout)

    async def _execute_internal(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        action_type = input_data.get("action_type", "create")

        if action_type == "create":
            request = VisualizationCreateRequest(**input_data)
            figure, cached = await self._create_visualization(
                chart_type=request.chart_type,
                data=request.data,
                report_id=request.report_id,
                title=request.title,
                config=request.config
            )
            return {
                "success": True,
                "data": VisualizationResponse(
                    figure=figure,
                    cached=cached,
                    message="Visualization created successfully."
                ).model_dump(),
                "error": None
            }

        elif action_type == "list":
            request = VisualizationListRequest(**input_data)
            charts = await self._list_visualizations(
                chart_type=request.chart_type,
                report_id=request.report_id,
                limit=request.limit
            )
            return {
                "success": True,
                "data": VisualizationResponse(charts=charts).model_dump(),
                "error": None
            }

        elif action_type == "get":
            chart_id = input_data.get("chart_id")
            if not chart_id:
                raise ValueError("chart_id is required for get action.")
            chart = await self._get_visualization(chart_id)
            return {
                "success": True,
                "data": VisualizationResponse(chart=chart).model_dump(),
                "error": None
            }

        else:
            raise ValueError(f"Unsupported action type: {action_type}")

    async def _create_visualization(
        self,
        chart_type: str,
        data: Dict[str, Any],
        report_id: Optional[str],
        title: Optional[str],
        config: Optional[Dict[str, Any]]
    ) -> tuple[Dict[str, Any], bool]:
        """Create a visualization"""
        try:
            # Generate cache key with data hash to prevent stale visuals
            data_hash = hashlib.md5(
                json.dumps(data, sort_keys=True).encode('utf-8')
            ).hexdigest()[:12]  # Use first 12 chars of hash
            
            cache_key = None
            if report_id:
                cache_key = f"{chart_type}:{report_id}:{data_hash}"
            
            if cache_key:
                cached = get_cached_figure(cache_key)
                if cached:
                    return cached, True

            # Create figure based on chart type
            if chart_type == "porter":
                from consultantos.models import PortersFiveForces
                porter_data = PortersFiveForces(**data)
                figure = create_porter_radar_figure(porter_data)
            elif chart_type == "swot":
                from consultantos.models import SWOTAnalysis
                swot_data = SWOTAnalysis(**data)
                figure = create_swot_matrix_figure(swot_data)
            else:
                # Generic chart creation (placeholder for other types)
                figure = self._create_generic_chart(chart_type, data, title, config)

            figure_json = figure_to_json(figure)

            # Cache if report_id provided (with TTL to expire stale entries)
            if cache_key:
                # Set cache with 24 hour TTL (86400 seconds)
                set_cached_figure(cache_key, figure_json, ttl=86400)

            return figure_json, False
        except Exception as e:
            logger.error(f"Failed to create visualization: {e}")
            raise

    def _create_generic_chart(
        self,
        chart_type: str,
        data: Dict[str, Any],
        title: Optional[str],
        config: Optional[Dict[str, Any]]
    ) -> Any:
        """Create a generic chart (placeholder implementation)"""
        # This would integrate with plotly or other charting libraries
        # For now, return a simple placeholder
        import plotly.graph_objects as go

        if chart_type == "bar":
            fig = go.Figure(data=[go.Bar(x=data.get("x", []), y=data.get("y", []))])
        elif chart_type == "line":
            fig = go.Figure(data=[go.Scatter(x=data.get("x", []), y=data.get("y", []), mode='lines+markers')])
        elif chart_type == "pie":
            fig = go.Figure(data=[go.Pie(labels=data.get("labels", []), values=data.get("values", []))])
        else:
            # Default to bar chart
            fig = go.Figure(data=[go.Bar(x=data.get("x", []), y=data.get("y", []))])

        if title:
            fig.update_layout(title=title)

        if config:
            fig.update_layout(**config)

        return fig

    async def _list_visualizations(
        self,
        chart_type: Optional[str],
        report_id: Optional[str],
        limit: int
    ) -> List[Dict[str, Any]]:
        """List visualizations (placeholder - would query database in production)"""
        # In production, this would query a database of saved charts
        # For now, return empty list
        return []

    async def _get_visualization(self, chart_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific visualization (placeholder)"""
        # In production, this would query database
        return None

