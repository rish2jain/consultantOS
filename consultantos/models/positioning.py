"""
Competitive positioning models for strategic intelligence
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class CompetitivePosition(BaseModel):
    """Individual competitive position marker"""
    axis_x: str = Field(..., description="Primary competitive dimension (e.g., 'Price', 'Quality')")
    axis_y: str = Field(..., description="Secondary competitive dimension (e.g., 'Innovation', 'Scale')")
    x_value: float = Field(..., ge=0, le=100, description="Position on X-axis (0-100)")
    y_value: float = Field(..., ge=0, le=100, description="Position on Y-axis (0-100)")
    market_share: float = Field(default=0.0, ge=0, le=100, description="Market share percentage")
    positioning_statement: str = Field(..., description="Strategic positioning narrative")

    class Config:
        json_schema_extra = {
            "example": {
                "axis_x": "Price",
                "axis_y": "Quality",
                "x_value": 75,
                "y_value": 85,
                "market_share": 23.5,
                "positioning_statement": "Premium quality at competitive pricing"
            }
        }


class PositionTrajectory(BaseModel):
    """Historical trajectory of competitive position"""
    company: str
    positions: List[Dict[str, Any]] = Field(default_factory=list, description="Historical position snapshots")
    velocity: float = Field(default=0.0, description="Rate of position change")
    direction: str = Field(default="stable", description="Direction of movement (advancing/retreating/stable)")
    momentum_score: float = Field(default=50.0, ge=0, le=100, description="Overall momentum (0-100)")

    class Config:
        json_schema_extra = {
            "example": {
                "company": "Tesla",
                "positions": [],
                "velocity": 0.15,
                "direction": "advancing",
                "momentum_score": 72.0
            }
        }


class StrategicGroup(BaseModel):
    """Strategic group cluster of companies competing on similar dimensions"""
    group_id: int = Field(..., description="Group identifier")
    companies: List[str] = Field(..., description="Companies in this group")
    centroid_x: float = Field(..., description="Group centroid X coordinate")
    centroid_y: float = Field(..., description="Group centroid Y coordinate")
    characteristics: str = Field(..., description="Shared competitive traits")
    white_space_distance: float = Field(..., description="Distance to nearest white space")


class WhiteSpaceOpportunity(BaseModel):
    """Identified white space opportunity in competitive landscape"""
    position_x: float = Field(..., description="White space X coordinate")
    position_y: float = Field(..., description="White space Y coordinate")
    market_potential: float = Field(..., description="Estimated market size (USD millions)")
    entry_barrier: float = Field(..., ge=0, le=100, description="Entry barrier score (0-100)")
    required_capabilities: List[str] = Field(..., description="Needed capabilities")
    risk_score: float = Field(..., ge=0, le=100, description="Risk score (0-100)")


class PositionThreat(BaseModel):
    """Competitive threat to current position"""
    threatening_company: str = Field(..., description="Threatening competitor")
    threat_type: str = Field(..., description="Threat type: collision/displacement/encirclement")
    severity: float = Field(..., ge=0, le=100, description="Threat severity (0-100)")
    time_to_impact: int = Field(..., description="Estimated days until impact")
    recommended_response: str = Field(..., description="Recommended defensive action")


class DynamicPositioning(BaseModel):
    """
    Advanced dynamic positioning analysis with movement vectors and clustering.

    This model extends basic positioning with:
    - Movement vectors and velocity analysis
    - Strategic group clustering
    - Collision detection and threat assessment
    - White space identification
    """
    company: str
    industry: str
    generated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    # Position and trajectory
    current_position: CompetitivePosition
    movement_vector_x: float = Field(default=0.0, description="3-month X-axis movement")
    movement_vector_y: float = Field(default=0.0, description="3-month Y-axis movement")
    velocity: float = Field(default=0.0, description="Speed of competitive movement")

    # Predicted future position (6-month)
    predicted_x: float = Field(default=0.0, description="Predicted X position in 6 months")
    predicted_y: float = Field(default=0.0, description="Predicted Y position in 6 months")

    # Competitor analysis
    competitor_positions: List[CompetitivePosition] = Field(default_factory=list)
    competitor_trajectories: List[PositionTrajectory] = Field(default_factory=list)

    # Strategic grouping
    strategic_groups: List[StrategicGroup] = Field(default_factory=list)

    # Opportunities and threats
    white_space_opportunities: List[WhiteSpaceOpportunity] = Field(default_factory=list)
    position_threats: List[PositionThreat] = Field(default_factory=list)

    # Strategic recommendations
    recommendations: List[str] = Field(default_factory=list)
    collision_risk: float = Field(default=0.0, ge=0, le=100, description="Overall collision risk (0-100)")
    confidence_score: float = Field(default=0.0, ge=0, le=100, description="Analysis confidence (0-100)")
    data_sources: List[str] = Field(default_factory=list)


class PositioningAnalysis(BaseModel):
    """Complete competitive positioning analysis"""
    company: str
    industry: str
    generated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    # Current position
    current_position: CompetitivePosition

    # Competitive landscape
    competitors: List[CompetitivePosition] = Field(default_factory=list)

    # Dynamic analysis
    trajectory: Optional[PositionTrajectory] = None
    position_threats: List[str] = Field(default_factory=list, description="Threats to current position")
    position_opportunities: List[str] = Field(default_factory=list, description="Opportunities to improve position")

    # Strategic insights
    white_space_opportunities: List[str] = Field(default_factory=list, description="Uncontested market spaces")
    crowded_segments: List[str] = Field(default_factory=list, description="Over-saturated segments to avoid")

    # Confidence and metadata
    confidence_score: float = Field(default=0.0, ge=0, le=100)
    data_sources: List[str] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "company": "Tesla",
                "industry": "Electric Vehicles",
                "current_position": {
                    "axis_x": "Price",
                    "axis_y": "Innovation",
                    "x_value": 70,
                    "y_value": 95,
                    "market_share": 18.0,
                    "positioning_statement": "Premium innovation leader"
                },
                "competitors": [],
                "position_threats": ["Legacy automakers scaling EV production"],
                "position_opportunities": ["Mass market expansion"],
                "white_space_opportunities": ["Affordable luxury segment"],
                "confidence_score": 85.0
            }
        }
