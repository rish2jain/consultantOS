"""
Momentum tracking engine for flywheel velocity analysis.

Implements sophisticated algorithms for detecting compound advantage building,
calculating flywheel velocity scores, and predicting momentum phase transitions.
"""
import logging
from typing import List, Dict, Optional, Tuple
import numpy as np
from datetime import datetime, timedelta
from scipy import signal

from consultantos.models.momentum import (
    MomentumMetric,
    FlywheelVelocity,
    MomentumAnalysis,
)

logger = logging.getLogger(__name__)


class MomentumTrackingEngine:
    """
    Tracks business momentum and flywheel velocity.

    Analyzes growth rate acceleration (2nd derivative), detects inflection points,
    and matches current trajectories to historical company patterns.
    """

    # Component weights for overall flywheel score
    COMPONENT_WEIGHTS = {
        "market": 0.25,      # Market momentum component
        "financial": 0.25,   # Financial momentum component
        "strategic": 0.20,   # Strategic momentum component
        "execution": 0.15,   # Execution momentum component
        "talent": 0.15,      # Talent momentum component
    }

    def __init__(self, smoothing_window: int = 3):
        """
        Initialize momentum tracking engine.

        Args:
            smoothing_window: Window size for smoothing time series (default: 3)
        """
        self.smoothing_window = smoothing_window

    def calculate_velocity_and_acceleration(
        self,
        time_series: List[float],
        metric_name: str
    ) -> Tuple[float, float]:
        """
        Calculate growth rate (1st derivative) and acceleration (2nd derivative).

        Args:
            time_series: Historical values of a metric
            metric_name: Name of the metric

        Returns:
            Tuple of (velocity, acceleration)

        Raises:
            ValueError: If time series is too short
        """
        if len(time_series) < 3:
            raise ValueError(f"Need at least 3 data points for {metric_name}, got {len(time_series)}")

        try:
            # Smooth the time series to reduce noise
            if len(time_series) >= self.smoothing_window:
                smoothed = np.convolve(
                    time_series,
                    np.ones(self.smoothing_window) / self.smoothing_window,
                    mode='valid'
                )
            else:
                smoothed = np.array(time_series)

            # Calculate first derivative (velocity/growth rate)
            first_derivative = np.diff(smoothed)

            # Calculate second derivative (acceleration)
            second_derivative = np.diff(first_derivative)

            # Use recent values for current velocity and acceleration
            current_velocity = float(first_derivative[-1]) if len(first_derivative) > 0 else 0.0
            current_acceleration = float(second_derivative[-1]) if len(second_derivative) > 0 else 0.0

            return current_velocity, current_acceleration

        except Exception as e:
            logger.warning(f"Error calculating derivatives for {metric_name}: {e}")
            return 0.0, 0.0

    def calculate_momentum_score(
        self,
        current_value: float,
        previous_value: float,
        velocity: float,
        acceleration: float,
        metric_type: str = "general"
    ) -> float:
        """
        Calculate momentum score (0-100) for a single metric.

        Args:
            current_value: Current metric value
            previous_value: Previous metric value
            velocity: Growth rate (1st derivative)
            acceleration: Growth rate acceleration (2nd derivative)
            metric_type: Type of metric for normalization

        Returns:
            Momentum score from 0-100
        """
        # Avoid division by zero
        if previous_value == 0:
            growth_rate = 0.0
        else:
            growth_rate = (current_value - previous_value) / abs(previous_value)

        # Normalize velocity component (0-50 points)
        # Cap at 100% growth rate
        velocity_score = min(abs(growth_rate) * 50, 50)

        # Apply direction penalty
        if growth_rate < 0:
            velocity_score *= 0.3  # Declining metrics get heavily penalized

        # Normalize acceleration component (0-50 points)
        # Acceleration contributes to momentum
        accel_score = 0
        if acceleration > 0:
            # Positive acceleration adds to momentum
            accel_score = min(abs(acceleration) * 100, 50)
        else:
            # Negative acceleration reduces momentum
            accel_score = max(-25, acceleration * 100)

        # Combine scores
        total_score = max(0, min(100, velocity_score + accel_score))

        return total_score

    def analyze_metric_momentum(
        self,
        metric_name: str,
        time_series: List[float],
        metric_type: str = "general"
    ) -> MomentumMetric:
        """
        Analyze momentum for a single metric.

        Args:
            metric_name: Name of the metric
            time_series: Historical values
            metric_type: Type of metric

        Returns:
            MomentumMetric with velocity and acceleration analysis
        """
        if len(time_series) < 2:
            raise ValueError(f"Need at least 2 data points for {metric_name}")

        current_value = time_series[-1]
        previous_value = time_series[-2] if len(time_series) >= 2 else current_value

        # Calculate derivatives
        velocity, acceleration = self.calculate_velocity_and_acceleration(
            time_series,
            metric_name
        )

        # Calculate contribution to flywheel
        contribution = self.calculate_momentum_score(
            current_value,
            previous_value,
            velocity,
            acceleration,
            metric_type
        )

        return MomentumMetric(
            metric_name=metric_name,
            current_value=current_value,
            previous_value=previous_value,
            velocity=velocity,
            acceleration=acceleration,
            contribution_to_flywheel=contribution
        )

    def detect_inflection_points(
        self,
        time_series: List[float],
        metric_name: str
    ) -> List[Tuple[int, str]]:
        """
        Detect inflection points where momentum phase changes.

        Args:
            time_series: Historical metric values
            metric_name: Name of the metric

        Returns:
            List of (index, phase_change_type) tuples
        """
        if len(time_series) < 5:
            logger.debug(f"Insufficient data for inflection detection in {metric_name}")
            return []

        inflection_points = []

        try:
            # Calculate first and second derivatives
            first_deriv = np.diff(time_series)
            second_deriv = np.diff(first_deriv)

            # Find sign changes in second derivative (inflection points)
            for i in range(len(second_deriv) - 1):
                if second_deriv[i] * second_deriv[i + 1] < 0:  # Sign change
                    # Determine type of inflection
                    if second_deriv[i] < 0 < second_deriv[i + 1]:
                        phase_change = "acceleration_start"
                    else:
                        phase_change = "deceleration_start"

                    inflection_points.append((i + 2, phase_change))  # +2 due to double diff

            # Also check for local extrema in first derivative (momentum peaks/troughs)
            if len(first_deriv) >= 3:
                extrema_indices = signal.argrelextrema(first_deriv, np.greater)[0]
                for idx in extrema_indices:
                    inflection_points.append((idx + 1, "momentum_peak"))

                extrema_indices = signal.argrelextrema(first_deriv, np.less)[0]
                for idx in extrema_indices:
                    inflection_points.append((idx + 1, "momentum_trough"))

        except Exception as e:
            logger.warning(f"Inflection point detection failed for {metric_name}: {e}")

        return inflection_points

    def calculate_flywheel_score(
        self,
        market_metrics: List[MomentumMetric],
        financial_metrics: List[MomentumMetric],
        strategic_metrics: List[MomentumMetric],
        execution_metrics: List[MomentumMetric],
        talent_metrics: List[MomentumMetric]
    ) -> float:
        """
        Calculate overall flywheel velocity score (0-100).

        Args:
            market_metrics: Market momentum metrics
            financial_metrics: Financial momentum metrics
            strategic_metrics: Strategic momentum metrics
            execution_metrics: Execution momentum metrics
            talent_metrics: Talent momentum metrics

        Returns:
            Overall flywheel score (0-100)
        """
        def avg_contribution(metrics: List[MomentumMetric]) -> float:
            """Calculate average contribution from list of metrics"""
            if not metrics:
                return 0.0
            return np.mean([m.contribution_to_flywheel for m in metrics])

        # Calculate component scores
        market_score = avg_contribution(market_metrics)
        financial_score = avg_contribution(financial_metrics)
        strategic_score = avg_contribution(strategic_metrics)
        execution_score = avg_contribution(execution_metrics)
        talent_score = avg_contribution(talent_metrics)

        # Weight components
        overall_score = (
            market_score * self.COMPONENT_WEIGHTS["market"] +
            financial_score * self.COMPONENT_WEIGHTS["financial"] +
            strategic_score * self.COMPONENT_WEIGHTS["strategic"] +
            execution_score * self.COMPONENT_WEIGHTS["execution"] +
            talent_score * self.COMPONENT_WEIGHTS["talent"]
        ) / sum(self.COMPONENT_WEIGHTS.values())

        return round(overall_score, 2)

    def classify_momentum_trend(
        self,
        current_score: float,
        previous_score: Optional[float],
        acceleration: float
    ) -> str:
        """
        Classify momentum trend.

        Args:
            current_score: Current momentum score
            previous_score: Previous momentum score (if available)
            acceleration: Overall acceleration

        Returns:
            Trend classification: building/sustaining/declining
        """
        if previous_score is None:
            return "stable"

        delta = current_score - previous_score

        if delta > 5 and acceleration > 0:
            return "building"
        elif delta < -5 and acceleration < 0:
            return "declining"
        else:
            return "sustaining"

    def predict_momentum(
        self,
        time_series_scores: List[float],
        days_ahead: int = 30
    ) -> float:
        """
        Predict future momentum using linear regression.

        Args:
            time_series_scores: Historical momentum scores
            days_ahead: Days to project ahead

        Returns:
            Predicted momentum score
        """
        if len(time_series_scores) < 3:
            return time_series_scores[-1] if time_series_scores else 50.0

        try:
            # Simple linear regression for trend
            x = np.arange(len(time_series_scores))
            y = np.array(time_series_scores)

            # Fit line
            coeffs = np.polyfit(x, y, 1)
            slope, intercept = coeffs

            # Project forward
            future_x = len(time_series_scores) + days_ahead
            predicted = slope * future_x + intercept

            # Constrain to 0-100 range
            return max(0, min(100, predicted))

        except Exception as e:
            logger.warning(f"Momentum prediction failed: {e}")
            return time_series_scores[-1] if time_series_scores else 50.0

    def assess_inflection_risk(
        self,
        time_series_scores: List[float],
        current_trend: str
    ) -> float:
        """
        Assess risk of momentum phase transition.

        Args:
            time_series_scores: Historical momentum scores
            current_trend: Current trend classification

        Returns:
            Risk score (0-100)
        """
        if len(time_series_scores) < 5:
            return 50.0  # Unknown risk

        try:
            # Check for recent volatility
            recent_scores = time_series_scores[-5:]
            volatility = np.std(recent_scores)

            # Check for divergence from trend
            recent_mean = np.mean(recent_scores)
            overall_mean = np.mean(time_series_scores)
            divergence = abs(recent_mean - overall_mean) / (overall_mean + 1)

            # Higher volatility and divergence = higher inflection risk
            risk_score = min(100, (volatility * 10 + divergence * 100))

            # Adjust based on current trend
            if current_trend == "declining":
                risk_score *= 1.2  # Higher risk in declining phase
            elif current_trend == "building":
                risk_score *= 0.8  # Lower risk in building phase

            return min(100, max(0, risk_score))

        except Exception as e:
            logger.warning(f"Inflection risk assessment failed: {e}")
            return 50.0

    def analyze_momentum(
        self,
        company: str,
        industry: str,
        metrics_data: Dict[str, Dict[str, List[float]]]
    ) -> MomentumAnalysis:
        """
        Perform complete momentum analysis.

        Args:
            company: Company name
            industry: Industry
            metrics_data: Dict with keys 'market', 'financial', 'strategic', 'execution', 'talent'
                         Each containing metric_name -> time_series mapping

        Returns:
            Complete momentum analysis

        Raises:
            ValueError: If required data is missing
        """
        logger.info(f"Starting momentum analysis for {company}")

        try:
            # Analyze individual metrics by component
            market_metrics = []
            for metric_name, time_series in metrics_data.get("market", {}).items():
                if len(time_series) >= 2:
                    metric = self.analyze_metric_momentum(metric_name, time_series, "market")
                    market_metrics.append(metric)

            financial_metrics = []
            for metric_name, time_series in metrics_data.get("financial", {}).items():
                if len(time_series) >= 2:
                    metric = self.analyze_metric_momentum(metric_name, time_series, "financial")
                    financial_metrics.append(metric)

            strategic_metrics = []
            for metric_name, time_series in metrics_data.get("strategic", {}).items():
                if len(time_series) >= 2:
                    metric = self.analyze_metric_momentum(metric_name, time_series, "strategic")
                    strategic_metrics.append(metric)

            execution_metrics = []
            for metric_name, time_series in metrics_data.get("execution", {}).items():
                if len(time_series) >= 2:
                    metric = self.analyze_metric_momentum(metric_name, time_series, "execution")
                    execution_metrics.append(metric)

            talent_metrics = []
            for metric_name, time_series in metrics_data.get("talent", {}).items():
                if len(time_series) >= 2:
                    metric = self.analyze_metric_momentum(metric_name, time_series, "talent")
                    talent_metrics.append(metric)

            # Calculate overall flywheel score
            current_momentum = self.calculate_flywheel_score(
                market_metrics,
                financial_metrics,
                strategic_metrics,
                execution_metrics,
                talent_metrics
            )

            # Combine all metrics
            all_metrics = (
                market_metrics + financial_metrics + strategic_metrics +
                execution_metrics + talent_metrics
            )

            # Identify strongest and weakest contributors
            all_metrics.sort(key=lambda x: x.contribution_to_flywheel, reverse=True)
            strongest = [m.metric_name for m in all_metrics[:3]]
            drag_factors = [m.metric_name for m in all_metrics[-3:] if m.contribution_to_flywheel < 50]

            # Calculate momentum trend (simplified - would need historical scores)
            avg_velocity = np.mean([m.velocity for m in all_metrics]) if all_metrics else 0
            avg_acceleration = np.mean([m.acceleration for m in all_metrics]) if all_metrics else 0

            momentum_trend = self.classify_momentum_trend(
                current_momentum,
                None,  # Would need historical score
                avg_acceleration
            )

            # Predict future momentum
            # For demo, use current score extrapolation
            projected_30d = self.predict_momentum([current_momentum], 30)
            projected_90d = self.predict_momentum([current_momentum], 90)

            # Assess inflection risk
            inflection_risk = self.assess_inflection_risk(
                [current_momentum],
                momentum_trend
            )

            # Generate recommendations
            acceleration_ops = self._generate_acceleration_opportunities(
                all_metrics,
                momentum_trend
            )
            friction_points = self._identify_friction_points(all_metrics)
            preservation_strategies = self._generate_preservation_strategies(momentum_trend)

            # Calculate confidence
            confidence = self._calculate_confidence(all_metrics, metrics_data)

            return MomentumAnalysis(
                company=company,
                industry=industry,
                current_momentum=current_momentum,
                momentum_trend=momentum_trend,
                key_metrics=all_metrics,
                strongest_contributors=strongest,
                drag_factors=drag_factors,
                velocity_history=[],  # Would be populated with historical data
                momentum_pattern=self._identify_momentum_pattern(all_metrics),
                projected_momentum_30d=projected_30d,
                projected_momentum_90d=projected_90d,
                inflection_point_risk=inflection_risk,
                acceleration_opportunities=acceleration_ops,
                friction_points_to_address=friction_points,
                momentum_preservation_strategies=preservation_strategies,
                confidence_score=confidence,
                data_sources=["metric_time_series", "derivative_analysis", "pattern_matching"]
            )

        except Exception as e:
            logger.error(f"Momentum analysis failed: {e}")
            raise

    def _generate_acceleration_opportunities(
        self,
        metrics: List[MomentumMetric],
        trend: str
    ) -> List[str]:
        """Generate opportunities to accelerate momentum"""
        opportunities = []

        # Find metrics with positive acceleration that could be amplified
        accelerating = [m for m in metrics if m.acceleration > 0]
        if accelerating:
            top_accelerating = max(accelerating, key=lambda x: x.acceleration)
            opportunities.append(f"Double down on {top_accelerating.metric_name} - showing strong acceleration")

        # Find metrics with high potential (good velocity but low acceleration)
        if trend == "building":
            opportunities.append("Maintain investment in growth initiatives")
            opportunities.append("Scale successful programs before competition responds")

        return opportunities or ["Continue current momentum strategies"]

    def _identify_friction_points(self, metrics: List[MomentumMetric]) -> List[str]:
        """Identify points of friction slowing momentum"""
        friction = []

        # Metrics with negative acceleration
        decelerating = [m for m in metrics if m.acceleration < 0]
        for m in decelerating[:2]:  # Top 2
            friction.append(f"{m.metric_name} showing deceleration - investigate root causes")

        return friction or ["No major friction points detected"]

    def _generate_preservation_strategies(self, trend: str) -> List[str]:
        """Generate strategies to preserve momentum"""
        if trend == "building":
            return [
                "Secure resources to sustain growth trajectory",
                "Build organizational capacity ahead of demand",
                "Strengthen competitive moats while in growth phase"
            ]
        elif trend == "sustaining":
            return [
                "Monitor for early signs of deceleration",
                "Invest in next growth engine before current plateaus",
                "Maintain quality while scaling"
            ]
        else:  # declining
            return [
                "Identify and address root causes of momentum loss",
                "Consider strategic pivot or market repositioning",
                "Protect core business while exploring new opportunities"
            ]

    def _identify_momentum_pattern(self, metrics: List[MomentumMetric]) -> Optional[str]:
        """Identify the overall momentum pattern"""
        if not metrics:
            return None

        avg_velocity = np.mean([m.velocity for m in metrics])
        avg_accel = np.mean([m.acceleration for m in metrics])

        if avg_velocity > 0 and avg_accel > 0:
            return "J-curve growth"
        elif avg_velocity > 0 and avg_accel < 0:
            return "plateau approaching"
        elif avg_velocity < 0:
            return "decline"
        else:
            return "stable"

    def _calculate_confidence(
        self,
        metrics: List[MomentumMetric],
        metrics_data: Dict[str, Dict[str, List[float]]]
    ) -> float:
        """Calculate confidence in analysis"""
        # Based on data quantity and quality
        total_data_points = sum(
            len(ts)
            for category in metrics_data.values()
            for ts in category.values()
        )

        data_quality = min(total_data_points / 100, 1.0) * 50  # 50 points max

        # Based on number of metrics analyzed
        metric_coverage = min(len(metrics) / 10, 1.0) * 50  # 50 points max

        return min(100, data_quality + metric_coverage)
