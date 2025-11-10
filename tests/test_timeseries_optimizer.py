"""
Comprehensive tests for time-series optimization layer.

Tests cover:
- Snapshot compression/decompression
- Time-range queries with pagination
- Batch write operations
- Query result caching
- Retention policy management
- Performance benchmarks
"""

import asyncio
import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

from consultantos.monitoring.timeseries_optimizer import TimeSeriesOptimizer
from consultantos.models.monitoring import MonitorAnalysisSnapshot


@pytest.fixture
def mock_db_service():
    """Mock database service for testing"""
    db = MagicMock()
    db.create_snapshot = AsyncMock(return_value=True)
    db.get_snapshots_in_range = AsyncMock(return_value=[])
    db.get_latest_snapshot = AsyncMock(return_value=None)
    db.delete_snapshots_before = AsyncMock(return_value=0)
    return db


@pytest.fixture
def optimizer(mock_db_service):
    """Create time-series optimizer instance"""
    return TimeSeriesOptimizer(
        db_service=mock_db_service,
        compression_threshold_bytes=500,
        batch_size=5,
        cache_ttl_seconds=300,
    )


@pytest.fixture
def sample_snapshot():
    """Create sample snapshot for testing"""
    return MonitorAnalysisSnapshot(
        monitor_id="test-monitor-123",
        timestamp=datetime.utcnow(),
        company="Tesla",
        industry="Electric Vehicles",
        competitive_forces={
            "competitive_rivalry": "High intensity competition with legacy automakers",
            "supplier_power": "Medium power due to battery supply constraints",
            "buyer_power": "Low power due to brand loyalty and limited alternatives",
            "threat_of_substitutes": "Medium threat from public transportation",
            "threat_of_new_entrants": "Low threat due to capital requirements",
        },
        market_trends=["EV adoption accelerating", "Battery costs declining"],
        financial_metrics={"revenue": 81500000000, "gross_margin": 25.6},
        strategic_position={"strengths": ["Brand", "Technology"], "weaknesses": ["Manufacturing"]},
    )


class TestSnapshotCompression:
    """Test snapshot compression/decompression"""

    @pytest.mark.asyncio
    async def test_compress_large_snapshot(self, optimizer, sample_snapshot):
        """Test compression of large snapshot"""
        # Compress
        compressed = optimizer._compress_snapshot(sample_snapshot)

        # Verify compressed fields have marker
        assert compressed.competitive_forces.get("_compressed") is True
        assert "data" in compressed.competitive_forces

        # Verify size reduction
        original_size = optimizer._estimate_snapshot_size(sample_snapshot)
        compressed_size = optimizer._estimate_snapshot_size(compressed)
        assert compressed_size < original_size

    @pytest.mark.asyncio
    async def test_decompress_snapshot(self, optimizer, sample_snapshot):
        """Test decompression restores original data"""
        # Compress
        compressed = optimizer._compress_snapshot(sample_snapshot)

        # Decompress
        decompressed = optimizer._decompress_snapshot(compressed)

        # Verify data matches original
        assert decompressed.competitive_forces == sample_snapshot.competitive_forces
        assert decompressed.financial_metrics == sample_snapshot.financial_metrics

    @pytest.mark.asyncio
    async def test_compression_threshold(self, optimizer, sample_snapshot):
        """Test compression only applies above threshold"""
        # Small snapshot (below threshold)
        small_snapshot = MonitorAnalysisSnapshot(
            monitor_id="test",
            timestamp=datetime.utcnow(),
            company="Test",
            industry="Test",
        )

        # Should not compress
        await optimizer.store_snapshot(small_snapshot, compress=True)

        # Verify store was called (not compressed)
        optimizer.db.create_snapshot.assert_called_once()

    @pytest.mark.asyncio
    async def test_no_compression_when_disabled(self, optimizer, sample_snapshot):
        """Test compression can be disabled"""
        await optimizer.store_snapshot(sample_snapshot, compress=False)

        # Verify stored without compression
        call_args = optimizer.db.create_snapshot.call_args[0][0]
        assert not call_args.competitive_forces.get("_compressed")


class TestBatchOperations:
    """Test batch write operations"""

    @pytest.mark.asyncio
    async def test_batch_write(self, optimizer, sample_snapshot):
        """Test batched write accumulation"""
        # Add snapshots to batch
        for i in range(3):
            snapshot = sample_snapshot.copy()
            snapshot.timestamp = datetime.utcnow() + timedelta(seconds=i)
            await optimizer.store_snapshot(snapshot, batch=True)

        # Verify not written yet (batch not full)
        assert optimizer.db.create_snapshot.call_count == 0
        assert len(optimizer._write_batch) == 3

    @pytest.mark.asyncio
    async def test_batch_auto_flush(self, optimizer, sample_snapshot):
        """Test batch auto-flushes when full"""
        # Add snapshots to fill batch (batch_size=5)
        for i in range(5):
            snapshot = sample_snapshot.copy()
            snapshot.timestamp = datetime.utcnow() + timedelta(seconds=i)
            await optimizer.store_snapshot(snapshot, batch=True)

        # Verify batch was flushed
        assert optimizer.db.create_snapshot.call_count == 5
        assert len(optimizer._write_batch) == 0

    @pytest.mark.asyncio
    async def test_manual_flush(self, optimizer, sample_snapshot):
        """Test manual batch flush"""
        # Add snapshots to batch
        for i in range(3):
            snapshot = sample_snapshot.copy()
            snapshot.timestamp = datetime.utcnow() + timedelta(seconds=i)
            await optimizer.store_snapshot(snapshot, batch=True)

        # Manually flush
        flushed = await optimizer.flush_pending_writes()

        # Verify flush
        assert flushed == 3
        assert optimizer.db.create_snapshot.call_count == 3
        assert len(optimizer._write_batch) == 0


class TestTimeRangeQueries:
    """Test time-range query operations"""

    @pytest.mark.asyncio
    async def test_get_snapshots_in_range(self, optimizer, sample_snapshot):
        """Test time-range query"""
        start_time = datetime.utcnow() - timedelta(days=7)
        end_time = datetime.utcnow()

        # Mock database response
        optimizer.db.get_snapshots_in_range.return_value = [sample_snapshot]

        # Query
        results = await optimizer.get_snapshots_in_range(
            monitor_id="test-monitor-123",
            start_time=start_time,
            end_time=end_time,
        )

        # Verify query
        optimizer.db.get_snapshots_in_range.assert_called_once_with(
            monitor_id="test-monitor-123",
            start_time=start_time,
            end_time=end_time,
            limit=None,
        )

        assert len(results) == 1

    @pytest.mark.asyncio
    async def test_query_result_caching(self, optimizer, sample_snapshot):
        """Test query results are cached"""
        start_time = datetime.utcnow() - timedelta(days=7)
        end_time = datetime.utcnow()

        optimizer.db.get_snapshots_in_range.return_value = [sample_snapshot]

        # First query
        results1 = await optimizer.get_snapshots_in_range(
            monitor_id="test-monitor-123",
            start_time=start_time,
            end_time=end_time,
        )

        # Second query (should hit cache)
        results2 = await optimizer.get_snapshots_in_range(
            monitor_id="test-monitor-123",
            start_time=start_time,
            end_time=end_time,
        )

        # Verify DB called only once
        assert optimizer.db.get_snapshots_in_range.call_count == 1

        # Results should match
        assert results1 == results2

    @pytest.mark.asyncio
    async def test_cache_expiration(self, optimizer, sample_snapshot):
        """Test cache entries expire"""
        start_time = datetime.utcnow() - timedelta(days=7)
        end_time = datetime.utcnow()

        optimizer.db.get_snapshots_in_range.return_value = [sample_snapshot]
        optimizer.cache_ttl = 1  # 1 second TTL

        # First query
        await optimizer.get_snapshots_in_range(
            monitor_id="test-monitor-123",
            start_time=start_time,
            end_time=end_time,
        )

        # Wait for cache expiration
        await asyncio.sleep(1.5)

        # Second query (cache expired)
        await optimizer.get_snapshots_in_range(
            monitor_id="test-monitor-123",
            start_time=start_time,
            end_time=end_time,
        )

        # Verify DB called twice
        assert optimizer.db.get_snapshots_in_range.call_count == 2

    @pytest.mark.asyncio
    async def test_get_latest_snapshot(self, optimizer, sample_snapshot):
        """Test get latest snapshot"""
        optimizer.db.get_latest_snapshot.return_value = sample_snapshot

        result = await optimizer.get_latest_snapshot("test-monitor-123")

        assert result.monitor_id == "test-monitor-123"
        optimizer.db.get_latest_snapshot.assert_called_once_with("test-monitor-123")

    @pytest.mark.asyncio
    async def test_get_snapshot_at_time(self, optimizer, sample_snapshot):
        """Test get snapshot closest to target time"""
        target_time = datetime.utcnow()

        # Create snapshots at different times
        snapshots = []
        for offset in [-60, -30, 10, 40]:  # minutes
            snapshot = sample_snapshot.copy()
            snapshot.timestamp = target_time + timedelta(minutes=offset)
            snapshots.append(snapshot)

        optimizer.db.get_snapshots_in_range.return_value = snapshots

        # Find closest to target
        result = await optimizer.get_snapshot_at_time(
            monitor_id="test-monitor-123",
            target_time=target_time,
            tolerance_hours=2,
        )

        # Should return snapshot at +10 minutes (closest)
        assert abs((result.timestamp - target_time).total_seconds()) == 600


class TestRetentionManagement:
    """Test retention policy management"""

    @pytest.mark.asyncio
    async def test_cleanup_old_snapshots(self, optimizer):
        """Test cleanup of old snapshots"""
        optimizer.db.delete_snapshots_before.return_value = 42

        deleted = await optimizer.cleanup_old_snapshots(
            monitor_id="test-monitor-123",
            retention_days=90,
            dry_run=False,
        )

        assert deleted == 42

    @pytest.mark.asyncio
    async def test_cleanup_dry_run(self, optimizer, sample_snapshot):
        """Test dry run doesn't delete"""
        # Mock snapshots to delete
        old_snapshots = [sample_snapshot] * 10
        optimizer.db.get_snapshots_in_range.return_value = old_snapshots

        count = await optimizer.cleanup_old_snapshots(
            monitor_id="test-monitor-123",
            retention_days=90,
            dry_run=True,
        )

        # Should count but not delete
        assert count == 10
        optimizer.db.delete_snapshots_before.assert_not_called()


class TestPerformanceBenchmarks:
    """Performance benchmarks for time-series operations"""

    @pytest.mark.asyncio
    async def test_compression_performance(self, optimizer, sample_snapshot):
        """Benchmark compression speed"""
        iterations = 100

        start_time = time.time()
        for _ in range(iterations):
            compressed = optimizer._compress_snapshot(sample_snapshot)
            decompressed = optimizer._decompress_snapshot(compressed)

        duration = time.time() - start_time
        ops_per_second = iterations / duration

        print(f"\nCompression benchmark: {ops_per_second:.1f} ops/sec")

        # Assert reasonable performance (>50 ops/sec)
        assert ops_per_second > 50

    @pytest.mark.asyncio
    async def test_batch_write_performance(self, optimizer, sample_snapshot):
        """Benchmark batch write performance"""
        batch_sizes = [10, 50, 100]

        for batch_size in batch_sizes:
            optimizer.batch_size = batch_size
            optimizer._write_batch.clear()

            start_time = time.time()

            # Add snapshots
            for i in range(batch_size):
                snapshot = sample_snapshot.copy()
                snapshot.timestamp = datetime.utcnow() + timedelta(seconds=i)
                await optimizer.store_snapshot(snapshot, batch=True)

            duration = time.time() - start_time
            snapshots_per_second = batch_size / duration

            print(
                f"\nBatch write (size={batch_size}): {snapshots_per_second:.1f} snapshots/sec"
            )

    @pytest.mark.asyncio
    async def test_query_cache_performance(self, optimizer, sample_snapshot):
        """Benchmark query cache hit performance"""
        start_time = datetime.utcnow() - timedelta(days=7)
        end_time = datetime.utcnow()

        optimizer.db.get_snapshots_in_range.return_value = [sample_snapshot] * 100

        # Warm cache
        await optimizer.get_snapshots_in_range(
            monitor_id="test-monitor-123",
            start_time=start_time,
            end_time=end_time,
        )

        # Benchmark cache hits
        iterations = 1000
        cache_start = time.time()

        for _ in range(iterations):
            await optimizer.get_snapshots_in_range(
                monitor_id="test-monitor-123",
                start_time=start_time,
                end_time=end_time,
            )

        cache_duration = time.time() - cache_start
        cache_ops_per_second = iterations / cache_duration

        print(f"\nQuery cache hits: {cache_ops_per_second:.1f} ops/sec")

        # Cache should be very fast (>1000 ops/sec)
        assert cache_ops_per_second > 1000


class TestEdgeCases:
    """Test edge cases and error handling"""

    @pytest.mark.asyncio
    async def test_empty_snapshot_range(self, optimizer):
        """Test empty time range"""
        optimizer.db.get_snapshots_in_range.return_value = []

        results = await optimizer.get_snapshots_in_range(
            monitor_id="test-monitor-123",
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow(),
        )

        assert results == []

    @pytest.mark.asyncio
    async def test_snapshot_without_compression_fields(self, optimizer):
        """Test snapshot with minimal data"""
        minimal_snapshot = MonitorAnalysisSnapshot(
            monitor_id="test",
            timestamp=datetime.utcnow(),
            company="Test",
            industry="Test",
        )

        # Should not fail
        compressed = optimizer._compress_snapshot(minimal_snapshot)
        decompressed = optimizer._decompress_snapshot(compressed)

        assert decompressed.company == "Test"

    @pytest.mark.asyncio
    async def test_get_trend_data(self, optimizer, sample_snapshot):
        """Test trend data extraction"""
        # Create series of snapshots
        snapshots = []
        for i in range(7):
            snapshot = sample_snapshot.copy()
            snapshot.timestamp = datetime.utcnow() - timedelta(days=7 - i)
            snapshots.append(snapshot)

        optimizer.db.get_snapshots_in_range.return_value = snapshots

        trend_data = await optimizer.get_trend_data(
            monitor_id="test-monitor-123",
            days=7,
        )

        assert len(trend_data) == 7
        assert "timestamp" in trend_data[0]
        assert "metrics" in trend_data[0]
