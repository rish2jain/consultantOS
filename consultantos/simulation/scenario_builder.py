"""
Scenario builder for competitive wargaming.

Provides templates and builders for common competitive scenarios like
price wars, new market entrants, product launches, and strategic responses.
"""

from typing import Dict, List, Optional
import logging
from datetime import datetime, timedelta

from consultantos.models.wargaming import (
    WargameScenario,
    Distribution,
    CompetitorAction,
    DecisionNode,
    DecisionTree,
)

logger = logging.getLogger(__name__)


class ScenarioBuilder:
    """
    Builder for competitive wargaming scenarios.

    Provides templates for common scenarios and utilities for
    building custom scenarios with competitive dynamics.
    """

    @staticmethod
    def build_price_war_scenario(
        our_market_share: float = 0.25,
        competitor_name: str = "Competitor A",
        timeframe: str = "Q2 2025",
    ) -> WargameScenario:
        """
        Build a price war scenario.

        Args:
            our_market_share: Our current market share (0-1)
            competitor_name: Name of competitor initiating price war
            timeframe: Scenario timeframe

        Returns:
            WargameScenario for price war
        """
        logger.info(f"Building price war scenario vs {competitor_name}")

        return WargameScenario(
            name=f"Price War vs {competitor_name}",
            description=f"{competitor_name} launches aggressive pricing strategy "
            f"to gain market share",
            variables={
                "baseline_revenue": Distribution(
                    type="normal",
                    params={"mean": 10_000_000, "std": 1_000_000},
                ),
                "market_share_change": Distribution(
                    type="triangular",
                    params={"min": -0.15, "mode": -0.05, "max": 0.05},
                ),
                "price_elasticity": Distribution(
                    type="uniform", params={"min": -2.5, "max": -1.5}
                ),
                "competitor_price_cut": Distribution(
                    type="triangular", params={"min": 0.15, "mode": 0.25, "max": 0.35}
                ),
                "our_price_response": Distribution(
                    type="triangular", params={"min": 0.05, "mode": 0.15, "max": 0.25}
                ),
            },
            formula=(
                "baseline_revenue * (1 + market_share_change) * "
                "(1 - our_price_response) * "
                "(1 + price_elasticity * our_price_response)"
            ),
            competitor_actions=[
                CompetitorAction(
                    competitor=competitor_name,
                    action="Aggressive price cut (25-35%)",
                    probability=0.7,
                ),
                CompetitorAction(
                    competitor=competitor_name,
                    action="Moderate price cut (15-25%)",
                    probability=0.25,
                ),
                CompetitorAction(
                    competitor=competitor_name,
                    action="No price action",
                    probability=0.05,
                ),
            ],
            our_actions=[
                "Match competitor price cut",
                "Partial price response",
                "Maintain price, enhance value",
                "Bundle products for effective discount",
            ],
            market_conditions="Intense price competition with multiple players",
            timeframe=timeframe,
        )

    @staticmethod
    def build_new_entrant_scenario(
        market_size: float = 50_000_000,
        entrant_name: str = "New Competitor",
        timeframe: str = "2025",
    ) -> WargameScenario:
        """
        Build a new market entrant scenario.

        Args:
            market_size: Total addressable market size
            entrant_name: Name of new competitor
            timeframe: Scenario timeframe

        Returns:
            WargameScenario for new entrant
        """
        logger.info(f"Building new entrant scenario: {entrant_name}")

        return WargameScenario(
            name=f"New Entrant: {entrant_name}",
            description=f"{entrant_name} enters market with disruptive offering",
            variables={
                "our_market_share": Distribution(
                    type="normal", params={"mean": 0.30, "std": 0.05}
                ),
                "entrant_share_capture": Distribution(
                    type="triangular", params={"min": 0.05, "mode": 0.15, "max": 0.25}
                ),
                "market_growth": Distribution(
                    type="normal", params={"mean": 0.10, "std": 0.05}
                ),
                "defensive_effectiveness": Distribution(
                    type="beta", params={"alpha": 5, "beta": 2, "scale": 1.0}
                ),
            },
            formula=(
                f"{market_size} * (1 + market_growth) * "
                "(our_market_share - entrant_share_capture * (1 - defensive_effectiveness))"
            ),
            competitor_actions=[
                CompetitorAction(
                    competitor=entrant_name,
                    action="Aggressive market entry with low pricing",
                    probability=0.6,
                ),
                CompetitorAction(
                    competitor=entrant_name,
                    action="Premium positioning with innovation",
                    probability=0.3,
                ),
                CompetitorAction(
                    competitor=entrant_name,
                    action="Delayed entry or pivot",
                    probability=0.1,
                ),
            ],
            our_actions=[
                "Strengthen customer relationships",
                "Accelerate product innovation",
                "Preemptive pricing adjustments",
                "Strategic partnerships",
            ],
            market_conditions="New entrant with VC backing and innovative approach",
            timeframe=timeframe,
        )

    @staticmethod
    def build_product_launch_scenario(
        investment: float = 5_000_000,
        timeframe: str = "6 months",
    ) -> WargameScenario:
        """
        Build a product launch scenario.

        Args:
            investment: Total investment in launch
            timeframe: Launch timeframe

        Returns:
            WargameScenario for product launch
        """
        logger.info(f"Building product launch scenario with ${investment:,.0f} investment")

        return WargameScenario(
            name="New Product Launch",
            description="Launch new product into existing market",
            variables={
                "market_adoption_rate": Distribution(
                    type="beta", params={"alpha": 2, "beta": 5, "scale": 0.50}
                ),
                "average_deal_size": Distribution(
                    type="lognormal", params={"mean": 10.5, "std": 0.5}
                ),
                "sales_cycle_months": Distribution(
                    type="triangular", params={"min": 2, "mode": 4, "max": 8}
                ),
                "churn_rate": Distribution(
                    type="beta", params={"alpha": 2, "beta": 20, "scale": 0.30}
                ),
                "marketing_efficiency": Distribution(
                    type="beta", params={"alpha": 4, "beta": 3, "scale": 1.0}
                ),
            },
            formula=(
                "average_deal_size * market_adoption_rate * "
                f"(1 - churn_rate) * marketing_efficiency * 100 - {investment}"
            ),
            competitor_actions=[
                CompetitorAction(
                    competitor="Incumbent A",
                    action="Match product features",
                    probability=0.5,
                ),
                CompetitorAction(
                    competitor="Incumbent A",
                    action="Price war response",
                    probability=0.3,
                ),
                CompetitorAction(
                    competitor="Incumbent B",
                    action="No immediate response",
                    probability=0.2,
                ),
            ],
            our_actions=[
                "Launch with limited beta",
                "Full market launch with marketing blitz",
                "Partner-led go-to-market",
                "Freemium model with upsell",
            ],
            market_conditions="Established market with multiple competitors",
            timeframe=timeframe,
        )

    @staticmethod
    def build_market_expansion_scenario(
        current_revenue: float = 20_000_000,
        new_market_size: float = 30_000_000,
        timeframe: str = "12 months",
    ) -> WargameScenario:
        """
        Build a market expansion scenario.

        Args:
            current_revenue: Current revenue in existing market
            new_market_size: Size of new market
            timeframe: Expansion timeframe

        Returns:
            WargameScenario for market expansion
        """
        logger.info(f"Building market expansion scenario into ${new_market_size:,.0f} market")

        return WargameScenario(
            name="Geographic/Vertical Market Expansion",
            description=f"Expand into new market with TAM of ${new_market_size:,.0f}",
            variables={
                "existing_market_retention": Distribution(
                    type="beta", params={"alpha": 9, "beta": 1, "scale": 1.0}
                ),
                "new_market_penetration": Distribution(
                    type="triangular", params={"min": 0.02, "mode": 0.08, "max": 0.15}
                ),
                "expansion_costs": Distribution(
                    type="normal", params={"mean": 3_000_000, "std": 500_000}
                ),
                "synergy_factor": Distribution(
                    type="beta", params={"alpha": 3, "beta": 2, "scale": 0.30}
                ),
            },
            formula=(
                f"({current_revenue} * existing_market_retention) + "
                f"({new_market_size} * new_market_penetration) + "
                f"({current_revenue} * synergy_factor) - expansion_costs"
            ),
            competitor_actions=[
                CompetitorAction(
                    competitor="Local Incumbent",
                    action="Aggressive defense with local partnerships",
                    probability=0.6,
                ),
                CompetitorAction(
                    competitor="Local Incumbent",
                    action="Price competition",
                    probability=0.3,
                ),
                CompetitorAction(
                    competitor="Other Expanders",
                    action="Also entering market",
                    probability=0.4,
                ),
            ],
            our_actions=[
                "Acquire local player",
                "Organic expansion with sales team",
                "Partnership-led entry",
                "Digital-first approach",
            ],
            market_conditions="New market with established local competitors",
            timeframe=timeframe,
        )

    @staticmethod
    def build_custom_scenario(
        name: str,
        description: str,
        variables: Dict[str, Distribution],
        formula: str,
        competitor_actions: Optional[List[CompetitorAction]] = None,
        our_actions: Optional[List[str]] = None,
        market_conditions: Optional[str] = None,
        timeframe: Optional[str] = None,
    ) -> WargameScenario:
        """
        Build a custom wargaming scenario.

        Args:
            name: Scenario name
            description: Scenario description
            variables: Dictionary of variable distributions
            formula: Outcome calculation formula
            competitor_actions: List of competitor actions
            our_actions: List of our potential actions
            market_conditions: Market conditions description
            timeframe: Scenario timeframe

        Returns:
            WargameScenario
        """
        logger.info(f"Building custom scenario: {name}")

        return WargameScenario(
            name=name,
            description=description,
            variables=variables,
            formula=formula,
            competitor_actions=competitor_actions or [],
            our_actions=our_actions or [],
            market_conditions=market_conditions,
            timeframe=timeframe,
        )

    @staticmethod
    def build_decision_tree(
        scenario: WargameScenario,
        our_decision_options: List[str],
        competitor_responses: Dict[str, List[tuple[str, float]]],
    ) -> DecisionTree:
        """
        Build a decision tree for strategic analysis.

        Args:
            scenario: Base scenario
            our_decision_options: Our available decision options
            competitor_responses: Competitor responses for each of our decisions
                Format: {our_action: [(competitor_action, probability), ...]}

        Returns:
            DecisionTree with expected values
        """
        logger.info(f"Building decision tree for scenario: {scenario.name}")

        nodes = {}
        node_counter = 0

        # Root decision node
        root_id = f"decision_{node_counter}"
        node_counter += 1

        nodes[root_id] = DecisionNode(
            id=root_id,
            type="decision",
            description="Our Strategic Decision",
            children=[],
        )

        # Build tree structure
        for our_action in our_decision_options:
            # Create chance node for this decision
            chance_id = f"chance_{node_counter}"
            node_counter += 1

            nodes[chance_id] = DecisionNode(
                id=chance_id,
                type="chance",
                description=f"After choosing: {our_action}",
                children=[],
            )
            nodes[root_id].children.append(chance_id)

            # Get competitor responses
            responses = competitor_responses.get(our_action, [])

            for competitor_action, probability in responses:
                # Create outcome node
                outcome_id = f"outcome_{node_counter}"
                node_counter += 1

                # Simple outcome value (in real implementation, would run simulation)
                # Here we use a placeholder calculation
                outcome_value = (
                    1_000_000 * (1 - probability * 0.5)
                )  # Simplified for example

                nodes[outcome_id] = DecisionNode(
                    id=outcome_id,
                    type="outcome",
                    description=f"Competitor: {competitor_action}",
                    probability=probability,
                    value=outcome_value,
                )
                nodes[chance_id].children.append(outcome_id)

        # Calculate expected values (backward induction)
        _calculate_expected_values(nodes, root_id)

        # Find optimal path
        optimal_path = _find_optimal_path(nodes, root_id)

        return DecisionTree(
            nodes=nodes,
            root_id=root_id,
            optimal_path=optimal_path,
            expected_value=nodes[root_id].expected_value,
        )


def _calculate_expected_values(nodes: Dict[str, DecisionNode], node_id: str) -> float:
    """
    Calculate expected values using backward induction.

    Args:
        nodes: Dictionary of all nodes
        node_id: Current node ID

    Returns:
        Expected value of this node
    """
    node = nodes[node_id]

    if node.type == "outcome":
        # Leaf node - return its value
        return node.value or 0.0

    if node.type == "chance":
        # Chance node - weighted average of children
        expected_value = 0.0
        for child_id in node.children:
            child_node = nodes[child_id]
            child_ev = _calculate_expected_values(nodes, child_id)
            expected_value += child_ev * (child_node.probability or 1.0)

        node.expected_value = expected_value
        return expected_value

    if node.type == "decision":
        # Decision node - maximum of children
        if not node.children:
            return 0.0

        child_evs = [
            _calculate_expected_values(nodes, child_id) for child_id in node.children
        ]
        expected_value = max(child_evs)

        node.expected_value = expected_value
        return expected_value

    return 0.0


def _find_optimal_path(nodes: Dict[str, DecisionNode], node_id: str) -> List[str]:
    """
    Find optimal decision path through tree.

    Args:
        nodes: Dictionary of all nodes
        node_id: Current node ID

    Returns:
        List of node IDs representing optimal path
    """
    node = nodes[node_id]

    if node.type == "outcome":
        # Leaf node
        return [node_id]

    if node.type == "chance":
        # Chance node - follow highest probability path
        if not node.children:
            return [node_id]

        best_child = max(
            node.children, key=lambda cid: nodes[cid].probability or 0.0
        )
        return [node_id] + _find_optimal_path(nodes, best_child)

    if node.type == "decision":
        # Decision node - follow highest EV path
        if not node.children:
            return [node_id]

        best_child = max(
            node.children, key=lambda cid: nodes[cid].expected_value or 0.0
        )
        return [node_id] + _find_optimal_path(nodes, best_child)

    return [node_id]
