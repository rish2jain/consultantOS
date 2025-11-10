"""
Statistical anomaly detection using Facebook Prophet.

Provides time series forecasting and anomaly detection to identify
material changes beyond normal variance and seasonality.
"""

import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class AnomalyType(str, Enum):
    """Types of anomalies detected"""
    POINT = "point"  # Single unusual value
    CONTEXTUAL = "contextual"  # Unusual in context (time/seasonality)
    TREND_REVERSAL = "trend_reversal"  # Direction change
    VOLATILITY_SPIKE = "volatility_spike"  # Sudden variance increase


class AnomalyScore(BaseModel):
    """Anomaly detection result"""

    metric_name: str = Field(description="Name of metric analyzed")

    anomaly_type: AnomalyType = Field(description="Type of anomaly")

    severity: float = Field(
        ge=0.0,
        le=10.0,
        description="Severity score (0-10, higher = more severe)"
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Detection confidence (0-1)"
    )

    explanation: str = Field(description="Human-readable explanation")

    statistical_details: Dict = Field(
        default_factory=dict,
        description="Statistical metrics (z-score, p-value, etc.)"
    )

    detected_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Detection timestamp"
    )

    forecast_value: Optional[float] = Field(
        default=None,
        description="Prophet forecast value"
    )

    actual_value: Optional[float] = Field(
        default=None,
        description="Actual observed value"
    )

    lower_bound: Optional[float] = Field(
        default=None,
        description="Lower confidence interval"
    )

    upper_bound: Optional[float] = Field(
        default=None,
        description="Upper confidence interval"
    )


class TrendAnalysis(BaseModel):
    """Trend analysis result"""

    metric_name: str
    trend_direction: str  # "increasing", "decreasing", "stable"
    trend_strength: float  # 0-1 scale
    reversal_detected: bool
    reversal_confidence: float = 0.0
    historical_trend: Optional[str] = None
    current_trend: Optional[str] = None


class AnomalyDetector:
    """
    Prophet-based anomaly detection for time series metrics.

    Detects statistical anomalies, trend reversals, and contextual outliers
    using Facebook Prophet's forecasting capabilities.
    """

    MIN_TRAINING_DAYS = 14  # Minimum historical data required
    DEFAULT_CONFIDENCE_INTERVAL = 0.80  # 80% confidence interval
    AGGRESSIVE_CONFIDENCE_INTERVAL = 0.95  # 95% for conservative detection

    def __init__(
        self,
        confidence_mode: str = "balanced",
        enable_seasonality: bool = True,
    ):
        """
        Initialize anomaly detector.

        Args:
            confidence_mode: "conservative" (95%), "balanced" (80%), "aggressive" (60%)
            enable_seasonality: Enable weekly/monthly seasonality detection
        """
        self.confidence_mode = confidence_mode
        self.enable_seasonality = enable_seasonality
        self.logger = logger

        # Set confidence interval based on mode
        self.interval_width = {
            "conservative": 0.95,
            "balanced": 0.80,
            "aggressive": 0.60,
        }.get(confidence_mode, 0.80)

        # Cache trained models per metric
        self._model_cache: Dict[str, any] = {}

    def fit_model(
        self,
        metric_name: str,
        historical_data: List[Tuple[datetime, float]],
    ) -> bool:
        """
        Train Prophet model on historical data.

        Args:
            metric_name: Name of metric to model
            historical_data: List of (timestamp, value) tuples

        Returns:
            True if model trained successfully, False otherwise
        """
        try:
            # Lazy import to avoid startup overhead
            from prophet import Prophet

            # Validate sufficient data
            if len(historical_data) < self.MIN_TRAINING_DAYS:
                self.logger.warning(
                    f"Insufficient data for {metric_name}: "
                    f"{len(historical_data)} points (min: {self.MIN_TRAINING_DAYS})"
                )
                return False

            # Prepare DataFrame for Prophet (requires 'ds' and 'y' columns)
            df = pd.DataFrame(historical_data, columns=["ds", "y"])

            # Remove any NaN or infinite values
            df = df.replace([np.inf, -np.inf], np.nan).dropna()

            if len(df) < self.MIN_TRAINING_DAYS:
                self.logger.warning(f"Too many invalid values in {metric_name}")
                return False

            # Initialize Prophet with appropriate settings
            model = Prophet(
                interval_width=self.interval_width,
                daily_seasonality=False,  # Not relevant for business metrics
                weekly_seasonality=self.enable_seasonality,
                yearly_seasonality=False,  # Need >1 year of data
                changepoint_prior_scale=0.05,  # Detect trend changes
            )

            # Add monthly seasonality if enabled
            if self.enable_seasonality and len(df) >= 60:  # 2 months minimum
                model.add_seasonality(
                    name='monthly',
                    period=30.5,
                    fourier_order=5
                )

            # Fit model
            model.fit(df, show_progress_bar=False)

            # Cache trained model
            self._model_cache[metric_name] = model

            self.logger.info(
                f"Trained Prophet model for {metric_name} "
                f"with {len(df)} data points"
            )

            return True

        except ImportError:
            self.logger.error("Prophet not installed. Run: pip install prophet")
            return False
        except Exception as e:
            self.logger.error(f"Error training model for {metric_name}: {e}")
            return False

    def detect_anomalies(
        self,
        metric_name: str,
        current_value: float,
        timestamp: Optional[datetime] = None,
    ) -> Optional[AnomalyScore]:
        """
        Detect anomalies using trained Prophet model.

        Args:
            metric_name: Name of metric to check
            current_value: Current observed value
            timestamp: Observation timestamp (default: now)

        Returns:
            AnomalyScore if anomaly detected, None otherwise
        """
        timestamp = timestamp or datetime.utcnow()

        # Check if model trained
        model = self._model_cache.get(metric_name)
        if not model:
            self.logger.warning(f"No trained model for {metric_name}")
            return None

        try:
            # Generate forecast for current timestamp
            future_df = pd.DataFrame({"ds": [timestamp]})
            forecast = model.predict(future_df)

            # Extract forecast and bounds
            yhat = forecast["yhat"].iloc[0]
            yhat_lower = forecast["yhat_lower"].iloc[0]
            yhat_upper = forecast["yhat_upper"].iloc[0]

            # Check if value outside confidence interval
            is_anomaly = current_value < yhat_lower or current_value > yhat_upper

            if not is_anomaly:
                return None  # Within normal range

            # Calculate severity (standard deviations from forecast)
            forecast_std = (yhat_upper - yhat_lower) / 4  # Approximate std
            z_score = abs((current_value - yhat) / forecast_std) if forecast_std > 0 else 0

            # Map z-score to 0-10 severity scale
            severity = min(10.0, z_score * 2.0)

            # Determine anomaly type
            if current_value > yhat_upper:
                direction = "above"
                deviation_pct = ((current_value - yhat) / yhat * 100) if yhat != 0 else 0
            else:
                direction = "below"
                deviation_pct = ((yhat - current_value) / yhat * 100) if yhat != 0 else 0

            # Generate explanation
            explanation = (
                f"{metric_name} is {abs(deviation_pct):.1f}% {direction} forecast "
                f"({current_value:.2f} vs {yhat:.2f}, {z_score:.1f}σ)"
            )

            # Determine confidence based on z-score
            confidence = min(1.0, z_score / 5.0)  # Higher z-score = higher confidence

            return AnomalyScore(
                metric_name=metric_name,
                anomaly_type=AnomalyType.POINT,
                severity=severity,
                confidence=confidence,
                explanation=explanation,
                statistical_details={
                    "z_score": z_score,
                    "deviation_pct": deviation_pct,
                    "forecast_std": forecast_std,
                    "direction": direction,
                },
                forecast_value=yhat,
                actual_value=current_value,
                lower_bound=yhat_lower,
                upper_bound=yhat_upper,
                detected_at=timestamp,
            )

        except Exception as e:
            self.logger.error(f"Error detecting anomalies for {metric_name}: {e}")
            return None

    def calculate_severity(
        self,
        z_score: float,
        context: Optional[Dict] = None,
    ) -> float:
        """
        Calculate anomaly severity score (0-10).

        Args:
            z_score: Standard deviations from expected
            context: Optional context (earnings day, holiday, etc.)

        Returns:
            Severity score 0-10
        """
        # Base severity from z-score
        base_severity = min(10.0, abs(z_score) * 2.0)

        # Adjust for context if provided
        if context:
            # Examples of contextual adjustments
            if context.get("earnings_day"):
                # Expected higher variance on earnings days
                base_severity *= 0.7

            if context.get("market_hours"):
                # More significant during market hours
                base_severity *= 1.2

            if context.get("holiday_period"):
                # Expected lower activity
                base_severity *= 0.8

        return min(10.0, max(0.0, base_severity))

    def trend_analysis(
        self,
        metric_name: str,
        recent_window_days: int = 7,
    ) -> Optional[TrendAnalysis]:
        """
        Analyze trend direction and detect reversals.

        Args:
            metric_name: Name of metric to analyze
            recent_window_days: Days to consider for current trend

        Returns:
            TrendAnalysis if model trained, None otherwise
        """
        model = self._model_cache.get(metric_name)
        if not model:
            return None

        try:
            # Generate forecast for past and future
            days_back = 30  # Look back 30 days
            days_forward = 7  # Forecast 7 days ahead

            dates = pd.date_range(
                start=datetime.utcnow() - timedelta(days=days_back),
                end=datetime.utcnow() + timedelta(days=days_forward),
                freq="D",
            )

            future_df = pd.DataFrame({"ds": dates})
            forecast = model.predict(future_df)

            # Extract trend component
            trend_values = forecast["trend"].values

            # Calculate historical trend (days_back to recent_window_days ago)
            historical_start_idx = 0
            historical_end_idx = days_back - recent_window_days
            historical_trend = np.mean(np.diff(trend_values[historical_start_idx:historical_end_idx]))

            # Calculate current trend (recent_window_days)
            current_start_idx = days_back - recent_window_days
            current_end_idx = days_back
            current_trend = np.mean(np.diff(trend_values[current_start_idx:current_end_idx]))

            # Determine trend directions
            def classify_trend(slope: float, threshold: float = 0.01) -> str:
                if abs(slope) < threshold:
                    return "stable"
                return "increasing" if slope > 0 else "decreasing"

            historical_direction = classify_trend(historical_trend)
            current_direction = classify_trend(current_trend)

            # Detect reversal
            reversal_detected = (
                historical_direction != current_direction
                and historical_direction != "stable"
                and current_direction != "stable"
            )

            # Calculate trend strength (0-1)
            max_slope = max(abs(historical_trend), abs(current_trend))
            trend_strength = min(1.0, abs(current_trend) / (max_slope + 0.001))

            # Calculate reversal confidence
            reversal_confidence = 0.0
            if reversal_detected:
                # Higher confidence if trends are opposite and strong
                reversal_confidence = min(1.0, trend_strength * 1.5)

            return TrendAnalysis(
                metric_name=metric_name,
                trend_direction=current_direction,
                trend_strength=trend_strength,
                reversal_detected=reversal_detected,
                reversal_confidence=reversal_confidence,
                historical_trend=historical_direction,
                current_trend=current_direction,
            )

        except Exception as e:
            self.logger.error(f"Error analyzing trend for {metric_name}: {e}")
            return None

    def get_forecast(
        self,
        metric_name: str,
        periods: int = 7,
    ) -> Optional[pd.DataFrame]:
        """
        Get Prophet forecast for future periods.

        Args:
            metric_name: Name of metric to forecast
            periods: Number of future periods to forecast

        Returns:
            DataFrame with forecast or None if model not trained
        """
        model = self._model_cache.get(metric_name)
        if not model:
            return None

        try:
            # Generate future dates
            future = model.make_future_dataframe(periods=periods, freq="D")

            # Generate forecast
            forecast = model.predict(future)

            # Return relevant columns
            return forecast[["ds", "yhat", "yhat_lower", "yhat_upper", "trend"]]

        except Exception as e:
            self.logger.error(f"Error generating forecast for {metric_name}: {e}")
            return None

    def detect_contextual_anomaly(
        self,
        metric_name: str,
        value: float,
        timestamp: datetime,
        context: Dict,
    ) -> Optional[AnomalyScore]:
        """
        Detect contextual anomalies (unusual given the context).

        Args:
            metric_name: Name of metric
            value: Observed value
            timestamp: Observation timestamp
            context: Context dict (e.g., {"event": "earnings_day"})

        Returns:
            AnomalyScore if contextual anomaly detected
        """
        # First check if it's a point anomaly
        anomaly = self.detect_anomalies(metric_name, value, timestamp)

        if not anomaly:
            return None

        # Adjust based on context
        if context.get("earnings_day"):
            # Expected higher variance on earnings days
            # Only flag if severity > 7 (very unusual even for earnings)
            if anomaly.severity < 7.0:
                return None

            anomaly.anomaly_type = AnomalyType.CONTEXTUAL
            anomaly.explanation += " (unusual even for earnings day)"

        elif context.get("market_closed"):
            # Activity during market close is more concerning
            anomaly.severity = min(10.0, anomaly.severity * 1.5)
            anomaly.anomaly_type = AnomalyType.CONTEXTUAL
            anomaly.explanation += " (during market close)"

        return anomaly

    def detect_volatility_spike(
        self,
        metric_name: str,
        recent_values: List[float],
        historical_values: List[float],
    ) -> Optional[AnomalyScore]:
        """
        Detect sudden increases in volatility.

        Args:
            metric_name: Name of metric
            recent_values: Recent values (e.g., last 7 days)
            historical_values: Historical values (e.g., previous 30 days)

        Returns:
            AnomalyScore if volatility spike detected
        """
        if len(recent_values) < 3 or len(historical_values) < 10:
            return None

        try:
            recent_std = np.std(recent_values)
            historical_std = np.std(historical_values)

            # Detect spike if recent volatility is significantly higher
            if recent_std > historical_std * 2.0:  # 2x threshold
                volatility_increase = (recent_std / historical_std - 1) * 100

                severity = min(10.0, volatility_increase / 10)
                confidence = min(1.0, volatility_increase / 200)

                return AnomalyScore(
                    metric_name=metric_name,
                    anomaly_type=AnomalyType.VOLATILITY_SPIKE,
                    severity=severity,
                    confidence=confidence,
                    explanation=(
                        f"{metric_name} volatility increased {volatility_increase:.0f}% "
                        f"(recent σ={recent_std:.2f} vs historical σ={historical_std:.2f})"
                    ),
                    statistical_details={
                        "recent_std": recent_std,
                        "historical_std": historical_std,
                        "volatility_increase_pct": volatility_increase,
                    },
                    detected_at=datetime.utcnow(),
                )

            return None

        except Exception as e:
            self.logger.error(f"Error detecting volatility spike for {metric_name}: {e}")
            return None

    def clear_cache(self, metric_name: Optional[str] = None) -> None:
        """
        Clear cached models.

        Args:
            metric_name: Specific metric to clear, or None for all
        """
        if metric_name:
            self._model_cache.pop(metric_name, None)
        else:
            self._model_cache.clear()
