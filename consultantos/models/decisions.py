"""
Strategic decision intelligence models
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class DecisionUrgency(str, Enum):
    """Decision urgency levels"""
    CRITICAL = "critical"  # Immediate action required
    HIGH = "high"  # Action needed within weeks
    MEDIUM = "medium"  # Action needed within months
    LOW = "low"  # Strategic consideration


class DecisionCategory(str, Enum):
    """Types of strategic decisions"""
    MARKET_ENTRY = "market_entry"
    PRODUCT_LAUNCH = "product_launch"
    PRICING = "pricing"
    PARTNERSHIP = "partnership"
    ACQUISITION = "acquisition"
    DIVESTITURE = "divestiture"
    INVESTMENT = "investment"
    ORGANIZATIONAL = "organizational"
    TECHNOLOGY = "technology"
    GEOGRAPHIC_EXPANSION = "geographic_expansion"


class DecisionOption(BaseModel):
    """Individual decision option with ROI modeling"""
    option_id: str
    option_name: str
    description: str

    # Financial modeling
    investment_required: float = Field(default=0.0, description="Upfront investment in USD")
    expected_annual_return: float = Field(default=0.0, description="Expected annual return in USD")
    roi_multiple: float = Field(default=1.0, ge=0, description="Return multiple (e.g., 2.8x)")
    payback_period_months: int = Field(default=12, ge=1, description="Months to recover investment")

    # Outcome analysis
    expected_impact: str = Field(..., description="Expected business impact")
    success_probability: float = Field(..., ge=0, le=100, description="Likelihood of success (0-100)")
    implementation_cost: str = Field(..., description="Resource requirements (low/medium/high)")
    time_to_value: str = Field(..., description="Time to realize benefits")
    timeline_days: int = Field(default=365, ge=1, description="Implementation timeline in days")

    # Risk assessment
    risks: List[str] = Field(default_factory=list)
    risk_level: str = Field(default="Medium", description="Risk level: Low/Medium/High")
    mitigation_strategies: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)

    # Strategic alignment
    strategic_fit: float = Field(..., ge=0, le=100, description="Alignment with strategy (0-100)")
    competitive_advantage: str = Field(..., description="How this creates advantage")
    implementation_steps: List[str] = Field(default_factory=list, description="Key implementation steps")

    class Config:
        json_schema_extra = {
            "example": {
                "option_id": "opt_001",
                "option_name": "Launch budget EV model",
                "description": "Develop and launch mass-market EV under $30k",
                "expected_impact": "Expand TAM by 3x, capture 15% mass market",
                "success_probability": 70.0,
                "implementation_cost": "high",
                "time_to_value": "24-36 months",
                "risks": ["Manufacturing scale challenges", "Margin compression"],
                "strategic_fit": 95.0,
                "competitive_advantage": "First-mover in affordable premium EV"
            }
        }


class StrategicDecision(BaseModel):
    """Strategic decision requiring action"""
    decision_id: str
    decision_category: DecisionCategory
    urgency: DecisionUrgency

    # Decision context
    decision_question: str = Field(..., description="The strategic question to answer")
    context: str = Field(..., description="Background and situational context")
    stakes: str = Field(..., description="What's at risk")

    # Options analysis
    options: List[DecisionOption] = Field(default_factory=list)
    recommended_option: Optional[str] = None  # option_id of recommendation

    # Decision support
    key_assumptions: List[str] = Field(default_factory=list)
    success_metrics: List[str] = Field(default_factory=list)
    decision_criteria: List[str] = Field(default_factory=list)

    # Framework insights
    porter_analysis: Optional[str] = None
    christensen_analysis: Optional[str] = None
    taleb_antifragility: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "decision_id": "dec_001",
                "decision_category": "product_launch",
                "urgency": "high",
                "decision_question": "Should we launch a mass-market EV now?",
                "context": "Premium segment saturating, competitors entering",
                "stakes": "Market leadership vs. margin protection",
                "options": [],
                "recommended_option": "opt_001",
                "key_assumptions": ["Demand exists at <$30k price point"],
                "success_metrics": ["Unit volume >200k/year", "Margin >15%"]
            }
        }


class DecisionBrief(BaseModel):
    """Executive decision brief"""
    company: str
    generated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    # Top decisions
    critical_decisions: List[StrategicDecision] = Field(default_factory=list)
    high_priority_decisions: List[StrategicDecision] = Field(default_factory=list)

    # Quick insights
    top_decision: Optional[StrategicDecision] = None
    decision_count: int = Field(default=0)

    # Synthesis
    strategic_themes: List[str] = Field(default_factory=list, description="Common themes across decisions")
    resource_conflicts: List[str] = Field(default_factory=list, description="Competing resource demands")

    # Metadata
    confidence_score: float = Field(default=0.0, ge=0, le=100)

    class Config:
        json_schema_extra = {
            "example": {
                "company": "Tesla",
                "critical_decisions": [],
                "high_priority_decisions": [],
                "decision_count": 3,
                "strategic_themes": ["Market expansion", "Cost reduction"],
                "resource_conflicts": ["R&D budget allocation"],
                "confidence_score": 82.0
            }
        }
