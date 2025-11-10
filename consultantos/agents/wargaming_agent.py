"""
Wargaming Agent for competitive scenario analysis.

Orchestrates Monte Carlo simulations, sensitivity analysis, and strategic
decision analysis for competitive scenarios.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

from consultantos.agents.base_agent import BaseAgent
from consultantos.simulation.monte_carlo import MonteCarloEngine
from consultantos.simulation.scenario_builder import ScenarioBuilder
from consultantos.models.wargaming import (
    WargameScenario,
    WargameResult,
    SimulationResult,
    SensitivityAnalysis,
    DecisionTree,
    ScenarioComparison,
)

logger = logging.getLogger(__name__)


class WargamingInsights(BaseModel):
    """Structured insights from AI analysis."""

    key_findings: List[str] = Field(
        ..., description="Key findings from simulation analysis"
    )
    strategic_recommendations: List[str] = Field(
        ..., description="Strategic recommendations based on results"
    )
    risk_assessment: str = Field(
        ..., description="Overall risk assessment and mitigation strategies"
    )
    competitive_dynamics: str = Field(
        ..., description="Analysis of competitive dynamics and responses"
    )
    confidence_reasoning: str = Field(
        ..., description="Reasoning behind confidence score"
    )


class WargamingAgent(BaseAgent):
    """
    Agent for competitive wargaming and Monte Carlo analysis.

    Capabilities:
    - Monte Carlo simulation with multiple distributions
    - Sensitivity analysis to identify key drivers
    - Strategic decision tree analysis
    - Competitive scenario comparison
    - AI-powered strategic insights
    """

    def __init__(
        self,
        name: str = "WargamingAgent",
        timeout: int = 120,
        num_iterations: int = 10000,
    ):
        """
        Initialize WargamingAgent.

        Args:
            name: Agent name
            timeout: Execution timeout in seconds
            num_iterations: Default Monte Carlo iterations
        """
        super().__init__(name=name, timeout=timeout)
        self.num_iterations = num_iterations
        self.scenario_builder = ScenarioBuilder()

        logger.info(
            f"Initialized WargamingAgent with {num_iterations} default iterations"
        )

    async def execute(
        self,
        scenario: WargameScenario,
        num_iterations: Optional[int] = None,
        include_sensitivity: bool = True,
        include_decision_tree: bool = False,
    ) -> WargameResult:
        """
        Execute wargaming analysis for a scenario.

        Args:
            scenario: Wargaming scenario to analyze
            num_iterations: Monte Carlo iterations (overrides default)
            include_sensitivity: Include sensitivity analysis
            include_decision_tree: Generate decision tree

        Returns:
            WargameResult with comprehensive analysis
        """
        try:
            return await asyncio.wait_for(
                self._execute_internal(
                    scenario,
                    num_iterations or self.num_iterations,
                    include_sensitivity,
                    include_decision_tree,
                ),
                timeout=self.timeout,
            )
        except asyncio.TimeoutError:
            logger.error(f"{self.name} timed out after {self.timeout}s")
            raise
        except Exception as e:
            logger.error(f"{self.name} failed: {e}", exc_info=True)
            raise

    async def _execute_internal(
        self,
        scenario: WargameScenario,
        num_iterations: int,
        include_sensitivity: bool,
        include_decision_tree: bool,
    ) -> WargameResult:
        """Internal execution logic."""
        start_time = datetime.utcnow()

        logger.info(
            f"Starting wargaming analysis: scenario='{scenario.name}', "
            f"iterations={num_iterations}, sensitivity={include_sensitivity}"
        )

        # Initialize Monte Carlo engine
        mc_engine = MonteCarloEngine(
            num_iterations=num_iterations,
            use_antithetic=True,  # Variance reduction
        )

        # Run Monte Carlo simulation
        logger.info("Running Monte Carlo simulation...")
        simulation_result = await mc_engine.simulate_scenario(
            variables=scenario.variables,
            formula=scenario.formula,
        )

        # Run sensitivity analysis if requested
        sensitivity_result = None
        if include_sensitivity:
            logger.info("Performing sensitivity analysis...")
            sensitivity_result = await mc_engine.sensitivity_analysis(
                variables=scenario.variables,
                formula=scenario.formula,
            )

        # Build decision tree if requested
        decision_tree = None
        if include_decision_tree and scenario.our_actions:
            logger.info("Building decision tree...")
            decision_tree = self._build_decision_tree(scenario)

        # Calculate strategic metrics
        win_probability = self._calculate_win_probability(simulation_result)
        risk_metrics = self._calculate_risk_metrics(simulation_result)

        # Generate AI insights
        logger.info("Generating strategic insights...")
        insights = await self._generate_insights(
            scenario, simulation_result, sensitivity_result
        )

        # Calculate confidence score
        confidence_score = self._calculate_confidence(
            simulation_result, sensitivity_result, len(scenario.competitor_actions)
        )

        # Calculate competitor response probabilities
        competitor_probs = {
            action.competitor: action.probability
            for action in scenario.competitor_actions
        }

        elapsed = (datetime.utcnow() - start_time).total_seconds()
        logger.info(
            f"Wargaming analysis complete in {elapsed:.2f}s: "
            f"win_prob={win_probability:.2%}, EV={simulation_result.mean:,.0f}"
        )

        return WargameResult(
            scenario=scenario,
            simulation=simulation_result,
            sensitivity=sensitivity_result,
            decision_tree=decision_tree,
            win_probability=win_probability,
            expected_value=simulation_result.mean,
            risk_metrics=risk_metrics,
            recommendations=insights.strategic_recommendations,
            confidence_score=confidence_score,
            competitor_response_probabilities=competitor_probs,
        )

    def _calculate_win_probability(self, simulation: SimulationResult) -> float:
        """
        Calculate probability of achieving strategic objectives.

        For now, we define "win" as positive outcome.
        In practice, this could be customized based on specific objectives.
        """
        return simulation.prob_positive

    def _calculate_risk_metrics(self, simulation: SimulationResult) -> Dict[str, float]:
        """Calculate comprehensive risk metrics."""
        return {
            "value_at_risk_95": simulation.var_95,
            "conditional_var_95": simulation.cvar_95,
            "volatility": simulation.std_dev,
            "downside_risk": float(
                simulation.std_dev if simulation.mean > 0 else simulation.std_dev * 1.5
            ),
            "coefficient_of_variation": float(
                abs(simulation.std_dev / simulation.mean)
                if simulation.mean != 0
                else 0
            ),
            "probability_of_loss": 1.0 - simulation.prob_positive,
        }

    def _build_decision_tree(self, scenario: WargameScenario) -> DecisionTree:
        """Build decision tree for scenario."""
        # Map our actions to competitor responses
        competitor_responses = {}

        for our_action in scenario.our_actions:
            # For each of our actions, include all competitor responses
            responses = [
                (action.action, action.probability)
                for action in scenario.competitor_actions
            ]
            competitor_responses[our_action] = responses

        return self.scenario_builder.build_decision_tree(
            scenario=scenario,
            our_decision_options=scenario.our_actions,
            competitor_responses=competitor_responses,
        )

    async def _generate_insights(
        self,
        scenario: WargameScenario,
        simulation: SimulationResult,
        sensitivity: Optional[SensitivityAnalysis],
    ) -> WargamingInsights:
        """Generate strategic insights using AI."""
        # Build context for AI
        context = self._build_analysis_context(scenario, simulation, sensitivity)

        # Generate insights using Gemini
        prompt = f"""Analyze this competitive wargaming scenario and provide strategic insights.

Scenario: {scenario.name}
Description: {scenario.description}

Simulation Results:
- Expected Value: ${simulation.mean:,.0f}
- Standard Deviation: ${simulation.std_dev:,.0f}
- Probability of Success: {simulation.prob_positive:.1%}
- Value at Risk (95%): ${simulation.var_95:,.0f}
- 90th Percentile Outcome: ${simulation.percentiles['p90']:,.0f}
- 10th Percentile Outcome: ${simulation.percentiles['p10']:,.0f}

{context}

Provide:
1. Key strategic findings (3-5 bullet points)
2. Strategic recommendations (3-5 actionable recommendations)
3. Risk assessment and mitigation strategies
4. Analysis of competitive dynamics
5. Reasoning for confidence in this analysis
"""

        try:
            insights = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="gemini-1.5-flash-002",
                response_model=WargamingInsights,
                messages=[{"role": "user", "content": prompt}],
            )
            return insights

        except Exception as e:
            logger.warning(f"Failed to generate AI insights: {e}")
            # Return fallback insights
            return self._generate_fallback_insights(scenario, simulation, sensitivity)

    def _build_analysis_context(
        self,
        scenario: WargameScenario,
        simulation: SimulationResult,
        sensitivity: Optional[SensitivityAnalysis],
    ) -> str:
        """Build context string for AI analysis."""
        context_parts = []

        # Add sensitivity analysis if available
        if sensitivity:
            context_parts.append("\nKey Drivers (Sensitivity Analysis):")
            for i, var_name in enumerate(sensitivity.rank_order[:3], 1):
                impact = sensitivity.variable_impacts[var_name]["impact_score"]
                context_parts.append(f"{i}. {var_name}: {impact:.1f}% of variance")

        # Add competitor actions
        if scenario.competitor_actions:
            context_parts.append("\nCompetitor Actions (by probability):")
            sorted_actions = sorted(
                scenario.competitor_actions, key=lambda x: x.probability, reverse=True
            )
            for action in sorted_actions[:3]:
                context_parts.append(
                    f"- {action.competitor}: {action.action} ({action.probability:.0%} probability)"
                )

        # Add our actions
        if scenario.our_actions:
            context_parts.append(f"\nOur Strategic Options: {', '.join(scenario.our_actions)}")

        # Add market conditions
        if scenario.market_conditions:
            context_parts.append(f"\nMarket Conditions: {scenario.market_conditions}")

        return "\n".join(context_parts)

    def _generate_fallback_insights(
        self,
        scenario: WargameScenario,
        simulation: SimulationResult,
        sensitivity: Optional[SensitivityAnalysis],
    ) -> WargamingInsights:
        """Generate basic insights when AI fails."""
        key_findings = [
            f"Expected outcome: ${simulation.mean:,.0f} with {simulation.prob_positive:.0%} success probability",
            f"High variability: ±${simulation.std_dev:,.0f} standard deviation",
            f"Downside risk: ${simulation.var_95:,.0f} in worst 5% of cases",
        ]

        recommendations = [
            "Monitor key variables closely as scenario unfolds",
            "Prepare contingency plans for downside scenarios",
            "Focus on actions that reduce outcome volatility",
        ]

        if sensitivity and sensitivity.rank_order:
            top_driver = sensitivity.rank_order[0]
            impact = sensitivity.variable_impacts[top_driver]["impact_score"]
            key_findings.append(f"Key driver: {top_driver} ({impact:.0f}% of variance)")
            recommendations.append(f"Prioritize managing {top_driver} to reduce risk")

        return WargamingInsights(
            key_findings=key_findings,
            strategic_recommendations=recommendations,
            risk_assessment="Moderate risk with significant uncertainty in outcomes",
            competitive_dynamics="Multiple competitor responses possible with varying probabilities",
            confidence_reasoning="Based on statistical analysis of simulation results",
        )

    def _calculate_confidence(
        self,
        simulation: SimulationResult,
        sensitivity: Optional[SensitivityAnalysis],
        num_competitor_actions: int,
    ) -> float:
        """
        Calculate confidence score for analysis.

        Factors:
        - Number of iterations (convergence)
        - Variance explained by sensitivity analysis
        - Number of competitor actions modeled
        """
        confidence = 0.0

        # Iterations factor (max 0.4)
        if simulation.num_iterations >= 10000:
            confidence += 0.4
        elif simulation.num_iterations >= 5000:
            confidence += 0.3
        elif simulation.num_iterations >= 1000:
            confidence += 0.2
        else:
            confidence += 0.1

        # Sensitivity analysis factor (max 0.3)
        if sensitivity:
            variance_explained = sensitivity.total_variance_explained
            confidence += min(variance_explained, 1.0) * 0.3

        # Competitor modeling factor (max 0.3)
        if num_competitor_actions >= 3:
            confidence += 0.3
        elif num_competitor_actions >= 2:
            confidence += 0.2
        elif num_competitor_actions >= 1:
            confidence += 0.1

        return min(confidence, 1.0)

    async def compare_scenarios(
        self, scenarios: List[WargameScenario], num_iterations: int = 10000
    ) -> ScenarioComparison:
        """
        Compare multiple scenarios.

        Args:
            scenarios: List of scenarios to compare
            num_iterations: Monte Carlo iterations per scenario

        Returns:
            ScenarioComparison with rankings and analysis
        """
        logger.info(f"Comparing {len(scenarios)} scenarios")

        # Run analysis for each scenario
        results = {}
        for scenario in scenarios:
            scenario_id = scenario.id or scenario.name
            result = await self.execute(
                scenario=scenario,
                num_iterations=num_iterations,
                include_sensitivity=True,
                include_decision_tree=False,
            )
            results[scenario_id] = result

        # Rank by expected value
        ranking = sorted(
            results.items(), key=lambda x: x[1].expected_value, reverse=True
        )

        # Calculate risk-return profiles
        risk_return = {
            scenario_id: {
                "expected_return": result.expected_value,
                "volatility": result.risk_metrics["volatility"],
                "sharpe_ratio": (
                    result.expected_value / result.risk_metrics["volatility"]
                    if result.risk_metrics["volatility"] > 0
                    else 0
                ),
                "win_probability": result.win_probability,
            }
            for scenario_id, result in results.items()
        }

        # Identify dominant strategy (if exists)
        dominant = self._find_dominant_strategy(risk_return)

        # Generate comparative recommendations
        recommendations = self._generate_comparative_recommendations(ranking, risk_return)

        return ScenarioComparison(
            scenarios=[s.id or s.name for s in scenarios],
            results=results,
            ranking=[(sid, r.expected_value) for sid, r in ranking],
            risk_return_analysis=risk_return,
            dominant_strategy=dominant,
            recommendations=recommendations,
        )

    def _find_dominant_strategy(
        self, risk_return: Dict[str, Dict[str, float]]
    ) -> Optional[str]:
        """Find dominant strategy if one exists."""
        # A strategy dominates if it has both higher return AND lower risk
        strategies = list(risk_return.items())

        for i, (strategy_i, metrics_i) in enumerate(strategies):
            dominates_all = True

            for j, (strategy_j, metrics_j) in enumerate(strategies):
                if i == j:
                    continue

                # Check if strategy_i dominates strategy_j
                if not (
                    metrics_i["expected_return"] >= metrics_j["expected_return"]
                    and metrics_i["volatility"] <= metrics_j["volatility"]
                ):
                    dominates_all = False
                    break

            if dominates_all:
                return strategy_i

        return None

    def _generate_comparative_recommendations(
        self,
        ranking: List[tuple[str, WargameResult]],
        risk_return: Dict[str, Dict[str, float]],
    ) -> List[str]:
        """Generate recommendations from scenario comparison."""
        recommendations = []

        # Top strategy
        top_scenario, top_result = ranking[0]
        recommendations.append(
            f"Highest expected value: {top_scenario} "
            f"(${top_result.expected_value:,.0f})"
        )

        # Best risk-adjusted
        best_sharpe = max(risk_return.items(), key=lambda x: x[1]["sharpe_ratio"])
        recommendations.append(
            f"Best risk-adjusted return: {best_sharpe[0]} "
            f"(Sharpe ratio: {best_sharpe[1]['sharpe_ratio']:.2f})"
        )

        # Highest win probability
        best_prob = max(risk_return.items(), key=lambda x: x[1]["win_probability"])
        recommendations.append(
            f"Highest win probability: {best_prob[0]} "
            f"({best_prob[1]['win_probability']:.0%})"
        )

        return recommendations
