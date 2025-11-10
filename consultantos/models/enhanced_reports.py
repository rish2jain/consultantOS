"""
Enhanced report models for multi-layered, actionable analysis outputs.

This module extends the base models with:
- Detailed framework analysis with scoring and metrics
- Actionable recommendations with timelines and owners
- Risk and opportunity scoring
- Competitive intelligence integration
- Scenario planning
- Multi-layered report structure
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ============================================================================
# ENHANCED FRAMEWORK MODELS
# ============================================================================

class PriorityLevel(str, Enum):
    """Priority levels for recommendations and actions"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Timeline(str, Enum):
    """Action timeline categories"""
    IMMEDIATE = "immediate"  # 0-3 months
    SHORT_TERM = "short_term"  # 3-12 months
    MEDIUM_TERM = "medium_term"  # 12-24 months
    LONG_TERM = "long_term"  # 24+ months


class ImpactLevel(str, Enum):
    """Impact levels for recommendations"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ConfidenceLevel(str, Enum):
    """Confidence levels for findings"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# Enhanced Porter's Five Forces
class PorterForceDetail(BaseModel):
    """Detailed analysis of a single Porter's force"""
    score: float = Field(..., ge=1, le=5, description="Force strength (1=weak, 5=strong)")
    assessment: str = Field(..., description="2-3 sentence analysis")
    barriers_to_entry: Optional[List[str]] = Field(None, description="Specific barriers")
    recent_competitors: Optional[List[str]] = Field(None, description="New entrants in last 2 years")
    entry_speed_analysis: Optional[str] = Field(None, description="How fast can new players enter?")
    capital_requirements: Optional[str] = Field(None, description="Capital needed to compete")
    supplier_concentration: Optional[str] = Field(None, description="Supplier market concentration")
    switching_costs: Optional[str] = Field(None, description="Costs to switch suppliers/buyers")
    substitute_technologies: Optional[List[str]] = Field(None, description="Emerging substitutes")
    performance_comparison: Optional[str] = Field(None, description="How substitutes compare")
    competitive_intensity_score: Optional[float] = Field(None, ge=0, le=10)
    battle_zones: Optional[List[str]] = Field(None, description="Areas of intense competition")
    differentiation_opportunities: Optional[List[str]] = Field(None, description="Ways to differentiate")
    strategic_implications: List[str] = Field(default_factory=list, description="Action items from this force")
    risk_score: Optional[float] = Field(None, ge=0, le=10, description="Risk level (0=low, 10=high)")
    opportunity_score: Optional[float] = Field(None, ge=0, le=10, description="Opportunity level (0=low, 10=high)")


class EnhancedPortersFiveForces(BaseModel):
    """Enhanced Porter's Five Forces with detailed metrics"""
    supplier_power: PorterForceDetail
    buyer_power: PorterForceDetail
    competitive_rivalry: PorterForceDetail
    threat_of_substitutes: PorterForceDetail
    threat_of_new_entrants: PorterForceDetail
    overall_intensity: str = Field(..., description="Low/Moderate/High")
    industry_attractiveness_score: float = Field(..., ge=0, le=100, description="Overall industry score")
    risk_opportunity_matrix: Dict[str, Dict[str, float]] = Field(
        default_factory=dict,
        description="Risk vs opportunity scores for each force"
    )
    strategic_implications: List[str] = Field(default_factory=list, description="Cross-force strategic actions")


# Enhanced SWOT Analysis
class SWOTElement(BaseModel):
    """Individual SWOT element with actionable details"""
    description: str = Field(..., description="The strength/weakness/opportunity/threat")
    importance_score: float = Field(..., ge=1, le=10, description="How important is this element?")
    evidence: List[str] = Field(default_factory=list, description="Supporting evidence")
    strategic_implications: List[str] = Field(default_factory=list, description="What to do about it")
    timeline: Optional[Timeline] = Field(None, description="When to address this")
    impact_level: ImpactLevel = Field(default=ImpactLevel.MEDIUM)
    confidence: ConfidenceLevel = Field(default=ConfidenceLevel.MEDIUM)


class EnhancedSWOTAnalysis(BaseModel):
    """Enhanced SWOT with actionable strategies"""
    strengths: List[SWOTElement] = Field(..., min_length=3)
    weaknesses: List[SWOTElement] = Field(..., min_length=3)
    opportunities: List[SWOTElement] = Field(..., min_length=3)
    threats: List[SWOTElement] = Field(..., min_length=3)
    strengths_to_leverage: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="How to use each strength competitively"
    )
    weaknesses_to_address: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Mitigation strategies for each weakness"
    )
    opportunities_to_pursue: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Prioritized opportunities with impact/feasibility"
    )
    threats_to_monitor: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Early warning indicators for each threat"
    )
    strategic_combinations: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="S+O pairings, W+T mitigations"
    )
    roadmap: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Timeline showing which factors to address first"
    )


# Enhanced PESTEL Analysis
class PESTELFactor(BaseModel):
    """Individual PESTEL factor with trend analysis"""
    factor: str = Field(..., description="The specific factor")
    current_state: str = Field(..., description="Today's landscape")
    trend_direction: str = Field(..., description="Moving favorable/unfavorable?")
    timeline: str = Field(..., description="How soon will changes matter?")
    impact_level: ImpactLevel
    early_warning_signals: List[str] = Field(default_factory=list)
    adaptation_required: List[str] = Field(default_factory=list, description="Specific adjustments needed")
    competitive_advantage: Optional[str] = Field(None, description="How to turn threat into opportunity")
    risk_score: float = Field(..., ge=0, le=10)


class EnhancedPESTELAnalysis(BaseModel):
    """Enhanced PESTEL with trend analysis"""
    political: List[PESTELFactor]
    economic: List[PESTELFactor]
    social: List[PESTELFactor]
    technological: List[PESTELFactor]
    environmental: List[PESTELFactor]
    legal: List[PESTELFactor]
    overall_risk_score: float = Field(..., ge=0, le=10, description="Aggregated risk")


# Enhanced Blue Ocean Strategy
class BlueOceanAction(BaseModel):
    """Individual Blue Ocean action item"""
    action: str = Field(..., description="What to eliminate/reduce/raise/create")
    rationale: str = Field(..., description="Why this action matters")
    estimated_impact: ImpactLevel
    cost_savings: Optional[str] = Field(None, description="If applicable")
    customer_value: Optional[str] = Field(None, description="If applicable")
    implementation_complexity: str = Field(..., description="Low/Medium/High")
    timeline: Timeline


class EnhancedBlueOceanStrategy(BaseModel):
    """Enhanced Blue Ocean with implementation details"""
    eliminate: List[BlueOceanAction]
    reduce: List[BlueOceanAction]
    raise_factors: List[BlueOceanAction] = Field(..., alias="raise")
    create: List[BlueOceanAction]
    strategic_profile_canvas: Dict[str, Any] = Field(
        default_factory=dict,
        description="Current vs future positioning"
    )
    uncontested_market_space: Dict[str, Any] = Field(
        default_factory=dict,
        description="Target customer segments"
    )
    value_innovation: List[str] = Field(default_factory=list, description="New value propositions")
    implementation_roadmap: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Steps to reach Blue Ocean"
    )
    risk_assessment: Dict[str, Any] = Field(
        default_factory=dict,
        description="Cannibalization risks, resource requirements"
    )

    class Config:
        populate_by_name = True


# ============================================================================
# ACTIONABLE RECOMMENDATIONS ENGINE
# ============================================================================

class ActionItem(BaseModel):
    """Individual actionable recommendation"""
    title: str = Field(..., description="Action title")
    description: str = Field(..., description="Detailed description")
    priority: PriorityLevel
    timeline: Timeline
    owner: Optional[str] = Field(None, description="Responsible team/person")
    expected_outcome: str = Field(..., description="What success looks like")
    success_metrics: List[str] = Field(default_factory=list, description="KPIs to track")
    resource_requirements: str = Field(..., description="Low/Medium/High")
    potential_impact: ImpactLevel
    risks: List[str] = Field(default_factory=list, description="Potential risks or dependencies")
    related_findings: List[str] = Field(default_factory=list, description="Which findings support this")


class RecommendationGroup(BaseModel):
    """Grouped recommendations by timeline"""
    timeline: Timeline
    actions: List[ActionItem]
    total_impact: ImpactLevel
    estimated_resources: str


class ActionableRecommendations(BaseModel):
    """Structured actionable recommendations"""
    immediate_actions: List[ActionItem] = Field(default_factory=list, description="0-3 months")
    short_term_actions: List[ActionItem] = Field(default_factory=list, description="3-12 months")
    medium_term_actions: List[ActionItem] = Field(default_factory=list, description="12-24 months")
    long_term_actions: List[ActionItem] = Field(default_factory=list, description="24+ months")
    critical_actions: List[ActionItem] = Field(default_factory=list, description="Top priority items")
    grouped_by_owner: Dict[str, List[ActionItem]] = Field(
        default_factory=dict,
        description="Actions grouped by responsible party"
    )


# ============================================================================
# RISK & OPPORTUNITY SCORING
# ============================================================================

class RiskItem(BaseModel):
    """Individual risk assessment"""
    title: str
    description: str
    likelihood: float = Field(..., ge=0, le=10, description="How likely (0-10)")
    impact: ImpactLevel
    risk_score: float = Field(..., ge=0, le=10, description="Overall risk score")
    mitigation_strategies: List[str] = Field(default_factory=list)
    early_warning_indicators: List[str] = Field(default_factory=list)
    related_factors: List[str] = Field(default_factory=list)


class OpportunityItem(BaseModel):
    """Individual opportunity assessment"""
    title: str
    description: str
    impact_potential: float = Field(..., ge=1, le=10, description="Potential impact (1-10)")
    feasibility: float = Field(..., ge=1, le=10, description="Ease of execution (1-10)")
    timeline_to_value: int = Field(..., description="Months to realize value")
    resource_requirements: str = Field(..., description="Low/Medium/High")
    strategic_fit: float = Field(..., ge=0, le=100, description="Alignment %")
    competitive_advantage_strength: float = Field(..., ge=1, le=10)
    priority_score: float = Field(..., ge=0, le=10, description="Impact × Feasibility")


class RiskOpportunityMatrix(BaseModel):
    """Risk and opportunity assessment"""
    risks: List[RiskItem]
    opportunities: List[OpportunityItem]
    risk_heatmap: Dict[str, Dict[str, float]] = Field(
        default_factory=dict,
        description="Likelihood vs Impact matrix"
    )
    opportunity_prioritization: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Ranked by Impact vs Effort"
    )


# ============================================================================
# COMPETITIVE INTELLIGENCE
# ============================================================================

class CompetitorAnalysis(BaseModel):
    """Competitor comparison"""
    competitor_name: str
    market_share: Optional[float] = Field(None, description="Market share %")
    key_strengths: List[str]
    key_weaknesses: List[str]
    pricing_strategy: Optional[str] = None
    recent_movements: List[str] = Field(default_factory=list, description="Recent announcements")
    talent_movement: List[str] = Field(default_factory=list, description="Key hires/departures")
    patent_activity: Optional[str] = None
    social_sentiment: Optional[float] = Field(None, ge=-1, le=1, description="Sentiment score")


class CompetitiveIntelligence(BaseModel):
    """Competitive intelligence integration"""
    competitor_matrix: List[CompetitorAnalysis]
    market_share_visualization: Dict[str, float] = Field(
        default_factory=dict,
        description="Company: market_share mapping"
    )
    pricing_analysis: Dict[str, Any] = Field(
        default_factory=dict,
        description="Price positioning data"
    )
    feature_comparison: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Feature comparison matrix"
    )
    recent_news: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Competitor news impacting landscape"
    )


# ============================================================================
# SCENARIO PLANNING
# ============================================================================

class Scenario(BaseModel):
    """Strategic scenario analysis"""
    name: str = Field(..., description="Optimistic/Base/Pessimistic")
    probability: float = Field(..., ge=0, le=1, description="Probability of scenario")
    description: str
    key_assumptions: List[str]
    trigger_events: List[str] = Field(default_factory=list, description="Events that would trigger this")
    strategic_adjustments: List[str] = Field(default_factory=list)
    contingency_plans: List[str] = Field(default_factory=list)
    early_warning_signals: List[str] = Field(default_factory=list)
    financial_projections: Dict[str, Any] = Field(
        default_factory=dict,
        description="Revenue, growth, etc."
    )


class ScenarioPlanning(BaseModel):
    """Multiple scenario analysis"""
    optimistic_scenario: Scenario
    base_scenario: Scenario
    pessimistic_scenario: Scenario
    scenario_comparison: Dict[str, Any] = Field(
        default_factory=dict,
        description="Side-by-side comparison"
    )


# ============================================================================
# MULTI-LAYERED REPORT STRUCTURE
# ============================================================================

class ExecutiveSummaryLayer(BaseModel):
    """1-page executive summary"""
    company_overview: Dict[str, Any] = Field(
        default_factory=dict,
        description="Name, industry, size, key metrics"
    )
    analysis_date: datetime
    analysis_scope: str = Field(..., description="What was analyzed and why")
    key_findings: List[str] = Field(..., min_length=3, max_length=5)
    strategic_recommendations: List[str] = Field(..., min_length=3, max_length=5)
    confidence_score: float = Field(..., ge=0, le=1)
    methodology_note: str = Field(..., description="Transparency on analysis quality")
    next_steps: List[str]
    visual_dashboard: Dict[str, Any] = Field(
        default_factory=dict,
        description="Key metrics visualization data"
    )


class DetailedAnalysisLayer(BaseModel):
    """Detailed framework breakdown"""
    framework_breakdowns: Dict[str, Any] = Field(
        default_factory=dict,
        description="Full framework narratives"
    )
    supporting_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Evidence and data"
    )
    cross_framework_insights: List[str] = Field(
        default_factory=list,
        description="Connections between frameworks"
    )
    risk_assessments: Dict[str, Any] = Field(
        default_factory=dict,
        description="Risk analysis"
    )
    opportunities: Dict[str, Any] = Field(
        default_factory=dict,
        description="Opportunity analysis"
    )


class SupportingAppendices(BaseModel):
    """Report appendices"""
    data_sources: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Sources and methodology"
    )
    detailed_metrics: Dict[str, Any] = Field(
        default_factory=dict,
        description="Scoring rationale"
    )
    alternative_scenarios: Optional[ScenarioPlanning] = None
    reference_materials: List[str] = Field(default_factory=list)
    frameworks_applied: List[str] = Field(default_factory=list)


class EnhancedStrategicReport(BaseModel):
    """Multi-layered enhanced strategic report"""
    executive_summary_layer: ExecutiveSummaryLayer
    detailed_analysis_layer: DetailedAnalysisLayer
    supporting_appendices: SupportingAppendices
    actionable_recommendations: ActionableRecommendations
    risk_opportunity_matrix: RiskOpportunityMatrix
    competitive_intelligence: Optional[CompetitiveIntelligence] = None
    scenario_planning: Optional[ScenarioPlanning] = None
    confidence_indicators: Dict[str, ConfidenceLevel] = Field(
        default_factory=dict,
        description="Confidence level for each finding"
    )
    quality_metrics: Dict[str, Any] = Field(
        default_factory=dict,
        description="Data completeness, analysis depth, etc."
    )
    metadata: Dict[str, Any] = Field(default_factory=dict)

