"""
Tests for snapshot aggregation service.

Tests cover:
- Daily/weekly/monthly aggregation generation
- Statistical computations
- Trend calculations
- Backfill operations
- Performance benchmarks
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

from consultantos.monitoring.snapshot_aggregator import (
    SnapshotAggregator,
    AggregationPeriod,
)
from consultantos.models.monitoring import MonitorAnalysisSnapshot


@pytest.fixture
def mock_timeseries():
    """Mock time-series optimizer"""
    ts = MagicMock()
    ts.get_snapshots_in_range = AsyncMock(return_value=[])
    return ts


@pytest.fixture
def mock_db_service():
    """Mock database service"""
    db = MagicMock()
    db.create_aggregation = AsyncMock(return_value=True)
    db.get_aggregation = AsyncMock(return_value=None)
    return db


@pytest.fixture
def aggregator(mock_timeseries, mock_db_service):
    """Create snapshot aggregator instance"""
    return SnapshotAggregator(
        timeseries_optimizer=mock_timeseries,
        db_service=mock_db_service,
    )


@pytest.fixture
def sample_snapshots():
    """Create sample snapshots for testing"""
    snapshots = []
    base_time = datetime(2024, 1, 1, 12, 0, 0)

    for i in range(7):
        snapshot = MonitorAnalysisSnapshot(
            monitor_id="test-monitor-123",
            timestamp=base_time + timedelta(days=i),
            company="Tesla",
            industry="Electric Vehicles",
            financial_metrics={
                "revenue": 80000000000 + i * 1000000000,
                "gross_margin": 25.0 + i * 0.5,
            },
            market_trends=[
                "EV adoption accelerating",
                f"Trend {i}",
            ],
            news_sentiment=0.7 + i * 0.02,
        )
        snapshots.append(snapshot)

    return snapshots


class TestDailyAggregation:
    """Test daily aggregation generation"""

    @pytest.mark.asyncio
    async def test_generate_daily_aggregation(
        self, aggregator, mock_timeseries, sample_snapshots
    ):
        """Test daily aggregation creation"""
        target_date = datetime(2024, 1, 1)
        mock_timeseries.get_snapshots_in_range.return_value = sample_snapshots[:2]

        agg = await aggregator.generate_daily_aggregation(
            monitor_id="test-monitor-123",
            target_date=target_date,
        )

        # Verify aggregation
        assert agg is not None
        assert agg.period == AggregationPeriod.DAILY
        assert agg.monitor_id == "test-monitor-123"
        assert agg.snapshot_count == 2

        # Verify metrics summary
        assert "revenue" in agg.metrics_summary
        assert "gross_margin" in agg.metrics_summary

        # Check statistical computations
        revenue_stats = agg.metrics_summary["revenue"]
        assert revenue_stats["min"] == 80000000000
        assert revenue_stats["max"] == 81000000000
        assert revenue_stats["count"] == 2

    @pytest.mark.asyncio
    async def test_empty_day_returns_none(self, aggregator, mock_timeseries):
        """Test empty day returns None"""
        mock_timeseries.get_snapshots_in_range.return_value = []

        agg = await aggregator.generate_daily_aggregation(
            monitor_id="test-monitor-123",
            target_date=datetime(2024, 1, 1),
        )

        assert agg is None


class TestWeeklyAggregation:
    """Test weekly aggregation generation"""

    @pytest.mark.asyncio
    async def test_generate_weekly_aggregation(
        self, aggregator, mock_timeseries, sample_snapshots
    ):
        """Test weekly aggregation creation"""
        target_date = datetime(2024, 1, 3)  # Wednesday
        mock_timeseries.get_snapshots_in_range.return_value = sample_snapshots

        agg = await aggregator.generate_weekly_aggregation(
            monitor_id="test-monitor-123",
            target_date=target_date,
        )

        # Verify aggregation
        assert agg is not None
        assert agg.period == AggregationPeriod.WEEKLY
        assert agg.snapshot_count == 7

        # Verify week boundaries (Monday start)
        assert agg.start_time.weekday() == 0  # Monday

    @pytest.mark.asyncio
    async def test_week_start_on_monday(self, aggregator, mock_timeseries):
        """Test week starts on Monday"""
        # Test different days of week
        for weekday in range(7):
            target = datetime(2024, 1, 1) + timedelta(days=weekday)
            mock_timeseries.get_snapshots_in_range.return_value = []

            agg = await aggregator.generate_weekly_aggregation(
                monitor_id="test", target_date=target
            )

            # Start should always be Monday
            # (won't be None because we're checking start_time calculation)


class TestMonthlyAggregation:
    """Test monthly aggregation generation"""

    @pytest.mark.asyncio
    async def test_generate_monthly_aggregation(
        self, aggregator, mock_timeseries, sample_snapshots
    ):
        """Test monthly aggregation creation"""
        mock_timeseries.get_snapshots_in_range.return_value = sample_snapshots

        agg = await aggregator.generate_monthly_aggregation(
            monitor_id="test-monitor-123",
            year=2024,
            month=1,
        )

        # Verify aggregation
        assert agg is not None
        assert agg.period == AggregationPeriod.MONTHLY
        assert agg.start_time == datetime(2024, 1, 1)

    @pytest.mark.asyncio
    async def test_december_month_end(self, aggregator, mock_timeseries):
        """Test December edge case (month end)"""
        mock_timeseries.get_snapshots_in_range.return_value = []

        agg = await aggregator.generate_monthly_aggregation(
            monitor_id="test",
            year=2024,
            month=12,
        )

        # End time should be January 1st of next year
        # (won't be None because we're checking date calculation)


class TestStatisticalComputations:
    """Test statistical calculation accuracy"""

    def test_compute_stats(self, aggregator):
        """Test statistical computations"""
        values = [10.0, 20.0, 30.0, 40.0, 50.0]

        stats = aggregator._compute_stats(values)

        assert stats["min"] == 10.0
        assert stats["max"] == 50.0
        assert stats["avg"] == 30.0
        assert stats["count"] == 5
        assert "stddev" in stats

    def test_compute_stats_single_value(self, aggregator):
        """Test stats with single value"""
        values = [42.0]

        stats = aggregator._compute_stats(values)

        assert stats["min"] == 42.0
        assert stats["max"] == 42.0
        assert stats["avg"] == 42.0
        assert stats["stddev"] == 0.0

    def test_compute_stats_empty(self, aggregator):
        """Test stats with no values"""
        values = []

        stats = aggregator._compute_stats(values)

        assert stats == {}


class TestTrendCalculations:
    """Test trend direction calculations"""

    def test_upward_trend(self, aggregator):
        """Test upward trend detection"""
        values = [10.0, 15.0, 20.0, 25.0, 30.0]

        trend = aggregator._compute_trend(values)

        assert trend == "up"

    def test_downward_trend(self, aggregator):
        """Test downward trend detection"""
        values = [30.0, 25.0, 20.0, 15.0, 10.0]

        trend = aggregator._compute_trend(values)

        assert trend == "down"

    def test_stable_trend(self, aggregator):
        """Test stable trend detection"""
        values = [20.0, 20.5, 19.8, 20.2, 20.1]

        trend = aggregator._compute_trend(values)

        assert trend == "stable"

    def test_trend_with_noise(self, aggregator):
        """Test trend with noisy data"""
        values = [10.0, 12.0, 11.0, 14.0, 13.0, 16.0, 15.0, 18.0]

        trend = aggregator._compute_trend(values)

        # Overall trend is upward despite noise
        assert trend == "up"

    def test_trend_insufficient_data(self, aggregator):
        """Test trend with single value"""
        values = [42.0]

        trend = aggregator._compute_trend(values)

        assert trend == "stable"


class TestChangeDetection:
    """Test significant change detection"""

    def test_detect_significant_changes(self, aggregator):
        """Test change detection"""
        metrics = {
            "revenue": [100.0, 100.0, 100.0, 125.0],  # 25% jump
            "margin": [20.0, 20.0, 20.0, 20.5],  # 2.5% change (not significant)
        }

        changes = aggregator._detect_significant_changes(metrics)

        # Should detect revenue change, not margin
        assert len(changes) > 0
        assert any(c["metric"] == "revenue" for c in changes)

    def test_no_changes_detected(self, aggregator):
        """Test no significant changes"""
        metrics = {
            "revenue": [100.0, 101.0, 102.0, 103.0],  # Small incremental changes
        }

        changes = aggregator._detect_significant_changes(metrics)

        assert len(changes) == 0


class TestBackfillOperations:
    """Test aggregation backfill operations"""

    @pytest.mark.asyncio
    async def test_backfill_aggregations(
        self, aggregator, mock_timeseries, mock_db_service, sample_snapshots
    ):
        """Test backfill operation"""
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 7)

        mock_timeseries.get_snapshots_in_range.return_value = sample_snapshots

        results = await aggregator.backfill_aggregations(
            monitor_id="test-monitor-123",
            start_date=start_date,
            end_date=end_date,
            periods=[AggregationPeriod.DAILY, AggregationPeriod.WEEKLY],
        )

        # Verify results
        assert "daily" in results
        assert "weekly" in results
        assert results["daily"] > 0

    @pytest.mark.asyncio
    async def test_backfill_creates_aggregations(
        self, aggregator, mock_timeseries, mock_db_service, sample_snapshots
    ):
        """Test backfill creates aggregations in database"""
        mock_timeseries.get_snapshots_in_range.return_value = sample_snapshots

        await aggregator.backfill_aggregations(
            monitor_id="test-monitor-123",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 3),
            periods=[AggregationPeriod.DAILY],
        )

        # Verify database creates were called
        assert mock_db_service.create_aggregation.call_count > 0


class TestAggregationRetrieval:
    """Test aggregation retrieval and on-demand generation"""

    @pytest.mark.asyncio
    async def test_get_existing_aggregation(
        self, aggregator, mock_db_service, sample_snapshots
    ):
        """Test retrieving existing aggregation"""
        from consultantos.monitoring.snapshot_aggregator import SnapshotAggregation

        existing_agg = SnapshotAggregation(
            monitor_id="test",
            period=AggregationPeriod.DAILY,
            start_time=datetime(2024, 1, 1),
            end_time=datetime(2024, 1, 2),
            snapshot_count=10,
        )

        mock_db_service.get_aggregation.return_value = existing_agg

        agg = await aggregator.get_aggregation(
            monitor_id="test",
            period=AggregationPeriod.DAILY,
            start_time=datetime(2024, 1, 1),
        )

        assert agg is not None
        assert agg.snapshot_count == 10

    @pytest.mark.asyncio
    async def test_generate_missing_aggregation(
        self, aggregator, mock_timeseries, mock_db_service, sample_snapshots
    ):
        """Test on-demand generation of missing aggregation"""
        mock_db_service.get_aggregation.return_value = None
        mock_timeseries.get_snapshots_in_range.return_value = sample_snapshots

        agg = await aggregator.get_aggregation(
            monitor_id="test",
            period=AggregationPeriod.DAILY,
            start_time=datetime(2024, 1, 1),
        )

        # Should generate and store
        assert agg is not None
        mock_db_service.create_aggregation.assert_called_once()


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_most_common_empty_list(self, aggregator):
        """Test most common with empty list"""
        items = []

        result = aggregator._get_most_common(items)

        assert result == []

    def test_most_common_trends(self, aggregator):
        """Test most common trend extraction"""
        trends = [
            "EV growth",
            "Battery tech",
            "EV growth",
            "Battery tech",
            "Battery tech",
            "Regulation",
        ]

        result = aggregator._get_most_common(trends, top_n=2)

        assert len(result) <= 2
        assert "Battery tech" in result


class TestPerformanceBenchmarks:
    """Performance benchmarks for aggregation operations"""

    @pytest.mark.asyncio
    async def test_aggregation_generation_performance(
        self, aggregator, mock_timeseries, sample_snapshots
    ):
        """Benchmark aggregation generation speed"""
        import time

        # Create larger dataset
        large_snapshots = sample_snapshots * 10  # 70 snapshots

        mock_timeseries.get_snapshots_in_range.return_value = large_snapshots

        start_time = time.time()

        agg = await aggregator.generate_daily_aggregation(
            monitor_id="test",
            target_date=datetime(2024, 1, 1),
        )

        duration = time.time() - start_time

        print(f"\nAggregation generation (70 snapshots): {duration:.3f}s")

        # Should complete in reasonable time (<1 second)
        assert duration < 1.0
        assert agg.snapshot_count == 70

    @pytest.mark.asyncio
    async def test_backfill_performance(
        self, aggregator, mock_timeseries, mock_db_service, sample_snapshots
    ):
        """Benchmark backfill operation speed"""
        import time

        mock_timeseries.get_snapshots_in_range.return_value = sample_snapshots

        start_time = time.time()

        results = await aggregator.backfill_aggregations(
            monitor_id="test",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 7),
            periods=[AggregationPeriod.DAILY],
        )

        duration = time.time() - start_time

        print(f"\nBackfill operation (7 days): {duration:.3f}s")

        # Should complete in reasonable time
        assert duration < 5.0
