"""
Strategic Intelligence Orchestrator

Coordinates strategic intelligence analysis by:
- Aggregating results from positioning, disruption, and systems agents
- Calculating strategic health scores
- Identifying top threats and opportunities
- Generating executive-level insights
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from consultantos.agents.positioning_agent import PositioningAgent
from consultantos.agents.disruption_agent import DisruptionAgent
from consultantos.agents.systems_agent import SystemsAgent
from consultantos.agents.momentum_agent import MomentumAgent
from consultantos.orchestrator.orchestrator import AnalysisOrchestrator

logger = logging.getLogger(__name__)


class StrategicOrchestrator:
    """
    Orchestrates strategic intelligence analysis across multiple agents.
    """

    def __init__(self):
        self.positioning_agent = PositioningAgent()
        self.disruption_agent = DisruptionAgent()
        self.systems_agent = SystemsAgent()
        self.momentum_agent = MomentumAgent()
        self.base_orchestrator = AnalysisOrchestrator()

    async def generate_strategic_overview(
        self,
        company: str,
        industry: str,
        monitor_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive strategic overview.

        Args:
            company: Company name
            industry: Industry sector
            monitor_id: Optional monitor ID for historical context

        Returns:
            Strategic overview with health scores, threats, opportunities
        """
        try:
            logger.info(f"Generating strategic overview for {company}")

            # Run base analysis to get integrated agent data
            base_result = await self.base_orchestrator.execute_phase_1(
                company=company,
                industry=industry,
                frameworks=["porter", "swot"],
                depth="quick"
            )

            # Run strategic agents in parallel with graceful degradation
            results = await asyncio.gather(
                self._run_positioning_analysis(company, industry, base_result),
                self._run_disruption_analysis(company, industry, base_result),
                self._run_systems_analysis(company, industry, base_result),
                self._run_momentum_analysis(company, industry, base_result),
                return_exceptions=True
            )

            positioning_result, disruption_result, systems_result, momentum_result = results

            # Extract successful results
            positioning = positioning_result if not isinstance(positioning_result, Exception) else None
            disruption = disruption_result if not isinstance(disruption_result, Exception) else None
            systems = systems_result if not isinstance(systems_result, Exception) else None
            momentum = momentum_result if not isinstance(momentum_result, Exception) else None

            # Calculate strategic health score
            health_score = self._calculate_strategic_health(
                positioning=positioning,
                disruption=disruption,
                systems=systems
            )

            # Extract top threats
            top_threats = self._extract_top_threats(
                positioning=positioning,
                disruption=disruption,
                systems=systems
            )

            # Extract top opportunities
            top_opportunities = self._extract_top_opportunities(
                positioning=positioning,
                systems=systems
            )

            # Determine critical decision
            critical_decision = self._identify_critical_decision(
                threats=top_threats,
                opportunities=top_opportunities
            )

            # Calculate component scores
            competitive_position_score = self._calculate_position_score(positioning)
            disruption_risk_score = self._calculate_disruption_score(disruption)
            system_health_score = self._calculate_system_score(systems)
            momentum_score = self._calculate_momentum_score(momentum)

            # Determine health level and trend
            health_level = self._determine_health_level(health_score)
            health_trend = self._determine_health_trend(health_score)

            # Generate immediate actions
            immediate_actions = self._generate_immediate_actions(
                threats=top_threats,
                opportunities=top_opportunities,
                health_score=health_score
            )

            return {
                "company": company,
                "industry": industry,
                "generated_at": datetime.utcnow().isoformat(),
                "strategic_health_score": health_score,
                "health_level": health_level,
                "health_trend": health_trend,
                "top_threats": top_threats[:3],
                "top_opportunities": top_opportunities[:3],
                "critical_decision": critical_decision,
                "competitive_position_score": competitive_position_score,
                "disruption_risk_score": disruption_risk_score,
                "system_health_score": system_health_score,
                "momentum_score": momentum_score,
                "immediate_actions": immediate_actions,
            }

        except Exception as e:
            logger.error(f"Error generating strategic overview: {e}", exc_info=True)
            raise

    async def _run_positioning_analysis(
        self, company: str, industry: str, base_result: Dict
    ) -> Any:
        """Run positioning analysis with error handling"""
        try:
            return await self.positioning_agent.execute({
                "company": company,
                "industry": industry,
                "market_data": base_result.get("market_analysis", {}),
                "financial_data": base_result.get("financial_analysis", {}),
                "research_data": base_result.get("research_summary", {}),
            })
        except Exception as e:
            logger.warning(f"Positioning analysis failed: {e}")
            return None

    async def _run_disruption_analysis(
        self, company: str, industry: str, base_result: Dict
    ) -> Any:
        """Run disruption analysis with error handling"""
        try:
            return await self.disruption_agent.execute({
                "company": company,
                "industry": industry,
                "market_data": base_result.get("market_analysis", {}),
                "financial_data": base_result.get("financial_analysis", {}),
                "research_data": base_result.get("research_summary", {}),
            })
        except Exception as e:
            logger.warning(f"Disruption analysis failed: {e}")
            return None

    async def _run_systems_analysis(
        self, company: str, industry: str, base_result: Dict
    ) -> Any:
        """Run systems analysis with error handling"""
        try:
            return await self.systems_agent.execute({
                "company": company,
                "industry": industry,
                "market_data": base_result.get("market_analysis", {}),
                "financial_data": base_result.get("financial_analysis", {}),
                "framework_analysis": base_result.get("framework_analysis", {}),
            })
        except Exception as e:
            logger.warning(f"Systems analysis failed: {e}")
            return None

    async def _run_momentum_analysis(
        self, company: str, industry: str, base_result: Dict
    ) -> Any:
        """Run momentum analysis with error handling"""
        try:
            return await self.momentum_agent.execute({
                "company": company,
                "industry": industry,
                "market_data": base_result.get("market_analysis", {}),
                "financial_data": base_result.get("financial_analysis", {}),
                "research_data": base_result.get("research_summary", {}),
            })
        except Exception as e:
            logger.warning(f"Momentum analysis failed: {e}")
            return None

    def _calculate_strategic_health(
        self, positioning: Any, disruption: Any, systems: Any
    ) -> float:
        """Calculate overall strategic health score (0-100)"""
        scores = []

        # Position score (0-100, higher is better)
        if positioning:
            position_score = self._calculate_position_score(positioning)
            scores.append(position_score)

        # Disruption score (invert: 0-100, lower disruption = higher health)
        if disruption:
            disruption_risk = getattr(disruption, 'overall_disruption_risk', 50)
            disruption_health = 100 - disruption_risk
            scores.append(disruption_health)

        # System health score
        if systems:
            system_score = self._calculate_system_score(systems)
            scores.append(system_score)

        # Default to 50 if no data
        if not scores:
            return 50.0

        # Weighted average (can be customized)
        return sum(scores) / len(scores)

    def _calculate_position_score(self, positioning: Any) -> float:
        """Calculate competitive position health (0-100)"""
        if not positioning:
            return 50.0

        # Use competitive_advantage_score if available
        if hasattr(positioning, 'competitive_advantage_score'):
            return float(getattr(positioning, 'competitive_advantage_score', 50))

        # Otherwise calculate from position data
        return 65.0  # Default moderate score

    def _calculate_disruption_score(self, disruption: Any) -> float:
        """Calculate disruption risk score (0-100, higher = more risk)"""
        if not disruption:
            return 30.0  # Default low-moderate risk

        return float(getattr(disruption, 'overall_disruption_risk', 30))

    def _calculate_system_score(self, systems: Any) -> float:
        """Calculate system health score (0-100)"""
        if not systems:
            return 60.0

        # Count reinforcing vs balancing loops
        feedback_loops = getattr(systems, 'feedback_loops', [])
        if not feedback_loops:
            return 60.0

        reinforcing_count = sum(
            1 for loop in feedback_loops if getattr(loop, 'loop_type', '') == 'Reinforcing'
        )
        total_loops = len(feedback_loops)

        # More reinforcing loops = better momentum
        if total_loops > 0:
            reinforcing_ratio = reinforcing_count / total_loops
            return 50 + (reinforcing_ratio * 50)  # 50-100 range

        return 60.0

    def _calculate_momentum_score(self, momentum: Any) -> float:
        """Calculate momentum score (0-100)"""
        if not momentum:
            return 60.0  # Default moderate momentum

        return float(getattr(momentum, 'overall_score', 60))

    def _extract_top_threats(
        self, positioning: Any, disruption: Any, systems: Any
    ) -> List[str]:
        """Extract and rank top threats"""
        threats = []

        # From disruption analysis
        if disruption:
            disruption_threats = getattr(disruption, 'active_threats', [])
            for threat in disruption_threats[:2]:
                threat_name = getattr(threat, 'source', 'Unknown threat')
                threat_score = getattr(threat, 'disruption_score', 0)
                threats.append(f"{threat_name} (Risk: {threat_score}/100)")

        # From positioning analysis
        if positioning:
            position_threats = getattr(positioning, 'position_threats', [])
            for threat in position_threats[:1]:
                threat_desc = getattr(threat, 'threat_description', 'Position threat')
                threats.append(threat_desc)

        # From systems analysis
        if systems:
            # Look for negative feedback loops
            feedback_loops = getattr(systems, 'feedback_loops', [])
            for loop in feedback_loops[:1]:
                if getattr(loop, 'loop_type', '') == 'Balancing':
                    loop_desc = getattr(loop, 'description', 'System constraint')
                    threats.append(f"System constraint: {loop_desc}")

        return threats if threats else ["No critical threats identified"]

    def _extract_top_opportunities(
        self, positioning: Any, systems: Any
    ) -> List[str]:
        """Extract and rank top opportunities"""
        opportunities = []

        # From positioning analysis
        if positioning:
            white_spaces = getattr(positioning, 'white_space_opportunities', [])
            for space in white_spaces[:2]:
                opp_desc = getattr(space, 'opportunity_description', 'White space opportunity')
                opportunities.append(opp_desc)

        # From systems analysis
        if systems:
            leverage_points = getattr(systems, 'leverage_points', [])
            for lp in leverage_points[:1]:
                intervention = getattr(lp, 'intervention_description', 'Leverage point')
                impact = getattr(lp, 'leverage_level', 0)
                opportunities.append(f"{intervention} (Impact level: {impact}/12)")

        return opportunities if opportunities else ["No major opportunities identified"]

    def _identify_critical_decision(
        self, threats: List[str], opportunities: List[str]
    ) -> Optional[str]:
        """Identify the most critical decision requiring attention"""
        if not threats and not opportunities:
            return None

        # Prioritize highest severity threat
        if threats and threats[0] != "No critical threats identified":
            return f"Address urgent threat: {threats[0]}"

        # Otherwise highlight top opportunity
        if opportunities and opportunities[0] != "No major opportunities identified":
            return f"Capture opportunity: {opportunities[0]}"

        return None

    def _determine_health_level(self, score: float) -> str:
        """Determine health level from score"""
        if score >= 80:
            return "excellent"
        elif score >= 70:
            return "strong"
        elif score >= 50:
            return "stable"
        elif score >= 30:
            return "concerning"
        else:
            return "critical"

    def _determine_health_trend(self, score: float) -> str:
        """Determine health trend (requires historical data)"""
        # TODO: Compare with previous scores when monitor history is available
        return "stable"

    def _generate_immediate_actions(
        self, threats: List[str], opportunities: List[str], health_score: float
    ) -> List[str]:
        """Generate immediate action items"""
        actions = []

        # Urgent actions for low health
        if health_score < 40:
            actions.append("URGENT: Convene strategy team to address critical health issues")

        # Threat-based actions
        if threats and len(threats) > 0 and threats[0] != "No critical threats identified":
            actions.append(f"Develop mitigation plan for: {threats[0]}")

        # Opportunity-based actions
        if opportunities and len(opportunities) > 0 and opportunities[0] != "No major opportunities identified":
            actions.append(f"Evaluate business case for: {opportunities[0]}")

        # Default action
        if not actions:
            actions.append("Continue monitoring strategic position")

        return actions[:5]  # Limit to 5 actions
