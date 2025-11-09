"""Pre-built dashboard templates for different use cases"""

from typing import Dict, List

from consultantos.dashboards.models import DashboardTemplate

# Template configurations
DASHBOARD_TEMPLATES: Dict[str, DashboardTemplate] = {
    "executive_summary": DashboardTemplate(
        id="template_exec",
        name="Executive Summary",
        description="High-level metrics and critical alerts for C-suite executives",
        sections=[
            {
                "type": "metric",
                "title": "Key Performance Metrics",
                "size": "full-width",
                "order": 1,
                "config": {"layout": "grid", "columns": 4}
            },
            {
                "type": "alert",
                "title": "Critical Alerts",
                "size": "large",
                "order": 2,
                "config": {"max_alerts": 5, "severity_filter": ["critical", "warning"]}
            },
            {
                "type": "chart",
                "title": "Revenue Trend",
                "size": "large",
                "order": 3,
                "config": {"chart_type": "line", "show_forecast": True}
            },
            {
                "type": "insight",
                "title": "Top Strategic Insights",
                "size": "medium",
                "order": 4,
                "config": {"max_insights": 3}
            }
        ],
        target_audience="executive",
        use_cases=["quarterly_review", "board_meeting", "investor_update"],
        default_refresh_interval=300
    ),

    "competitive_intelligence": DashboardTemplate(
        id="template_comp",
        name="Competitive Intelligence",
        description="Real-time competitive landscape and competitor tracking",
        sections=[
            {
                "type": "landscape",
                "title": "Competitive Positioning Map",
                "size": "full-width",
                "order": 1,
                "config": {
                    "x_axis": "price",
                    "y_axis": "quality",
                    "bubble_size": "market_share",
                    "interactive": True
                }
            },
            {
                "type": "table",
                "title": "Competitor Comparison",
                "size": "large",
                "order": 2,
                "config": {
                    "columns": ["company", "market_share", "revenue", "growth_rate"],
                    "sortable": True,
                    "highlight_changes": True
                }
            },
            {
                "type": "alert",
                "title": "Competitor Moves",
                "size": "medium",
                "order": 3,
                "config": {"category_filter": ["competitive"], "max_alerts": 10}
            },
            {
                "type": "chart",
                "title": "Market Share Trends",
                "size": "large",
                "order": 4,
                "config": {"chart_type": "stacked_area", "show_competitors": True}
            }
        ],
        target_audience="strategist",
        use_cases=["competitive_analysis", "market_monitoring", "strategic_planning"],
        default_refresh_interval=600
    ),

    "market_analysis": DashboardTemplate(
        id="template_market",
        name="Market Analysis",
        description="Comprehensive market trends, size, and opportunity analysis",
        sections=[
            {
                "type": "chart",
                "title": "Market Size & Growth",
                "size": "large",
                "order": 1,
                "config": {"chart_type": "combo", "show_forecast": True}
            },
            {
                "type": "map",
                "title": "Geographic Distribution",
                "size": "large",
                "order": 2,
                "config": {"map_type": "choropleth", "metric": "market_size"}
            },
            {
                "type": "table",
                "title": "Segment Analysis",
                "size": "medium",
                "order": 3,
                "config": {
                    "columns": ["segment", "size", "growth", "attractiveness"],
                    "sortable": True
                }
            },
            {
                "type": "trends",
                "title": "Emerging Trends",
                "size": "medium",
                "order": 4,
                "config": {"time_range": "30d", "show_sentiment": True}
            },
            {
                "type": "metric",
                "title": "Market Metrics",
                "size": "full-width",
                "order": 5,
                "config": {"layout": "grid", "columns": 5}
            }
        ],
        target_audience="analyst",
        use_cases=["market_research", "opportunity_assessment", "industry_analysis"],
        default_refresh_interval=900
    ),

    "financial_performance": DashboardTemplate(
        id="template_finance",
        name="Financial Performance",
        description="Real-time financial metrics, ratios, and performance tracking",
        sections=[
            {
                "type": "metric",
                "title": "Key Financial Metrics",
                "size": "full-width",
                "order": 1,
                "config": {
                    "layout": "grid",
                    "columns": 4,
                    "metrics": ["revenue", "profit_margin", "roce", "debt_to_equity"]
                }
            },
            {
                "type": "chart",
                "title": "Revenue vs Profit",
                "size": "large",
                "order": 2,
                "config": {"chart_type": "dual_axis", "show_trend": True}
            },
            {
                "type": "chart",
                "title": "Cash Flow Analysis",
                "size": "large",
                "order": 3,
                "config": {"chart_type": "waterfall", "breakdown": True}
            },
            {
                "type": "table",
                "title": "Financial Ratios",
                "size": "medium",
                "order": 4,
                "config": {
                    "columns": ["ratio", "current", "benchmark", "trend"],
                    "highlight_outliers": True
                }
            },
            {
                "type": "alert",
                "title": "Financial Alerts",
                "size": "medium",
                "order": 5,
                "config": {"category_filter": ["financial"], "severity_filter": ["critical"]}
            }
        ],
        target_audience="cfo",
        use_cases=["financial_review", "investor_relations", "budget_planning"],
        default_refresh_interval=300
    ),

    "risk_monitor": DashboardTemplate(
        id="template_risk",
        name="Risk Monitor",
        description="Real-time risk tracking and early warning system",
        sections=[
            {
                "type": "alert",
                "title": "Active Risk Alerts",
                "size": "full-width",
                "order": 1,
                "config": {
                    "severity_filter": ["critical", "warning"],
                    "group_by": "category",
                    "show_timeline": True
                }
            },
            {
                "type": "chart",
                "title": "Risk Heat Map",
                "size": "large",
                "order": 2,
                "config": {
                    "chart_type": "heatmap",
                    "x_axis": "likelihood",
                    "y_axis": "impact"
                }
            },
            {
                "type": "table",
                "title": "Risk Register",
                "size": "large",
                "order": 3,
                "config": {
                    "columns": ["risk", "category", "likelihood", "impact", "mitigation"],
                    "sortable": True,
                    "filterable": True
                }
            },
            {
                "type": "metric",
                "title": "Risk Indicators",
                "size": "medium",
                "order": 4,
                "config": {"layout": "grid", "columns": 3}
            },
            {
                "type": "trends",
                "title": "Risk Trends",
                "size": "medium",
                "order": 5,
                "config": {"show_sentiment": True, "category_breakdown": True}
            }
        ],
        target_audience="risk_manager",
        use_cases=["risk_management", "compliance", "crisis_monitoring"],
        default_refresh_interval=180
    ),

    "innovation_tracker": DashboardTemplate(
        id="template_innovation",
        name="Innovation Tracker",
        description="Track innovation trends, R&D progress, and emerging technologies",
        sections=[
            {
                "type": "trends",
                "title": "Emerging Technologies",
                "size": "full-width",
                "order": 1,
                "config": {"time_range": "90d", "show_sentiment": True, "category": "technology"}
            },
            {
                "type": "chart",
                "title": "R&D Investment",
                "size": "large",
                "order": 2,
                "config": {"chart_type": "bar", "breakdown": "project"}
            },
            {
                "type": "table",
                "title": "Innovation Pipeline",
                "size": "large",
                "order": 3,
                "config": {
                    "columns": ["project", "stage", "investment", "expected_roi", "timeline"],
                    "sortable": True
                }
            },
            {
                "type": "landscape",
                "title": "Technology Landscape",
                "size": "medium",
                "order": 4,
                "config": {
                    "x_axis": "maturity",
                    "y_axis": "market_potential",
                    "bubble_size": "investment"
                }
            },
            {
                "type": "insight",
                "title": "Innovation Insights",
                "size": "medium",
                "order": 5,
                "config": {"source_filter": ["research_agent"], "max_insights": 5}
            }
        ],
        target_audience="cto",
        use_cases=["innovation_management", "technology_scouting", "r_and_d_planning"],
        default_refresh_interval=1800
    )
}


def get_template(template_id: str) -> DashboardTemplate:
    """Get dashboard template by ID"""
    if template_id not in DASHBOARD_TEMPLATES:
        raise ValueError(f"Template '{template_id}' not found")
    return DASHBOARD_TEMPLATES[template_id]


def list_templates() -> List[DashboardTemplate]:
    """List all available dashboard templates"""
    return list(DASHBOARD_TEMPLATES.values())


def get_templates_for_audience(audience: str) -> List[DashboardTemplate]:
    """Get templates suitable for a specific audience"""
    return [t for t in DASHBOARD_TEMPLATES.values() if t.target_audience == audience]


def get_templates_for_use_case(use_case: str) -> List[DashboardTemplate]:
    """Get templates suitable for a specific use case"""
    return [t for t in DASHBOARD_TEMPLATES.values() if use_case in t.use_cases]
