"""
System dynamics models for strategic intelligence
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class LoopType(str, Enum):
    """Feedback loop types"""
    REINFORCING = "reinforcing"  # Amplifies change (virtuous/vicious cycles)
    BALANCING = "balancing"  # Resists change (equilibrium-seeking)


class CausalLink(BaseModel):
    """Causal relationship between system elements"""
    from_element: str
    to_element: str
    polarity: str = Field(..., description="+ (same direction) or - (opposite direction)")
    strength: float = Field(..., ge=0, le=100, description="Relationship strength (0-100)")
    delay: str = Field(..., description="Time delay (none/short/medium/long)")
    description: str

    class Config:
        json_schema_extra = {
            "example": {
                "from_element": "Brand perception",
                "to_element": "Sales volume",
                "polarity": "+",
                "strength": 85.0,
                "delay": "short",
                "description": "Strong brand drives sales with minimal delay"
            }
        }


class FeedbackLoop(BaseModel):
    """System feedback loop"""
    loop_id: str
    loop_name: str
    loop_type: LoopType

    # Loop structure
    elements: List[str] = Field(..., description="Elements in the loop sequence")
    causal_links: List[CausalLink] = Field(default_factory=list)

    # Loop dynamics
    strength: float = Field(..., ge=0, le=100, description="Overall loop strength (0-100)")
    dominant: bool = Field(default=False, description="Is this the dominant loop?")
    time_constant: str = Field(..., description="How fast the loop operates")

    # Strategic implications
    current_state: str = Field(..., description="Current loop behavior (growing/declining/stable)")
    impact: str = Field(..., description="Business impact of this loop")
    intervention_points: List[str] = Field(default_factory=list, description="Where to intervene")

    class Config:
        json_schema_extra = {
            "example": {
                "loop_id": "R1",
                "loop_name": "Quality reputation flywheel",
                "loop_type": "reinforcing",
                "elements": ["Product quality", "Customer satisfaction", "Word of mouth", "New customers", "Revenue", "R&D investment"],
                "strength": 78.0,
                "dominant": True,
                "time_constant": "6-12 months",
                "current_state": "growing",
                "impact": "Primary growth driver",
                "intervention_points": ["Accelerate R&D investment", "Amplify word of mouth"]
            }
        }


class LeveragePoint(BaseModel):
    """Meadows' leverage points for system intervention"""
    leverage_id: str
    leverage_name: str
    leverage_level: int = Field(..., ge=1, le=12, description="Meadows' 12 levels (1=highest)")

    # Context
    description: str
    current_state: str
    proposed_intervention: str

    # Impact assessment
    impact_potential: float = Field(..., ge=0, le=100, description="Potential impact (0-100)")
    implementation_difficulty: float = Field(..., ge=0, le=100, description="Implementation difficulty (0-100)")
    time_to_impact: str = Field(..., description="Time to see results")

    # Strategic fit
    strategic_priority: str = Field(..., description="Priority: critical/high/medium/low")
    dependencies: List[str] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "leverage_id": "lp_001",
                "leverage_name": "Shift mindset from quarterly to long-term value",
                "leverage_level": 2,
                "description": "Change organizational paradigm from short-term optimization to long-term value creation",
                "current_state": "Heavy quarterly earnings focus",
                "proposed_intervention": "Implement long-term value metrics in exec compensation",
                "impact_potential": 95.0,
                "implementation_difficulty": 80.0,
                "time_to_impact": "12-24 months",
                "strategic_priority": "critical"
            }
        }


class SystemDynamicsAnalysis(BaseModel):
    """Complete system dynamics analysis"""
    company: str
    industry: str
    generated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    # System structure
    key_variables: List[str] = Field(default_factory=list, description="Important system variables")
    causal_links: List[CausalLink] = Field(default_factory=list)

    # Feedback loops
    reinforcing_loops: List[FeedbackLoop] = Field(default_factory=list)
    balancing_loops: List[FeedbackLoop] = Field(default_factory=list)
    dominant_loop: Optional[str] = None  # loop_id

    # Leverage analysis
    leverage_points: List[LeveragePoint] = Field(default_factory=list)
    high_leverage_interventions: List[str] = Field(default_factory=list)

    # System behavior
    system_archetype: Optional[str] = None  # e.g., "limits to growth", "shifting the burden"
    current_behavior: str = Field(default="", description="Overall system behavior pattern")
    unintended_consequences: List[str] = Field(default_factory=list)

    # Strategic insights
    structural_issues: List[str] = Field(default_factory=list)
    quick_fixes_to_avoid: List[str] = Field(default_factory=list)
    fundamental_solutions: List[str] = Field(default_factory=list)

    # Metadata
    confidence_score: float = Field(default=0.0, ge=0, le=100)
    data_sources: List[str] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "company": "Tesla",
                "industry": "Electric Vehicles",
                "key_variables": ["Production capacity", "Demand", "Brand value", "Technology lead"],
                "dominant_loop": "R1",
                "system_archetype": "success to the successful",
                "current_behavior": "Reinforcing growth with emerging capacity constraints",
                "high_leverage_interventions": ["Shift to modular manufacturing", "Invest in vertical integration"],
                "structural_issues": ["Single-factory dependency creates bottleneck"],
                "confidence_score": 75.0
            }
        }
