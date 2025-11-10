"""
Analytics models for ConsultantOS
Supports custom formulas, charts, dashboards, and KPI tracking
"""
from enum import Enum
from datetime import datetime
from typing import Dict, Any, List, Optional, Literal
from pydantic import BaseModel, Field, validator


# Chart type enumerations
class ChartType(str, Enum):
    """Supported chart types"""
    LINE = "line"
    BAR = "bar"
    COLUMN = "column"
    PIE = "pie"
    SCATTER = "scatter"
    HEATMAP = "heatmap"
    WATERFALL = "waterfall"
    FUNNEL = "funnel"
    GAUGE = "gauge"
    SANKEY = "sankey"
    TREEMAP = "treemap"
    AREA = "area"


class TrendDirection(str, Enum):
    """KPI trend directions"""
    UP = "up"
    DOWN = "down"
    STABLE = "stable"


class AlertSeverity(str, Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class DashboardLayout(str, Enum):
    """Dashboard layout types"""
    GRID = "grid"
    FLEX = "flex"
    CUSTOM = "custom"


# Formula Models
class Formula(BaseModel):
    """Custom formula definition"""
    formula_id: str = Field(default_factory=lambda: str(__import__('uuid').uuid4()))
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    expression: str = Field(..., min_length=1)
    variables: List[str] = Field(default_factory=list)
    category: str = Field(default="custom")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    examples: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @validator('expression')
    def validate_expression(cls, v):
        """Basic expression validation"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Expression cannot be empty")
        return v.strip()


class FormulaEvaluationRequest(BaseModel):
    """Request to evaluate a formula"""
    formula: Formula
    context: Dict[str, Any] = Field(default_factory=dict)


class FormulaEvaluationResult(BaseModel):
    """Result of formula evaluation"""
    formula_id: str
    expression: str
    result: float
    context: Dict[str, Any]
    evaluated_at: datetime = Field(default_factory=datetime.utcnow)
    error: Optional[str] = None


# Chart Models
class ChartConfig(BaseModel):
    """Chart configuration and customization"""
    title: Optional[str] = None
    subtitle: Optional[str] = None
    x_axis_label: Optional[str] = None
    y_axis_label: Optional[str] = None
    colors: Optional[List[str]] = None
    show_legend: bool = True
    show_grid: bool = True
    responsive: bool = True
    height: Optional[int] = Field(None, ge=200, le=2000)
    width: Optional[int] = Field(None, ge=300, le=4000)
    annotations: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    custom_options: Optional[Dict[str, Any]] = Field(default_factory=dict)


class DataSource(BaseModel):
    """Data source for chart"""
    type: Literal["formula", "api", "static"] = "formula"
    formula_id: Optional[str] = None
    api_endpoint: Optional[str] = None
    data: Optional[List[Dict[str, Any]]] = None
    refresh_interval: Optional[int] = None  # seconds


class Chart(BaseModel):
    """Chart definition"""
    chart_id: str = Field(default_factory=lambda: str(__import__('uuid').uuid4()))
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    chart_type: ChartType
    data_source: DataSource
    config: ChartConfig = Field(default_factory=ChartConfig)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = False


class ChartData(BaseModel):
    """Chart data for rendering"""
    chart_id: str
    chart_type: ChartType
    data: Dict[str, Any]
    config: ChartConfig
    rendered_at: datetime = Field(default_factory=datetime.utcnow)


# KPI Models
class KPI(BaseModel):
    """Key Performance Indicator definition"""
    kpi_id: str = Field(default_factory=lambda: str(__import__('uuid').uuid4()))
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    formula: Formula
    current_value: Optional[float] = None
    target_value: Optional[float] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    unit: Optional[str] = None  # e.g., "%", "$", "units"
    trend: TrendDirection = TrendDirection.STABLE
    percentage_change: Optional[float] = None
    alert_threshold: Optional[float] = None
    alert_enabled: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class KPIAlert(BaseModel):
    """KPI threshold alert"""
    alert_id: str = Field(default_factory=lambda: str(__import__('uuid').uuid4()))
    kpi_id: str
    severity: AlertSeverity
    message: str
    threshold_value: float
    actual_value: float
    triggered_at: datetime = Field(default_factory=datetime.utcnow)
    acknowledged: bool = False


class KPIHistory(BaseModel):
    """Historical KPI value"""
    kpi_id: str
    value: float
    timestamp: datetime
    context: Optional[Dict[str, Any]] = None


# Dashboard Models
class DashboardPosition(BaseModel):
    """Position of an element in dashboard grid"""
    x: int = Field(..., ge=0)
    y: int = Field(..., ge=0)
    width: int = Field(default=1, ge=1, le=12)
    height: int = Field(default=1, ge=1, le=12)


class DashboardElement(BaseModel):
    """Element in dashboard (chart or KPI widget)"""
    element_id: str = Field(default_factory=lambda: str(__import__('uuid').uuid4()))
    type: Literal["chart", "kpi", "text", "divider"] = "chart"
    chart_id: Optional[str] = None
    kpi_id: Optional[str] = None
    content: Optional[str] = None
    position: DashboardPosition
    order: int = Field(default=0)


class Dashboard(BaseModel):
    """Complete dashboard definition"""
    dashboard_id: str = Field(default_factory=lambda: str(__import__('uuid').uuid4()))
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    layout: DashboardLayout = DashboardLayout.GRID
    elements: List[DashboardElement] = Field(default_factory=list)
    kpis: List[str] = Field(default_factory=list)  # KPI IDs
    charts: List[str] = Field(default_factory=list)  # Chart IDs
    refresh_interval: int = Field(default=300, ge=30, le=3600)  # seconds
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    is_template: bool = False

    class Config:
        use_enum_values = False


# Template Models
class DashboardTemplate(BaseModel):
    """Pre-built dashboard template"""
    template_id: str = Field(default_factory=lambda: str(__import__('uuid').uuid4()))
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category: str = Field(default="general")  # executive, sales, finance, marketing, operations
    dashboard: Dashboard
    preview_image: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    industry_tags: List[str] = Field(default_factory=list)


class TemplateLibrary(BaseModel):
    """Collection of templates"""
    templates: List[DashboardTemplate] = Field(default_factory=list)
    total_count: int = Field(default=0)


# Export Models
class ExportFormat(str, Enum):
    """Export formats"""
    PDF = "pdf"
    EXCEL = "excel"
    POWERPOINT = "powerpoint"
    PNG = "png"
    JSON = "json"


class DashboardExportRequest(BaseModel):
    """Request to export dashboard"""
    dashboard_id: str
    format: ExportFormat
    include_data: bool = True
    page_orientation: Optional[Literal["portrait", "landscape"]] = "landscape"
    custom_title: Optional[str] = None


class DashboardExportResult(BaseModel):
    """Result of dashboard export"""
    dashboard_id: str
    format: ExportFormat
    file_url: str
    file_size: int
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Request/Response Models
class CreateFormulaRequest(BaseModel):
    """Request to create a formula"""
    name: str
    description: Optional[str] = None
    expression: str
    examples: Optional[Dict[str, Any]] = None
    category: str = "custom"


class CreateChartRequest(BaseModel):
    """Request to create a chart"""
    name: str
    description: Optional[str] = None
    chart_type: ChartType
    data_source: DataSource
    config: ChartConfig = Field(default_factory=ChartConfig)


class CreateDashboardRequest(BaseModel):
    """Request to create a dashboard"""
    name: str
    description: Optional[str] = None
    layout: DashboardLayout = DashboardLayout.GRID
    elements: List[DashboardElement] = Field(default_factory=list)
    refresh_interval: int = Field(default=300, ge=30, le=3600)
    tags: List[str] = Field(default_factory=list)


class UpdateDashboardRequest(BaseModel):
    """Request to update a dashboard"""
    name: Optional[str] = None
    description: Optional[str] = None
    layout: Optional[DashboardLayout] = None
    elements: Optional[List[DashboardElement]] = None
    refresh_interval: Optional[int] = Field(None, ge=30, le=3600)
    tags: Optional[List[str]] = None


class DashboardResponse(BaseModel):
    """Response with dashboard and all related data"""
    dashboard: Dashboard
    charts: List[Chart]
    kpis: List[KPI]
    alerts: List[KPIAlert]
    last_refresh: datetime


# Analytics Summary Models
class AnalyticsSummary(BaseModel):
    """Summary of analytics activity"""
    total_dashboards: int = 0
    total_charts: int = 0
    total_kpis: int = 0
    total_formulas: int = 0
    active_alerts: int = 0
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    top_charts: List[Chart] = Field(default_factory=list)
    recent_alerts: List[KPIAlert] = Field(default_factory=list)


__all__ = [
    # Enums
    "ChartType",
    "TrendDirection",
    "AlertSeverity",
    "DashboardLayout",
    "ExportFormat",
    # Models
    "Formula",
    "FormulaEvaluationRequest",
    "FormulaEvaluationResult",
    "ChartConfig",
    "DataSource",
    "Chart",
    "ChartData",
    "KPI",
    "KPIAlert",
    "KPIHistory",
    "DashboardPosition",
    "DashboardElement",
    "Dashboard",
    "DashboardTemplate",
    "TemplateLibrary",
    # Requests
    "CreateFormulaRequest",
    "CreateChartRequest",
    "CreateDashboardRequest",
    "UpdateDashboardRequest",
    "DashboardExportRequest",
    # Responses
    "DashboardResponse",
    "DashboardExportResult",
    "AnalyticsSummary",
]
