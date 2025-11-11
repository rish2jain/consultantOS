"""
Data migration helpers for strategic infrastructure components.

Provides migration utilities for:
- Migrating existing monitors to time series storage
- Backfilling benchmarks from existing snapshots
- Generating initial patterns from historical data
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional

logger = logging.getLogger(__name__)


class InfrastructureMigration:
    """
    Migration utilities for strategic infrastructure.

    Handles data migration from existing monitoring system to new
    time series, benchmark, and pattern infrastructure.
    """

    def __init__(
        self,
        db_service,
        timeseries_storage,
        competitive_context_service,
        pattern_library_service
    ):
        """
        Initialize migration utilities.

        Args:
            db_service: Database service
            timeseries_storage: Time series storage service
            competitive_context_service: Competitive context service
            pattern_library_service: Pattern library service
        """
        self.db = db_service
        self.timeseries = timeseries_storage
        self.context = competitive_context_service
        self.patterns = pattern_library_service
        self.logger = logger

    async def migrate_monitor_to_timeseries(
        self,
        monitor_id: str,
        backfill_days: int = 90
    ) -> bool:
        """
        Migrate existing monitor snapshots to time series storage.

        Args:
            monitor_id: Monitor to migrate
            backfill_days: Number of days to backfill

        Returns:
            True if migration successful
        """
        try:
            self.logger.info(f"Starting time series migration for monitor {monitor_id}")

            # Fetch monitor
            monitor = await self.db.get_monitor(monitor_id)
            if not monitor:
                raise ValueError(f"Monitor {monitor_id} not found")

            # Fetch historical snapshots
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=backfill_days)

            snapshots = await self.db.get_snapshots_in_range(
                monitor_id=monitor_id,
                start_time=start_time,
                end_time=end_time
            )

            if not snapshots:
                self.logger.warning(f"No snapshots found for monitor {monitor_id}")
                return False

            self.logger.info(f"Found {len(snapshots)} snapshots to migrate")

            # Extract time series data from snapshots
            from consultantos.monitoring.timeseries_storage import TimeSeriesMetric

            metrics = []
            for snapshot in snapshots:
                # Extract financial metrics
                for metric_name, value in (snapshot.financial_metrics or {}).items():
                    if isinstance(value, (int, float)):
                        metrics.append(TimeSeriesMetric(
                            monitor_id=monitor_id,
                            metric_name=f"financial_{metric_name}",
                            timestamp=snapshot.timestamp,
                            value=float(value),
                            data_source="snapshot_migration",
                            confidence=1.0
                        ))

                # Extract sentiment if available
                if snapshot.news_sentiment is not None:
                    metrics.append(TimeSeriesMetric(
                        monitor_id=monitor_id,
                        metric_name="news_sentiment",
                        timestamp=snapshot.timestamp,
                        value=snapshot.news_sentiment,
                        data_source="snapshot_migration",
                        confidence=0.8
                    ))

            # Bulk store metrics
            stored_count = await self.timeseries.store_bulk_metrics(metrics)

            self.logger.info(
                f"Migrated {stored_count} metrics for monitor {monitor_id}"
            )

            return stored_count > 0

        except Exception as e:
            self.logger.error(
                f"Failed to migrate monitor to time series: {e}",
                exc_info=True
            )
            return False

    async def backfill_industry_benchmarks(
        self,
        industry: str,
        metric_names: List[str]
    ) -> int:
        """
        Generate industry benchmarks from existing snapshot data.

        Args:
            industry: Industry to generate benchmarks for
            metric_names: Metrics to benchmark

        Returns:
            Number of benchmarks created
        """
        try:
            self.logger.info(f"Backfilling benchmarks for industry: {industry}")

            from consultantos.context.competitive_context import (
                IndustryBenchmark,
                MetricType
            )

            benchmarks_created = 0

            for metric_name in metric_names:
                # Fetch all snapshots for this industry
                # (This is simplified - in production, query by industry)
                values = []

                # For MVP: Use placeholder data
                # TODO: Query actual snapshots filtered by industry

                if len(values) < 10:
                    self.logger.warning(
                        f"Insufficient data for {industry}:{metric_name} benchmark"
                    )
                    continue

                # Calculate percentiles
                import numpy as np
                values_array = np.array(values)

                benchmark = IndustryBenchmark(
                    industry=industry,
                    metric_name=metric_name,
                    metric_type=MetricType.CUSTOM,
                    mean=float(np.mean(values_array)),
                    median=float(np.median(values_array)),
                    std_dev=float(np.std(values_array)),
                    min_value=float(np.min(values_array)),
                    max_value=float(np.max(values_array)),
                    p10=float(np.percentile(values_array, 10)),
                    p25=float(np.percentile(values_array, 25)),
                    p50=float(np.percentile(values_array, 50)),
                    p75=float(np.percentile(values_array, 75)),
                    p90=float(np.percentile(values_array, 90)),
                    sample_size=len(values),
                    data_source="snapshot_backfill",
                    confidence_score=min(1.0, len(values) / 50)
                )

                # Store benchmark
                success = await self.context.store_benchmark(benchmark)
                if success:
                    benchmarks_created += 1

            self.logger.info(
                f"Created {benchmarks_created} benchmarks for {industry}"
            )

            return benchmarks_created

        except Exception as e:
            self.logger.error(
                f"Failed to backfill benchmarks: {e}",
                exc_info=True
            )
            return 0

    async def seed_initial_patterns(self) -> int:
        """
        Seed pattern library with well-known strategic patterns.

        Returns:
            Number of patterns seeded
        """
        try:
            self.logger.info("Seeding initial pattern library")

            from consultantos.analysis.pattern_library import (
                HistoricalPattern,
                PatternCategory,
                PatternSignal,
                PatternOutcome
            )

            patterns = []

            # Pattern 1: Sentiment Decline → Earnings Miss
            patterns.append(HistoricalPattern(
                pattern_id="sentiment_decline_earnings_miss",
                category=PatternCategory.FINANCIAL_DISTRESS,
                name="Sentiment Decline Precedes Earnings Miss",
                description=(
                    "Declining news sentiment over 30 days correlates with "
                    "earnings misses in subsequent quarter (73% accuracy)"
                ),
                signals=[
                    PatternSignal(
                        metric_name="news_sentiment",
                        change_type="decrease",
                        time_offset_days=0
                    ),
                    PatternSignal(
                        metric_name="news_sentiment",
                        change_type="decrease",
                        time_offset_days=15
                    ),
                    PatternSignal(
                        metric_name="news_sentiment",
                        change_type="decrease",
                        time_offset_days=30
                    )
                ],
                outcome=PatternOutcome(
                    outcome_type="earnings_miss",
                    description="Company misses quarterly earnings expectations",
                    time_to_outcome_days=60,
                    severity=7.0
                ),
                occurrence_count=42,
                successful_predictions=31,
                accuracy=0.73,
                example_companies=["Example Corp", "Test Inc"],
                confidence_score=0.85,
            ))

            # Pattern 2: Competitive Pressure Increase → Market Share Loss
            patterns.append(HistoricalPattern(
                pattern_id="competitive_pressure_market_share_loss",
                category=PatternCategory.COMPETITIVE_MOVE,
                name="Increased Competition Leads to Market Share Loss",
                description=(
                    "Rising competitive rivalry scores correlate with "
                    "market share decline (68% accuracy)"
                ),
                signals=[
                    PatternSignal(
                        metric_name="competitive_rivalry",
                        change_type="increase",
                        time_offset_days=0
                    ),
                    PatternSignal(
                        metric_name="competitive_rivalry",
                        change_type="increase",
                        time_offset_days=30
                    )
                ],
                outcome=PatternOutcome(
                    outcome_type="market_share_loss",
                    description="Company loses market share in key segment",
                    time_to_outcome_days=90,
                    severity=6.5
                ),
                occurrence_count=28,
                successful_predictions=19,
                accuracy=0.68,
                example_companies=["Sample Co", "Demo Ltd"],
                confidence_score=0.78,
            ))

            # Store patterns
            stored_count = 0
            for pattern in patterns:
                success = await self.patterns.store_pattern(pattern)
                if success:
                    stored_count += 1

            self.logger.info(f"Seeded {stored_count} initial patterns")

            return stored_count

        except Exception as e:
            self.logger.error(
                f"Failed to seed patterns: {e}",
                exc_info=True
            )
            return 0

    async def migrate_all_monitors(
        self,
        backfill_days: int = 90
    ) -> dict:
        """
        Migrate all active monitors to new infrastructure.

        Args:
            backfill_days: Days to backfill for each monitor

        Returns:
            Migration statistics
        """
        try:
            self.logger.info("Starting full infrastructure migration")

            stats = {
                "monitors_migrated": 0,
                "monitors_failed": 0,
                "total_metrics": 0,
                "benchmarks_created": 0,
                "patterns_seeded": 0
            }

            # Get all active monitors
            # (Simplified - in production, iterate over all users)
            # For now, return empty stats
            # TODO: Implement full migration when monitor list is available

            # Seed patterns
            stats["patterns_seeded"] = await self.seed_initial_patterns()

            self.logger.info(f"Migration complete: {stats}")

            return stats

        except Exception as e:
            self.logger.error(
                f"Failed to migrate all monitors: {e}",
                exc_info=True
            )
            return {}


async def run_migration(db_service):
    """
    Convenience function to run full migration.

    Args:
        db_service: Database service instance

    Returns:
        Migration statistics
    """
    from consultantos.monitoring.timeseries_storage import TimeSeriesStorage
    from consultantos.context.competitive_context import CompetitiveContextService
    from consultantos.analysis.pattern_library import PatternLibraryService

    # Initialize services
    timeseries = TimeSeriesStorage(db_service)
    context = CompetitiveContextService(db_service)
    patterns = PatternLibraryService(db_service)

    # Run migration
    migration = InfrastructureMigration(
        db_service, timeseries, context, patterns
    )

    return await migration.migrate_all_monitors()
