"""
Disruption analysis models for detecting competitive threats and vulnerabilities
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional


class DisruptionThreat(BaseModel):
    """
    Individual disruption threat analysis.

    Attributes:
        threat_name: Name/description of the disruptive threat
        disruption_score: Overall disruption risk (0-100)
        growth_velocity: Growth rate relative to industry average (multiplier)
        business_model: Business model type (subscription/platform/marketplace/etc.)
        customer_jobs: Jobs-to-be-Done that this threat addresses
        timeline_to_impact: Estimated days until material market impact
        recommended_response: Strategic response recommendation
        threat_indicators: Key signals indicating this threat
    """
    threat_name: str = Field(..., description="Name of the disruptive threat")
    disruption_score: float = Field(..., ge=0, le=100, description="Disruption risk score (0-100)")
    growth_velocity: float = Field(..., description="Growth multiplier vs industry average")
    business_model: str = Field(..., description="Business model type")
    customer_jobs: List[str] = Field(..., description="Customer jobs being addressed")
    timeline_to_impact: int = Field(..., description="Days until material impact")
    recommended_response: str = Field(..., description="Strategic response")
    threat_indicators: List[str] = Field(..., description="Key threat signals")


class VulnerabilityBreakdown(BaseModel):
    """
    Breakdown of disruption vulnerability by component.

    Attributes:
        incumbent_overserving: Score for overserving customers (0-100)
        asymmetric_threat_velocity: Score for fast-growing asymmetric threats (0-100)
        technology_shift: Score for technology adoption momentum (0-100)
        customer_job_misalignment: Score for job-to-be-done misalignment (0-100)
        business_model_innovation: Score for business model disruption risk (0-100)
    """
    incumbent_overserving: float = Field(..., ge=0, le=100, description="Overserving score (0-100)")
    asymmetric_threat_velocity: float = Field(..., ge=0, le=100, description="Threat velocity (0-100)")
    technology_shift: float = Field(..., ge=0, le=100, description="Tech shift momentum (0-100)")
    customer_job_misalignment: float = Field(..., ge=0, le=100, description="Job misalignment (0-100)")
    business_model_innovation: float = Field(..., ge=0, le=100, description="Model innovation (0-100)")


class TechnologyTrend(BaseModel):
    """
    Emerging technology trend analysis.

    Attributes:
        technology: Technology name/category
        keyword_velocity: Search trend velocity (% change)
        adoption_rate: Competitor adoption percentage
        enabler_score: Score as enabling technology (0-100)
        maturity_stage: Technology maturity (emerging/growing/mature/declining)
    """
    technology: str = Field(..., description="Technology name")
    keyword_velocity: float = Field(..., description="Search trend velocity (%)")
    adoption_rate: float = Field(..., ge=0, le=100, description="Competitor adoption (%)")
    enabler_score: float = Field(..., ge=0, le=100, description="Enabler potential (0-100)")
    maturity_stage: str = Field(..., description="Maturity: emerging/growing/mature/declining")


class CustomerJobMisalignment(BaseModel):
    """
    Customer jobs-to-be-done misalignment analysis.

    Attributes:
        job_description: Description of customer job
        misalignment_score: Degree of misalignment (0-100)
        alternative_searches: "Alternative to X" search patterns
        pain_points: Identified customer pain points
        opportunity_size: Market opportunity size (USD millions)
    """
    job_description: str = Field(..., description="Customer job description")
    misalignment_score: float = Field(..., ge=0, le=100, description="Misalignment (0-100)")
    alternative_searches: List[str] = Field(..., description="Alternative search patterns")
    pain_points: List[str] = Field(..., description="Customer pain points")
    opportunity_size: float = Field(..., description="Opportunity size (USD millions)")


class BusinessModelShift(BaseModel):
    """
    Business model innovation trend.

    Attributes:
        model_type: Type of business model (subscription/platform/marketplace/etc.)
        shift_velocity: Rate of shift toward this model (% per year)
        competitive_adoption: Percentage of competitors adopting
        value_network_impact: Impact on value network (high/medium/low)
        disruption_potential: Potential to disrupt incumbent (0-100)
    """
    model_type: str = Field(..., description="Business model type")
    shift_velocity: float = Field(..., description="Shift rate (% per year)")
    competitive_adoption: float = Field(..., ge=0, le=100, description="Competitor adoption (%)")
    value_network_impact: str = Field(..., description="Value network impact: high/medium/low")
    disruption_potential: float = Field(..., ge=0, le=100, description="Disruption potential (0-100)")


class DisruptionAssessment(BaseModel):
    """
    Comprehensive disruption vulnerability assessment.

    Main output from DisruptionAgent analyzing disruption risk across
    multiple dimensions with Christensen's disruption theory framework.
    """
    company: str = Field(..., description="Company being analyzed")
    industry: str = Field(..., description="Industry sector")

    # Overall risk metrics
    overall_risk: float = Field(..., ge=0, le=100, description="Overall disruption risk (0-100)")
    risk_trend: float = Field(..., description="30-day risk delta")
    risk_level: str = Field(..., description="Risk level: critical/high/medium/low")

    # Primary threats
    primary_threats: List[DisruptionThreat] = Field(..., description="Top disruption threats")

    # Vulnerability breakdown
    vulnerability_breakdown: VulnerabilityBreakdown = Field(..., description="Risk component scores")

    # Technology analysis
    technology_trends: List[TechnologyTrend] = Field(default_factory=list, description="Emerging tech trends")

    # Customer job analysis
    job_misalignments: List[CustomerJobMisalignment] = Field(default_factory=list, description="JTBD gaps")

    # Business model shifts
    model_shifts: List[BusinessModelShift] = Field(default_factory=list, description="Model innovations")

    # Strategic recommendations
    strategic_recommendations: List[str] = Field(..., description="Response strategies")
    early_warning_signals: List[str] = Field(..., description="Signals to monitor")

    # Metadata
    confidence_score: float = Field(..., ge=0, le=100, description="Analysis confidence (0-100)")
    data_sources: List[str] = Field(default_factory=list, description="Data source URLs")
    generated_at: str = Field(..., description="ISO timestamp")


class DisruptionScoreComponents(BaseModel):
    """
    Detailed breakdown of disruption score calculation.

    Used for transparency and debugging of disruption scoring.
    """
    overserving_score: float = Field(..., ge=0, le=30, description="Overserving component (0-30)")
    threat_velocity_score: float = Field(..., ge=0, le=25, description="Threat velocity (0-25)")
    tech_momentum_score: float = Field(..., ge=0, le=20, description="Tech momentum (0-20)")
    job_misalignment_score: float = Field(..., ge=0, le=15, description="Job misalignment (0-15)")
    model_innovation_score: float = Field(..., ge=0, le=10, description="Model innovation (0-10)")
    total_score: float = Field(..., ge=0, le=100, description="Total disruption score (0-100)")

    # Calculation metadata
    weights_used: Dict[str, float] = Field(..., description="Component weights")
    calculation_notes: str = Field(default="", description="Calculation methodology notes")
