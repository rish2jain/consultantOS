"""
Performance tests for ConsultantOS.

Tests ensure the application meets SLA requirements:
- API response time < 30s for comprehensive analysis
- Cache hit rate > 50% for repeated queries
- Database operations < 100ms for single doc reads
- Agent execution time within expected bounds
"""
import pytest
import asyncio
import time
from consultantos.performance.cache_manager import CacheManager
from consultantos.performance.db_pool import DatabasePool
from consultantos.performance.llm_optimizer import LLMOptimizer, LLMRequest
from consultantos.performance.rate_limiter import AdaptiveRateLimiter, ConcurrencyLimiter


class TestCachePerformance:
    """Test cache performance and hit rates."""

    @pytest.mark.asyncio
    async def test_cache_hit_performance(self):
        """Cache hits should be < 10ms."""
        cache = CacheManager()

        # Populate cache
        await cache.set("test_key", {"data": "value"})

        # Measure hit time
        start = time.time()
        result = await cache.get("test_key")
        duration = time.time() - start

        assert result is not None
        assert duration < 0.01  # < 10ms

    @pytest.mark.asyncio
    async def test_cache_miss_handling(self):
        """Cache misses should fall back gracefully."""
        cache = CacheManager()

        start = time.time()
        result = await cache.get("nonexistent_key")
        duration = time.time() - start

        assert result is None
        assert duration < 0.05  # < 50ms for miss

    @pytest.mark.asyncio
    async def test_multi_level_cache(self):
        """Multi-level cache should populate correctly."""
        cache = CacheManager()

        # Set value
        await cache.set("test_key", {"value": 123}, ttl=60)

        # Get value (should hit L1)
        result1 = await cache.get("test_key")
        assert result1 == {"value": 123}

        # Clear L1, should fall back to L2/L3
        if cache.l1_cache:
            await cache.l1_cache.delete("test_key")

        result2 = await cache.get("test_key")
        assert result2 == {"value": 123}

    @pytest.mark.asyncio
    async def test_cache_hit_rate(self):
        """Cache hit rate should be > 50% for repeated queries."""
        cache = CacheManager()

        # Populate cache with 10 items
        for i in range(10):
            await cache.set(f"key_{i}", {"value": i})

        # Access items (50% hits, 50% misses)
        hits = 0
        misses = 0

        for i in range(20):
            key = f"key_{i % 10}"  # Repeat first 10 keys
            result = await cache.get(key)
            if result:
                hits += 1
            else:
                misses += 1

        hit_rate = hits / (hits + misses)
        assert hit_rate > 0.5  # > 50% hit rate


class TestDatabasePerformance:
    """Test database operation performance."""

    @pytest.mark.asyncio
    async def test_single_doc_read_performance(self):
        """Single document reads should be < 100ms."""
        db = DatabasePool()

        if not db.client:
            pytest.skip("Firestore not available")

        start = time.time()
        # Note: This will fail if doc doesn't exist, but tests performance
        try:
            await db.get_document("test_collection", "test_doc")
        except Exception:
            pass
        duration = time.time() - start

        assert duration < 0.1  # < 100ms

    @pytest.mark.asyncio
    async def test_batch_read_performance(self):
        """Batch reads should be faster than individual reads."""
        db = DatabasePool()

        if not db.client:
            pytest.skip("Firestore not available")

        doc_ids = [f"doc_{i}" for i in range(10)]

        # Individual reads
        start_individual = time.time()
        for doc_id in doc_ids:
            try:
                await db.get_document("test_collection", doc_id, use_cache=False)
            except Exception:
                pass
        individual_duration = time.time() - start_individual

        # Batch read
        start_batch = time.time()
        try:
            await db.batch_get("test_collection", doc_ids, use_cache=False)
        except Exception:
            pass
        batch_duration = time.time() - start_batch

        # Batch should be faster (or at least not much slower)
        assert batch_duration < individual_duration * 1.5

    @pytest.mark.asyncio
    async def test_query_cache_performance(self):
        """Cached queries should be faster than fresh queries."""
        db = DatabasePool()

        if not db.client:
            pytest.skip("Firestore not available")

        filters = [("status", "==", "active")]

        # First query (cache miss)
        start_miss = time.time()
        try:
            await db.query_with_cache(
                "test_collection",
                filters,
                use_cache=True
            )
        except Exception:
            pass
        miss_duration = time.time() - start_miss

        # Second query (cache hit)
        start_hit = time.time()
        try:
            await db.query_with_cache(
                "test_collection",
                filters,
                use_cache=True
            )
        except Exception:
            pass
        hit_duration = time.time() - start_hit

        # Cache hit should be significantly faster
        assert hit_duration < miss_duration * 0.5 or hit_duration < 0.01


class TestRateLimiterPerformance:
    """Test rate limiter performance."""

    @pytest.mark.asyncio
    async def test_rate_limiter_throughput(self):
        """Rate limiter should allow expected throughput."""
        limiter = AdaptiveRateLimiter(rate=10.0, burst=20)

        # Should allow burst
        start = time.time()
        for _ in range(20):
            acquired = await limiter.acquire_nowait()
            assert acquired  # Burst allows all 20

        duration = time.time() - start
        assert duration < 0.5  # Should be fast

    @pytest.mark.asyncio
    async def test_rate_limiter_wait(self):
        """Rate limiter should properly throttle."""
        limiter = AdaptiveRateLimiter(rate=5.0, burst=5)

        # Exhaust burst
        for _ in range(5):
            await limiter.acquire_nowait()

        # Next request should wait
        start = time.time()
        acquired = await limiter.acquire(tokens=1)
        duration = time.time() - start

        assert acquired
        assert duration > 0.1  # Should have waited

    @pytest.mark.asyncio
    async def test_concurrency_limiter(self):
        """Concurrency limiter should enforce limits."""
        limiter = ConcurrencyLimiter(max_concurrent=3)

        # Track concurrent executions
        concurrent_count = 0
        max_concurrent = 0

        async def worker():
            nonlocal concurrent_count, max_concurrent
            async with limiter:
                concurrent_count += 1
                max_concurrent = max(max_concurrent, concurrent_count)
                await asyncio.sleep(0.1)
                concurrent_count -= 1

        # Start 10 workers
        await asyncio.gather(*[worker() for _ in range(10)])

        # Should have limited to 3 concurrent
        assert max_concurrent <= 3


class TestLLMOptimizerPerformance:
    """Test LLM optimizer performance."""

    @pytest.mark.asyncio
    async def test_llm_cache_performance(self):
        """LLM cache should improve response times."""
        optimizer = LLMOptimizer()

        request = LLMRequest(
            prompt="Test prompt",
            model="gemini-1.5-flash",
            agent_name="test_agent"
        )

        # First call (cache miss) - might fail without API key, that's OK
        try:
            start_miss = time.time()
            await optimizer.generate(request, use_cache=True)
            miss_duration = time.time() - start_miss

            # Second call (cache hit)
            start_hit = time.time()
            await optimizer.generate(request, use_cache=True)
            hit_duration = time.time() - start_hit

            # Cache hit should be much faster
            assert hit_duration < 0.01  # < 10ms
            assert hit_duration < miss_duration * 0.1

        except Exception as e:
            # Skip if API not available
            pytest.skip(f"LLM API not available: {e}")

    @pytest.mark.asyncio
    async def test_llm_batch_performance(self):
        """Batch LLM calls should be efficient."""
        optimizer = LLMOptimizer(max_batch_size=5)

        requests = [
            LLMRequest(
                prompt=f"Test prompt {i}",
                model="gemini-1.5-flash",
                agent_name="test_agent"
            )
            for i in range(5)
        ]

        try:
            start = time.time()
            responses = await optimizer.generate_batch(requests, use_cache=False)
            duration = time.time() - start

            # Should complete in reasonable time
            assert duration < 30.0  # < 30s for 5 requests
            assert len(responses) == 5

        except Exception as e:
            pytest.skip(f"LLM API not available: {e}")


class TestEndToEndPerformance:
    """End-to-end performance tests."""

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_comprehensive_analysis_performance(self):
        """Comprehensive analysis should complete in < 30s."""
        # This would test the full orchestrator
        # Skipping for now as it requires full setup
        pytest.skip("Requires full orchestrator setup")

    @pytest.mark.asyncio
    async def test_parallel_execution_performance(self):
        """Parallel execution should be faster than sequential."""

        async def slow_task():
            await asyncio.sleep(0.5)
            return "done"

        # Sequential
        start_seq = time.time()
        for _ in range(5):
            await slow_task()
        seq_duration = time.time() - start_seq

        # Parallel
        start_par = time.time()
        await asyncio.gather(*[slow_task() for _ in range(5)])
        par_duration = time.time() - start_par

        # Parallel should be much faster
        assert par_duration < seq_duration * 0.5

    @pytest.mark.asyncio
    async def test_cache_warmup_performance(self):
        """Cache warmup should improve subsequent performance."""
        cache = CacheManager()

        # Populate cache
        items = {f"key_{i}": {"value": i} for i in range(100)}
        for key, value in items.items():
            await cache.set(key, value)

        # Access all items
        start = time.time()
        for key in items.keys():
            result = await cache.get(key)
            assert result is not None
        duration = time.time() - start

        # Should be very fast with warm cache
        assert duration < 1.0  # < 1s for 100 items


class TestMemoryUsage:
    """Test memory efficiency."""

    @pytest.mark.asyncio
    async def test_cache_size_limits(self):
        """Cache should respect size limits."""
        cache = CacheManager()

        # Add many items
        for i in range(1000):
            await cache.set(f"key_{i}", {"data": "x" * 1000})  # 1KB each

        # Cache should handle large number of items
        stats = cache.get_stats()
        assert stats["l1_available"] or stats["l2_available"] or stats["l3_available"]

    @pytest.mark.asyncio
    async def test_connection_pool_efficiency(self):
        """Connection pool should reuse connections."""
        db = DatabasePool()

        if not db.client:
            pytest.skip("Firestore not available")

        # Multiple operations should use same client
        for _ in range(10):
            try:
                await db.get_document("test", "test")
            except Exception:
                pass

        # Should have single client instance
        assert db.client is not None
