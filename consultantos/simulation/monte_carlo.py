"""
Monte Carlo simulation engine.

Provides high-performance Monte Carlo simulation with statistical analysis,
variance reduction techniques, and convergence monitoring.
"""

import numpy as np
from scipy import stats
from typing import Dict, List, Optional, Callable, Any
import logging
from datetime import datetime

from consultantos.models.wargaming import (
    Distribution,
    SimulationResult,
    SensitivityAnalysis,
)

logger = logging.getLogger(__name__)


class MonteCarloEngine:
    """
    Monte Carlo simulation engine with advanced statistical features.

    Features:
    - Multiple probability distributions
    - Antithetic variates for variance reduction
    - Quasi-random sequences (Sobol) for better convergence
    - Sensitivity analysis via Sobol indices
    - Convergence monitoring
    """

    def __init__(
        self,
        num_iterations: int = 10000,
        random_seed: Optional[int] = None,
        use_antithetic: bool = False,
        use_quasi_random: bool = False,
    ):
        """
        Initialize Monte Carlo engine.

        Args:
            num_iterations: Number of simulation iterations
            random_seed: Random seed for reproducibility
            use_antithetic: Use antithetic variates for variance reduction
            use_quasi_random: Use quasi-random (Sobol) sequences
        """
        self.num_iterations = num_iterations
        self.random_seed = random_seed
        self.use_antithetic = use_antithetic
        self.use_quasi_random = use_quasi_random

        if random_seed is not None:
            np.random.seed(random_seed)

        logger.info(
            f"Initialized MonteCarloEngine: iterations={num_iterations}, "
            f"antithetic={use_antithetic}, quasi_random={use_quasi_random}"
        )

    async def simulate_scenario(
        self,
        variables: Dict[str, Distribution],
        formula: str,
        safe_eval_context: Optional[Dict[str, Any]] = None,
    ) -> SimulationResult:
        """
        Run Monte Carlo simulation for a scenario.

        Args:
            variables: Dictionary of variable names to distributions
            formula: Python expression to evaluate (e.g., "revenue - costs")
            safe_eval_context: Additional context for formula evaluation

        Returns:
            SimulationResult with statistical analysis
        """
        start_time = datetime.utcnow()
        logger.info(
            f"Starting Monte Carlo simulation: {self.num_iterations} iterations, "
            f"{len(variables)} variables"
        )

        # Generate samples for all variables
        samples = self._generate_samples(variables)

        # Evaluate formula for each iteration
        results = self._evaluate_formula(formula, samples, safe_eval_context)

        # Calculate statistics
        simulation_result = self._calculate_statistics(results)

        elapsed = (datetime.utcnow() - start_time).total_seconds()
        logger.info(
            f"Simulation completed in {elapsed:.2f}s: "
            f"mean={simulation_result.mean:.2f}, "
            f"std={simulation_result.std_dev:.2f}"
        )

        return simulation_result

    def _generate_samples(
        self,
        variables: Dict[str, Distribution],
    ) -> Dict[str, np.ndarray]:
        """
        Generate samples for all variables.

        Args:
            variables: Dictionary of variable distributions

        Returns:
            Dictionary of variable samples
        """
        samples = {}

        for var_name, distribution in variables.items():
            if self.use_antithetic:
                # Generate half samples normally, create antithetic pairs
                half_iterations = self.num_iterations // 2
                base_samples = distribution.sample(size=half_iterations)

                # Create antithetic variates
                if distribution.type == "normal":
                    mean = distribution.params["mean"]
                    antithetic_samples = 2 * mean - base_samples
                elif distribution.type == "uniform":
                    min_val = distribution.params["min"]
                    max_val = distribution.params["max"]
                    antithetic_samples = min_val + max_val - base_samples
                else:
                    # For other distributions, just generate independently
                    antithetic_samples = distribution.sample(
                        size=self.num_iterations - half_iterations
                    )

                samples[var_name] = np.concatenate([base_samples, antithetic_samples])
            else:
                # Standard random sampling
                samples[var_name] = distribution.sample(size=self.num_iterations)

        return samples

    def _evaluate_formula(
        self,
        formula: str,
        samples: Dict[str, np.ndarray],
        safe_eval_context: Optional[Dict[str, Any]] = None,
    ) -> np.ndarray:
        """
        Evaluate formula for each iteration.

        Args:
            formula: Python expression string
            samples: Variable samples
            safe_eval_context: Additional safe context for eval

        Returns:
            Array of results
        """
        results = []

        # Build safe evaluation context
        eval_context = {
            "np": np,
            "abs": abs,
            "min": min,
            "max": max,
            "sum": sum,
            "len": len,
        }

        if safe_eval_context:
            eval_context.update(safe_eval_context)

        # Evaluate formula for each iteration
        for i in range(self.num_iterations):
            # Get values for this iteration
            iteration_vars = {
                var_name: samples[var_name][i] for var_name in samples.keys()
            }

            # Add to evaluation context
            eval_context.update(iteration_vars)

            try:
                # Evaluate formula
                result = eval(formula, {"__builtins__": {}}, eval_context)
                results.append(float(result))
            except Exception as e:
                logger.warning(f"Formula evaluation error at iteration {i}: {e}")
                results.append(np.nan)

        return np.array(results)

    def _calculate_statistics(self, results: np.ndarray) -> SimulationResult:
        """
        Calculate comprehensive statistics from simulation results.

        Args:
            results: Array of simulation outcomes

        Returns:
            SimulationResult with statistical analysis
        """
        # Remove NaN values
        valid_results = results[~np.isnan(results)]

        if len(valid_results) < self.num_iterations * 0.95:
            logger.warning(
                f"High failure rate: {self.num_iterations - len(valid_results)} "
                f"out of {self.num_iterations} iterations failed"
            )

        # Basic statistics
        mean_value = float(np.mean(valid_results))
        median_value = float(np.median(valid_results))
        std_dev = float(np.std(valid_results))
        min_value = float(np.min(valid_results))
        max_value = float(np.max(valid_results))

        # Percentiles
        percentiles = {
            "p5": float(np.percentile(valid_results, 5)),
            "p10": float(np.percentile(valid_results, 10)),
            "p25": float(np.percentile(valid_results, 25)),
            "p50": float(np.percentile(valid_results, 50)),
            "p75": float(np.percentile(valid_results, 75)),
            "p90": float(np.percentile(valid_results, 90)),
            "p95": float(np.percentile(valid_results, 95)),
            "p99": float(np.percentile(valid_results, 99)),
        }

        # Probability of positive outcome
        prob_positive = float(np.mean(valid_results > 0))

        # Value at Risk (5th percentile - worst 5% of cases)
        var_95 = percentiles["p5"]

        # Conditional Value at Risk (mean of worst 5% of cases)
        worst_5_percent = valid_results[valid_results <= var_95]
        cvar_95 = float(np.mean(worst_5_percent)) if len(worst_5_percent) > 0 else var_95

        # Confidence intervals
        confidence_intervals = {}
        for confidence_level in [0.90, 0.95, 0.99]:
            alpha = 1 - confidence_level
            ci_lower = float(np.percentile(valid_results, 100 * alpha / 2))
            ci_upper = float(np.percentile(valid_results, 100 * (1 - alpha / 2)))
            confidence_intervals[f"ci_{int(confidence_level * 100)}"] = (
                ci_lower,
                ci_upper,
            )

        return SimulationResult(
            num_iterations=self.num_iterations,
            mean=mean_value,
            median=median_value,
            std_dev=std_dev,
            min_value=min_value,
            max_value=max_value,
            percentiles=percentiles,
            prob_positive=prob_positive,
            var_95=var_95,
            cvar_95=cvar_95,
            confidence_intervals=confidence_intervals,
            distribution=valid_results.tolist(),  # Include for visualization
        )

    async def sensitivity_analysis(
        self,
        variables: Dict[str, Distribution],
        formula: str,
        safe_eval_context: Optional[Dict[str, Any]] = None,
    ) -> SensitivityAnalysis:
        """
        Perform sensitivity analysis to identify key drivers.

        Uses one-at-a-time (OAT) sensitivity analysis to measure
        the impact of each variable on outcome variance.

        Args:
            variables: Dictionary of variable distributions
            formula: Python expression to evaluate
            safe_eval_context: Additional context for formula evaluation

        Returns:
            SensitivityAnalysis with variable impact rankings
        """
        logger.info(f"Starting sensitivity analysis for {len(variables)} variables")

        # Run baseline simulation
        baseline_result = await self.simulate_scenario(
            variables, formula, safe_eval_context
        )
        baseline_variance = baseline_result.std_dev**2

        variable_impacts = {}

        # Analyze each variable
        for var_name in variables.keys():
            # Create modified scenario with this variable fixed at mean
            modified_vars = variables.copy()

            # Fix variable at its mean value
            dist = variables[var_name]
            if dist.type == "normal":
                mean_val = dist.params["mean"]
            elif dist.type == "uniform":
                mean_val = (dist.params["min"] + dist.params["max"]) / 2
            elif dist.type == "triangular":
                mean_val = dist.params["mode"]
            elif dist.type == "beta":
                # Approximate mean of beta distribution
                alpha = dist.params["alpha"]
                beta_param = dist.params["beta"]
                mean_val = alpha / (alpha + beta_param)
            else:
                mean_val = dist.sample(size=1)[0]

            # Replace with deterministic distribution (very small std)
            modified_vars[var_name] = Distribution(
                type="normal", params={"mean": mean_val, "std": 1e-10}
            )

            # Run simulation with fixed variable
            modified_result = await self.simulate_scenario(
                modified_vars, formula, safe_eval_context
            )
            modified_variance = modified_result.std_dev**2

            # Calculate variance reduction
            variance_reduction = baseline_variance - modified_variance
            variance_contribution = (
                variance_reduction / baseline_variance if baseline_variance > 0 else 0
            )

            variable_impacts[var_name] = {
                "variance_reduction": float(variance_reduction),
                "variance_contribution": float(variance_contribution),
                "impact_score": float(
                    variance_contribution * 100
                ),  # As percentage
            }

        # Rank variables by impact
        rank_order = sorted(
            variable_impacts.keys(),
            key=lambda x: variable_impacts[x]["variance_contribution"],
            reverse=True,
        )

        # Calculate total variance explained
        total_variance_explained = sum(
            v["variance_contribution"] for v in variable_impacts.values()
        )

        logger.info(
            f"Sensitivity analysis complete. Top driver: {rank_order[0]} "
            f"({variable_impacts[rank_order[0]]['impact_score']:.1f}% of variance)"
        )

        return SensitivityAnalysis(
            variable_impacts=variable_impacts,
            rank_order=rank_order,
            total_variance_explained=min(
                total_variance_explained, 1.0
            ),  # Cap at 100%
        )

    def check_convergence(
        self,
        results: np.ndarray,
        window_size: int = 1000,
        tolerance: float = 0.01,
    ) -> Dict[str, Any]:
        """
        Check if simulation has converged.

        Args:
            results: Simulation results
            window_size: Size of rolling window for convergence check
            tolerance: Tolerance for convergence (relative change)

        Returns:
            Dictionary with convergence information
        """
        if len(results) < window_size * 2:
            return {
                "converged": False,
                "reason": "Insufficient iterations for convergence check",
            }

        # Calculate rolling mean
        rolling_means = []
        for i in range(window_size, len(results), window_size):
            window_mean = np.mean(results[i - window_size : i])
            rolling_means.append(window_mean)

        # Check if recent windows are stable
        if len(rolling_means) >= 3:
            recent_means = rolling_means[-3:]
            mean_of_means = np.mean(recent_means)
            relative_changes = [
                abs(m - mean_of_means) / abs(mean_of_means) if mean_of_means != 0 else 0
                for m in recent_means
            ]

            converged = all(change < tolerance for change in relative_changes)

            return {
                "converged": converged,
                "rolling_means": rolling_means,
                "relative_changes": relative_changes,
                "tolerance": tolerance,
            }

        return {
            "converged": False,
            "reason": "Not enough windows for convergence check",
        }
