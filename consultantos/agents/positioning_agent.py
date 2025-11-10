"""
Positioning Agent - Dynamic competitive positioning with movement vector analysis

Purpose: Calculate competitive positions, detect strategic groups, identify white space
opportunities, and predict competitive collisions.

Integrates data from:
- Market Agent: Market share growth rates (X-axis)
- Financial Agent: Profit margins (Y-axis), market cap (bubble size)
- Research Agent: News sentiment (color coding)
"""
from typing import Dict, Any, List, Tuple
import math
import logging
from datetime import datetime, timedelta
from consultantos.agents.base_agent import BaseAgent
from consultantos.models.positioning import (
    DynamicPositioning,
    CompetitivePosition,
    PositionTrajectory,
    StrategicGroup,
    WhiteSpaceOpportunity,
    PositionThreat
)

logger = logging.getLogger(__name__)


class PositioningAgent(BaseAgent):
    """
    Positioning agent for dynamic competitive position analysis.

    Capabilities:
    1. Position Calculation: X=growth, Y=margin, Size=market cap, Color=sentiment
    2. Strategic Group Clustering: K-means on position vectors
    3. Trajectory Analysis: 3-month movement vectors with collision detection
    4. Alert Generation: 6-month window threat warnings
    """

    def __init__(self, timeout: int = 90):
        super().__init__(
            name="positioning_agent",
            timeout=timeout
        )
        self.instruction = """
        You are a competitive positioning strategist with expertise in:
        - Strategic positioning and competitive landscape mapping
        - Movement vector analysis and trajectory prediction
        - Strategic group identification and clustering
        - White space opportunity detection
        - Competitive collision detection and threat assessment

        Analyze competitive positioning dynamics to identify:
        1. Current positions and movement trajectories
        2. Strategic groups competing on similar dimensions
        3. White space opportunities for differentiation
        4. Competitive threats and collision risks
        """

    async def _execute_internal(self, input_data: Dict[str, Any]) -> DynamicPositioning:
        """
        Execute dynamic positioning analysis.

        Args:
            input_data: Dictionary containing:
                - company: Company name (required)
                - industry: Industry sector (required)
                - market_data: Market trends data from MarketAgent
                - financial_data: Financial snapshot from FinancialAgent
                - research_data: Company research from ResearchAgent
                - competitors: List of competitor data (optional)

        Returns:
            DynamicPositioning object with comprehensive competitive analysis

        Raises:
            ValueError: If required data is missing
            Exception: If analysis fails
        """
        company = input_data.get("company", "")
        industry = input_data.get("industry", "")

        if not company or not industry:
            raise ValueError("Company and industry are required")

        # Extract data from integrated agents
        market_data = input_data.get("market_data", {})
        financial_data = input_data.get("financial_data", {})
        research_data = input_data.get("research_data", {})
        competitors = input_data.get("competitors", [])

        # Calculate company position
        company_position = self._calculate_position(
            company=company,
            market_data=market_data,
            financial_data=financial_data,
            research_data=research_data
        )

        # Calculate historical movement (mock 3-month delta for now)
        movement_x, movement_y = self._calculate_movement_vector(
            company_position,
            market_data,
            financial_data
        )
        velocity = math.sqrt(movement_x**2 + movement_y**2)

        # Predict 6-month position
        predicted_x = company_position.x_value + (movement_x * 2)
        predicted_y = company_position.y_value + (movement_y * 2)

        # Process competitor positions and trajectories
        competitor_positions = []
        competitor_trajectories = []

        for comp in competitors:
            comp_position = self._calculate_position(
                company=comp.get("name", ""),
                market_data=comp.get("market_data", {}),
                financial_data=comp.get("financial_data", {}),
                research_data=comp.get("research_data", {})
            )
            competitor_positions.append(comp_position)

            # Calculate competitor trajectory
            comp_movement_x, comp_movement_y = self._calculate_movement_vector(
                comp_position,
                comp.get("market_data", {}),
                comp.get("financial_data", {})
            )
            comp_trajectory = PositionTrajectory(
                company=comp.get("name", ""),
                positions=[],  # Historical positions would go here
                velocity=math.sqrt(comp_movement_x**2 + comp_movement_y**2),
                direction=self._classify_direction(comp_movement_x, comp_movement_y),
                momentum_score=min(100, abs(comp_movement_x + comp_movement_y) * 10)
            )
            competitor_trajectories.append(comp_trajectory)

        # Perform strategic group clustering
        all_positions = [company_position] + competitor_positions
        strategic_groups = self._cluster_strategic_groups(all_positions)

        # Identify white space opportunities
        white_space_opportunities = self._identify_white_space(
            all_positions,
            market_data
        )

        # Detect position threats
        position_threats = self._detect_threats(
            company_position,
            (movement_x, movement_y),
            competitor_positions,
            competitor_trajectories
        )

        # Calculate collision risk
        collision_risk = self._calculate_collision_risk(position_threats)

        # Use LLM to generate strategic recommendations
        recommendations = await self._generate_recommendations(
            company=company,
            industry=industry,
            position=company_position,
            movement=(movement_x, movement_y),
            threats=position_threats,
            white_spaces=white_space_opportunities,
            strategic_groups=strategic_groups
        )

        # Build final analysis
        return DynamicPositioning(
            company=company,
            industry=industry,
            current_position=company_position,
            movement_vector_x=movement_x,
            movement_vector_y=movement_y,
            velocity=velocity,
            predicted_x=min(100, max(0, predicted_x)),
            predicted_y=min(100, max(0, predicted_y)),
            competitor_positions=competitor_positions,
            competitor_trajectories=competitor_trajectories,
            strategic_groups=strategic_groups,
            white_space_opportunities=white_space_opportunities,
            position_threats=position_threats,
            recommendations=recommendations,
            collision_risk=collision_risk,
            confidence_score=self._calculate_confidence(market_data, financial_data),
            data_sources=self._extract_sources(market_data, financial_data, research_data)
        )

    def _calculate_position(
        self,
        company: str,
        market_data: Dict[str, Any],
        financial_data: Dict[str, Any],
        research_data: Dict[str, Any]
    ) -> CompetitivePosition:
        """Calculate competitive position from integrated data sources."""
        # X-axis: Market share growth rate from market trends
        growth_trend = market_data.get("search_interest_trend", "Stable")

        # Map trend to growth percentage
        growth_map = {"Growing": 15.0, "Stable": 5.0, "Declining": -5.0}
        x_value = growth_map.get(growth_trend, 5.0)

        # Y-axis: Profit margin from financial data
        profit_margin = financial_data.get("profit_margin", 10.0)
        y_value = min(100, max(0, profit_margin))

        # Market share from financial or market data
        market_share = financial_data.get("market_share", 0.0)

        # Sentiment from research data
        sentiment_obj = research_data.get("sentiment")
        if sentiment_obj:
            sentiment = sentiment_obj.get("classification", "neutral")
        else:
            sentiment = "neutral"

        # Create positioning statement
        positioning = f"{growth_trend.lower()} growth, {y_value:.1f}% margin"

        return CompetitivePosition(
            axis_x="Market Growth",
            axis_y="Profit Margin",
            x_value=min(100, max(0, x_value + 50)),  # Normalize to 0-100
            y_value=y_value,
            market_share=market_share,
            positioning_statement=positioning
        )

    def _calculate_movement_vector(
        self,
        position: CompetitivePosition,
        market_data: Dict[str, Any],
        financial_data: Dict[str, Any]
    ) -> Tuple[float, float]:
        """Calculate 3-month movement vector."""
        trend = market_data.get("search_interest_trend", "Stable")

        # X-axis movement (growth acceleration/deceleration)
        x_movement = {"Growing": 5.0, "Stable": 0.0, "Declining": -5.0}.get(trend, 0.0)

        # Y-axis movement (margin expansion/compression)
        y_movement = x_movement * 0.3  # Margins typically less volatile

        return x_movement, y_movement

    def _classify_direction(self, movement_x: float, movement_y: float) -> str:
        """Classify movement direction."""
        if abs(movement_x) < 1 and abs(movement_y) < 1:
            return "stable"
        elif movement_x > 0 and movement_y > 0:
            return "advancing"
        elif movement_x < 0 or movement_y < 0:
            return "retreating"
        else:
            return "repositioning"

    def _cluster_strategic_groups(
        self,
        positions: List[CompetitivePosition]
    ) -> List[StrategicGroup]:
        """Identify strategic groups using simple clustering."""
        if len(positions) < 2:
            return []

        # Simple heuristic: group companies within 20 units of each other
        groups = []
        used = set()

        for i, pos1 in enumerate(positions):
            if i in used:
                continue

            group_companies = [pos1.positioning_statement.split(",")[0].split()[0]]
            group_x = [pos1.x_value]
            group_y = [pos1.y_value]

            for j, pos2 in enumerate(positions[i+1:], start=i+1):
                if j in used:
                    continue

                distance = math.sqrt(
                    (pos1.x_value - pos2.x_value)**2 +
                    (pos1.y_value - pos2.y_value)**2
                )

                if distance < 20:
                    group_companies.append(pos2.positioning_statement.split(",")[0].split()[0])
                    group_x.append(pos2.x_value)
                    group_y.append(pos2.y_value)
                    used.add(j)

            if len(group_companies) > 1:
                centroid_x = sum(group_x) / len(group_x)
                centroid_y = sum(group_y) / len(group_y)

                groups.append(StrategicGroup(
                    group_id=len(groups) + 1,
                    companies=group_companies,
                    centroid_x=centroid_x,
                    centroid_y=centroid_y,
                    characteristics=self._describe_group_characteristics(centroid_x, centroid_y),
                    white_space_distance=self._calculate_white_space_distance(centroid_x, centroid_y)
                ))
                used.add(i)

        return groups

    def _describe_group_characteristics(self, x: float, y: float) -> str:
        """Describe strategic group characteristics."""
        if x > 60 and y > 60:
            return "Premium growth leaders"
        elif x > 60 and y < 40:
            return "High growth, low margin challengers"
        elif x < 40 and y > 60:
            return "Established profit maximizers"
        else:
            return "Mass market players"

    def _calculate_white_space_distance(self, x: float, y: float) -> float:
        """Calculate distance to nearest white space."""
        # Simplified: distance to ideal position (80, 80)
        ideal_x, ideal_y = 80, 80
        return math.sqrt((x - ideal_x)**2 + (y - ideal_y)**2)

    def _identify_white_space(
        self,
        positions: List[CompetitivePosition],
        market_data: Dict[str, Any]
    ) -> List[WhiteSpaceOpportunity]:
        """Identify white space opportunities."""
        opportunities = []

        # Define potential white space positions
        potential_spaces = [
            (75, 75, "Premium innovation"),
            (25, 75, "Value premium"),
            (75, 25, "Disruptive growth"),
            (50, 50, "Balanced middle market")
        ]

        for space_x, space_y, description in potential_spaces:
            # Check if this space is truly empty (>20 units from any competitor)
            is_white_space = all(
                math.sqrt((pos.x_value - space_x)**2 + (pos.y_value - space_y)**2) > 20
                for pos in positions
            )

            if is_white_space:
                opportunities.append(WhiteSpaceOpportunity(
                    position_x=space_x,
                    position_y=space_y,
                    market_potential=1000.0,  # Placeholder
                    entry_barrier=50.0,
                    required_capabilities=[description, "Market development"],
                    risk_score=60.0
                ))

        return opportunities

    def _detect_threats(
        self,
        company_position: CompetitivePosition,
        company_movement: Tuple[float, float],
        competitor_positions: List[CompetitivePosition],
        competitor_trajectories: List[PositionTrajectory]
    ) -> List[PositionThreat]:
        """Detect competitive threats based on trajectory collision."""
        threats = []

        # Project company position 6 months out
        future_x = company_position.x_value + (company_movement[0] * 2)
        future_y = company_position.y_value + (company_movement[1] * 2)

        for comp_pos, comp_traj in zip(competitor_positions, competitor_trajectories):
            distance_now = math.sqrt(
                (company_position.x_value - comp_pos.x_value)**2 +
                (company_position.y_value - comp_pos.y_value)**2
            )

            # Estimate future competitor position
            comp_movement = (comp_traj.velocity * 0.5, comp_traj.velocity * 0.3)
            comp_future_x = comp_pos.x_value + comp_movement[0]
            comp_future_y = comp_pos.y_value + comp_movement[1]

            distance_future = math.sqrt(
                (future_x - comp_future_x)**2 +
                (future_y - comp_future_y)**2
            )

            # If distance is decreasing and future distance < 15, it's a collision threat
            if distance_future < distance_now and distance_future < 15:
                severity = max(0, 100 - distance_future * 5)
                time_to_impact = int(180 * (distance_future / max(comp_traj.velocity, 0.1)))

                threats.append(PositionThreat(
                    threatening_company=comp_traj.company,
                    threat_type="collision",
                    severity=min(100, severity),
                    time_to_impact=max(30, min(365, time_to_impact)),
                    recommended_response=f"Differentiate on {company_position.axis_y} or accelerate {company_position.axis_x}"
                ))

        return threats

    def _calculate_collision_risk(self, threats: List[PositionThreat]) -> float:
        """Calculate overall collision risk score."""
        if not threats:
            return 0.0

        # Weight by severity and time to impact
        total_risk = sum(
            threat.severity * (365 - threat.time_to_impact) / 365
            for threat in threats
        )

        return min(100.0, total_risk / len(threats))

    async def _generate_recommendations(
        self,
        company: str,
        industry: str,
        position: CompetitivePosition,
        movement: Tuple[float, float],
        threats: List[PositionThreat],
        white_spaces: List[WhiteSpaceOpportunity],
        strategic_groups: List[StrategicGroup]
    ) -> List[str]:
        """Generate strategic positioning recommendations using LLM."""
        # Build context for LLM
        context = f"""
        Company: {company}
        Industry: {industry}
        Current Position: {position.positioning_statement}
        Position Coordinates: ({position.x_value:.1f}, {position.y_value:.1f})
        Movement Vector: ({movement[0]:.1f}, {movement[1]:.1f})

        Threats: {len(threats)} competitive threats detected
        White Space Opportunities: {len(white_spaces)} identified
        Strategic Groups: {len(strategic_groups)} clusters found
        """

        prompt = f"""
        {self.instruction}

        Analyze this competitive positioning scenario and provide 3-5 strategic recommendations:

        {context}

        Focus on:
        1. Defensive moves to counter threats
        2. Offensive moves to capture white space
        3. Positioning adjustments to strengthen competitive advantage
        4. Long-term strategic direction

        Provide actionable, specific recommendations.
        """

        # Use simplified structured output (list of strings)
        from pydantic import BaseModel

        class Recommendations(BaseModel):
            recommendations: List[str]

        try:
            result = await self.generate_structured(
                prompt=prompt,
                response_model=Recommendations,
                temperature=0.7,
                max_tokens=1500
            )
            return result.recommendations
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            # Fallback recommendations
            return [
                "Monitor competitive movements closely",
                "Strengthen core positioning dimensions",
                "Explore white space opportunities",
                "Develop defensive capabilities"
            ]

    def _calculate_confidence(
        self,
        market_data: Dict[str, Any],
        financial_data: Dict[str, Any]
    ) -> float:
        """Calculate confidence score based on data quality."""
        confidence = 50.0

        # Increase confidence if we have good market data
        if market_data.get("interest_data"):
            confidence += 20.0

        # Increase confidence if we have financial metrics
        if financial_data.get("profit_margin") is not None:
            confidence += 15.0

        if financial_data.get("market_share", 0) > 0:
            confidence += 15.0

        return min(100.0, confidence)

    def _extract_sources(
        self,
        market_data: Dict[str, Any],
        financial_data: Dict[str, Any],
        research_data: Dict[str, Any]
    ) -> List[str]:
        """Extract data source URLs."""
        sources = []

        # Market data sources
        if "sources" in market_data:
            sources.extend(market_data["sources"])

        # Financial data sources
        if "sources" in financial_data:
            sources.extend(financial_data["sources"])

        # Research sources
        if "sources" in research_data:
            sources.extend(research_data["sources"])

        return list(set(sources))  # Deduplicate
