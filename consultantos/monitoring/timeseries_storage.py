"""
Time series storage and analysis for monitoring metrics.

Extends intelligence monitoring with full time series capabilities:
- Time series storage for all key metrics (not just snapshots)
- Derivative calculation (growth rate, acceleration)
- Rolling window aggregations
- Trend detection
- Export for visualization
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum

from pydantic import BaseModel, Field
import numpy as np

logger = logging.getLogger(__name__)


class TrendDirection(str, Enum):
    """Trend direction classification"""
    UPWARD = "upward"
    DOWNWARD = "downward"
    STABLE = "stable"
    VOLATILE = "volatile"


class TimeSeriesMetric(BaseModel):
    """Single time series data point"""

    monitor_id: str
    metric_name: str
    timestamp: datetime
    value: float

    # Metadata
    data_source: str = Field(description="Source of metric")
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence in data point"
    )


class TimeSeriesDerivatives(BaseModel):
    """Calculated derivatives for time series"""

    monitor_id: str
    metric_name: str
    timestamp: datetime

    # First derivative (rate of change)
    growth_rate: Optional[float] = Field(
        default=None,
        description="Period-over-period growth rate"
    )

    # Second derivative (acceleration)
    acceleration: Optional[float] = Field(
        default=None,
        description="Change in growth rate"
    )

    # Rolling statistics
    rolling_7d_avg: Optional[float] = None
    rolling_30d_avg: Optional[float] = None
    rolling_60d_avg: Optional[float] = None
    rolling_90d_avg: Optional[float] = None

    # Volatility
    rolling_7d_std: Optional[float] = None
    rolling_30d_std: Optional[float] = None


class TrendAnalysis(BaseModel):
    """Trend analysis result"""

    monitor_id: str
    metric_name: str
    analysis_period_days: int

    # Trend classification
    direction: TrendDirection
    strength: float = Field(
        ge=0.0,
        le=1.0,
        description="Trend strength (0=weak, 1=strong)"
    )

    # Linear regression parameters
    slope: float = Field(description="Trend line slope")
    intercept: float
    r_squared: float = Field(description="Goodness of fit")

    # Inflection points
    inflection_points: List[datetime] = Field(
        default_factory=list,
        description="Points where trend direction changed"
    )

    # Forecast
    forecast_7d: Optional[float] = None
    forecast_30d: Optional[float] = None

    analyzed_at: datetime = Field(default_factory=datetime.utcnow)


class TimeSeriesExport(BaseModel):
    """Time series data export for visualization"""

    monitor_id: str
    metric_name: str

    # Time series data
    timestamps: List[datetime]
    values: List[float]

    # Derivatives
    growth_rates: Optional[List[Optional[float]]] = None
    accelerations: Optional[List[Optional[float]]] = None

    # Rolling averages
    ma_7d: Optional[List[Optional[float]]] = None
    ma_30d: Optional[List[Optional[float]]] = None

    # Trend line
    trend_values: Optional[List[float]] = None

    # Metadata
    period_start: datetime
    period_end: datetime
    data_points: int


class TimeSeriesStorage:
    """
    Time series storage and analysis service.

    Stores and analyzes time series data for monitoring metrics,
    calculating derivatives, trends, and providing data for visualization.
    """

    def __init__(self, db_service):
        """
        Initialize time series storage.

        Args:
            db_service: Database service for persistence
        """
        self.db = db_service
        self.logger = logger

    async def store_metric(
        self,
        metric: TimeSeriesMetric
    ) -> bool:
        """
        Store time series metric.

        Args:
            metric: Metric data point to store

        Returns:
            True if stored successfully
        """
        try:
            collection = self.db.db.collection("timeseries_metrics")

            # Document ID: monitor_id_metric_timestamp
            doc_id = (
                f"{metric.monitor_id}_{metric.metric_name}_"
                f"{int(metric.timestamp.timestamp())}"
            )

            doc_ref = collection.document(doc_id)
            await doc_ref.set(metric.dict())

            self.logger.debug(
                f"Stored metric: {metric.metric_name} for monitor {metric.monitor_id}"
            )

            return True

        except Exception as e:
            self.logger.error(f"Failed to store metric: {e}", exc_info=True)
            return False

    async def store_bulk_metrics(
        self,
        metrics: List[TimeSeriesMetric]
    ) -> int:
        """
        Store multiple metrics in batch.

        Args:
            metrics: List of metrics to store

        Returns:
            Number of metrics stored successfully
        """
        try:
            collection = self.db.db.collection("timeseries_metrics")

            # Use batched writes (max 500 per batch)
            batch = self.db.db.batch()
            stored_count = 0

            for i, metric in enumerate(metrics):
                doc_id = (
                    f"{metric.monitor_id}_{metric.metric_name}_"
                    f"{int(metric.timestamp.timestamp())}"
                )

                doc_ref = collection.document(doc_id)
                batch.set(doc_ref, metric.dict())
                stored_count += 1

                # Commit every 500 writes
                if (i + 1) % 500 == 0:
                    await batch.commit()
                    batch = self.db.db.batch()

            # Commit remaining
            if stored_count % 500 != 0:
                await batch.commit()

            self.logger.info(f"Bulk stored {stored_count} metrics")

            return stored_count

        except Exception as e:
            self.logger.error(f"Failed to bulk store metrics: {e}", exc_info=True)
            return 0

    async def get_time_series(
        self,
        monitor_id: str,
        metric_name: str,
        start_time: datetime,
        end_time: datetime,
        limit: Optional[int] = None
    ) -> List[TimeSeriesMetric]:
        """
        Retrieve time series data.

        Args:
            monitor_id: Monitor identifier
            metric_name: Metric name
            start_time: Start of time range
            end_time: End of time range
            limit: Optional limit on data points

        Returns:
            List of time series metrics ordered by timestamp
        """
        try:
            collection = self.db.db.collection("timeseries_metrics")

            query = collection.where("monitor_id", "==", monitor_id)
            query = query.where("metric_name", "==", metric_name)
            query = query.where("timestamp", ">=", start_time)
            query = query.where("timestamp", "<=", end_time)
            query = query.order_by("timestamp")

            if limit:
                query = query.limit(limit)

            docs = await query.stream()
            metrics = [TimeSeriesMetric(**doc.to_dict()) for doc in docs]

            return metrics

        except Exception as e:
            self.logger.error(f"Failed to get time series: {e}", exc_info=True)
            return []

    async def calculate_derivatives(
        self,
        monitor_id: str,
        metric_name: str,
        days_back: int = 90
    ) -> List[TimeSeriesDerivatives]:
        """
        Calculate derivatives for time series.

        Computes growth rates, acceleration, and rolling statistics.

        Args:
            monitor_id: Monitor identifier
            metric_name: Metric name
            days_back: Number of days to analyze

        Returns:
            List of derivative calculations
        """
        try:
            # Fetch time series data
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=days_back)

            metrics = await self.get_time_series(
                monitor_id, metric_name, start_time, end_time
            )

            if len(metrics) < 2:
                self.logger.warning("Insufficient data for derivative calculation")
                return []

            # Convert to numpy arrays for efficient computation
            timestamps = [m.timestamp for m in metrics]
            values = np.array([m.value for m in metrics])

            derivatives = []

            for i in range(len(metrics)):
                deriv = TimeSeriesDerivatives(
                    monitor_id=monitor_id,
                    metric_name=metric_name,
                    timestamp=metrics[i].timestamp
                )

                # First derivative (growth rate)
                if i > 0:
                    time_diff = (timestamps[i] - timestamps[i-1]).total_seconds() / 86400  # days
                    if time_diff > 0 and values[i-1] != 0:
                        deriv.growth_rate = (values[i] - values[i-1]) / values[i-1] / time_diff

                # Second derivative (acceleration)
                if i > 1:
                    prev_growth = (values[i-1] - values[i-2]) / values[i-2] if values[i-2] != 0 else 0
                    curr_growth = deriv.growth_rate or 0
                    time_diff = (timestamps[i] - timestamps[i-1]).total_seconds() / 86400
                    if time_diff > 0:
                        deriv.acceleration = (curr_growth - prev_growth) / time_diff

                # Rolling averages
                deriv.rolling_7d_avg = self._rolling_avg(values, i, window_size=7)
                deriv.rolling_30d_avg = self._rolling_avg(values, i, window_size=30)
                deriv.rolling_60d_avg = self._rolling_avg(values, i, window_size=60)
                deriv.rolling_90d_avg = self._rolling_avg(values, i, window_size=90)

                # Rolling standard deviation
                deriv.rolling_7d_std = self._rolling_std(values, i, window_size=7)
                deriv.rolling_30d_std = self._rolling_std(values, i, window_size=30)

                derivatives.append(deriv)

            # Store derivatives
            await self._store_derivatives(derivatives)

            return derivatives

        except Exception as e:
            self.logger.error(f"Failed to calculate derivatives: {e}", exc_info=True)
            return []

    async def detect_trend(
        self,
        monitor_id: str,
        metric_name: str,
        days_back: int = 30
    ) -> Optional[TrendAnalysis]:
        """
        Detect trend in time series using linear regression.

        Args:
            monitor_id: Monitor identifier
            metric_name: Metric name
            days_back: Number of days to analyze

        Returns:
            Trend analysis or None if insufficient data
        """
        try:
            # Fetch time series data
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=days_back)

            metrics = await self.get_time_series(
                monitor_id, metric_name, start_time, end_time
            )

            if len(metrics) < 3:
                return None

            # Prepare data for linear regression
            timestamps = np.array([
                (m.timestamp - metrics[0].timestamp).total_seconds()
                for m in metrics
            ])
            values = np.array([m.value for m in metrics])

            # Linear regression
            slope, intercept = np.polyfit(timestamps, values, 1)
            predicted = slope * timestamps + intercept
            r_squared = 1 - (np.sum((values - predicted) ** 2) / np.sum((values - np.mean(values)) ** 2))

            # Classify trend
            direction = self._classify_trend_direction(slope, r_squared)
            strength = min(abs(r_squared), 1.0)

            # Find inflection points (where derivative changes sign)
            inflection_points = self._find_inflection_points(metrics, values)

            # Forecast
            day_seconds = 86400
            forecast_7d = slope * (timestamps[-1] + 7 * day_seconds) + intercept
            forecast_30d = slope * (timestamps[-1] + 30 * day_seconds) + intercept

            trend = TrendAnalysis(
                monitor_id=monitor_id,
                metric_name=metric_name,
                analysis_period_days=days_back,
                direction=direction,
                strength=strength,
                slope=slope,
                intercept=intercept,
                r_squared=r_squared,
                inflection_points=inflection_points,
                forecast_7d=forecast_7d,
                forecast_30d=forecast_30d
            )

            return trend

        except Exception as e:
            self.logger.error(f"Failed to detect trend: {e}", exc_info=True)
            return None

    async def export_for_visualization(
        self,
        monitor_id: str,
        metric_name: str,
        days_back: int = 90
    ) -> Optional[TimeSeriesExport]:
        """
        Export time series data for visualization.

        Args:
            monitor_id: Monitor identifier
            metric_name: Metric name
            days_back: Number of days to export

        Returns:
            Exported time series data
        """
        try:
            # Fetch time series and derivatives
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=days_back)

            metrics = await self.get_time_series(
                monitor_id, metric_name, start_time, end_time
            )

            if not metrics:
                return None

            derivatives = await self.calculate_derivatives(
                monitor_id, metric_name, days_back
            )

            # Build export
            export = TimeSeriesExport(
                monitor_id=monitor_id,
                metric_name=metric_name,
                timestamps=[m.timestamp for m in metrics],
                values=[m.value for m in metrics],
                period_start=start_time,
                period_end=end_time,
                data_points=len(metrics)
            )

            # Add derivatives if available
            if derivatives:
                export.growth_rates = [d.growth_rate for d in derivatives]
                export.accelerations = [d.acceleration for d in derivatives]
                export.ma_7d = [d.rolling_7d_avg for d in derivatives]
                export.ma_30d = [d.rolling_30d_avg for d in derivatives]

            # Add trend line
            trend = await self.detect_trend(monitor_id, metric_name, days_back)
            if trend:
                timestamps_sec = np.array([
                    (t - metrics[0].timestamp).total_seconds()
                    for t in export.timestamps
                ])
                export.trend_values = (trend.slope * timestamps_sec + trend.intercept).tolist()

            return export

        except Exception as e:
            self.logger.error(f"Failed to export time series: {e}", exc_info=True)
            return None

    # Private helper methods

    def _rolling_avg(
        self,
        values: np.ndarray,
        index: int,
        window_size: int
    ) -> Optional[float]:
        """Calculate rolling average"""
        start_idx = max(0, index - window_size + 1)
        if index - start_idx < 2:  # Need at least 2 points
            return None
        return float(np.mean(values[start_idx:index+1]))

    def _rolling_std(
        self,
        values: np.ndarray,
        index: int,
        window_size: int
    ) -> Optional[float]:
        """Calculate rolling standard deviation"""
        start_idx = max(0, index - window_size + 1)
        if index - start_idx < 2:
            return None
        return float(np.std(values[start_idx:index+1]))

    def _classify_trend_direction(
        self,
        slope: float,
        r_squared: float
    ) -> TrendDirection:
        """Classify trend direction based on slope and fit"""
        if r_squared < 0.3:
            return TrendDirection.VOLATILE

        # Normalize slope to value range for better classification
        # A slope of 50 over 2.6M seconds (30 days) is significant
        normalized_slope = slope * 86400  # Per day slope

        if abs(normalized_slope) < 0.5:  # Threshold for "stable"
            return TrendDirection.STABLE
        elif slope > 0:
            return TrendDirection.UPWARD
        else:
            return TrendDirection.DOWNWARD

    def _find_inflection_points(
        self,
        metrics: List[TimeSeriesMetric],
        values: np.ndarray
    ) -> List[datetime]:
        """Find inflection points where trend direction changes"""
        inflection_points = []

        # Calculate first derivative
        derivatives = np.diff(values)

        # Find sign changes
        for i in range(1, len(derivatives)):
            if np.sign(derivatives[i]) != np.sign(derivatives[i-1]):
                inflection_points.append(metrics[i].timestamp)

        return inflection_points

    async def _store_derivatives(
        self,
        derivatives: List[TimeSeriesDerivatives]
    ) -> bool:
        """Store calculated derivatives"""
        try:
            collection = self.db.db.collection("timeseries_derivatives")

            batch = self.db.db.batch()
            for i, deriv in enumerate(derivatives):
                doc_id = (
                    f"{deriv.monitor_id}_{deriv.metric_name}_"
                    f"{int(deriv.timestamp.timestamp())}"
                )

                doc_ref = collection.document(doc_id)
                batch.set(doc_ref, deriv.dict())

                if (i + 1) % 500 == 0:
                    await batch.commit()
                    batch = self.db.db.batch()

            if len(derivatives) % 500 != 0:
                await batch.commit()

            return True

        except Exception as e:
            self.logger.error(f"Failed to store derivatives: {e}")
            return False
