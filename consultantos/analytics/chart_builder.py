"""
Chart builder for creating interactive Plotly visualizations
Supports 12+ chart types with customization options
"""
import logging
from typing import Dict, Any, List, Optional
import json
from datetime import datetime

try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

from consultantos.models.analytics import Chart, ChartType, ChartConfig, ChartData


logger = logging.getLogger(__name__)


class ChartBuilderError(Exception):
    """Chart building error"""
    pass


class ChartBuilder:
    """
    Build interactive Plotly charts with multiple types and customization
    """

    CHART_DEFAULTS = {
        "line": {
            "marker": {"size": 6},
            "mode": "lines+markers",
        },
        "bar": {
            "orientation": "v",
        },
        "column": {
            "orientation": "v",
        },
        "pie": {
            "hole": 0,
        },
        "scatter": {
            "marker": {"size": 8},
            "mode": "markers",
        },
        "heatmap": {
            "colorscale": "Viridis",
        },
        "waterfall": {
            "orientation": "v",
        },
        "funnel": {
            "orientation": "v",
        },
        "gauge": {
            "type": "indicator",
        },
        "sankey": {
            "type": "sankey",
        },
        "treemap": {
            "type": "treemap",
        },
        "area": {
            "mode": "lines",
            "fill": "tozeroy",
        },
    }

    def __init__(self):
        """Initialize chart builder"""
        if not PLOTLY_AVAILABLE:
            raise ChartBuilderError("Plotly is not installed")

    async def build_chart(
        self,
        chart: Chart,
        data: List[Dict[str, Any]],
    ) -> str:
        """
        Build and return chart as HTML/JSON

        Args:
            chart: Chart definition
            data: Data for the chart

        Returns:
            JSON representation of chart

        Raises:
            ChartBuilderError: If chart building fails
        """
        try:
            if not data:
                raise ChartBuilderError("No data provided for chart")

            fig = self._create_figure(chart, data)
            self._apply_config(fig, chart.config)

            return fig.to_json()

        except Exception as e:
            logger.error(f"Chart building error: {str(e)}")
            raise ChartBuilderError(f"Failed to build chart: {str(e)}")

    def _create_figure(self, chart: Chart, data: List[Dict[str, Any]]) -> go.Figure:
        """Create Plotly figure based on chart type"""
        chart_type = chart.chart_type

        if chart_type == ChartType.LINE:
            return self._create_line_chart(data, chart.config)
        elif chart_type == ChartType.BAR:
            return self._create_bar_chart(data, chart.config)
        elif chart_type == ChartType.COLUMN:
            return self._create_column_chart(data, chart.config)
        elif chart_type == ChartType.PIE:
            return self._create_pie_chart(data, chart.config)
        elif chart_type == ChartType.SCATTER:
            return self._create_scatter_chart(data, chart.config)
        elif chart_type == ChartType.HEATMAP:
            return self._create_heatmap(data, chart.config)
        elif chart_type == ChartType.WATERFALL:
            return self._create_waterfall(data, chart.config)
        elif chart_type == ChartType.FUNNEL:
            return self._create_funnel(data, chart.config)
        elif chart_type == ChartType.GAUGE:
            return self._create_gauge(data, chart.config)
        elif chart_type == ChartType.SANKEY:
            return self._create_sankey(data, chart.config)
        elif chart_type == ChartType.TREEMAP:
            return self._create_treemap(data, chart.config)
        elif chart_type == ChartType.AREA:
            return self._create_area_chart(data, chart.config)
        else:
            raise ChartBuilderError(f"Unsupported chart type: {chart_type}")

    def _create_line_chart(self, data: List[Dict[str, Any]], config: ChartConfig) -> go.Figure:
        """Create line chart"""
        fig = go.Figure()

        for item in data:
            fig.add_trace(
                go.Scatter(
                    x=item.get("x", []),
                    y=item.get("y", []),
                    name=item.get("name", ""),
                    mode="lines+markers",
                    marker=dict(size=6),
                )
            )

        return fig

    def _create_bar_chart(self, data: List[Dict[str, Any]], config: ChartConfig) -> go.Figure:
        """Create horizontal bar chart"""
        fig = go.Figure()

        for item in data:
            fig.add_trace(
                go.Bar(
                    y=item.get("x", []),
                    x=item.get("y", []),
                    name=item.get("name", ""),
                    orientation="h",
                )
            )

        return fig

    def _create_column_chart(self, data: List[Dict[str, Any]], config: ChartConfig) -> go.Figure:
        """Create vertical column/bar chart"""
        fig = go.Figure()

        for item in data:
            fig.add_trace(
                go.Bar(
                    x=item.get("x", []),
                    y=item.get("y", []),
                    name=item.get("name", ""),
                )
            )

        return fig

    def _create_pie_chart(self, data: List[Dict[str, Any]], config: ChartConfig) -> go.Figure:
        """Create pie chart"""
        item = data[0] if data else {}

        fig = go.Figure(
            data=[
                go.Pie(
                    labels=item.get("labels", []),
                    values=item.get("values", []),
                    hole=0,
                )
            ]
        )

        return fig

    def _create_scatter_chart(self, data: List[Dict[str, Any]], config: ChartConfig) -> go.Figure:
        """Create scatter plot"""
        fig = go.Figure()

        for item in data:
            fig.add_trace(
                go.Scatter(
                    x=item.get("x", []),
                    y=item.get("y", []),
                    name=item.get("name", ""),
                    mode="markers",
                    marker=dict(size=8),
                )
            )

        return fig

    def _create_heatmap(self, data: List[Dict[str, Any]], config: ChartConfig) -> go.Figure:
        """Create heatmap"""
        item = data[0] if data else {}

        fig = go.Figure(
            data=[
                go.Heatmap(
                    z=item.get("z", []),
                    x=item.get("x", []),
                    y=item.get("y", []),
                    colorscale="Viridis",
                )
            ]
        )

        return fig

    def _create_waterfall(self, data: List[Dict[str, Any]], config: ChartConfig) -> go.Figure:
        """Create waterfall chart"""
        item = data[0] if data else {}

        fig = go.Figure(
            data=[
                go.Waterfall(
                    x=item.get("x", []),
                    y=item.get("y", []),
                    measure=item.get("measure", []),
                )
            ]
        )

        return fig

    def _create_funnel(self, data: List[Dict[str, Any]], config: ChartConfig) -> go.Figure:
        """Create funnel chart"""
        item = data[0] if data else {}

        fig = go.Figure(
            data=[
                go.Funnel(
                    x=item.get("x", []),
                    y=item.get("y", []),
                )
            ]
        )

        return fig

    def _create_gauge(self, data: List[Dict[str, Any]], config: ChartConfig) -> go.Figure:
        """Create gauge chart"""
        item = data[0] if data else {"value": 0}

        fig = go.Figure(
            data=[
                go.Indicator(
                    mode="gauge+number",
                    value=item.get("value", 0),
                    domain={"x": [0, 1], "y": [0, 1]},
                    gauge={
                        "axis": {"range": [item.get("min", 0), item.get("max", 100)]},
                        "bar": {"color": "darkblue"},
                        "steps": [
                            {"range": [0, 25], "color": "lightgray"},
                            {"range": [25, 50], "color": "gray"},
                            {"range": [50, 75], "color": "lightblue"},
                            {"range": [75, 100], "color": "blue"},
                        ],
                        "threshold": {
                            "line": {"color": "red", "width": 4},
                            "thickness": 0.75,
                            "value": item.get("threshold", 50),
                        },
                    },
                )
            ]
        )

        return fig

    def _create_sankey(self, data: List[Dict[str, Any]], config: ChartConfig) -> go.Figure:
        """Create Sankey diagram"""
        item = data[0] if data else {}

        fig = go.Figure(
            data=[
                go.Sankey(
                    node=dict(
                        pad=15,
                        line=dict(color="black", width=0.5),
                        label=item.get("labels", []),
                        color=item.get("colors", []),
                    ),
                    link=dict(
                        source=item.get("source", []),
                        target=item.get("target", []),
                        value=item.get("value", []),
                    ),
                )
            ]
        )

        return fig

    def _create_treemap(self, data: List[Dict[str, Any]], config: ChartConfig) -> go.Figure:
        """Create treemap"""
        item = data[0] if data else {}

        fig = go.Figure(
            data=[
                go.Treemap(
                    labels=item.get("labels", []),
                    parents=item.get("parents", []),
                    values=item.get("values", []),
                )
            ]
        )

        return fig

    def _create_area_chart(self, data: List[Dict[str, Any]], config: ChartConfig) -> go.Figure:
        """Create area chart"""
        fig = go.Figure()

        for item in data:
            fig.add_trace(
                go.Scatter(
                    x=item.get("x", []),
                    y=item.get("y", []),
                    name=item.get("name", ""),
                    mode="lines",
                    fill="tozeroy",
                )
            )

        return fig

    def _apply_config(self, fig: go.Figure, config: ChartConfig) -> None:
        """Apply configuration to figure"""
        layout_updates = {}

        if config.title:
            layout_updates["title"] = config.title

        if config.x_axis_label or config.y_axis_label:
            layout_updates["xaxis"] = {"title": config.x_axis_label or ""}
            layout_updates["yaxis"] = {"title": config.y_axis_label or ""}

        if not config.show_legend:
            layout_updates["showlegend"] = False

        if not config.show_grid:
            layout_updates["xaxis"] = layout_updates.get("xaxis", {})
            layout_updates["xaxis"]["showgrid"] = False
            layout_updates["yaxis"] = layout_updates.get("yaxis", {})
            layout_updates["yaxis"]["showgrid"] = False

        if config.height:
            layout_updates["height"] = config.height

        if config.width:
            layout_updates["width"] = config.width

        if config.responsive:
            layout_updates["autosize"] = True

        if config.custom_options:
            layout_updates.update(config.custom_options)

        fig.update_layout(**layout_updates)

    def get_chart_html(
        self,
        chart_json: str,
        include_plotly_js: bool = True,
    ) -> str:
        """Convert chart JSON to standalone HTML"""
        try:
            chart_dict = json.loads(chart_json)
            fig = go.Figure(chart_dict)
            return fig.to_html(include_plotlyjs=include_plotly_js)
        except Exception as e:
            logger.error(f"Error generating HTML: {str(e)}")
            raise ChartBuilderError(f"Failed to generate HTML: {str(e)}")


# Helper functions for common chart patterns
async def create_time_series_chart(
    data: List[Dict[str, Any]],
    title: str = "Time Series",
) -> str:
    """Create time series line chart"""
    builder = ChartBuilder()
    chart = Chart(
        name=title,
        chart_type=ChartType.LINE,
        data_source=None,  # type: ignore
        config=ChartConfig(
            title=title,
            show_legend=True,
            show_grid=True,
        ),
    )
    return await builder.build_chart(chart, data)


async def create_comparison_chart(
    data: List[Dict[str, Any]],
    title: str = "Comparison",
) -> str:
    """Create bar comparison chart"""
    builder = ChartBuilder()
    chart = Chart(
        name=title,
        chart_type=ChartType.COLUMN,
        data_source=None,  # type: ignore
        config=ChartConfig(
            title=title,
            show_legend=True,
        ),
    )
    return await builder.build_chart(chart, data)


async def create_distribution_chart(
    data: List[Dict[str, Any]],
    title: str = "Distribution",
) -> str:
    """Create scatter/distribution chart"""
    builder = ChartBuilder()
    chart = Chart(
        name=title,
        chart_type=ChartType.SCATTER,
        data_source=None,  # type: ignore
        config=ChartConfig(
            title=title,
            show_legend=True,
        ),
    )
    return await builder.build_chart(chart, data)


__all__ = [
    "ChartBuilder",
    "ChartBuilderError",
    "create_time_series_chart",
    "create_comparison_chart",
    "create_distribution_chart",
]
