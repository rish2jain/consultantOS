"""
Evidence-based models for enforcing specificity in analysis outputs.
These models require concrete metrics and evidence for every claim.
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime


# ============================================================================
# EVIDENCE SUBMODELS - Building blocks for specific claims
# ============================================================================

class MetricEvidence(BaseModel):
    """A specific metric with value and context"""
    metric_name: str = Field(..., description="e.g., 'Market Share', 'Revenue Growth'")
    value: Union[float, str] = Field(..., description="Actual value, e.g., 45.2, '$15B'")
    unit: Optional[str] = Field(None, description="Unit of measurement, e.g., '%', 'USD', 'users'")
    comparison: Optional[str] = Field(None, description="vs competitors/industry avg, e.g., 'vs industry avg 23%'")
    time_period: Optional[str] = Field(None, description="Time period for metric, e.g., 'Q3 2024', 'YoY'")
    source: Optional[str] = Field(None, description="Data source")

    @field_validator('value')
    def value_not_empty(cls, v):
        if isinstance(v, str) and not v.strip():
            raise ValueError('Value cannot be empty')
        return v


class CompetitorComparison(BaseModel):
    """Specific competitor comparison data"""
    competitor_name: str = Field(..., description="Competitor company name")
    metric: str = Field(..., description="What's being compared")
    our_value: Union[float, str] = Field(..., description="Our company's value")
    their_value: Union[float, str] = Field(..., description="Competitor's value")
    advantage: str = Field(..., description="Who has advantage and by how much")


class TrendData(BaseModel):
    """Trend with specific data points"""
    trend_name: str = Field(..., description="Name of trend")
    direction: str = Field(..., description="Rising/Falling/Stable")
    change_rate: Optional[float] = Field(None, description="Rate of change, e.g., 15.3")
    change_unit: Optional[str] = Field(None, description="Unit for change, e.g., '% YoY'")
    data_points: Optional[List[Dict[str, Any]]] = Field(None, description="Time series data points")
    impact: str = Field(..., description="Specific impact on company")


class RiskAssessment(BaseModel):
    """Quantified risk with likelihood and impact"""
    risk_factor: str = Field(..., description="Specific risk description")
    likelihood: float = Field(..., ge=0, le=1, description="Probability (0-1)")
    impact_score: float = Field(..., ge=1, le=10, description="Impact severity (1-10)")
    mitigation: str = Field(..., description="Specific mitigation strategy")
    evidence: str = Field(..., description="Why this risk exists - cite specific data")


# ============================================================================
# ENHANCED FRAMEWORK MODELS WITH REQUIRED EVIDENCE
# ============================================================================

class PorterForceDetail(BaseModel):
    """Detailed analysis of a single Porter's force"""
    force_name: str = Field(..., description="Name of the force")
    score: float = Field(..., ge=1, le=5, description="Force intensity (1=weak, 5=strong)")
    key_factors: List[str] = Field(..., min_length=2, max_length=5, description="Specific contributing factors")
    metrics: List[MetricEvidence] = Field(..., min_length=1, description="Supporting metrics")
    competitive_implication: str = Field(..., description="What this means for strategy")


class EnhancedPortersFiveForces(BaseModel):
    """Porter's Five Forces with required evidence"""
    supplier_power: PorterForceDetail
    buyer_power: PorterForceDetail
    competitive_rivalry: PorterForceDetail
    threat_of_substitutes: PorterForceDetail
    threat_of_new_entrants: PorterForceDetail
    overall_intensity: str = Field(..., description="Low/Moderate/High")
    strategic_position: str = Field(..., description="Company's position given these forces")
    key_battlegrounds: List[str] = Field(..., min_length=2, description="Where competition is most intense")


class SWOTItem(BaseModel):
    """Individual SWOT item with evidence"""
    statement: str = Field(..., description="The strength/weakness/opportunity/threat")
    evidence: MetricEvidence = Field(..., description="Supporting metric or data")
    impact: str = Field(..., description="Strategic impact or implication")

    @field_validator('statement')
    def statement_not_generic(cls, v):
        generic_terms = ['good', 'strong', 'weak', 'poor', 'high', 'low']
        if any(v.lower().startswith(term) for term in generic_terms) and len(v) < 20:
            raise ValueError(f'Statement too generic: {v}. Provide specific details.')
        return v


class EnhancedSWOTAnalysis(BaseModel):
    """SWOT with required evidence for each item"""
    strengths: List[SWOTItem] = Field(..., min_length=3, max_length=5)
    weaknesses: List[SWOTItem] = Field(..., min_length=3, max_length=5)
    opportunities: List[SWOTItem] = Field(..., min_length=3, max_length=5)
    threats: List[SWOTItem] = Field(..., min_length=3, max_length=5)
    strategic_options: List[str] = Field(..., min_length=2, description="S-O, W-T strategies")


class PESTELFactor(BaseModel):
    """PESTEL factor with specific impact assessment"""
    factor: str = Field(..., description="Specific factor description")
    current_state: str = Field(..., description="Current situation with data")
    trend: TrendData = Field(..., description="How this is changing")
    impact_on_company: str = Field(..., description="Specific impact with metrics")
    time_horizon: str = Field(..., description="When this will impact: immediate/1yr/3yr/5yr")


class EnhancedPESTELAnalysis(BaseModel):
    """PESTEL with trend data and impact assessment"""
    political: List[PESTELFactor] = Field(..., min_length=2, max_length=3)
    economic: List[PESTELFactor] = Field(..., min_length=2, max_length=3)
    social: List[PESTELFactor] = Field(..., min_length=2, max_length=3)
    technological: List[PESTELFactor] = Field(..., min_length=2, max_length=3)
    environmental: List[PESTELFactor] = Field(..., min_length=1, max_length=3)
    legal: List[PESTELFactor] = Field(..., min_length=1, max_length=3)
    critical_factors: List[str] = Field(..., min_length=3, description="Top 3 factors by impact")


class BlueOceanAction(BaseModel):
    """Blue Ocean action with specific metrics"""
    action: str = Field(..., description="What to eliminate/reduce/raise/create")
    current_level: Optional[MetricEvidence] = Field(None, description="Current state if applicable")
    target_level: Optional[MetricEvidence] = Field(None, description="Target state if applicable")
    rationale: str = Field(..., description="Why this creates value")
    implementation_cost: str = Field(..., description="Resource requirements: Low/Medium/High")


class EnhancedBlueOceanStrategy(BaseModel):
    """Blue Ocean with value curve and implementation details"""
    eliminate: List[BlueOceanAction] = Field(..., min_length=2)
    reduce: List[BlueOceanAction] = Field(..., min_length=2)
    raise_factors: List[BlueOceanAction] = Field(..., min_length=2)
    create: List[BlueOceanAction] = Field(..., min_length=2)
    value_innovation: str = Field(..., description="How this creates new market space")
    target_segment: str = Field(..., description="Specific customer segment with size")
    differentiation_score: float = Field(..., ge=1, le=10, description="How different from competition")


# ============================================================================
# ENHANCED SYNTHESIS WITH EVIDENCE REQUIREMENTS
# ============================================================================

class KeyFinding(BaseModel):
    """A key finding with full evidence chain"""
    finding: str = Field(..., description="The insight or conclusion")
    confidence: float = Field(..., ge=0, le=1, description="Confidence level (0-1)")
    supporting_data: List[MetricEvidence] = Field(..., min_length=2, description="Supporting metrics")
    source_frameworks: List[str] = Field(..., description="Which frameworks support this")
    strategic_implication: str = Field(..., description="What this means for strategy")


class StrategicRecommendation(BaseModel):
    """Recommendation with implementation details"""
    recommendation: str = Field(..., description="What to do")
    priority: str = Field(..., description="High/Medium/Low")
    rationale: List[str] = Field(..., min_length=2, description="Why (with evidence)")
    expected_impact: MetricEvidence = Field(..., description="Quantified expected outcome")
    implementation_timeline: str = Field(..., description="Specific timeline")
    resources_required: str = Field(..., description="What's needed")
    success_metrics: List[str] = Field(..., min_length=2, description="How to measure success")
    risks: List[RiskAssessment] = Field(..., min_length=1, description="Implementation risks")


class EnhancedExecutiveSummary(BaseModel):
    """Executive summary with mandatory evidence"""
    company_name: str
    industry: str
    analysis_date: datetime = Field(default_factory=datetime.now)
    market_position: MetricEvidence = Field(..., description="Current market position")
    competitive_advantage: str = Field(..., min_length=50, description="Core differentiation")
    key_findings: List[KeyFinding] = Field(..., min_length=3, max_length=5)
    primary_recommendation: StrategicRecommendation
    secondary_recommendations: List[StrategicRecommendation] = Field(..., min_length=2)
    confidence_score: float = Field(..., ge=0, le=1)
    data_quality_assessment: Dict[str, float] = Field(..., description="Quality scores by data source")
    critical_assumptions: List[str] = Field(..., min_length=2, description="Key assumptions made")


# ============================================================================
# VALIDATION HELPERS
# ============================================================================

class InsightValidator:
    """Validates insights for specificity and evidence"""

    GENERIC_TERMS = [
        'good', 'bad', 'strong', 'weak', 'high', 'low', 'positive', 'negative',
        'significant', 'important', 'notable', 'considerable', 'substantial'
    ]

    REQUIRED_EVIDENCE_PATTERNS = [
        r'\d+\.?\d*\s*%',  # Percentages
        r'\$\d+\.?\d*[BMK]?',  # Dollar amounts
        r'\d+\.?\d*[xX]',  # Multipliers
        r'#\d+',  # Rankings
        r'\d{4}',  # Years
        r'Q[1-4]\s*\d{4}',  # Quarters
        r'\d+\.?\d*\s*(million|billion|thousand)',  # Large numbers
    ]

    @classmethod
    def validate_specificity(cls, text: str, min_length: int = 20) -> bool:
        """Check if text is specific enough"""
        # Too short
        if len(text) < min_length:
            return False

        # Starts with generic term
        for term in cls.GENERIC_TERMS:
            if text.lower().startswith(term + ' '):
                return False

        # Has no numbers or specifics
        import re
        has_evidence = any(re.search(pattern, text) for pattern in cls.REQUIRED_EVIDENCE_PATTERNS)

        return has_evidence

    @classmethod
    def validate_finding(cls, finding: KeyFinding) -> bool:
        """Validate a key finding has proper evidence"""
        # Finding must be specific
        if not cls.validate_specificity(finding.finding, min_length=30):
            return False

        # Must have at least 2 supporting metrics
        if len(finding.supporting_data) < 2:
            return False

        # Each metric must have a value
        for metric in finding.supporting_data:
            if not metric.value:
                return False

        return True

    @classmethod
    def generate_quality_report(cls, summary: EnhancedExecutiveSummary) -> Dict[str, Any]:
        """Generate quality assessment of the analysis"""
        report = {
            'overall_quality': 0.0,
            'specificity_score': 0.0,
            'evidence_score': 0.0,
            'completeness_score': 0.0,
            'issues': [],
            'strengths': []
        }

        # Check each finding
        valid_findings = 0
        for finding in summary.key_findings:
            if cls.validate_finding(finding):
                valid_findings += 1
            else:
                report['issues'].append(f"Finding lacks evidence: {finding.finding[:50]}...")

        report['evidence_score'] = valid_findings / len(summary.key_findings)

        # Check recommendations
        for rec in [summary.primary_recommendation] + summary.secondary_recommendations:
            if rec.expected_impact and rec.expected_impact.value:
                report['strengths'].append(f"Quantified impact: {rec.expected_impact.metric_name}")
            else:
                report['issues'].append(f"Recommendation lacks quantified impact: {rec.recommendation[:50]}...")

        # Overall score
        report['overall_quality'] = (
            report['evidence_score'] * 0.5 +
            summary.confidence_score * 0.3 +
            (1.0 if len(report['issues']) < 3 else 0.5) * 0.2
        )

        return report