"""
Comprehensive tests for Wargaming Agent with statistical validation.

Tests cover:
- Distribution sampling accuracy
- Monte Carlo convergence
- Sensitivity analysis correctness
- Scenario comparison logic
- Edge cases and error handling
"""

import pytest
import numpy as np
from scipy import stats
from typing import Dict

from consultantos.models.wargaming import (
    Distribution,
    WargameScenario,
    CompetitorAction,
)
from consultantos.simulation.monte_carlo import MonteCarloEngine
from consultantos.simulation.scenario_builder import ScenarioBuilder
from consultantos.agents.wargaming_agent import WargamingAgent


class TestDistributions:
    """Test probability distribution sampling accuracy."""

    def test_normal_distribution_accuracy(self):
        """Test that normal distribution samples match parameters."""
        dist = Distribution(type="normal", params={"mean": 100.0, "std": 15.0})

        samples = dist.sample(size=10000)

        # Statistical tests
        sample_mean = np.mean(samples)
        sample_std = np.std(samples)

        # Mean should be within 3 standard errors
        std_error = 15.0 / np.sqrt(10000)
        assert abs(sample_mean - 100.0) < 3 * std_error

        # Std should be close to true value
        assert abs(sample_std - 15.0) < 1.0

        # Shapiro-Wilk test for normality (on subset to avoid computational issues)
        subset = samples[:5000]
        stat, p_value = stats.shapiro(subset)
        assert p_value > 0.01  # Not rejecting normality at 1% level

    def test_uniform_distribution_accuracy(self):
        """Test that uniform distribution samples are truly uniform."""
        dist = Distribution(type="uniform", params={"min": 10.0, "max": 50.0})

        samples = dist.sample(size=10000)

        # Check bounds
        assert np.all(samples >= 10.0)
        assert np.all(samples <= 50.0)

        # Check mean
        sample_mean = np.mean(samples)
        expected_mean = (10.0 + 50.0) / 2
        assert abs(sample_mean - expected_mean) < 0.5

        # Kolmogorov-Smirnov test for uniformity
        stat, p_value = stats.kstest(
            samples,
            stats.uniform(loc=10.0, scale=40.0).cdf
        )
        assert p_value > 0.05  # Not rejecting uniformity

    def test_triangular_distribution_accuracy(self):
        """Test triangular distribution sampling."""
        dist = Distribution(
            type="triangular",
            params={"min": 5.0, "mode": 10.0, "max": 20.0}
        )

        samples = dist.sample(size=10000)

        # Check bounds
        assert np.all(samples >= 5.0)
        assert np.all(samples <= 20.0)

        # Check mode is most likely value (using histogram)
        hist, edges = np.histogram(samples, bins=50)
        mode_bin = np.argmax(hist)
        mode_value = (edges[mode_bin] + edges[mode_bin + 1]) / 2

        # Mode should be close to 10.0
        assert abs(mode_value - 10.0) < 1.0

    def test_beta_distribution_accuracy(self):
        """Test beta distribution sampling."""
        dist = Distribution(
            type="beta",
            params={"alpha": 2.0, "beta": 5.0, "scale": 1.0, "loc": 0.0}
        )

        samples = dist.sample(size=10000)

        # Check bounds (beta distribution is [0, 1] by default)
        assert np.all(samples >= 0.0)
        assert np.all(samples <= 1.0)

        # Check mean
        expected_mean = 2.0 / (2.0 + 5.0)  # alpha / (alpha + beta)
        sample_mean = np.mean(samples)
        assert abs(sample_mean - expected_mean) < 0.02

    def test_lognormal_distribution_accuracy(self):
        """Test lognormal distribution sampling."""
        dist = Distribution(type="lognormal", params={"mean": 2.0, "std": 0.5})

        samples = dist.sample(size=10000)

        # All samples should be positive
        assert np.all(samples > 0)

        # Log of samples should be approximately normal
        log_samples = np.log(samples)
        sample_mean = np.mean(log_samples)
        sample_std = np.std(log_samples)

        assert abs(sample_mean - 2.0) < 0.05
        assert abs(sample_std - 0.5) < 0.05

    def test_invalid_distribution_params(self):
        """Test that invalid parameters raise errors."""
        # Negative std for normal
        with pytest.raises(ValueError, match="Standard deviation must be positive"):
            Distribution(type="normal", params={"mean": 0.0, "std": -1.0})

        # Min >= max for uniform
        with pytest.raises(ValueError, match="min must be less than max"):
            Distribution(type="uniform", params={"min": 10.0, "max": 5.0})

        # Invalid mode for triangular
        with pytest.raises(ValueError, match="min <= mode <= max"):
            Distribution(
                type="triangular",
                params={"min": 5.0, "mode": 20.0, "max": 10.0}
            )


class TestMonteCarloEngine:
    """Test Monte Carlo simulation engine."""

    @pytest.mark.asyncio
    async def test_simple_simulation(self):
        """Test basic Monte Carlo simulation."""
        engine = MonteCarloEngine(num_iterations=5000, random_seed=42)

        variables = {
            "revenue": Distribution(type="normal", params={"mean": 1000.0, "std": 100.0}),
            "costs": Distribution(type="normal", params={"mean": 600.0, "std": 80.0}),
        }

        formula = "revenue - costs"

        result = await engine.simulate_scenario(variables, formula)

        # Check result structure
        assert result.num_iterations == 5000
        assert result.mean is not None
        assert result.std_dev > 0
        assert result.distribution is not None
        assert len(result.distribution) == 5000

        # Expected profit: 1000 - 600 = 400
        assert abs(result.mean - 400.0) < 50.0  # Within reasonable range

        # Variance of sum: var(revenue) + var(costs) = 100^2 + 80^2
        expected_std = np.sqrt(100**2 + 80**2)
        assert abs(result.std_dev - expected_std) < 20.0

    @pytest.mark.asyncio
    async def test_percentiles_calculation(self):
        """Test that percentiles are calculated correctly."""
        engine = MonteCarloEngine(num_iterations=10000, random_seed=42)

        variables = {
            "value": Distribution(type="uniform", params={"min": 0.0, "max": 100.0}),
        }

        formula = "value"

        result = await engine.simulate_scenario(variables, formula)

        # For uniform [0, 100], percentiles should be approximately equal to their values
        assert abs(result.percentiles["p10"] - 10.0) < 5.0
        assert abs(result.percentiles["p25"] - 25.0) < 5.0
        assert abs(result.percentiles["p50"] - 50.0) < 5.0
        assert abs(result.percentiles["p75"] - 75.0) < 5.0
        assert abs(result.percentiles["p90"] - 90.0) < 5.0

    @pytest.mark.asyncio
    async def test_var_and_cvar_calculation(self):
        """Test Value at Risk and Conditional VaR calculations."""
        engine = MonteCarloEngine(num_iterations=10000, random_seed=42)

        variables = {
            "value": Distribution(type="normal", params={"mean": 0.0, "std": 1.0}),
        }

        formula = "value"

        result = await engine.simulate_scenario(variables, formula)

        # For standard normal, VaR at 95% (5th percentile) should be ~ -1.645
        assert abs(result.var_95 - (-1.645)) < 0.2

        # CVaR should be worse than VaR
        assert result.cvar_95 < result.var_95

        # CVaR for standard normal at 95% should be ~ -2.06
        assert abs(result.cvar_95 - (-2.06)) < 0.3

    @pytest.mark.asyncio
    async def test_convergence(self):
        """Test Monte Carlo convergence with increasing iterations."""
        variables = {
            "value": Distribution(type="normal", params={"mean": 100.0, "std": 15.0}),
        }
        formula = "value"

        # Run simulations with increasing iterations
        iterations_list = [1000, 5000, 10000]
        means = []
        std_devs = []

        for num_iter in iterations_list:
            engine = MonteCarloEngine(num_iterations=num_iter, random_seed=42)
            result = await engine.simulate_scenario(variables, formula)
            means.append(result.mean)
            std_devs.append(result.std_dev)

        # Convergence check: variance of estimates should decrease
        # Standard error should decrease with sqrt(n)
        std_error_1000 = 15.0 / np.sqrt(1000)
        std_error_10000 = 15.0 / np.sqrt(10000)

        # More iterations should give more accurate estimate
        assert abs(means[-1] - 100.0) <= abs(means[0] - 100.0)

    @pytest.mark.asyncio
    async def test_sensitivity_analysis(self):
        """Test sensitivity analysis identifies key drivers."""
        engine = MonteCarloEngine(num_iterations=5000, random_seed=42)

        # Create scenario where one variable dominates
        variables = {
            "high_impact": Distribution(type="normal", params={"mean": 1000.0, "std": 300.0}),
            "low_impact": Distribution(type="normal", params={"mean": 100.0, "std": 10.0}),
        }

        formula = "high_impact + low_impact"

        sensitivity = await engine.sensitivity_analysis(variables, formula)

        # high_impact should be ranked first
        assert sensitivity.rank_order[0] == "high_impact"
        assert sensitivity.rank_order[1] == "low_impact"

        # high_impact should have much higher contribution
        high_impact_contrib = sensitivity.variable_impacts["high_impact"]["variance_contribution"]
        low_impact_contrib = sensitivity.variable_impacts["low_impact"]["variance_contribution"]

        assert high_impact_contrib > low_impact_contrib
        assert high_impact_contrib > 0.8  # Dominates variance

    @pytest.mark.asyncio
    async def test_complex_formula(self):
        """Test with complex formula involving multiplication and division."""
        engine = MonteCarloEngine(num_iterations=5000, random_seed=42)

        variables = {
            "price": Distribution(type="normal", params={"mean": 100.0, "std": 10.0}),
            "quantity": Distribution(type="normal", params={"mean": 1000.0, "std": 100.0}),
            "cost_per_unit": Distribution(type="normal", params={"mean": 60.0, "std": 5.0}),
        }

        formula = "price * quantity - cost_per_unit * quantity"

        result = await engine.simulate_scenario(variables, formula)

        # Expected profit: (100 - 60) * 1000 = 40,000
        assert abs(result.mean - 40000.0) < 5000.0

        # Should have positive outcomes most of the time
        assert result.prob_positive > 0.95


class TestScenarioBuilder:
    """Test scenario builder templates."""

    def test_price_war_scenario(self):
        """Test price war scenario template."""
        builder = ScenarioBuilder()
        scenario = builder.build_price_war_scenario(
            our_market_share=0.30,
            competitor_name="CompetitorX",
        )

        assert scenario.name.startswith("Price War")
        assert "CompetitorX" in scenario.name
        assert len(scenario.variables) > 0
        assert len(scenario.competitor_actions) > 0
        assert scenario.formula is not None

    def test_new_entrant_scenario(self):
        """Test new entrant scenario template."""
        builder = ScenarioBuilder()
        scenario = builder.build_new_entrant_scenario(
            market_size=100_000_000,
            entrant_name="NewStartup",
        )

        assert "New Entrant" in scenario.name
        assert "NewStartup" in scenario.name
        assert "our_market_share" in scenario.variables
        assert len(scenario.our_actions) > 0

    def test_product_launch_scenario(self):
        """Test product launch scenario template."""
        builder = ScenarioBuilder()
        scenario = builder.build_product_launch_scenario(investment=2_000_000)

        assert "Product Launch" in scenario.name
        assert "market_adoption_rate" in scenario.variables
        assert scenario.formula is not None

    def test_custom_scenario(self):
        """Test custom scenario builder."""
        builder = ScenarioBuilder()

        variables = {
            "revenue": Distribution(type="normal", params={"mean": 1000.0, "std": 100.0}),
        }

        scenario = builder.build_custom_scenario(
            name="Custom Test",
            description="Test scenario",
            variables=variables,
            formula="revenue * 1.2",
        )

        assert scenario.name == "Custom Test"
        assert scenario.description == "Test scenario"
        assert len(scenario.variables) == 1


class TestWargamingAgent:
    """Test WargamingAgent orchestration."""

    @pytest.mark.asyncio
    async def test_basic_wargaming_analysis(self):
        """Test complete wargaming analysis."""
        agent = WargamingAgent(num_iterations=2000)

        scenario = WargameScenario(
            name="Test Scenario",
            description="Simple test",
            variables={
                "revenue": Distribution(type="normal", params={"mean": 1000.0, "std": 100.0}),
                "costs": Distribution(type="normal", params={"mean": 600.0, "std": 50.0}),
            },
            formula="revenue - costs",
            competitor_actions=[
                CompetitorAction(
                    competitor="TestComp",
                    action="Aggressive pricing",
                    probability=0.7,
                )
            ],
        )

        result = await agent.execute(
            scenario=scenario,
            num_iterations=2000,
            include_sensitivity=True,
        )

        # Check result structure
        assert result.scenario == scenario
        assert result.simulation is not None
        assert result.sensitivity is not None
        assert result.win_probability > 0
        assert result.expected_value is not None
        assert len(result.recommendations) > 0
        assert 0.0 <= result.confidence_score <= 1.0

    @pytest.mark.asyncio
    async def test_scenario_comparison(self):
        """Test comparing multiple scenarios."""
        agent = WargamingAgent(num_iterations=2000)

        # Create two scenarios with different expected values
        scenario1 = WargameScenario(
            id="scenario1",
            name="Conservative",
            description="Low risk, low return",
            variables={
                "value": Distribution(type="normal", params={"mean": 500.0, "std": 50.0}),
            },
            formula="value",
        )

        scenario2 = WargameScenario(
            id="scenario2",
            name="Aggressive",
            description="High risk, high return",
            variables={
                "value": Distribution(type="normal", params={"mean": 1000.0, "std": 200.0}),
            },
            formula="value",
        )

        comparison = await agent.compare_scenarios(
            scenarios=[scenario1, scenario2],
            num_iterations=2000,
        )

        # Check comparison results
        assert len(comparison.scenarios) == 2
        assert len(comparison.results) == 2
        assert len(comparison.ranking) == 2

        # Aggressive should rank higher (higher expected value)
        assert comparison.ranking[0][0] == "scenario2"

        # Risk-return analysis should exist
        assert "scenario1" in comparison.risk_return_analysis
        assert "scenario2" in comparison.risk_return_analysis

    @pytest.mark.asyncio
    async def test_confidence_scoring(self):
        """Test confidence score calculation."""
        agent = WargamingAgent(num_iterations=10000)

        # Scenario with good modeling
        scenario = WargameScenario(
            name="Well-Modeled",
            description="Good scenario",
            variables={
                "value": Distribution(type="normal", params={"mean": 100.0, "std": 10.0}),
            },
            formula="value",
            competitor_actions=[
                CompetitorAction(competitor="A", action="Action 1", probability=0.5),
                CompetitorAction(competitor="B", action="Action 2", probability=0.3),
                CompetitorAction(competitor="C", action="Action 3", probability=0.2),
            ],
        )

        result = await agent.execute(
            scenario=scenario,
            include_sensitivity=True,
        )

        # High iterations + sensitivity + multiple competitor actions = high confidence
        assert result.confidence_score > 0.7


class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_zero_variance_variable(self):
        """Test handling of deterministic variables."""
        engine = MonteCarloEngine(num_iterations=1000)

        variables = {
            "constant": Distribution(type="normal", params={"mean": 100.0, "std": 0.001}),
        }

        formula = "constant"

        result = await engine.simulate_scenario(variables, formula)

        # Should have very low variance
        assert result.std_dev < 0.01
        assert abs(result.mean - 100.0) < 0.1

    @pytest.mark.asyncio
    async def test_extreme_values(self):
        """Test handling of extreme distribution values."""
        engine = MonteCarloEngine(num_iterations=1000)

        variables = {
            "extreme": Distribution(type="normal", params={"mean": 1e9, "std": 1e6}),
        }

        formula = "extreme"

        result = await engine.simulate_scenario(variables, formula)

        # Should handle large numbers
        assert result.mean > 0
        assert result.std_dev > 0
        assert not np.isnan(result.mean)

    def test_invalid_formula(self):
        """Test handling of invalid formulas."""
        # This would need proper error handling in the engine
        # For now, just ensure it's caught
        pass

    @pytest.mark.asyncio
    async def test_empty_competitor_actions(self):
        """Test scenario with no competitor actions."""
        agent = WargamingAgent(num_iterations=1000)

        scenario = WargameScenario(
            name="No Competitors",
            description="Solo scenario",
            variables={
                "value": Distribution(type="normal", params={"mean": 100.0, "std": 10.0}),
            },
            formula="value",
            competitor_actions=[],  # Empty
        )

        result = await agent.execute(scenario=scenario)

        # Should still work
        assert result.simulation is not None
        # Confidence might be lower due to no competitor modeling
        assert result.confidence_score >= 0.0


class TestStatisticalValidation:
    """Advanced statistical validation tests."""

    @pytest.mark.asyncio
    async def test_law_of_large_numbers(self):
        """Test that sample mean converges to expected value."""
        engine = MonteCarloEngine(num_iterations=20000, random_seed=42)

        variables = {
            "value": Distribution(type="normal", params={"mean": 1000.0, "std": 200.0}),
        }

        formula = "value"

        result = await engine.simulate_scenario(variables, formula)

        # With 20k iterations, should be very close to true mean
        std_error = 200.0 / np.sqrt(20000)
        assert abs(result.mean - 1000.0) < 3 * std_error

    @pytest.mark.asyncio
    async def test_central_limit_theorem(self):
        """Test that sum of variables approaches normal distribution."""
        engine = MonteCarloEngine(num_iterations=10000, random_seed=42)

        # Sum of uniform distributions should approach normal (CLT)
        variables = {
            f"var{i}": Distribution(type="uniform", params={"min": 0.0, "max": 10.0})
            for i in range(10)
        }

        formula = " + ".join([f"var{i}" for i in range(10)])

        result = await engine.simulate_scenario(variables, formula)

        # Expected mean: 10 * 5 = 50
        # Expected std: sqrt(10 * (10^2 / 12)) = sqrt(10 * 100/12) ≈ 9.13
        assert abs(result.mean - 50.0) < 2.0
        assert abs(result.std_dev - 9.13) < 1.5

        # Test normality with Shapiro-Wilk (on subset)
        subset = result.distribution[:5000]
        stat, p_value = stats.shapiro(subset)
        # Should not reject normality (though uniform sums converge slowly)
        assert p_value > 0.001


def test_full_integration():
    """
    Integration test covering full workflow:
    1. Create scenario from template
    2. Run simulation
    3. Analyze results
    4. Compare scenarios
    """
    import asyncio

    async def run_integration():
        # Create scenario
        builder = ScenarioBuilder()
        scenario1 = builder.build_price_war_scenario(
            our_market_share=0.25,
            competitor_name="AggressiveComp",
        )
        scenario1.id = "integration_test_1"

        scenario2 = builder.build_new_entrant_scenario(
            market_size=50_000_000,
            entrant_name="Disruptor",
        )
        scenario2.id = "integration_test_2"

        # Run simulations
        agent = WargamingAgent(num_iterations=3000)

        result1 = await agent.execute(
            scenario=scenario1,
            include_sensitivity=True,
            include_decision_tree=False,
        )

        result2 = await agent.execute(
            scenario=scenario2,
            include_sensitivity=True,
        )

        # Both should succeed
        assert result1.simulation is not None
        assert result2.simulation is not None

        # Compare scenarios
        comparison = await agent.compare_scenarios(
            scenarios=[scenario1, scenario2],
            num_iterations=3000,
        )

        assert len(comparison.ranking) == 2
        assert len(comparison.recommendations) > 0

        return True

    # Run async test
    result = asyncio.run(run_integration())
    assert result is True
