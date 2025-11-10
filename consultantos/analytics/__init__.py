"""
Analytics modules for ConsultantOS
Provides formula parsing, chart building, dashboard creation, and KPI tracking
"""
try:
    from consultantos.analytics.sentiment_analyzer import SentimentAnalyzer
except ImportError:
    SentimentAnalyzer = None

from consultantos.analytics.formula_parser import (
    FormulaParser,
    FormulaParserError,
    FORMULA_TEMPLATES,
)
from consultantos.analytics.chart_builder import (
    ChartBuilder,
    ChartBuilderError,
    create_time_series_chart,
    create_comparison_chart,
    create_distribution_chart,
)
from consultantos.analytics.dashboard_builder import (
    DashboardBuilder,
    DashboardBuilderError,
)
from consultantos.analytics.kpi_tracker import (
    KPITracker,
    KPITrackerError,
    AlertEngine,
)

__all__ = [
    # Existing
    "SentimentAnalyzer",
    # Formula Parser
    "FormulaParser",
    "FormulaParserError",
    "FORMULA_TEMPLATES",
    # Chart Builder
    "ChartBuilder",
    "ChartBuilderError",
    "create_time_series_chart",
    "create_comparison_chart",
    "create_distribution_chart",
    # Dashboard Builder
    "DashboardBuilder",
    "DashboardBuilderError",
    # KPI Tracker
    "KPITracker",
    "KPITrackerError",
    "AlertEngine",
]
