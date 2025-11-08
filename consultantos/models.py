"""
Data models for ConsultantOS using Pydantic
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


# ============================================================================
# INPUT MODELS
# ============================================================================

class AnalysisRequest(BaseModel):
    """User request for strategic analysis"""
    company: str = Field(..., description="Company name or ticker symbol")
    industry: Optional[str] = Field(None, description="Industry sector (optional, will be auto-detected)")
    frameworks: List[str] = Field(
        default=["porter", "swot", "pestel", "blue_ocean"],
        description="Frameworks to apply"
    )
    depth: str = Field(default="standard", description="Analysis depth: quick/standard/deep")


# ============================================================================
# AGENT OUTPUT MODELS
# ============================================================================

class CompanyResearch(BaseModel):
    """Research agent output"""
    company_name: str
    description: str = Field(..., description="Company overview")
    products_services: List[str]
    target_market: str
    key_competitors: List[str]
    recent_news: List[str]
    sources: List[str] = Field(..., description="Citation URLs")


class MarketTrends(BaseModel):
    """Market analyst output"""
    search_interest_trend: str = Field(..., description="Growing/Stable/Declining")
    interest_data: Dict[str, Any] = Field(..., description="Time series data")
    geographic_distribution: Dict[str, Any]
    related_searches: List[str]
    competitive_comparison: Dict[str, Any] = Field(..., description="Company vs competitors")


class FinancialSnapshot(BaseModel):
    """Financial analyst output"""
    ticker: str
    market_cap: Optional[float] = None
    revenue: Optional[float] = Field(None, description="Latest annual revenue")
    revenue_growth: Optional[float] = Field(None, description="YoY growth percentage")
    profit_margin: Optional[float] = None
    pe_ratio: Optional[float] = None
    key_metrics: Dict[str, Any] = Field(default_factory=dict, description="Additional financial metrics")
    risk_assessment: str


# ============================================================================
# FRAMEWORK MODELS
# ============================================================================

class PortersFiveForces(BaseModel):
    """Porter's 5 Forces analysis"""
    supplier_power: float = Field(..., ge=1, le=5, description="1=weak, 5=strong")
    buyer_power: float = Field(..., ge=1, le=5)
    competitive_rivalry: float = Field(..., ge=1, le=5)
    threat_of_substitutes: float = Field(..., ge=1, le=5)
    threat_of_new_entrants: float = Field(..., ge=1, le=5)
    overall_intensity: str = Field(..., description="Low/Moderate/High")
    detailed_analysis: Dict[str, str] = Field(..., description="Per-force 2-3 sentence analysis")


class SWOTAnalysis(BaseModel):
    """SWOT analysis"""
    strengths: List[str] = Field(..., min_length=3, max_length=5)
    weaknesses: List[str] = Field(..., min_length=3, max_length=5)
    opportunities: List[str] = Field(..., min_length=3, max_length=5)
    threats: List[str] = Field(..., min_length=3, max_length=5)


class PESTELAnalysis(BaseModel):
    """PESTEL analysis"""
    political: List[str]
    economic: List[str]
    social: List[str]
    technological: List[str]
    environmental: List[str]
    legal: List[str]


class BlueOceanStrategy(BaseModel):
    """Blue Ocean Strategy (Four Actions Framework)"""
    eliminate: List[str] = Field(..., description="Factors to eliminate")
    reduce: List[str] = Field(..., description="Factors to reduce below industry")
    raise_factors: List[str] = Field(..., alias="raise", description="Factors to raise above industry")
    create: List[str] = Field(..., description="New factors to create")
    
    class Config:
        populate_by_name = True


class FrameworkAnalysis(BaseModel):
    """Combined framework analysis output"""
    porter_five_forces: Optional[PortersFiveForces] = None
    swot_analysis: Optional[SWOTAnalysis] = None
    pestel_analysis: Optional[PESTELAnalysis] = None
    blue_ocean_strategy: Optional[BlueOceanStrategy] = None


# ============================================================================
# SYNTHESIS MODEL
# ============================================================================

class ExecutiveSummary(BaseModel):
    """Final synthesis output"""
    company_name: str
    industry: str
    analysis_date: datetime = Field(default_factory=datetime.now)
    key_findings: List[str] = Field(..., min_length=3, max_length=5, description="Top insights")
    strategic_recommendation: str = Field(..., description="Primary recommendation")
    confidence_score: float = Field(..., ge=0, le=1, description="Analysis confidence")
    supporting_evidence: List[str]
    next_steps: List[str]


# ============================================================================
# FINAL REPORT MODEL
# ============================================================================

class StrategicReport(BaseModel):
    """Complete report structure"""
    executive_summary: ExecutiveSummary
    company_research: CompanyResearch
    market_trends: MarketTrends
    financial_snapshot: FinancialSnapshot
    framework_analysis: FrameworkAnalysis
    recommendations: List[str] = Field(..., min_length=3, description="Actionable recommendations")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Generation metadata: timestamp, agent versions, quality scores"
    )

