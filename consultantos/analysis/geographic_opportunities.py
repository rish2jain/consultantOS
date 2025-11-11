"""
Geographic Opportunity Heatmap Module.

Analyzes regional interest data from Google Trends to identify
underserved markets with high demand potential.

Features:
- Opportunity index calculation (demand / competitive_intensity)
- ROI modeling for market expansion
- Investment requirement estimation
- Geographic ranking with actionable insights
"""

import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from consultantos.models import MarketTrends

logger = logging.getLogger(__name__)


class OpportunityIndex(BaseModel):
    """Opportunity index for a geographic region"""

    region: str = Field(
        description="Geographic region (state, country, city)"
    )

    demand_score: float = Field(
        ge=0.0,
        le=100.0,
        description="Search interest demand score (0-100)"
    )

    competitive_intensity: float = Field(
        ge=0.0,
        le=10.0,
        description="Competitive presence intensity (0-10)"
    )

    opportunity_index: float = Field(
        ge=0.0,
        le=100.0,
        description="Opportunity index: demand / competitive_intensity"
    )

    market_size_estimate: Optional[float] = Field(
        None,
        description="Estimated addressable market size (USD)"
    )

    growth_trajectory: str = Field(
        description="Growth trend: Growing/Stable/Declining"
    )

    seasonality_factor: Optional[float] = Field(
        None,
        ge=0.0,
        le=2.0,
        description="Seasonality multiplier (1.0 = no seasonality)"
    )


class GeographicOpportunity(BaseModel):
    """Detailed market expansion opportunity analysis"""

    region: str = Field(
        description="Target region"
    )

    opportunity_index: float = Field(
        ge=0.0,
        le=100.0,
        description="Overall opportunity score (0-100)"
    )

    ranking: int = Field(
        ge=1,
        description="Ranking among analyzed regions (1 = best)"
    )

    demand_drivers: List[str] = Field(
        description="Key factors driving demand in this region"
    )

    competitive_landscape: str = Field(
        description="Competitive situation in region"
    )

    expansion_strategy: str = Field(
        description="Recommended market entry approach"
    )

    estimated_investment: float = Field(
        ge=0.0,
        description="Estimated capital requirement (USD)"
    )

    investment_breakdown: Dict[str, float] = Field(
        default_factory=dict,
        description="Investment allocation (marketing, operations, etc.)"
    )

    expected_roi: float = Field(
        ge=-1.0,
        le=10.0,
        description="Expected ROI multiple (3-5 year horizon)"
    )

    roi_confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence in ROI estimate (0.0-1.0)"
    )

    payback_period_months: Optional[int] = Field(
        None,
        description="Expected payback period in months"
    )

    market_size_estimate: float = Field(
        ge=0.0,
        description="Total addressable market (TAM) estimate (USD)"
    )

    market_share_target: float = Field(
        ge=0.0,
        le=1.0,
        description="Realistic market share target (0.0-1.0)"
    )

    risk_factors: List[str] = Field(
        default_factory=list,
        description="Key risks to successful expansion"
    )

    success_factors: List[str] = Field(
        default_factory=list,
        description="Critical success factors"
    )

    timeline_months: int = Field(
        ge=0,
        description="Recommended expansion timeline (months)"
    )

    quick_wins: List[str] = Field(
        default_factory=list,
        description="Quick win opportunities (0-3 months)"
    )


class GeographicOpportunityResult(BaseModel):
    """Result of geographic opportunity analysis"""

    company: str = Field(description="Company analyzed")

    opportunities: List[GeographicOpportunity] = Field(
        description="Ranked expansion opportunities"
    )

    regional_indices: List[OpportunityIndex] = Field(
        description="Opportunity index for all regions"
    )

    top_recommendation: Optional[GeographicOpportunity] = Field(
        None,
        description="Highest-ranked opportunity"
    )

    total_addressable_market: float = Field(
        ge=0.0,
        description="Total TAM across all opportunities (USD)"
    )

    analysis_timestamp: datetime = Field(
        default_factory=datetime.utcnow
    )


def analyze_geographic_opportunities(
    market_trends: MarketTrends,
    company: str,
    industry: str,
    current_presence: Optional[Dict[str, float]] = None,
    investment_budget: Optional[float] = None
) -> GeographicOpportunityResult:
    """
    Analyze regional interest data to identify underserved high-demand markets.

    Calculates opportunity index as: demand_score / competitive_intensity
    Higher scores indicate markets with strong demand but low competition.

    Args:
        market_trends: Market trends data with geographic distribution
        company: Company name
        industry: Industry for market sizing
        current_presence: Optional dict of region -> market_share (0.0-1.0)
        investment_budget: Optional total budget constraint (USD)

    Returns:
        GeographicOpportunityResult with ranked opportunities and ROI models

    Example:
        >>> trends = MarketTrends(
        ...     geographic_distribution={
        ...         "California": 100, "Texas": 85, "Florida": 70
        ...     }
        ... )
        >>> result = analyze_geographic_opportunities(trends, "Tesla", "EV")
        >>> result.top_recommendation.region
        'Texas'  # High demand, lower competition
    """
    logger.info(f"Analyzing geographic opportunities for {company}")

    current_presence = current_presence or {}

    # Calculate opportunity indices for all regions
    regional_indices = _calculate_opportunity_indices(
        market_trends.geographic_distribution,
        current_presence,
        industry
    )

    # Sort by opportunity index
    regional_indices.sort(key=lambda x: x.opportunity_index, reverse=True)

    # Generate detailed opportunities for top regions
    opportunities = []
    total_tam = 0.0

    for rank, index in enumerate(regional_indices[:10], start=1):  # Top 10 regions
        opportunity = _generate_opportunity_analysis(
            index,
            rank,
            company,
            industry,
            current_presence.get(index.region, 0.0),
            investment_budget
        )
        opportunities.append(opportunity)
        total_tam += opportunity.market_size_estimate

    # Filter opportunities within budget if specified
    if investment_budget:
        opportunities = _filter_by_budget(opportunities, investment_budget)

    return GeographicOpportunityResult(
        company=company,
        opportunities=opportunities,
        regional_indices=regional_indices,
        top_recommendation=opportunities[0] if opportunities else None,
        total_addressable_market=total_tam,
        analysis_timestamp=datetime.utcnow()
    )


def _calculate_opportunity_indices(
    geographic_distribution: Dict[str, Any],
    current_presence: Dict[str, float],
    industry: str
) -> List[OpportunityIndex]:
    """Calculate opportunity index for each region"""

    indices = []

    for region, demand_score in geographic_distribution.items():
        # Normalize demand score to 0-100
        if isinstance(demand_score, (int, float)):
            normalized_demand = min(float(demand_score), 100.0)
        else:
            normalized_demand = 50.0  # Default moderate demand

        # Estimate competitive intensity
        # Higher current presence = higher competition
        current_share = current_presence.get(region, 0.0)
        competitive_intensity = _estimate_competitive_intensity(
            region, industry, current_share
        )

        # Calculate opportunity index
        # Avoid division by zero
        if competitive_intensity > 0:
            opp_index = (normalized_demand / competitive_intensity) * 10
        else:
            opp_index = normalized_demand

        # Cap at 100
        opp_index = min(opp_index, 100.0)

        # Estimate market size
        market_size = _estimate_market_size(region, industry, normalized_demand)

        # Determine growth trajectory
        growth_trajectory = _determine_growth_trajectory(normalized_demand)

        indices.append(OpportunityIndex(
            region=region,
            demand_score=normalized_demand,
            competitive_intensity=competitive_intensity,
            opportunity_index=opp_index,
            market_size_estimate=market_size,
            growth_trajectory=growth_trajectory,
            seasonality_factor=1.0  # Can be enhanced with time-series analysis
        ))

    return indices


def _estimate_competitive_intensity(
    region: str,
    industry: str,
    current_share: float
) -> float:
    """
    Estimate competitive intensity on 0-10 scale.

    Factors:
    - Current market share (higher = more competitive)
    - Region size (larger markets = more competitive)
    - Industry dynamics
    """

    # Base intensity from current presence
    intensity = current_share * 10

    # Adjust for region characteristics
    major_markets = [
        "California", "New York", "Texas", "Florida",
        "United States", "China", "United Kingdom", "Germany"
    ]

    if region in major_markets:
        intensity += 2.0  # Major markets are more competitive

    # Industry-specific adjustments
    competitive_industries = ["Technology", "Retail", "Finance", "Healthcare"]
    if industry in competitive_industries:
        intensity += 1.0

    # Cap at 10
    return min(intensity, 10.0)


def _estimate_market_size(region: str, industry: str, demand_score: float) -> float:
    """
    Estimate total addressable market (TAM) for region.

    Simplified model - would be enhanced with actual market data.
    """

    # Base market multipliers by region (relative to US = 1.0)
    region_multipliers = {
        "California": 0.15,
        "Texas": 0.10,
        "New York": 0.09,
        "Florida": 0.08,
        "Illinois": 0.05,
        "Pennsylvania": 0.05,
        "United States": 1.0,
        "China": 1.5,
        "India": 0.8,
        "United Kingdom": 0.25,
        "Germany": 0.30,
        "Japan": 0.40
    }

    # Industry base TAM (USD billions)
    industry_tam = {
        "Technology": 500_000_000_000,
        "Electric Vehicles": 300_000_000_000,
        "Retail": 400_000_000_000,
        "Finance": 600_000_000_000,
        "Healthcare": 450_000_000_000,
        "Energy": 350_000_000_000
    }

    base_tam = industry_tam.get(industry, 100_000_000_000)  # Default $100B
    region_multiplier = region_multipliers.get(region, 0.02)  # Default 2%
    demand_multiplier = demand_score / 100.0

    tam = base_tam * region_multiplier * demand_multiplier

    return tam


def _determine_growth_trajectory(demand_score: float) -> str:
    """Determine growth trajectory based on demand score"""
    if demand_score >= 75:
        return "Growing"
    elif demand_score >= 40:
        return "Stable"
    else:
        return "Declining"


def _generate_opportunity_analysis(
    index: OpportunityIndex,
    ranking: int,
    company: str,
    industry: str,
    current_share: float,
    budget: Optional[float]
) -> GeographicOpportunity:
    """Generate detailed opportunity analysis for a region"""

    # Estimate investment requirement
    market_size = index.market_size_estimate or 1_000_000_000
    investment = _estimate_investment_requirement(market_size, index.competitive_intensity)

    # Calculate investment breakdown
    breakdown = {
        "marketing": investment * 0.40,
        "operations": investment * 0.30,
        "technology": investment * 0.15,
        "hiring": investment * 0.10,
        "contingency": investment * 0.05
    }

    # Estimate ROI
    roi, confidence = _estimate_roi(
        index.opportunity_index,
        index.competitive_intensity,
        index.growth_trajectory
    )

    # Market share target
    if current_share > 0:
        # Grow existing presence
        share_target = min(current_share * 1.5, 0.25)
    else:
        # New market entry
        if index.competitive_intensity < 3:
            share_target = 0.15  # Low competition
        elif index.competitive_intensity < 6:
            share_target = 0.08  # Moderate competition
        else:
            share_target = 0.03  # High competition

    # Payback period
    payback_months = int((investment / (market_size * share_target * 0.20)) * 12)

    # Determine strategy
    if current_share > 0:
        strategy = f"Scale existing presence through aggressive marketing and operations expansion"
    elif index.competitive_intensity < 4:
        strategy = f"First-mover advantage: Rapid market entry with strong brand positioning"
    else:
        strategy = f"Differentiated entry: Focus on underserved segments and unique value proposition"

    return GeographicOpportunity(
        region=index.region,
        opportunity_index=index.opportunity_index,
        ranking=ranking,
        demand_drivers=[
            f"High search interest ({index.demand_score:.0f}/100)",
            f"Growing market demand" if index.growth_trajectory == "Growing" else "Stable demand",
            f"Low competitive pressure" if index.competitive_intensity < 5 else "Moderate competition"
        ],
        competitive_landscape=(
            f"Competitive intensity: {index.competitive_intensity:.1f}/10. "
            f"{'Highly competitive market' if index.competitive_intensity > 7 else 'Moderate competition' if index.competitive_intensity > 4 else 'Low competition opportunity'}"
        ),
        expansion_strategy=strategy,
        estimated_investment=investment,
        investment_breakdown=breakdown,
        expected_roi=roi,
        roi_confidence=confidence,
        payback_period_months=payback_months if payback_months < 60 else None,
        market_size_estimate=market_size,
        market_share_target=share_target,
        risk_factors=[
            "Regulatory barriers to entry" if index.competitive_intensity > 6 else "Market education required",
            "Local competition intensifies",
            "Economic downturn in region",
            "Cultural/language barriers" if index.region not in ["United States", "United Kingdom"] else "Regional preferences differ"
        ],
        success_factors=[
            "Strong local partnerships",
            "Localized product offerings",
            "Competitive pricing strategy",
            "Excellent customer service"
        ],
        timeline_months=12 if index.competitive_intensity < 5 else 18,
        quick_wins=[
            "Digital marketing campaigns",
            "Pilot program with select customers",
            "Local market research and validation"
        ]
    )


def _estimate_investment_requirement(market_size: float, competitive_intensity: float) -> float:
    """
    Estimate capital requirement for market expansion.

    Rule of thumb: 2-5% of TAM depending on competition
    """
    base_percentage = 0.02  # 2%

    # Increase investment for higher competition
    competition_multiplier = 1.0 + (competitive_intensity / 10.0)

    investment = market_size * base_percentage * competition_multiplier

    # Cap between $100K and $50M for realism
    investment = max(100_000, min(investment, 50_000_000))

    return investment


def _estimate_roi(
    opportunity_index: float,
    competitive_intensity: float,
    growth_trajectory: str
) -> tuple[float, float]:
    """
    Estimate ROI multiple and confidence level.

    Returns:
        (roi_multiple, confidence_score)
    """

    # Base ROI from opportunity index
    base_roi = 1.0 + (opportunity_index / 50.0)  # 1.0 to 3.0

    # Adjust for competition
    competition_penalty = competitive_intensity / 20.0
    base_roi -= competition_penalty

    # Adjust for growth
    if growth_trajectory == "Growing":
        base_roi *= 1.2
    elif growth_trajectory == "Declining":
        base_roi *= 0.8

    # Cap ROI
    roi = max(0.5, min(base_roi, 5.0))

    # Confidence calculation
    # Higher opportunity index = higher confidence
    # Lower competition = higher confidence
    confidence = (opportunity_index / 100.0) * (1.0 - competitive_intensity / 20.0)
    confidence = max(0.3, min(confidence, 0.9))

    return roi, confidence


def _filter_by_budget(
    opportunities: List[GeographicOpportunity],
    budget: float
) -> List[GeographicOpportunity]:
    """Filter opportunities to fit within budget constraint"""

    # Sort by ROI efficiency (ROI / investment)
    opportunities_with_efficiency = [
        (opp, opp.expected_roi / opp.estimated_investment)
        for opp in opportunities
    ]
    opportunities_with_efficiency.sort(key=lambda x: x[1], reverse=True)

    # Select opportunities that fit budget
    selected = []
    remaining_budget = budget

    for opp, efficiency in opportunities_with_efficiency:
        if opp.estimated_investment <= remaining_budget:
            selected.append(opp)
            remaining_budget -= opp.estimated_investment

    # Re-sort by ranking
    selected.sort(key=lambda x: x.ranking)

    return selected
