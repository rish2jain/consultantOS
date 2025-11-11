"""
Tests for strategic infrastructure components.

Tests competitive context, time series storage, and pattern library.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
import numpy as np

from consultantos.context.competitive_context import (
    CompetitiveContextService,
    IndustryBenchmark,
    MetricType,
    MetricPercentile,
)
from consultantos.monitoring.timeseries_storage import (
    TimeSeriesStorage,
    TimeSeriesMetric,
    TrendDirection,
)
from consultantos.analysis.pattern_library import (
    PatternLibraryService,
    HistoricalPattern,
    PatternCategory,
    PatternSignal,
    PatternOutcome,
)


@pytest.fixture
def mock_db_service():
    """Mock database service"""
    db = MagicMock()
    db.db = MagicMock()
    return db


@pytest.fixture
def competitive_context_service(mock_db_service):
    """Fixture for competitive context service"""
    return CompetitiveContextService(mock_db_service)


@pytest.fixture
def timeseries_storage(mock_db_service):
    """Fixture for time series storage"""
    return TimeSeriesStorage(mock_db_service)


@pytest.fixture
def pattern_library_service(mock_db_service):
    """Fixture for pattern library service"""
    return PatternLibraryService(mock_db_service)


@pytest.fixture
def sample_benchmark():
    """Sample industry benchmark"""
    return IndustryBenchmark(
        industry="Electric Vehicles",
        metric_name="supplier_power",
        metric_type=MetricType.COMPETITIVE_FORCE,
        mean=3.5,
        median=3.4,
        std_dev=0.8,
        min_value=1.0,
        max_value=5.0,
        p10=2.0,
        p25=2.8,
        p50=3.4,
        p75=4.2,
        p90=4.8,
        sample_size=50,
        data_source="test_data",
        confidence_score=0.85
    )


# Competitive Context Tests

@pytest.mark.asyncio
async def test_store_benchmark(competitive_context_service, sample_benchmark):
    """Test storing industry benchmark"""
    # Mock database operations
    mock_collection = MagicMock()
    mock_doc_ref = MagicMock()
    mock_doc_ref.set = AsyncMock()
    mock_collection.document = MagicMock(return_value=mock_doc_ref)
    competitive_context_service.db.db.collection = MagicMock(return_value=mock_collection)

    # Store benchmark
    result = await competitive_context_service.store_benchmark(sample_benchmark)

    assert result is True
    mock_doc_ref.set.assert_called_once()


@pytest.mark.asyncio
async def test_calculate_percentile(competitive_context_service, sample_benchmark):
    """Test percentile calculation"""
    # Mock get_benchmark
    with patch.object(
        competitive_context_service,
        'get_benchmark',
        return_value=sample_benchmark
    ):
        # Calculate percentile for value 4.5 (should be ~90th percentile)
        percentile = await competitive_context_service.calculate_percentile(
            company="Tesla",
            industry="Electric Vehicles",
            metric_name="supplier_power",
            value=4.5
        )

        assert percentile is not None
        assert percentile.company == "Tesla"
        assert 80 <= percentile.percentile <= 95  # Should be around 90th percentile
        assert "Tesla's supplier_power" in percentile.comparative_statement


@pytest.mark.asyncio
async def test_percentile_edge_cases(competitive_context_service, sample_benchmark):
    """Test percentile calculation edge cases"""
    with patch.object(
        competitive_context_service,
        'get_benchmark',
        return_value=sample_benchmark
    ):
        # Test minimum value
        percentile_min = await competitive_context_service.calculate_percentile(
            company="Test", industry="EV", metric_name="test", value=1.0
        )
        assert percentile_min.percentile == 0.0

        # Test maximum value
        percentile_max = await competitive_context_service.calculate_percentile(
            company="Test", industry="EV", metric_name="test", value=5.0
        )
        assert percentile_max.percentile == 100.0


# Time Series Tests

@pytest.mark.asyncio
async def test_store_metric(timeseries_storage):
    """Test storing time series metric"""
    # Mock database operations
    mock_collection = MagicMock()
    mock_doc_ref = MagicMock()
    mock_doc_ref.set = AsyncMock()
    mock_collection.document = MagicMock(return_value=mock_doc_ref)
    timeseries_storage.db.db.collection = MagicMock(return_value=mock_collection)

    # Create metric
    metric = TimeSeriesMetric(
        monitor_id="test_monitor",
        metric_name="revenue",
        timestamp=datetime.utcnow(),
        value=1000000.0,
        data_source="test"
    )

    # Store metric
    result = await timeseries_storage.store_metric(metric)

    assert result is True
    mock_doc_ref.set.assert_called_once()


@pytest.mark.asyncio
async def test_calculate_derivatives(timeseries_storage):
    """Test derivative calculation"""
    # Create sample time series data
    base_time = datetime.utcnow()
    metrics = [
        TimeSeriesMetric(
            monitor_id="test",
            metric_name="revenue",
            timestamp=base_time + timedelta(days=i),
            value=1000.0 * (1 + i * 0.1),  # 10% daily growth
            data_source="test"
        )
        for i in range(10)
    ]

    # Mock get_time_series
    with patch.object(
        timeseries_storage,
        'get_time_series',
        return_value=metrics
    ):
        with patch.object(
            timeseries_storage,
            '_store_derivatives',
            return_value=True
        ):
            # Calculate derivatives
            derivatives = await timeseries_storage.calculate_derivatives(
                monitor_id="test",
                metric_name="revenue",
                days_back=10
            )

            assert len(derivatives) == 10
            # First point should have no growth rate
            assert derivatives[0].growth_rate is None
            # Later points should have growth rates
            assert derivatives[5].growth_rate is not None
            # Should have rolling averages
            assert derivatives[7].rolling_7d_avg is not None


@pytest.mark.asyncio
async def test_detect_trend(timeseries_storage):
    """Test trend detection"""
    # Create upward trending data
    base_time = datetime.utcnow()
    metrics = [
        TimeSeriesMetric(
            monitor_id="test",
            metric_name="revenue",
            timestamp=base_time + timedelta(days=i),
            value=1000.0 + i * 50.0,  # Linear growth
            data_source="test"
        )
        for i in range(30)
    ]

    # Mock get_time_series
    with patch.object(
        timeseries_storage,
        'get_time_series',
        return_value=metrics
    ):
        # Detect trend
        trend = await timeseries_storage.detect_trend(
            monitor_id="test",
            metric_name="revenue",
            days_back=30
        )

        assert trend is not None
        assert trend.direction == TrendDirection.UPWARD
        assert trend.slope > 0
        assert trend.r_squared > 0.9  # Should be strong fit
        assert trend.forecast_7d is not None
        assert trend.forecast_30d is not None


# Pattern Library Tests

@pytest.fixture
def sample_pattern():
    """Sample historical pattern"""
    return HistoricalPattern(
        pattern_id="test_pattern",
        category=PatternCategory.FINANCIAL_DISTRESS,
        name="Test Pattern",
        description="Test pattern for unit tests",
        signals=[
            PatternSignal(
                metric_name="sentiment",
                change_type="decrease",
                time_offset_days=0
            ),
            PatternSignal(
                metric_name="sentiment",
                change_type="decrease",
                time_offset_days=30
            )
        ],
        outcome=PatternOutcome(
            outcome_type="earnings_miss",
            description="Earnings miss",
            time_to_outcome_days=60,
            severity=7.0
        ),
        occurrence_count=20,
        successful_predictions=15,
        accuracy=0.75,
        example_companies=["CompanyA", "CompanyB"],
        confidence_score=0.8
    )


@pytest.mark.asyncio
async def test_store_pattern(pattern_library_service, sample_pattern):
    """Test storing historical pattern"""
    # Mock database operations
    mock_collection = MagicMock()
    mock_doc_ref = MagicMock()
    mock_doc_ref.set = AsyncMock()
    mock_collection.document = MagicMock(return_value=mock_doc_ref)
    pattern_library_service.db.db.collection = MagicMock(return_value=mock_collection)

    # Store pattern
    result = await pattern_library_service.store_pattern(sample_pattern)

    assert result is True
    mock_doc_ref.set.assert_called_once()


@pytest.mark.asyncio
async def test_pattern_validation(pattern_library_service):
    """Test pattern validation"""
    # Pattern with insufficient occurrences
    invalid_pattern = HistoricalPattern(
        pattern_id="invalid",
        category=PatternCategory.DISRUPTION,
        name="Invalid Pattern",
        description="Too few occurrences",
        signals=[
            PatternSignal(
                metric_name="test_metric",
                change_type="increase",
                time_offset_days=0
            )
        ],
        outcome=PatternOutcome(
            outcome_type="test",
            description="test",
            time_to_outcome_days=30,
            severity=5.0
        ),
        occurrence_count=2,  # Too few
        successful_predictions=1,
        accuracy=0.5,
        confidence_score=0.5
    )

    # Mock database
    mock_collection = MagicMock()
    pattern_library_service.db.db.collection = MagicMock(return_value=mock_collection)

    # Should raise ValueError
    with pytest.raises(ValueError, match="minimum 3 occurrences"):
        await pattern_library_service.store_pattern(invalid_pattern)


@pytest.mark.asyncio
async def test_update_pattern_accuracy(pattern_library_service, sample_pattern):
    """Test updating pattern accuracy"""
    # Mock get_pattern and store_pattern
    with patch.object(
        pattern_library_service,
        'get_pattern',
        return_value=sample_pattern
    ):
        with patch.object(
            pattern_library_service,
            'store_pattern',
            return_value=True
        ):
            # Update with successful prediction
            result = await pattern_library_service.update_pattern_accuracy(
                pattern_id="test_pattern",
                outcome_occurred=True,
                company="NewCompany",
                date=datetime.utcnow()
            )

            assert result is True


@pytest.mark.asyncio
async def test_confidence_calculation(pattern_library_service):
    """Test confidence score calculation"""
    # High occurrence, high accuracy
    confidence_high = pattern_library_service._calculate_confidence(
        occurrence_count=100,
        accuracy=0.9
    )
    assert confidence_high > 0.85

    # Low occurrence, high accuracy
    confidence_low_n = pattern_library_service._calculate_confidence(
        occurrence_count=5,
        accuracy=0.9
    )
    assert confidence_low_n < confidence_high

    # High occurrence, low accuracy
    confidence_low_acc = pattern_library_service._calculate_confidence(
        occurrence_count=100,
        accuracy=0.5
    )
    assert confidence_low_acc < confidence_high


# Integration Tests

@pytest.mark.asyncio
async def test_end_to_end_workflow(
    competitive_context_service,
    timeseries_storage,
    pattern_library_service,
    sample_benchmark
):
    """Test integrated workflow across all components"""
    # Mock all database operations
    mock_collection = MagicMock()
    mock_doc_ref = MagicMock()
    mock_doc_ref.set = AsyncMock()
    mock_doc_ref.get = AsyncMock(return_value=MagicMock(exists=True, to_dict=lambda: sample_benchmark.dict()))
    mock_collection.document = MagicMock(return_value=mock_doc_ref)

    competitive_context_service.db.db.collection = MagicMock(return_value=mock_collection)
    timeseries_storage.db.db.collection = MagicMock(return_value=mock_collection)
    pattern_library_service.db.db.collection = MagicMock(return_value=mock_collection)

    # 1. Store benchmark
    benchmark_stored = await competitive_context_service.store_benchmark(sample_benchmark)
    assert benchmark_stored is True

    # 2. Store time series metrics
    metric = TimeSeriesMetric(
        monitor_id="test",
        metric_name="revenue",
        timestamp=datetime.utcnow(),
        value=1000000.0,
        data_source="test"
    )
    metric_stored = await timeseries_storage.store_metric(metric)
    assert metric_stored is True

    # 3. Calculate percentile
    with patch.object(
        competitive_context_service,
        'get_benchmark',
        return_value=sample_benchmark
    ):
        percentile = await competitive_context_service.calculate_percentile(
            company="Test",
            industry="Electric Vehicles",
            metric_name="supplier_power",
            value=4.0
        )
        assert percentile is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
