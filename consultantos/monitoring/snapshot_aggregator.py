"""
Snapshot aggregation service for time-series analytics.

Generates daily/weekly/monthly summaries from raw snapshots to optimize
dashboard queries and reduce database load.
"""

import asyncio
import logging
from collections import defaultdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class AggregationPeriod(str, Enum):
    """Aggregation time periods"""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class SnapshotAggregation(BaseModel):
    """Aggregated snapshot summary for a time period"""

    monitor_id: str
    period: AggregationPeriod
    start_time: datetime
    end_time: datetime
    snapshot_count: int

    # Statistical summaries
    metrics_summary: Dict[str, Dict[str, float]] = Field(
        default_factory=dict,
        description="Per-metric statistics: {metric_name: {min, max, avg, stddev}}",
    )

    # Trend indicators
    trends: Dict[str, str] = Field(
        default_factory=dict,
        description="Trend direction per metric: up, down, stable",
    )

    # Moving averages
    moving_averages: Dict[str, float] = Field(
        default_factory=dict,
        description="7-day and 30-day moving averages",
    )

    # Change detection
    significant_changes: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of significant changes detected in period",
    )

    # Common values
    most_common_market_trends: List[str] = Field(
        default_factory=list, description="Most frequent market trends"
    )

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TimeSeriesProtocol(Protocol):
    """Protocol for time-series optimizer interface"""

    async def get_snapshots_in_range(
        self,
        monitor_id: str,
        start_time: datetime,
        end_time: datetime,
        limit: Optional[int] = None,
        page_size: int = 100,
    ) -> List[Any]:
        """Get snapshots in time range"""
        ...


class SnapshotAggregator:
    """
    Generate aggregated summaries from raw monitoring snapshots.

    Reduces query load by pre-computing common analytics:
    - Daily/weekly/monthly rollups
    - Moving averages (7-day, 30-day)
    - Trend calculations
    - Statistical summaries (min, max, avg, stddev)
    """

    def __init__(
        self,
        timeseries_optimizer: TimeSeriesProtocol,
        db_service: Any,
    ):
        """
        Initialize snapshot aggregator.

        Args:
            timeseries_optimizer: Time-series optimizer for snapshot retrieval
            db_service: Database service for storing aggregations
        """
        self.timeseries = timeseries_optimizer
        self.db = db_service

    async def generate_daily_aggregation(
        self, monitor_id: str, target_date: datetime
    ) -> Optional[SnapshotAggregation]:
        """
        Generate daily aggregation for a specific date.

        Args:
            monitor_id: Monitor identifier
            target_date: Date to aggregate

        Returns:
            Daily aggregation or None if no snapshots
        """
        # Define day boundaries
        start_time = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(days=1)

        return await self._generate_aggregation(
            monitor_id=monitor_id,
            period=AggregationPeriod.DAILY,
            start_time=start_time,
            end_time=end_time,
        )

    async def generate_weekly_aggregation(
        self, monitor_id: str, target_date: datetime
    ) -> Optional[SnapshotAggregation]:
        """
        Generate weekly aggregation for week containing target date.

        Args:
            monitor_id: Monitor identifier
            target_date: Date within target week

        Returns:
            Weekly aggregation or None if no snapshots
        """
        # Find week start (Monday)
        days_since_monday = target_date.weekday()
        start_time = (target_date - timedelta(days=days_since_monday)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        end_time = start_time + timedelta(days=7)

        return await self._generate_aggregation(
            monitor_id=monitor_id,
            period=AggregationPeriod.WEEKLY,
            start_time=start_time,
            end_time=end_time,
        )

    async def generate_monthly_aggregation(
        self, monitor_id: str, year: int, month: int
    ) -> Optional[SnapshotAggregation]:
        """
        Generate monthly aggregation.

        Args:
            monitor_id: Monitor identifier
            year: Target year
            month: Target month (1-12)

        Returns:
            Monthly aggregation or None if no snapshots
        """
        start_time = datetime(year, month, 1)

        # Calculate last day of month
        if month == 12:
            end_time = datetime(year + 1, 1, 1)
        else:
            end_time = datetime(year, month + 1, 1)

        return await self._generate_aggregation(
            monitor_id=monitor_id,
            period=AggregationPeriod.MONTHLY,
            start_time=start_time,
            end_time=end_time,
        )

    async def backfill_aggregations(
        self,
        monitor_id: str,
        start_date: datetime,
        end_date: datetime,
        periods: List[AggregationPeriod],
    ) -> Dict[str, int]:
        """
        Backfill aggregations for historical data.

        Args:
            monitor_id: Monitor identifier
            start_date: Start of backfill period
            end_date: End of backfill period
            periods: Aggregation periods to generate

        Returns:
            Count of aggregations created per period
        """
        results = {period.value: 0 for period in periods}

        try:
            # Generate daily aggregations
            if AggregationPeriod.DAILY in periods:
                current_date = start_date
                while current_date < end_date:
                    agg = await self.generate_daily_aggregation(monitor_id, current_date)
                    if agg:
                        await self.db.create_aggregation(agg)
                        results[AggregationPeriod.DAILY.value] += 1

                    current_date += timedelta(days=1)

            # Generate weekly aggregations
            if AggregationPeriod.WEEKLY in periods:
                current_date = start_date
                while current_date < end_date:
                    agg = await self.generate_weekly_aggregation(monitor_id, current_date)
                    if agg:
                        await self.db.create_aggregation(agg)
                        results[AggregationPeriod.WEEKLY.value] += 1

                    current_date += timedelta(weeks=1)

            # Generate monthly aggregations
            if AggregationPeriod.MONTHLY in periods:
                current_date = start_date
                while current_date < end_date:
                    agg = await self.generate_monthly_aggregation(
                        monitor_id, current_date.year, current_date.month
                    )
                    if agg:
                        await self.db.create_aggregation(agg)
                        results[AggregationPeriod.MONTHLY.value] += 1

                    # Move to next month
                    if current_date.month == 12:
                        current_date = datetime(current_date.year + 1, 1, 1)
                    else:
                        current_date = datetime(
                            current_date.year, current_date.month + 1, 1
                        )

            logger.info(f"Backfill completed for monitor {monitor_id}: {results}")
            return results

        except Exception as e:
            logger.error(f"Backfill failed for monitor {monitor_id}: {e}", exc_info=True)
            return results

    async def get_aggregation(
        self,
        monitor_id: str,
        period: AggregationPeriod,
        start_time: datetime,
    ) -> Optional[SnapshotAggregation]:
        """
        Retrieve existing aggregation or generate if missing.

        Args:
            monitor_id: Monitor identifier
            period: Aggregation period
            start_time: Period start time

        Returns:
            Aggregation or None
        """
        # Try to retrieve from database
        existing = await self.db.get_aggregation(monitor_id, period, start_time)
        if existing:
            return existing

        # Generate on-demand
        if period == AggregationPeriod.DAILY:
            end_time = start_time + timedelta(days=1)
        elif period == AggregationPeriod.WEEKLY:
            end_time = start_time + timedelta(weeks=1)
        elif period == AggregationPeriod.MONTHLY:
            # Calculate month end
            if start_time.month == 12:
                end_time = datetime(start_time.year + 1, 1, 1)
            else:
                end_time = datetime(start_time.year, start_time.month + 1, 1)

        agg = await self._generate_aggregation(
            monitor_id=monitor_id,
            period=period,
            start_time=start_time,
            end_time=end_time,
        )

        # Store for future use
        if agg:
            await self.db.create_aggregation(agg)

        return agg

    # Private helper methods

    async def _generate_aggregation(
        self,
        monitor_id: str,
        period: AggregationPeriod,
        start_time: datetime,
        end_time: datetime,
    ) -> Optional[SnapshotAggregation]:
        """Generate aggregation for time period."""
        try:
            # Fetch all snapshots in period
            snapshots = await self.timeseries.get_snapshots_in_range(
                monitor_id=monitor_id,
                start_time=start_time,
                end_time=end_time,
            )

            if not snapshots:
                logger.debug(
                    f"No snapshots found for {monitor_id} in period "
                    f"{start_time} to {end_time}"
                )
                return None

            # Extract all metrics from snapshots
            all_metrics = defaultdict(list)
            market_trends = []

            for snapshot in snapshots:
                # Financial metrics
                if snapshot.financial_metrics:
                    for key, value in snapshot.financial_metrics.items():
                        if isinstance(value, (int, float)):
                            all_metrics[key].append(value)

                # News sentiment
                if snapshot.news_sentiment is not None:
                    all_metrics["news_sentiment"].append(snapshot.news_sentiment)

                # Market trends
                if snapshot.market_trends:
                    market_trends.extend(snapshot.market_trends)

            # Compute statistical summaries
            metrics_summary = {}
            for metric_name, values in all_metrics.items():
                if values:
                    metrics_summary[metric_name] = self._compute_stats(values)

            # Compute trends
            trends = {}
            for metric_name, values in all_metrics.items():
                if len(values) >= 2:
                    trends[metric_name] = self._compute_trend(values)

            # Compute moving averages (if enough data)
            moving_averages = {}
            for metric_name, values in all_metrics.items():
                if values:
                    moving_averages[f"{metric_name}_ma"] = sum(values) / len(values)

            # Detect significant changes
            significant_changes = self._detect_significant_changes(all_metrics)

            # Find most common market trends
            most_common_trends = self._get_most_common(market_trends, top_n=5)

            # Create aggregation
            aggregation = SnapshotAggregation(
                monitor_id=monitor_id,
                period=period,
                start_time=start_time,
                end_time=end_time,
                snapshot_count=len(snapshots),
                metrics_summary=metrics_summary,
                trends=trends,
                moving_averages=moving_averages,
                significant_changes=significant_changes,
                most_common_market_trends=most_common_trends,
            )

            logger.info(
                f"Generated {period.value} aggregation for {monitor_id}: "
                f"{len(snapshots)} snapshots, {len(metrics_summary)} metrics"
            )

            return aggregation

        except Exception as e:
            logger.error(
                f"Failed to generate aggregation for {monitor_id}: {e}", exc_info=True
            )
            return None

    def _compute_stats(self, values: List[float]) -> Dict[str, float]:
        """Compute statistical summary for metric values."""
        if not values:
            return {}

        import statistics

        stats = {
            "min": min(values),
            "max": max(values),
            "avg": statistics.mean(values),
            "count": len(values),
        }

        # Standard deviation (if enough data points)
        if len(values) >= 2:
            stats["stddev"] = statistics.stdev(values)
        else:
            stats["stddev"] = 0.0

        return stats

    def _compute_trend(self, values: List[float]) -> str:
        """
        Compute trend direction from time-series values.

        Returns: "up", "down", or "stable"
        """
        if len(values) < 2:
            return "stable"

        # Simple linear regression slope
        n = len(values)
        x_values = list(range(n))

        # Calculate slope
        x_mean = sum(x_values) / n
        y_mean = sum(values) / n

        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, values))
        denominator = sum((x - x_mean) ** 2 for x in x_values)

        if denominator == 0:
            return "stable"

        slope = numerator / denominator

        # Determine trend based on slope magnitude
        # Threshold: 5% of mean value
        threshold = abs(y_mean * 0.05) if y_mean != 0 else 0.01

        if slope > threshold:
            return "up"
        elif slope < -threshold:
            return "down"
        else:
            return "stable"

    def _detect_significant_changes(
        self, all_metrics: Dict[str, List[float]]
    ) -> List[Dict[str, Any]]:
        """Detect significant changes within period."""
        changes = []

        for metric_name, values in all_metrics.items():
            if len(values) < 2:
                continue

            # Check for large jumps
            for i in range(1, len(values)):
                prev = values[i - 1]
                curr = values[i]

                if prev == 0:
                    continue

                pct_change = abs((curr - prev) / prev)

                # Threshold: 20% change
                if pct_change > 0.2:
                    changes.append(
                        {
                            "metric": metric_name,
                            "change_pct": round(pct_change * 100, 1),
                            "previous": prev,
                            "current": curr,
                            "index": i,
                        }
                    )

        return changes[:10]  # Limit to top 10 changes

    def _get_most_common(self, items: List[str], top_n: int = 5) -> List[str]:
        """Get most common items from list."""
        from collections import Counter

        if not items:
            return []

        counts = Counter(items)
        return [item for item, _ in counts.most_common(top_n)]
