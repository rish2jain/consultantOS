"""Dashboard data models for live, interactive analytics"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, ConfigDict


class AlertSeverity(str, Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class TrendDirection(str, Enum):
    """Trend direction indicators"""
    UP = "up"
    DOWN = "down"
    STABLE = "stable"


class SectionType(str, Enum):
    """Dashboard section types"""
    CHART = "chart"
    TABLE = "table"
    METRIC = "metric"
    INSIGHT = "insight"
    ALERT = "alert"
    MAP = "map"
    LANDSCAPE = "landscape"
    TRENDS = "trends"


class Alert(BaseModel):
    """Real-time alert for critical business events"""
    id: str
    title: str
    message: str
    severity: AlertSeverity
    category: str  # competitive, financial, market, regulatory
    source: str  # Which agent generated this
    timestamp: datetime
    company: Optional[str] = None
    action_required: bool = False
    action_url: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "alert_001",
                "title": "Competitor Price Drop",
                "message": "Tesla reduced Model 3 price by 15% - significant competitive threat",
                "severity": "critical",
                "category": "competitive",
                "source": "market_agent",
                "timestamp": "2025-11-08T10:30:00Z",
                "company": "Tesla",
                "action_required": True,
                "action_url": "/scenarios/pricing"
            }
        }
    )


class Metric(BaseModel):
    """Real-time business metric with trend analysis"""
    id: str
    name: str
    value: float
    unit: str  # $, %, units, etc.
    change: float  # % change since last period
    change_absolute: Optional[float] = None
    trend: TrendDirection
    confidence: float = Field(ge=0.0, le=1.0)
    last_updated: datetime
    source: str
    benchmark: Optional[float] = None  # Industry benchmark
    target: Optional[float] = None  # Target value

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "metric_revenue",
                "name": "Quarterly Revenue",
                "value": 25000000.0,
                "unit": "$",
                "change": 12.5,
                "change_absolute": 2777777.78,
                "trend": "up",
                "confidence": 0.92,
                "last_updated": "2025-11-08T10:00:00Z",
                "source": "financial_agent",
                "benchmark": 22000000.0,
                "target": 30000000.0
            }
        }
    )


class DashboardSection(BaseModel):
    """Interactive dashboard section with real-time data"""
    id: str
    title: str
    type: SectionType
    data: Dict[str, Any] = Field(default_factory=dict)  # Flexible data structure based on type
    last_updated: datetime
    refresh_interval: int = 300  # seconds - default 5 minutes
    order: int = 0  # Display order
    size: str = "medium"  # small, medium, large, full-width
    config: Dict[str, Any] = Field(default_factory=dict)  # Section-specific configuration

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "section_revenue_trend",
                "title": "Revenue Trend",
                "type": "chart",
                "data": {
                    "chart_type": "line",
                    "x": ["Q1", "Q2", "Q3", "Q4"],
                    "y": [20000000, 22000000, 23000000, 25000000],
                    "labels": {"x": "Quarter", "y": "Revenue ($)"}
                },
                "last_updated": "2025-11-08T10:00:00Z",
                "refresh_interval": 300,
                "order": 1,
                "size": "large",
                "config": {"show_grid": True, "animate": True}
            }
        }
    )


class LiveDashboard(BaseModel):
    """Real-time interactive dashboard"""
    id: str
    company: str
    industry: str
    template: str  # Template name
    created_at: datetime
    last_updated: datetime
    user_id: str
    sections: List[DashboardSection]
    alerts: List[Alert] = Field(default_factory=list)
    metrics: List[Metric] = Field(default_factory=list)
    refresh_enabled: bool = True
    auto_refresh_interval: int = 300  # seconds
    metadata: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "dash_tesla_001",
                "company": "Tesla",
                "industry": "Electric Vehicles",
                "template": "executive_summary",
                "created_at": "2025-11-08T09:00:00Z",
                "last_updated": "2025-11-08T10:00:00Z",
                "user_id": "user_123",
                "sections": [],
                "alerts": [],
                "metrics": [],
                "refresh_enabled": True,
                "auto_refresh_interval": 300,
                "metadata": {"frameworks": ["porter", "swot"], "depth": "standard"}
            }
        }
    )


class DashboardTemplate(BaseModel):
    """Pre-configured dashboard template"""
    id: str
    name: str
    description: str
    sections: List[Dict[str, Any]]  # Section configurations
    target_audience: str  # executive, analyst, researcher
    use_cases: List[str]
    default_refresh_interval: int = 300

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "template_exec",
                "name": "Executive Summary",
                "description": "High-level metrics and alerts for executives",
                "sections": [
                    {"type": "metric", "title": "Key Metrics", "size": "medium"},
                    {"type": "alert", "title": "Critical Alerts", "size": "medium"},
                    {"type": "chart", "title": "Revenue Trend", "size": "large"}
                ],
                "target_audience": "executive",
                "use_cases": ["quarterly_review", "board_meeting"],
                "default_refresh_interval": 300
            }
        }
    )


class ScenarioAssumptions(BaseModel):
    """Assumptions for scenario planning"""
    market_growth_rate: float = Field(ge=-50.0, le=200.0)  # % annual growth
    competitor_entry: bool = False
    regulatory_change: bool = False
    price_change: float = 0.0  # % price adjustment
    cost_change: float = 0.0  # % cost adjustment
    market_share_target: Optional[float] = None
    custom_assumptions: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "market_growth_rate": 5.0,
                "competitor_entry": False,
                "regulatory_change": False,
                "price_change": -10.0,
                "cost_change": 5.0,
                "market_share_target": 25.0,
                "custom_assumptions": {"ev_adoption_rate": 15.0}
            }
        }
    )


class ScenarioForecast(BaseModel):
    """Forecast results from scenario planning"""
    scenario_id: str
    company: str
    assumptions: ScenarioAssumptions
    forecast_period: int  # months
    revenue_forecast: List[float]
    profit_forecast: List[float]
    market_share_forecast: List[float]
    risk_score: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    key_insights: List[str] = Field(default_factory=list)
    created_at: datetime

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "scenario_id": "scenario_001",
                "company": "Tesla",
                "assumptions": {},
                "forecast_period": 12,
                "revenue_forecast": [25000000, 26000000, 27000000],
                "profit_forecast": [2500000, 2700000, 2900000],
                "market_share_forecast": [22.0, 23.5, 25.0],
                "risk_score": 0.35,
                "confidence": 0.78,
                "key_insights": [
                    "Price reduction drives volume growth",
                    "Market share gains offset margin pressure"
                ],
                "created_at": "2025-11-08T10:30:00Z"
            }
        }
    )


class DashboardUpdate(BaseModel):
    """Real-time dashboard update message"""
    dashboard_id: str
    update_type: str  # metric, alert, section, full
    timestamp: datetime
    data: Dict[str, Any]

    class Config:
        json_schema_extra = {
            "example": {
                "dashboard_id": "dash_tesla_001",
                "update_type": "alert",
                "timestamp": "2025-11-08T10:35:00Z",
                "data": {
                    "alert": {
                        "id": "alert_002",
                        "title": "New Competitor Entry",
                        "severity": "warning"
                    }
                }
            }
        }
