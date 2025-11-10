"""
Flywheel momentum models for strategic intelligence
"""
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from datetime import datetime


class MomentumMetric(BaseModel):
    """Individual momentum metric measurement"""
    metric_name: str
    current_value: float
    previous_value: float
    velocity: float = Field(..., description="Rate of change")
    acceleration: float = Field(..., description="Change in velocity")
    contribution_to_flywheel: float = Field(..., ge=0, le=100, description="Contribution to overall momentum (0-100)")

    class Config:
        json_schema_extra = {
            "example": {
                "metric_name": "Customer NPS",
                "current_value": 72.0,
                "previous_value": 68.0,
                "velocity": 4.0,
                "acceleration": 1.2,
                "contribution_to_flywheel": 25.0
            }
        }


class FlywheelVelocity(BaseModel):
    """Flywheel velocity measurement over time"""
    timestamp: str
    velocity_score: float = Field(..., ge=0, le=100, description="Overall flywheel velocity (0-100)")
    acceleration: float = Field(..., description="Change in velocity")
    trend: str = Field(..., description="accelerating/decelerating/stable")

    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2024-01-15T00:00:00Z",
                "velocity_score": 75.0,
                "acceleration": 2.5,
                "trend": "accelerating"
            }
        }


class MomentumAnalysis(BaseModel):
    """Complete flywheel momentum analysis"""
    company: str
    industry: str
    generated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    # Current momentum
    current_momentum: float = Field(..., ge=0, le=100, description="Current flywheel momentum (0-100)")
    momentum_trend: str = Field(..., description="building/sustaining/declining")

    # Component metrics
    key_metrics: List[MomentumMetric] = Field(default_factory=list)
    strongest_contributors: List[str] = Field(default_factory=list, description="Metrics driving momentum")
    drag_factors: List[str] = Field(default_factory=list, description="Metrics slowing momentum")

    # Historical analysis
    velocity_history: List[FlywheelVelocity] = Field(default_factory=list)
    momentum_pattern: Optional[str] = None  # e.g., "J-curve growth", "plateau", "decline"

    # Predictive analysis
    projected_momentum_30d: float = Field(default=0.0, ge=0, le=100)
    projected_momentum_90d: float = Field(default=0.0, ge=0, le=100)
    inflection_point_risk: float = Field(default=0.0, ge=0, le=100, description="Risk of momentum reversal (0-100)")

    # Strategic recommendations
    acceleration_opportunities: List[str] = Field(default_factory=list)
    friction_points_to_address: List[str] = Field(default_factory=list)
    momentum_preservation_strategies: List[str] = Field(default_factory=list)

    # Metadata
    confidence_score: float = Field(default=0.0, ge=0, le=100)
    data_sources: List[str] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "company": "Tesla",
                "industry": "Electric Vehicles",
                "current_momentum": 78.0,
                "momentum_trend": "building",
                "strongest_contributors": ["Brand perception", "Technology leadership"],
                "drag_factors": ["Production constraints", "Service capacity"],
                "projected_momentum_30d": 80.0,
                "inflection_point_risk": 15.0,
                "acceleration_opportunities": ["Expand Supercharger network", "Launch new model"],
                "confidence_score": 82.0
            }
        }
