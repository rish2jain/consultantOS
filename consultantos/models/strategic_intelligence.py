"""
Enhanced strategic intelligence report models
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from consultantos.models.positioning import PositioningAnalysis, DynamicPositioning
from consultantos.models.disruption import DisruptionAssessment
from consultantos.models.decisions import DecisionBrief, StrategicDecision
from consultantos.models.systems import SystemDynamicsAnalysis
from consultantos.models.momentum import MomentumAnalysis
from consultantos.models.social_media import SocialSignalSummary


class StrategicHealthScore(BaseModel):
    """Comprehensive strategic health scoring"""
    overall_health: float = Field(..., ge=0, le=100, description="Overall strategic health (0-100)")
    
    # Component scores
    competitive_position_score: float = Field(..., ge=0, le=100)
    disruption_resilience_score: float = Field(..., ge=0, le=100)
    system_health_score: float = Field(..., ge=0, le=100)
    momentum_score: float = Field(..., ge=0, le=100)
    
    # Health indicators
    health_level: str = Field(..., description="critical/concerning/stable/strong/excellent")
    trend: str = Field(..., description="improving/stable/declining")
    
    # Critical flags
    critical_issues: List[str] = Field(default_factory=list)
    immediate_actions: List[str] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "overall_health": 72.0,
                "competitive_position_score": 75.0,
                "disruption_resilience_score": 65.0,
                "system_health_score": 70.0,
                "momentum_score": 78.0,
                "health_level": "strong",
                "trend": "improving",
                "critical_issues": [],
                "immediate_actions": ["Address production bottleneck"]
            }
        }


class EnhancedStrategicReport(BaseModel):
    """Comprehensive strategic intelligence report with traditional and enhanced analysis"""
    report_id: str
    company: str
    industry: str
    generated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    
    # Traditional outputs (from existing system)
    research: Optional[dict] = None  # CompanyResearch from research_agent
    market: Optional[dict] = None  # MarketTrends from market_agent
    financial: Optional[dict] = None  # FinancialSnapshot from financial_agent
    frameworks: Optional[dict] = None  # FrameworkAnalysis from framework_agent
    executive_summary: Optional[str] = None  # From synthesis_agent
    
    # Enhanced strategic intelligence (NEW)
    competitive_positioning: Optional[PositioningAnalysis] = None
    dynamic_positioning: Optional[DynamicPositioning] = None
    disruption_assessment: Optional[DisruptionAssessment] = None
    system_dynamics: Optional[SystemDynamicsAnalysis] = None
    flywheel_momentum: Optional[MomentumAnalysis] = None
    decision_brief: Optional[DecisionBrief] = None
    social_signals: Optional[SocialSignalSummary] = None
    
    # Meta scores and insights
    overall_strategic_health: Optional[StrategicHealthScore] = None
    confidence_score: float = Field(default=0.0, ge=0, le=100)
    
    # Executive quick view
    top_threats: List[str] = Field(default_factory=list)
    top_opportunities: List[str] = Field(default_factory=list)
    critical_decision: Optional[StrategicDecision] = None
    
    # Metadata
    analysis_depth: str = Field(default="standard", description="quick/standard/deep/comprehensive")
    partial_results: bool = Field(default=False)
    errors: List[str] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "report_id": "rpt_123",
                "company": "Tesla",
                "industry": "Electric Vehicles",
                "analysis_depth": "comprehensive",
                "confidence_score": 85.0,
                "top_threats": ["Legacy automaker EV competition", "Supply chain constraints"],
                "top_opportunities": ["Mass market expansion", "Energy storage growth"],
                "partial_results": False
            }
        }


class StrategicInsight(BaseModel):
    """Individual strategic insight for feed"""
    insight_id: str
    insight_type: str = Field(..., description="threat/opportunity/decision/momentum/disruption")
    title: str
    description: str
    severity: float = Field(..., ge=0, le=100, description="Importance score (0-100)")
    actionable: bool = Field(default=False)
    related_decision_id: Optional[str] = None
    generated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    
    class Config:
        json_schema_extra = {
            "example": {
                "insight_id": "ins_001",
                "insight_type": "threat",
                "title": "Emerging low-cost EV competitor detected",
                "description": "New startup entering market with $25k EV targeting mass market",
                "severity": 75.0,
                "actionable": True,
                "generated_at": "2024-01-15T10:30:00Z"
            }
        }


class GeographicExpansionOpportunity(BaseModel):
    """Geographic expansion opportunity analysis"""
    region: str
    market_size_usd_millions: float
    growth_rate: float = Field(..., description="Annual growth rate percentage")
    entry_barrier_score: float = Field(..., ge=0, le=100)
    competitive_intensity: float = Field(..., ge=0, le=100)
    recommended_entry_mode: str = Field(..., description="greenfield/acquisition/partnership/franchise")
    estimated_time_to_profitability: int = Field(..., description="Months to profitability")
    risk_factors: List[str] = Field(default_factory=list)
    
    class Config:
        json_schema_extra = {
            "example": {
                "region": "Southeast Asia",
                "market_size_usd_millions": 45000.0,
                "growth_rate": 18.5,
                "entry_barrier_score": 55.0,
                "competitive_intensity": 65.0,
                "recommended_entry_mode": "partnership",
                "estimated_time_to_profitability": 24,
                "risk_factors": ["Regulatory uncertainty", "Local competition"]
            }
        }
