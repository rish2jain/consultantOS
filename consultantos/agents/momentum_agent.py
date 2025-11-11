"""
Momentum Agent - Flywheel momentum tracking based on Jim Collins' framework

Purpose: Track and analyze business momentum across multiple dimensions to identify
acceleration opportunities and momentum phase (Building, Accelerating, Sustaining, Declining).

Based on Jim Collins' Flywheel concept from "Good to Great" and "Turning the Flywheel".
"""
from typing import Dict, Any, List
import logging
from datetime import datetime, timedelta
from consultantos.agents.base_agent import BaseAgent
from consultantos.models.momentum import (
    MomentumAnalysis,
    MomentumMetric,
    FlywheelVelocity,
    InflectionPoint,
    MomentumComponent,
    HistoricalMatch
)

logger = logging.getLogger(__name__)


class MomentumAgent(BaseAgent):
    """
    Momentum agent for tracking flywheel velocity and acceleration.

    Analyzes momentum across 5 key dimensions:
    1. Market Momentum: Customer acquisition, brand awareness, market share growth
    2. Financial Momentum: Revenue growth, margin expansion, cash generation
    3. Strategic Momentum: Competitive position, market timing, strategic clarity
    4. Execution Momentum: Operational efficiency, delivery speed, quality
    5. Talent Momentum: Retention rate, hiring quality, team engagement
    """

    def __init__(self, timeout: int = 60):
        super().__init__(
            name="momentum_agent",
            timeout=timeout
        )
        self.instruction = """
        You are a business momentum analyst with expertise in:
        - Jim Collins' Flywheel framework and momentum concepts
        - Growth trajectory analysis and inflection point detection
        - Multi-dimensional momentum measurement
        - Historical pattern matching and outcome prediction
        - Acceleration opportunity identification

        Analyze business momentum to identify:
        1. Current momentum score and trend across dimensions
        2. Phase of flywheel (Building, Accelerating, Sustaining, Declining)
        3. Key momentum drivers and drag factors
        4. Historical pattern matches with similar companies
        5. Inflection points and acceleration opportunities
        """

    async def _execute_internal(self, input_data: Dict[str, Any]) -> MomentumAnalysis:
        """
        Execute momentum analysis.

        Args:
            input_data: Dictionary containing:
                - company: Company name (required)
                - industry: Industry sector (required)
                - market_data: Market trends data
                - financial_data: Financial snapshot
                - research_data: Company research
                - historical_data: Time-series data for trend analysis (optional)

        Returns:
            MomentumAnalysis object with comprehensive momentum tracking

        Raises:
            ValueError: If required data is missing
            Exception: If analysis fails
        """
        company = input_data.get("company", "")
        industry = input_data.get("industry", "")

        if not company or not industry:
            raise ValueError("Company and industry are required")

        market_data = input_data.get("market_data", {})
        financial_data = input_data.get("financial_data", {})
        research_data = input_data.get("research_data", {})
        historical_data = input_data.get("historical_data", [])

        # Calculate momentum components
        market_momentum = self._calculate_market_momentum(market_data, research_data)
        financial_momentum = self._calculate_financial_momentum(financial_data)
        strategic_momentum = self._calculate_strategic_momentum(market_data, research_data)
        execution_momentum = self._calculate_execution_momentum(research_data)
        talent_momentum = self._calculate_talent_momentum(research_data)

        # Calculate overall momentum score (weighted average)
        overall_score = (
            market_momentum * 0.25 +
            financial_momentum * 0.25 +
            strategic_momentum * 0.20 +
            execution_momentum * 0.15 +
            talent_momentum * 0.15
        )

        # Determine momentum phase
        phase, phase_confidence = self._determine_momentum_phase(
            overall_score=overall_score,
            market_momentum=market_momentum,
            financial_momentum=financial_momentum
        )

        # Find historical matches
        historical_matches = self._find_historical_matches(
            industry=industry,
            momentum_profile={
                "market": market_momentum,
                "financial": financial_momentum,
                "strategic": strategic_momentum,
            }
        )

        # Detect inflection points
        inflection_points = self._detect_inflection_points(historical_data)

        # Generate momentum components with trend data
        components = self._generate_momentum_components(
            market_momentum=market_momentum,
            financial_momentum=financial_momentum,
            strategic_momentum=strategic_momentum,
            execution_momentum=execution_momentum,
            talent_momentum=talent_momentum
        )

        # Generate prediction
        prediction = self._generate_momentum_prediction(phase, overall_score)

        return MomentumAnalysis(
            company=company,
            industry=industry,
            analysis_date=datetime.utcnow().isoformat(),
            overall_score=round(overall_score, 1),
            market_momentum=round(market_momentum, 1),
            financial_momentum=round(financial_momentum, 1),
            strategic_momentum=round(strategic_momentum, 1),
            execution_momentum=round(execution_momentum, 1),
            talent_momentum=round(talent_momentum, 1),
            phase=phase,
            phase_confidence=phase_confidence,
            historical_matches=historical_matches,
            prediction=prediction,
            inflection_points=inflection_points,
            components=components,
            last_updated=datetime.utcnow().isoformat()
        )

    def _calculate_market_momentum(self, market_data: Dict, research_data: Dict) -> float:
        """Calculate market momentum (0-100)"""
        # Extract market indicators
        market_share_growth = market_data.get("market_share_growth", 0)
        brand_strength = research_data.get("brand_sentiment", 50)
        customer_acquisition = market_data.get("customer_growth_rate", 0)

        # Normalize and combine
        market_share_score = min(100, max(0, 50 + (market_share_growth * 10)))
        brand_score = brand_strength
        acquisition_score = min(100, max(0, 50 + (customer_acquisition * 5)))

        return (market_share_score + brand_score + acquisition_score) / 3

    def _calculate_financial_momentum(self, financial_data: Dict) -> float:
        """Calculate financial momentum (0-100)"""
        revenue_growth = financial_data.get("revenue_growth_rate", 0)
        margin_trend = financial_data.get("margin_trend", 0)
        cash_generation = financial_data.get("cash_flow_strength", 50)

        # Normalize
        revenue_score = min(100, max(0, 50 + (revenue_growth * 10)))
        margin_score = min(100, max(0, 50 + (margin_trend * 20)))
        cash_score = cash_generation

        return (revenue_score + margin_score + cash_score) / 3

    def _calculate_strategic_momentum(self, market_data: Dict, research_data: Dict) -> float:
        """Calculate strategic momentum (0-100)"""
        competitive_position = market_data.get("competitive_strength", 50)
        market_timing = research_data.get("market_timing_score", 50)
        strategic_clarity = research_data.get("strategy_clarity", 60)

        return (competitive_position + market_timing + strategic_clarity) / 3

    def _calculate_execution_momentum(self, research_data: Dict) -> float:
        """Calculate execution momentum (0-100)"""
        operational_efficiency = research_data.get("operational_score", 65)
        delivery_speed = research_data.get("delivery_performance", 70)
        quality_metrics = research_data.get("quality_score", 70)

        return (operational_efficiency + delivery_speed + quality_metrics) / 3

    def _calculate_talent_momentum(self, research_data: Dict) -> float:
        """Calculate talent momentum (0-100)"""
        retention_rate = research_data.get("employee_retention", 75)
        hiring_quality = research_data.get("hiring_quality_score", 65)
        engagement = research_data.get("employee_engagement", 60)

        return (retention_rate + hiring_quality + engagement) / 3

    def _determine_momentum_phase(
        self, overall_score: float, market_momentum: float, financial_momentum: float
    ) -> tuple:
        """Determine current momentum phase and confidence"""
        # Phase determination logic
        if overall_score >= 75 and market_momentum >= 70 and financial_momentum >= 70:
            return "Accelerating", 0.85
        elif overall_score >= 70:
            return "Sustaining", 0.80
        elif overall_score >= 50:
            return "Building", 0.75
        else:
            return "Declining", 0.70

    def _find_historical_matches(
        self, industry: str, momentum_profile: Dict[str, float]
    ) -> List[HistoricalMatch]:
        """Find historical company matches with similar momentum profiles"""
        # Mock historical matches - in production, query database
        matches = [
            HistoricalMatch(
                company="Salesforce",
                time_period="2008-2010",
                match_confidence=0.78,
                outcome="Successful transition to market leader",
                similarity_factors=["Strong execution", "Market positioning", "Talent retention"],
                outcome_timeframe_months=24
            )
        ]
        return matches

    def _detect_inflection_points(self, historical_data: List[Dict]) -> List[InflectionPoint]:
        """Detect momentum inflection points from historical data"""
        if not historical_data:
            return []

        inflection_points = []
        # Mock inflection point - in production, analyze time series
        inflection_points.append(
            InflectionPoint(
                date=(datetime.utcnow() - timedelta(days=30)).isoformat(),
                metric="Market Momentum",
                threshold_crossed=70,
                significance="major",
                strategic_note="Crossed critical growth threshold"
            )
        )
        return inflection_points

    def _generate_momentum_components(
        self,
        market_momentum: float,
        financial_momentum: float,
        strategic_momentum: float,
        execution_momentum: float,
        talent_momentum: float
    ) -> List[MomentumComponent]:
        """Generate detailed momentum component breakdown"""
        components = []

        # Market component
        components.append(MomentumComponent(
            name="Market",
            score=round(market_momentum, 1),
            trend_data=self._generate_trend_data(market_momentum, days=90),
            acceleration="moderate_up",
            key_drivers=["Customer acquisition", "Brand awareness"],
            last_updated=datetime.utcnow().isoformat()
        ))

        # Financial component
        components.append(MomentumComponent(
            name="Financial",
            score=round(financial_momentum, 1),
            trend_data=self._generate_trend_data(financial_momentum, days=90),
            acceleration="stable",
            key_drivers=["Revenue growth", "Margin improvement"],
            last_updated=datetime.utcnow().isoformat()
        ))

        # Strategic component
        components.append(MomentumComponent(
            name="Strategic",
            score=round(strategic_momentum, 1),
            trend_data=self._generate_trend_data(strategic_momentum, days=90),
            acceleration="moderate_up",
            key_drivers=["Market positioning", "Competitive advantage"],
            last_updated=datetime.utcnow().isoformat()
        ))

        # Execution component
        components.append(MomentumComponent(
            name="Execution",
            score=round(execution_momentum, 1),
            trend_data=self._generate_trend_data(execution_momentum, days=90),
            acceleration="moderate_up",
            key_drivers=["Operational efficiency", "Delivery speed"],
            last_updated=datetime.utcnow().isoformat()
        ))

        # Talent component
        components.append(MomentumComponent(
            name="Talent",
            score=round(talent_momentum, 1),
            trend_data=self._generate_trend_data(talent_momentum, days=90),
            acceleration="stable",
            key_drivers=["Retention rate", "Hiring quality"],
            last_updated=datetime.utcnow().isoformat()
        ))

        return components

    def _generate_trend_data(self, current_score: float, days: int = 90) -> List[float]:
        """Generate mock trend data for visualization"""
        # Generate upward trending data
        base = max(0, current_score - 20)
        increment = (current_score - base) / days
        return [base + (i * increment) for i in range(days)]

    def _generate_momentum_prediction(self, phase: str, overall_score: float) -> str:
        """Generate momentum prediction narrative"""
        if phase == "Accelerating":
            return f"Strong momentum trajectory. Expected to maintain acceleration with current score of {overall_score:.1f}. Continue investing in momentum drivers."
        elif phase == "Building":
            return f"Building momentum phase detected (score: {overall_score:.1f}). Expected to enter Accelerating phase within 6 months with sustained effort."
        elif phase == "Sustaining":
            return f"Sustaining momentum at {overall_score:.1f}. Focus on preventing decline through continuous improvement."
        else:
            return f"Momentum declining (score: {overall_score:.1f}). Immediate intervention required to reverse trend."
