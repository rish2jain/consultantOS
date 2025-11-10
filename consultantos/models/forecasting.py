"""
Forecasting models for enhanced multi-scenario time series forecasting
Phase 1 Week 3-4: Enhanced Forecasting Agent
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator


class ScenarioType(str, Enum):
    """Forecast scenario types"""
    OPTIMISTIC = "optimistic"
    BASELINE = "baseline"
    PESSIMISTIC = "pessimistic"


class MetricType(str, Enum):
    """Supported forecast metric types"""
    REVENUE = "revenue"
    MARKET_SHARE = "market_share"
    CUSTOMER_GROWTH = "customer_growth"
    SALES_VOLUME = "sales_volume"
    CUSTOM = "custom"


class ForecastScenario(BaseModel):
    """
    Individual forecast scenario with predictions and confidence intervals
    """
    scenario_type: ScenarioType = Field(..., description="Type of scenario (optimistic/baseline/pessimistic)")
    dates: List[str] = Field(..., description="Forecast dates in YYYY-MM-DD format")
    predictions: List[float] = Field(..., description="Predicted values for each date")
    lower_bound: List[float] = Field(..., description="Lower confidence interval bounds")
    upper_bound: List[float] = Field(..., description="Upper confidence interval bounds")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence level (0.0-1.0)")
    assumptions: Dict[str, Any] = Field(
        default_factory=dict,
        description="Scenario-specific assumptions and parameters"
    )

    @validator('predictions', 'lower_bound', 'upper_bound')
    def validate_lists_equal_length(cls, v, values):
        """Ensure all lists have same length as dates"""
        if 'dates' in values and len(v) != len(values['dates']):
            raise ValueError(f"List length {len(v)} must match dates length {len(values['dates'])}")
        return v

    @validator('lower_bound')
    def validate_lower_bound(cls, v, values):
        """Ensure lower_bound <= predictions"""
        if 'predictions' in values:
            for i, (lower, pred) in enumerate(zip(v, values['predictions'])):
                if lower > pred:
                    raise ValueError(f"Lower bound {lower} exceeds prediction {pred} at index {i}")
        return v

    @validator('upper_bound')
    def validate_upper_bound(cls, v, values):
        """Ensure predictions <= upper_bound"""
        if 'predictions' in values:
            for i, (upper, pred) in enumerate(zip(v, values['predictions'])):
                if upper < pred:
                    raise ValueError(f"Upper bound {upper} below prediction {pred} at index {i}")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "scenario_type": "baseline",
                "dates": ["2025-12-01", "2025-12-02", "2025-12-03"],
                "predictions": [100000.0, 101500.0, 103000.0],
                "lower_bound": [95000.0, 96500.0, 98000.0],
                "upper_bound": [105000.0, 106500.0, 108000.0],
                "confidence": 0.95,
                "assumptions": {
                    "growth_rate": 0.015,
                    "seasonality": "moderate",
                    "external_factors": "stable_market"
                }
            }
        }


class EnhancedForecastResult(BaseModel):
    """
    Complete forecast result with multiple scenarios and insights
    """
    metric_name: str = Field(..., description="Name of the forecasted metric")
    metric_type: MetricType = Field(default=MetricType.CUSTOM, description="Type of metric being forecasted")
    company: Optional[str] = Field(None, description="Company being analyzed")
    industry: Optional[str] = Field(None, description="Industry context")
    scenarios: List[ForecastScenario] = Field(..., description="Forecast scenarios (optimistic/baseline/pessimistic)")
    recommended_scenario: ScenarioType = Field(..., description="Recommended scenario for planning")
    key_insights: List[str] = Field(..., description="Key insights and observations from forecast")
    methodology: str = Field(..., description="Forecasting methodology description")
    data_source: str = Field(default="sample_data", description="Source of historical data")
    forecast_horizon_days: int = Field(..., gt=0, description="Number of days forecasted")
    historical_data_points: int = Field(..., gt=0, description="Number of historical data points used")
    model_accuracy: Optional[Dict[str, float]] = Field(
        None,
        description="Model accuracy metrics (MAPE, RMSE, etc.)"
    )
    generated_at: datetime = Field(default_factory=datetime.now, description="Forecast generation timestamp")

    @validator('scenarios')
    def validate_scenarios(cls, v):
        """Ensure all three scenario types are present"""
        scenario_types = {s.scenario_type for s in v}
        required_types = {ScenarioType.OPTIMISTIC, ScenarioType.BASELINE, ScenarioType.PESSIMISTIC}
        if scenario_types != required_types:
            raise ValueError(f"Must include all scenario types: {required_types}")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "metric_name": "Revenue",
                "metric_type": "revenue",
                "company": "Tesla",
                "industry": "Electric Vehicles",
                "scenarios": [
                    {
                        "scenario_type": "baseline",
                        "dates": ["2025-12-01"],
                        "predictions": [100000.0],
                        "lower_bound": [95000.0],
                        "upper_bound": [105000.0],
                        "confidence": 0.95,
                        "assumptions": {"growth_rate": 0.015}
                    }
                ],
                "recommended_scenario": "baseline",
                "key_insights": [
                    "Strong upward trend detected",
                    "Seasonal patterns identified",
                    "High confidence in baseline scenario"
                ],
                "methodology": "Prophet with seasonal decomposition",
                "data_source": "alpha_vantage",
                "forecast_horizon_days": 30,
                "historical_data_points": 100,
                "model_accuracy": {
                    "mape": 5.2,
                    "rmse": 2500.0
                },
                "generated_at": "2025-11-09T12:00:00"
            }
        }


class ForecastRequest(BaseModel):
    """
    Request for forecast generation
    """
    company: str = Field(..., description="Company name")
    industry: Optional[str] = Field(None, description="Industry context")
    metric_name: str = Field(default="Revenue", description="Metric to forecast")
    metric_type: MetricType = Field(default=MetricType.REVENUE, description="Type of metric")
    forecast_horizon_days: int = Field(default=30, gt=0, le=365, description="Forecast horizon (1-365 days)")
    ticker: Optional[str] = Field(None, description="Stock ticker for real data (optional)")
    use_real_data: bool = Field(default=False, description="Use real financial data if available")

    class Config:
        json_schema_extra = {
            "example": {
                "company": "Tesla",
                "industry": "Electric Vehicles",
                "metric_name": "Revenue",
                "metric_type": "revenue",
                "forecast_horizon_days": 30,
                "ticker": "TSLA",
                "use_real_data": True
            }
        }


class ForecastComparisonRequest(BaseModel):
    """
    Request to compare multiple forecast scenarios
    """
    forecast_id_1: str = Field(..., description="First forecast ID")
    forecast_id_2: str = Field(..., description="Second forecast ID")
    comparison_metric: str = Field(default="predictions", description="Metric to compare")

    class Config:
        json_schema_extra = {
            "example": {
                "forecast_id_1": "forecast_123",
                "forecast_id_2": "forecast_456",
                "comparison_metric": "predictions"
            }
        }


class ForecastHistoryEntry(BaseModel):
    """
    Historical forecast entry for accuracy tracking
    """
    forecast_id: str = Field(..., description="Unique forecast identifier")
    company: str = Field(..., description="Company name")
    metric_name: str = Field(..., description="Forecasted metric")
    generated_at: datetime = Field(..., description="When forecast was generated")
    forecast_horizon_days: int = Field(..., description="Forecast horizon")
    recommended_scenario: ScenarioType = Field(..., description="Recommended scenario")
    actual_accuracy: Optional[float] = Field(None, description="Actual accuracy if data available")

    class Config:
        json_schema_extra = {
            "example": {
                "forecast_id": "forecast_123",
                "company": "Tesla",
                "metric_name": "Revenue",
                "generated_at": "2025-11-09T12:00:00",
                "forecast_horizon_days": 30,
                "recommended_scenario": "baseline",
                "actual_accuracy": 92.5
            }
        }
