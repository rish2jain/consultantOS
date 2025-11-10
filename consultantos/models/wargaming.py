"""
Wargaming and Monte Carlo simulation models.

Provides data models for competitive scenario planning, probability distributions,
and simulation results.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Literal
from pydantic import BaseModel, Field, field_validator
import numpy as np


class Distribution(BaseModel):
    """Probability distribution for Monte Carlo variables."""

    type: Literal["normal", "uniform", "triangular", "beta", "lognormal"] = Field(
        ...,
        description="Type of probability distribution"
    )
    params: Dict[str, float] = Field(
        ...,
        description="Distribution parameters (varies by type)"
    )

    @field_validator('params')
    @classmethod
    def validate_params(cls, v: Dict[str, float], info) -> Dict[str, float]:
        """Validate distribution parameters based on type."""
        dist_type = info.data.get('type') if hasattr(info, 'data') else None

        if dist_type == "normal":
            if "mean" not in v or "std" not in v:
                raise ValueError("Normal distribution requires 'mean' and 'std' parameters")
            if v["std"] <= 0:
                raise ValueError("Standard deviation must be positive")

        elif dist_type == "uniform":
            if "min" not in v or "max" not in v:
                raise ValueError("Uniform distribution requires 'min' and 'max' parameters")
            if v["min"] >= v["max"]:
                raise ValueError("min must be less than max")

        elif dist_type == "triangular":
            if "min" not in v or "mode" not in v or "max" not in v:
                raise ValueError("Triangular distribution requires 'min', 'mode', and 'max' parameters")
            if not (v["min"] <= v["mode"] <= v["max"]):
                raise ValueError("Must satisfy: min <= mode <= max")

        elif dist_type == "beta":
            if "alpha" not in v or "beta" not in v:
                raise ValueError("Beta distribution requires 'alpha' and 'beta' parameters")
            if v["alpha"] <= 0 or v["beta"] <= 0:
                raise ValueError("Alpha and beta must be positive")

        elif dist_type == "lognormal":
            if "mean" not in v or "std" not in v:
                raise ValueError("Lognormal distribution requires 'mean' and 'std' parameters")
            if v["std"] <= 0:
                raise ValueError("Standard deviation must be positive")

        return v

    def sample(self, size: int = 1) -> np.ndarray:
        """
        Sample from the distribution.

        Args:
            size: Number of samples to generate

        Returns:
            Array of samples
        """
        if self.type == "normal":
            return np.random.normal(
                self.params["mean"],
                self.params["std"],
                size=size
            )
        elif self.type == "uniform":
            return np.random.uniform(
                self.params["min"],
                self.params["max"],
                size=size
            )
        elif self.type == "triangular":
            return np.random.triangular(
                self.params["min"],
                self.params["mode"],
                self.params["max"],
                size=size
            )
        elif self.type == "beta":
            # Beta distribution scaled to [0, 1] by default
            # Can add scale/loc params if needed
            scale = self.params.get("scale", 1.0)
            loc = self.params.get("loc", 0.0)
            return loc + scale * np.random.beta(
                self.params["alpha"],
                self.params["beta"],
                size=size
            )
        elif self.type == "lognormal":
            return np.random.lognormal(
                self.params["mean"],
                self.params["std"],
                size=size
            )
        else:
            raise ValueError(f"Unknown distribution type: {self.type}")


class CompetitorAction(BaseModel):
    """Model for competitor actions in a scenario."""

    competitor: str = Field(..., description="Competitor name")
    action: str = Field(..., description="Action description (e.g., 'price cut 20%')")
    probability: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Probability of this action occurring"
    )
    impact_formula: Optional[str] = Field(
        None,
        description="Formula for impact on outcome variables"
    )


class WargameScenario(BaseModel):
    """Competitive wargaming scenario definition."""

    id: Optional[str] = Field(None, description="Unique scenario ID")
    name: str = Field(..., description="Scenario name")
    description: str = Field(..., description="Scenario description")

    # Variables and their distributions
    variables: Dict[str, Distribution] = Field(
        ...,
        description="Variables with probability distributions"
    )

    # Formula to calculate outcome
    formula: str = Field(
        ...,
        description="Python expression for outcome calculation (e.g., 'revenue - costs')"
    )

    # Competitor actions
    competitor_actions: List[CompetitorAction] = Field(
        default_factory=list,
        description="Possible competitor actions and their probabilities"
    )

    # Strategic context
    our_actions: List[str] = Field(
        default_factory=list,
        description="Our strategic actions in this scenario"
    )

    market_conditions: Optional[str] = Field(
        None,
        description="Market conditions context"
    )

    timeframe: Optional[str] = Field(
        None,
        description="Timeframe for scenario (e.g., 'Q1 2025', '6 months')"
    )

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Price War Scenario",
                "description": "Competitor launches aggressive pricing strategy",
                "variables": {
                    "market_share": {
                        "type": "normal",
                        "params": {"mean": 0.25, "std": 0.05}
                    },
                    "price_reduction": {
                        "type": "uniform",
                        "params": {"min": 0.10, "max": 0.30}
                    }
                },
                "formula": "revenue * (1 - price_reduction) * market_share",
                "competitor_actions": [
                    {
                        "competitor": "CompetitorA",
                        "action": "Price cut 25%",
                        "probability": 0.7
                    }
                ],
                "our_actions": ["Match price", "Enhance value proposition"],
                "timeframe": "Q2 2025"
            }
        }


class SimulationResult(BaseModel):
    """Results from Monte Carlo simulation."""

    num_iterations: int = Field(..., description="Number of simulation iterations")

    # Summary statistics
    mean: float = Field(..., description="Mean outcome value")
    median: float = Field(..., description="Median outcome value")
    std_dev: float = Field(..., description="Standard deviation")
    min_value: float = Field(..., description="Minimum value observed")
    max_value: float = Field(..., description="Maximum value observed")

    # Percentiles
    percentiles: Dict[str, float] = Field(
        ...,
        description="Key percentiles (p10, p25, p50, p75, p90, p95, p99)"
    )

    # Probability of positive outcome
    prob_positive: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Probability of positive outcome (> 0)"
    )

    # Value at Risk (VaR)
    var_95: float = Field(
        ...,
        description="Value at Risk at 95% confidence (5th percentile)"
    )

    # Conditional Value at Risk (CVaR)
    cvar_95: float = Field(
        ...,
        description="Conditional VaR (expected value in worst 5% of cases)"
    )

    # Full distribution (optional, for visualization)
    distribution: Optional[List[float]] = Field(
        None,
        description="Full distribution of outcomes (can be large)"
    )

    # Confidence intervals
    confidence_intervals: Dict[str, tuple] = Field(
        default_factory=dict,
        description="Confidence intervals at various levels"
    )


class SensitivityAnalysis(BaseModel):
    """Sensitivity analysis results (tornado diagram data)."""

    variable_impacts: Dict[str, Dict[str, float]] = Field(
        ...,
        description="Impact of each variable on outcome variance"
    )

    rank_order: List[str] = Field(
        ...,
        description="Variables ranked by impact (most to least important)"
    )

    total_variance_explained: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Proportion of variance explained by analyzed variables"
    )


class DecisionNode(BaseModel):
    """Node in a decision tree."""

    id: str
    type: Literal["decision", "chance", "outcome"]
    description: str
    probability: Optional[float] = None
    value: Optional[float] = None
    children: List[str] = Field(default_factory=list)
    expected_value: Optional[float] = None


class DecisionTree(BaseModel):
    """Decision tree for strategic analysis."""

    nodes: Dict[str, DecisionNode] = Field(
        ...,
        description="All nodes in the tree, keyed by node ID"
    )
    root_id: str = Field(..., description="Root node ID")
    optimal_path: Optional[List[str]] = Field(
        None,
        description="Optimal decision path through tree"
    )
    expected_value: Optional[float] = Field(
        None,
        description="Expected value of optimal strategy"
    )


class WargameResult(BaseModel):
    """Complete wargaming analysis result."""

    scenario: WargameScenario = Field(..., description="The scenario analyzed")

    simulation: SimulationResult = Field(
        ...,
        description="Monte Carlo simulation results"
    )

    sensitivity: Optional[SensitivityAnalysis] = Field(
        None,
        description="Sensitivity analysis results"
    )

    decision_tree: Optional[DecisionTree] = Field(
        None,
        description="Strategic decision tree"
    )

    # Strategic insights
    win_probability: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Probability of achieving strategic objectives"
    )

    expected_value: float = Field(
        ...,
        description="Expected value of scenario outcome"
    )

    risk_metrics: Dict[str, float] = Field(
        ...,
        description="Key risk metrics (VaR, CVaR, volatility, etc.)"
    )

    recommendations: List[str] = Field(
        ...,
        description="Strategic recommendations based on analysis"
    )

    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence in analysis quality"
    )

    competitor_response_probabilities: Dict[str, float] = Field(
        default_factory=dict,
        description="Probabilities of different competitor responses"
    )

    created_at: datetime = Field(default_factory=datetime.utcnow)


class ScenarioComparison(BaseModel):
    """Comparison of multiple scenarios."""

    scenarios: List[str] = Field(..., description="Scenario IDs being compared")

    results: Dict[str, WargameResult] = Field(
        ...,
        description="Results for each scenario"
    )

    ranking: List[tuple[str, float]] = Field(
        ...,
        description="Scenarios ranked by expected value"
    )

    risk_return_analysis: Dict[str, Dict[str, float]] = Field(
        ...,
        description="Risk-return profile for each scenario"
    )

    dominant_strategy: Optional[str] = Field(
        None,
        description="Dominant strategy if one exists"
    )

    recommendations: List[str] = Field(
        ...,
        description="Comparative strategic recommendations"
    )


# Request/Response models for API

class CreateScenarioRequest(BaseModel):
    """Request to create a new wargaming scenario."""

    scenario: WargameScenario


class SimulateRequest(BaseModel):
    """Request to run Monte Carlo simulation."""

    scenario_id: Optional[str] = None
    scenario: Optional[WargameScenario] = None
    num_iterations: int = Field(
        10000,
        ge=1000,
        le=100000,
        description="Number of Monte Carlo iterations"
    )
    include_sensitivity: bool = Field(
        True,
        description="Include sensitivity analysis"
    )
    include_decision_tree: bool = Field(
        False,
        description="Generate decision tree"
    )

    @field_validator('scenario_id', 'scenario')
    @classmethod
    def validate_scenario_source(cls, v, info):
        """Ensure either scenario_id or scenario is provided."""
        values = info.data
        scenario_id = values.get('scenario_id')
        scenario = values.get('scenario')

        if not scenario_id and not scenario:
            raise ValueError("Either scenario_id or scenario must be provided")

        return v


class CompareRequest(BaseModel):
    """Request to compare multiple scenarios."""

    scenario_ids: List[str] = Field(
        ...,
        min_length=2,
        description="Scenario IDs to compare"
    )
    num_iterations: int = Field(
        10000,
        ge=1000,
        le=100000,
        description="Number of Monte Carlo iterations per scenario"
    )
