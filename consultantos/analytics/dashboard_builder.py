"""
Dashboard builder for creating interactive analytics dashboards
Supports grid layout, custom templates, and responsive design
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from consultantos.models.analytics import (
    Dashboard,
    DashboardElement,
    DashboardPosition,
    DashboardTemplate,
    DashboardLayout,
    Chart,
    KPI,
)


logger = logging.getLogger(__name__)


class DashboardBuilderError(Exception):
    """Dashboard building error"""
    pass


class DashboardBuilder:
    """
    Build interactive dashboards with custom layouts and templates
    """

    # Pre-built templates
    TEMPLATES = {
        "executive": {
            "name": "Executive Dashboard",
            "description": "High-level business metrics for executives",
            "layout": DashboardLayout.GRID,
            "elements": [],
            "category": "executive",
        },
        "sales": {
            "name": "Sales Dashboard",
            "description": "Sales metrics and pipeline tracking",
            "layout": DashboardLayout.GRID,
            "elements": [],
            "category": "sales",
        },
        "finance": {
            "name": "Finance Dashboard",
            "description": "Financial metrics and budget tracking",
            "layout": DashboardLayout.GRID,
            "elements": [],
            "category": "finance",
        },
        "marketing": {
            "name": "Marketing Dashboard",
            "description": "Marketing campaigns and ROI metrics",
            "layout": DashboardLayout.GRID,
            "elements": [],
            "category": "marketing",
        },
        "operations": {
            "name": "Operations Dashboard",
            "description": "Operational metrics and efficiency",
            "layout": DashboardLayout.GRID,
            "elements": [],
            "category": "operations",
        },
    }

    def __init__(self):
        """Initialize dashboard builder"""
        pass

    async def create_dashboard(
        self,
        name: str,
        description: Optional[str] = None,
        layout: DashboardLayout = DashboardLayout.GRID,
        elements: Optional[List[DashboardElement]] = None,
        refresh_interval: int = 300,
        tags: Optional[List[str]] = None,
        created_by: Optional[str] = None,
    ) -> Dashboard:
        """
        Create a new dashboard

        Args:
            name: Dashboard name
            description: Dashboard description
            layout: Layout type (grid, flex, custom)
            elements: Dashboard elements (charts, KPIs, etc.)
            refresh_interval: Auto-refresh interval in seconds
            tags: Dashboard tags
            created_by: User who created dashboard

        Returns:
            Dashboard object
        """
        try:
            dashboard = Dashboard(
                name=name,
                description=description,
                layout=layout,
                elements=elements or [],
                refresh_interval=refresh_interval,
                tags=tags or [],
                created_by=created_by,
            )

            logger.info(f"Created dashboard: {dashboard.dashboard_id}")
            return dashboard

        except Exception as e:
            logger.error(f"Error creating dashboard: {str(e)}")
            raise DashboardBuilderError(f"Failed to create dashboard: {str(e)}")

    async def add_element(
        self,
        dashboard: Dashboard,
        element: DashboardElement,
    ) -> Dashboard:
        """
        Add element to dashboard

        Args:
            dashboard: Dashboard object
            element: Element to add

        Returns:
            Updated dashboard
        """
        dashboard.elements.append(element)
        dashboard.updated_at = datetime.utcnow()

        if element.chart_id:
            if element.chart_id not in dashboard.charts:
                dashboard.charts.append(element.chart_id)

        if element.kpi_id:
            if element.kpi_id not in dashboard.kpis:
                dashboard.kpis.append(element.kpi_id)

        return dashboard

    async def remove_element(
        self,
        dashboard: Dashboard,
        element_id: str,
    ) -> Dashboard:
        """
        Remove element from dashboard

        Args:
            dashboard: Dashboard object
            element_id: Element ID to remove

        Returns:
            Updated dashboard
        """
        dashboard.elements = [
            e for e in dashboard.elements if e.element_id != element_id
        ]
        dashboard.updated_at = datetime.utcnow()
        return dashboard

    async def update_element_position(
        self,
        dashboard: Dashboard,
        element_id: str,
        position: DashboardPosition,
    ) -> Dashboard:
        """
        Update element position in dashboard

        Args:
            dashboard: Dashboard object
            element_id: Element ID
            position: New position

        Returns:
            Updated dashboard
        """
        for element in dashboard.elements:
            if element.element_id == element_id:
                element.position = position
                break

        dashboard.updated_at = datetime.utcnow()
        return dashboard

    async def reorder_elements(
        self,
        dashboard: Dashboard,
        element_ids: List[str],
    ) -> Dashboard:
        """
        Reorder dashboard elements

        Args:
            dashboard: Dashboard object
            element_ids: List of element IDs in desired order

        Returns:
            Updated dashboard
        """
        element_map = {e.element_id: e for e in dashboard.elements}
        dashboard.elements = [element_map[id] for id in element_ids if id in element_map]

        for i, element in enumerate(dashboard.elements):
            element.order = i

        dashboard.updated_at = datetime.utcnow()
        return dashboard

    async def get_template(
        self,
        template_name: str,
    ) -> DashboardTemplate:
        """
        Get pre-built template

        Args:
            template_name: Template name

        Returns:
            Dashboard template

        Raises:
            DashboardBuilderError: If template not found
        """
        if template_name not in self.TEMPLATES:
            raise DashboardBuilderError(f"Template not found: {template_name}")

        template_data = self.TEMPLATES[template_name]

        dashboard = Dashboard(
            name=template_data["name"],
            description=template_data["description"],
            layout=template_data["layout"],
            elements=template_data["elements"],
            is_template=True,
        )

        return DashboardTemplate(
            name=template_data["name"],
            description=template_data["description"],
            category=template_data["category"],
            dashboard=dashboard,
        )

    async def create_from_template(
        self,
        template_name: str,
        name: str,
        created_by: Optional[str] = None,
    ) -> Dashboard:
        """
        Create dashboard from template

        Args:
            template_name: Template name
            name: New dashboard name
            created_by: User who created dashboard

        Returns:
            New dashboard based on template
        """
        template = await self.get_template(template_name)

        dashboard = Dashboard(
            name=name,
            description=template.description,
            layout=template.dashboard.layout,
            elements=template.dashboard.elements.copy(),
            refresh_interval=template.dashboard.refresh_interval,
            created_by=created_by,
        )

        return dashboard

    async def export_as_json(self, dashboard: Dashboard) -> str:
        """Export dashboard as JSON"""
        return dashboard.json(indent=2)

    async def import_from_json(self, json_str: str) -> Dashboard:
        """Import dashboard from JSON"""
        return Dashboard.parse_raw(json_str)

    def validate_layout(
        self,
        dashboard: Dashboard,
        grid_cols: int = 12,
    ) -> bool:
        """
        Validate dashboard layout grid

        Args:
            dashboard: Dashboard object
            grid_cols: Number of grid columns

        Returns:
            True if layout is valid
        """
        if dashboard.layout != DashboardLayout.GRID:
            return True

        # Check for overlapping elements
        for i, element1 in enumerate(dashboard.elements):
            for element2 in dashboard.elements[i + 1 :]:
                if self._elements_overlap(element1, element2, grid_cols):
                    logger.warning(f"Elements overlap: {element1.element_id} and {element2.element_id}")
                    return False

        return True

    def _elements_overlap(
        self,
        elem1: DashboardElement,
        elem2: DashboardElement,
        grid_cols: int,
    ) -> bool:
        """Check if two elements overlap"""
        x1_start = elem1.position.x
        x1_end = elem1.position.x + elem1.position.width
        y1_start = elem1.position.y
        y1_end = elem1.position.y + elem1.position.height

        x2_start = elem2.position.x
        x2_end = elem2.position.x + elem2.position.width
        y2_start = elem2.position.y
        y2_end = elem2.position.y + elem2.position.height

        x_overlap = x1_start < x2_end and x1_end > x2_start
        y_overlap = y1_start < y2_end and y1_end > y2_start

        return x_overlap and y_overlap

    async def get_dashboard_html(
        self,
        dashboard: Dashboard,
        charts_html: Dict[str, str],
    ) -> str:
        """
        Generate dashboard HTML

        Args:
            dashboard: Dashboard object
            charts_html: Map of chart_id to HTML

        Returns:
            Dashboard HTML
        """
        # This is a simplified version
        # In production, would use template engine like Jinja2
        html = f"""
        <html>
        <head>
            <title>{dashboard.name}</title>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .dashboard {{ padding: 20px; }}
                .element {{ margin: 10px; border: 1px solid #ccc; padding: 10px; }}
            </style>
        </head>
        <body>
            <div class="dashboard">
                <h1>{dashboard.name}</h1>
                <p>{dashboard.description}</p>
        """

        for element in dashboard.elements:
            if element.chart_id and element.chart_id in charts_html:
                html += f'<div class="element">{charts_html[element.chart_id]}</div>'
            elif element.type == "text":
                html += f'<div class="element"><p>{element.content}</p></div>'

        html += """
            </div>
        </body>
        </html>
        """
        return html


__all__ = [
    "DashboardBuilder",
    "DashboardBuilderError",
]
