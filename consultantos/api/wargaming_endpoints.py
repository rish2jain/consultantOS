"""
Wargaming API endpoints.

Provides endpoints for:
- Creating and managing scenarios
- Running Monte Carlo simulations
- Comparing scenarios
- Generating visualizations
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
import logging
from datetime import datetime
import uuid

from consultantos.models.wargaming import (
    WargameScenario,
    WargameResult,
    SimulateRequest,
    CompareRequest,
    CreateScenarioRequest,
    ScenarioComparison,
)
from consultantos.agents.wargaming_agent import WargamingAgent
from consultantos.simulation.scenario_builder import ScenarioBuilder
from consultantos.visualizations.wargaming_charts import (
    create_distribution_chart,
    create_tornado_diagram,
    create_cdf_chart,
    create_decision_tree_chart,
    create_risk_heatmap,
    create_comparison_chart,
)
from consultantos.database import get_db_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/wargaming", tags=["wargaming"])

# In-memory storage for demo (replace with database in production)
_scenarios_db: dict[str, WargameScenario] = {}
_results_db: dict[str, WargameResult] = {}


@router.post("/scenarios", response_model=WargameScenario)
async def create_scenario(request: CreateScenarioRequest):
    """
    Create a new wargaming scenario.

    This endpoint allows you to define a custom competitive scenario
    with variables, formulas, and competitor actions.
    """
    try:
        scenario = request.scenario

        # Generate ID if not provided
        if not scenario.id:
            scenario.id = f"scenario_{uuid.uuid4().hex[:8]}"

        # Store scenario
        _scenarios_db[scenario.id] = scenario

        logger.info(f"Created scenario: {scenario.id} - {scenario.name}")

        return scenario

    except Exception as e:
        logger.error(f"Failed to create scenario: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/scenarios", response_model=List[WargameScenario])
async def list_scenarios():
    """
    List all saved wargaming scenarios.

    Returns a list of all scenarios that have been created.
    """
    return list(_scenarios_db.values())


@router.get("/scenarios/{scenario_id}", response_model=WargameScenario)
async def get_scenario(scenario_id: str):
    """
    Get a specific scenario by ID.
    """
    if scenario_id not in _scenarios_db:
        raise HTTPException(status_code=404, detail=f"Scenario {scenario_id} not found")

    return _scenarios_db[scenario_id]


@router.delete("/scenarios/{scenario_id}")
async def delete_scenario(scenario_id: str):
    """
    Delete a scenario.
    """
    if scenario_id not in _scenarios_db:
        raise HTTPException(status_code=404, detail=f"Scenario {scenario_id} not found")

    del _scenarios_db[scenario_id]

    logger.info(f"Deleted scenario: {scenario_id}")

    return {"status": "deleted", "scenario_id": scenario_id}


@router.post("/scenarios/templates/{template_name}", response_model=WargameScenario)
async def create_from_template(
    template_name: str,
    our_market_share: Optional[float] = 0.25,
    competitor_name: Optional[str] = "Competitor A",
    market_size: Optional[float] = 50_000_000,
    investment: Optional[float] = 5_000_000,
    current_revenue: Optional[float] = 20_000_000,
):
    """
    Create a scenario from a predefined template.

    Available templates:
    - price_war: Price war scenario
    - new_entrant: New market entrant scenario
    - product_launch: New product launch scenario
    - market_expansion: Geographic/vertical expansion scenario

    Each template has customizable parameters.
    """
    scenario_builder = ScenarioBuilder()

    try:
        if template_name == "price_war":
            scenario = scenario_builder.build_price_war_scenario(
                our_market_share=our_market_share,
                competitor_name=competitor_name,
            )
        elif template_name == "new_entrant":
            scenario = scenario_builder.build_new_entrant_scenario(
                market_size=market_size,
                entrant_name=competitor_name,
            )
        elif template_name == "product_launch":
            scenario = scenario_builder.build_product_launch_scenario(
                investment=investment,
            )
        elif template_name == "market_expansion":
            scenario = scenario_builder.build_market_expansion_scenario(
                current_revenue=current_revenue,
                new_market_size=market_size,
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown template: {template_name}. "
                f"Available: price_war, new_entrant, product_launch, market_expansion",
            )

        # Generate ID and store
        scenario.id = f"scenario_{uuid.uuid4().hex[:8]}"
        _scenarios_db[scenario.id] = scenario

        logger.info(f"Created scenario from template '{template_name}': {scenario.id}")

        return scenario

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create scenario from template: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/simulate", response_model=WargameResult)
async def simulate_scenario(request: SimulateRequest):
    """
    Run Monte Carlo simulation for a scenario.

    You can either:
    1. Provide a scenario_id to simulate an existing scenario
    2. Provide a scenario object directly for one-time simulation

    The simulation returns:
    - Statistical analysis (mean, median, percentiles, etc.)
    - Risk metrics (VaR, CVaR, volatility)
    - Win probability and expected value
    - Optional sensitivity analysis
    - Optional decision tree
    - AI-generated strategic insights
    """
    try:
        # Get scenario
        if request.scenario_id:
            if request.scenario_id not in _scenarios_db:
                raise HTTPException(
                    status_code=404,
                    detail=f"Scenario {request.scenario_id} not found"
                )
            scenario = _scenarios_db[request.scenario_id]
        elif request.scenario:
            scenario = request.scenario
        else:
            raise HTTPException(
                status_code=400,
                detail="Either scenario_id or scenario must be provided"
            )

        # Initialize agent
        agent = WargamingAgent(num_iterations=request.num_iterations)

        # Run simulation
        logger.info(
            f"Running simulation: scenario='{scenario.name}', "
            f"iterations={request.num_iterations}"
        )

        result = await agent.execute(
            scenario=scenario,
            num_iterations=request.num_iterations,
            include_sensitivity=request.include_sensitivity,
            include_decision_tree=request.include_decision_tree,
        )

        # Store result
        result_id = f"result_{uuid.uuid4().hex[:8]}"
        _results_db[result_id] = result

        logger.info(
            f"Simulation complete: EV=${result.expected_value:,.0f}, "
            f"win_prob={result.win_probability:.2%}"
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Simulation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")


@router.post("/compare", response_model=ScenarioComparison)
async def compare_scenarios(request: CompareRequest):
    """
    Compare multiple scenarios.

    Runs simulations for all specified scenarios and provides:
    - Ranking by expected value
    - Risk-return analysis for each scenario
    - Identification of dominant strategy (if exists)
    - Comparative recommendations

    Useful for evaluating multiple strategic options.
    """
    try:
        # Validate all scenarios exist
        scenarios = []
        for scenario_id in request.scenario_ids:
            if scenario_id not in _scenarios_db:
                raise HTTPException(
                    status_code=404,
                    detail=f"Scenario {scenario_id} not found"
                )
            scenarios.append(_scenarios_db[scenario_id])

        # Initialize agent
        agent = WargamingAgent(num_iterations=request.num_iterations)

        # Run comparison
        logger.info(f"Comparing {len(scenarios)} scenarios")

        comparison = await agent.compare_scenarios(
            scenarios=scenarios,
            num_iterations=request.num_iterations,
        )

        logger.info(
            f"Comparison complete. Best scenario: "
            f"{comparison.ranking[0][0]} (EV=${comparison.ranking[0][1]:,.0f})"
        )

        return comparison

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Comparison failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")


@router.get("/visualizations/distribution/{result_id}")
async def get_distribution_chart(result_id: str):
    """
    Get probability distribution chart for a simulation result.

    Returns a Plotly JSON chart showing the histogram of outcomes
    with key statistics (mean, median, percentiles).
    """
    if result_id not in _results_db:
        raise HTTPException(status_code=404, detail=f"Result {result_id} not found")

    result = _results_db[result_id]

    try:
        fig = create_distribution_chart(
            simulation=result.simulation,
            title=f"Distribution - {result.scenario.name}",
        )
        return fig.to_json()

    except Exception as e:
        logger.error(f"Failed to create distribution chart: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/visualizations/tornado/{result_id}")
async def get_tornado_diagram(result_id: str, top_n: int = 10):
    """
    Get tornado diagram (sensitivity analysis) for a simulation result.

    Shows which variables have the biggest impact on outcome variance.
    Useful for identifying key drivers and focusing risk management.
    """
    if result_id not in _results_db:
        raise HTTPException(status_code=404, detail=f"Result {result_id} not found")

    result = _results_db[result_id]

    if not result.sensitivity:
        raise HTTPException(
            status_code=400,
            detail="Result does not include sensitivity analysis"
        )

    try:
        fig = create_tornado_diagram(
            sensitivity=result.sensitivity,
            title=f"Key Drivers - {result.scenario.name}",
            top_n=top_n,
        )
        return fig.to_json()

    except Exception as e:
        logger.error(f"Failed to create tornado diagram: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/visualizations/cdf/{result_id}")
async def get_cdf_chart(result_id: str):
    """
    Get cumulative distribution function chart.

    Shows the probability of achieving different outcome levels.
    Useful for understanding downside risk and upside potential.
    """
    if result_id not in _results_db:
        raise HTTPException(status_code=404, detail=f"Result {result_id} not found")

    result = _results_db[result_id]

    try:
        fig = create_cdf_chart(
            simulation=result.simulation,
            title=f"Cumulative Probability - {result.scenario.name}",
        )
        return fig.to_json()

    except Exception as e:
        logger.error(f"Failed to create CDF chart: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/visualizations/decision-tree/{result_id}")
async def get_decision_tree_chart(result_id: str):
    """
    Get decision tree visualization.

    Shows strategic decision options, competitor responses,
    and expected values for each path.
    """
    if result_id not in _results_db:
        raise HTTPException(status_code=404, detail=f"Result {result_id} not found")

    result = _results_db[result_id]

    if not result.decision_tree:
        raise HTTPException(
            status_code=400,
            detail="Result does not include decision tree"
        )

    try:
        fig = create_decision_tree_chart(
            decision_tree=result.decision_tree,
            title=f"Decision Tree - {result.scenario.name}",
        )
        return fig.to_json()

    except Exception as e:
        logger.error(f"Failed to create decision tree chart: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint for wargaming service."""
    return {
        "status": "healthy",
        "service": "wargaming",
        "scenarios_count": len(_scenarios_db),
        "results_count": len(_results_db),
        "timestamp": datetime.utcnow().isoformat(),
    }
