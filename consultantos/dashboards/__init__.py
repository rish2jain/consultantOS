"""Live Dashboard System for ConsultantOS

Provides real-time, interactive dashboards as remarkable differentiation
from static PDF reports.
"""

from consultantos.dashboards.models import (
    Alert,
    DashboardSection,
    DashboardTemplate,
    LiveDashboard,
    Metric,
    ScenarioAssumptions,
    ScenarioForecast,
)
from consultantos.dashboards.repository import DashboardRepository
from consultantos.dashboards.service import DashboardService
from consultantos.dashboards.templates import DASHBOARD_TEMPLATES

__all__ = [
    "Alert",
    "DashboardRepository",
    "DashboardSection",
    "DashboardService",
    "DashboardTemplate",
    "DASHBOARD_TEMPLATES",
    "LiveDashboard",
    "Metric",
    "ScenarioAssumptions",
    "ScenarioForecast",
]
