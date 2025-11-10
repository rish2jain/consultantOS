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

class EntityMention(BaseModel):
    """Named entity extracted from text"""
    text: str = Field(..., description="Entity text")
    label: str = Field(..., description="Entity type (ORG, PERSON, GPE, DATE, etc.)")
    start: int = Field(..., description="Start character index")
    end: int = Field(..., description="End character index")


class SentimentScore(BaseModel):
    """Sentiment analysis result"""
    polarity: float = Field(..., ge=-1.0, le=1.0, description="Sentiment polarity (-1.0 to 1.0)")
    subjectivity: float = Field(..., ge=0.0, le=1.0, description="Subjectivity score (0.0 to 1.0)")
    classification: str = Field(..., description="Sentiment classification: positive/negative/neutral")


class EntityRelationship(BaseModel):
    """Relationship between two entities"""
    entity1: Dict[str, str] = Field(..., description="First entity (text, label)")
    entity2: Dict[str, str] = Field(..., description="Second entity (text, label)")
    distance: int = Field(..., description="Character distance between entities")
    context: str = Field(..., description="Surrounding text context")


class CompanyResearch(BaseModel):
    """Research agent output with NLP enrichment"""
    company_name: str
    description: str = Field(..., description="Company overview")
    products_services: List[str]
    target_market: str
    key_competitors: List[str]
    recent_news: List[str]
    sources: List[str] = Field(..., description="Citation URLs")

    # NLP enrichment fields
    entities: List[EntityMention] = Field(default_factory=list, description="Extracted named entities")
    sentiment: Optional[SentimentScore] = Field(None, description="Overall sentiment analysis")
    entity_relationships: List[EntityRelationship] = Field(default_factory=list, description="Entity co-occurrences")
    keywords: List[Dict[str, Any]] = Field(default_factory=list, description="Key terms and phrases")


class MarketTrends(BaseModel):
    """Market analyst output"""
    search_interest_trend: str = Field(..., description="Growing/Stable/Declining")
    interest_data: Dict[str, Any] = Field(..., description="Time series data")
    geographic_distribution: Dict[str, Any]
    related_searches: List[str]
    competitive_comparison: Dict[str, Any] = Field(..., description="Company vs competitors")


class AnalystRecommendations(BaseModel):
    """Analyst recommendation data from Finnhub"""
    strong_buy: int = Field(0, description="Number of strong buy recommendations")
    buy: int = Field(0, description="Number of buy recommendations")
    hold: int = Field(0, description="Number of hold recommendations")
    sell: int = Field(0, description="Number of sell recommendations")
    strong_sell: int = Field(0, description="Number of strong sell recommendations")
    total_analysts: int = Field(0, description="Total number of analysts")
    consensus: str = Field("Unknown", description="Consensus rating: Buy/Hold/Sell/Unknown")
    period: Optional[str] = Field(None, description="Period of recommendation (e.g., 2024-01)")


class NewsSentiment(BaseModel):
    """News sentiment analysis from Finnhub"""
    articles_count: int = Field(0, description="Number of articles analyzed")
    sentiment_score: float = Field(0.0, ge=-1.0, le=1.0, description="Sentiment score (-1.0 to 1.0)")
    sentiment: str = Field("Neutral", description="Sentiment label: Positive/Neutral/Negative")
    recent_headlines: List[str] = Field(default_factory=list, description="Recent news headlines")


class DataSourceValidation(BaseModel):
    """Cross-validation result between data sources"""
    metric: str = Field(..., description="Metric being validated (e.g., market_cap)")
    yfinance_value: Optional[float] = Field(None, description="Value from yfinance")
    finnhub_value: Optional[float] = Field(None, description="Value from Finnhub")
    discrepancy_pct: Optional[float] = Field(None, description="Percentage difference")
    is_valid: bool = Field(True, description="Whether discrepancy is within acceptable range")
    note: Optional[str] = Field(None, description="Validation note or warning")


class FinancialSnapshot(BaseModel):
    """Financial analyst output with multi-source data and technical analysis"""
    ticker: str
    market_cap: Optional[float] = None
    revenue: Optional[float] = Field(None, description="Latest annual revenue")
    revenue_growth: Optional[float] = Field(None, description="YoY growth percentage")
    profit_margin: Optional[float] = None
    pe_ratio: Optional[float] = None
    key_metrics: Dict[str, Any] = Field(default_factory=dict, description="Additional financial metrics")
    risk_assessment: str

    # Enhanced fields from Finnhub integration
    analyst_recommendations: Optional[AnalystRecommendations] = Field(None, description="Analyst recommendations from Finnhub")
    news_sentiment: Optional[NewsSentiment] = Field(None, description="News sentiment analysis from Finnhub")
    data_sources: List[str] = Field(default_factory=list, description="Data sources used (yfinance, finnhub, alpha_vantage)")
    cross_validation: List[DataSourceValidation] = Field(default_factory=list, description="Cross-validation results between sources")

    # Technical analysis from Alpha Vantage (optional - graceful degradation)
    rsi: Optional[float] = Field(None, description="RSI technical indicator (0-100)")
    rsi_signal: Optional[str] = Field(None, description="RSI trading signal (Buy/Sell/Hold)")
    macd_trend: Optional[str] = Field(None, description="MACD trend (Bullish/Bearish/Neutral)")
    trend_signal: Optional[str] = Field(None, description="Golden/Death Cross signal")
    price_vs_sma50: Optional[str] = Field(None, description="Price position vs 50-day SMA (Above/Below)")
    price_vs_sma200: Optional[str] = Field(None, description="Price position vs 200-day SMA (Above/Below)")
    current_price: Optional[float] = Field(None, description="Current stock price from Alpha Vantage")

    # Sector analysis (optional)
    sector: Optional[str] = Field(None, description="Company sector")
    sector_performance_ytd: Optional[float] = Field(None, description="Sector YTD performance %")
    company_vs_sector: Optional[str] = Field(None, description="Outperforming/Underperforming/Inline")


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
    market_trends: Optional[MarketTrends] = None  # Optional for graceful degradation
    financial_snapshot: FinancialSnapshot
    framework_analysis: FrameworkAnalysis
    recommendations: List[str] = Field(..., min_length=3, description="Actionable recommendations")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Generation metadata: timestamp, agent versions, quality scores"
    )

