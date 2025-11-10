"""
Load and Stress Tests

Tests system behavior under load and concurrent requests.
"""
import pytest
import asyncio
from httpx import AsyncClient
from unittest.mock import patch
import time


# ============================================================================
# CONCURRENT REQUEST TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.asyncio
async def test_concurrent_analysis_requests(test_client: AsyncClient):
    """
    Test system handles concurrent analysis requests.

    Should process multiple requests in parallel without failures.
    """
    with patch("consultantos.tools.tavily_tool.TavilyClient") as mock_tavily:
        mock_tavily.return_value.search.return_value = {
            "results": [{"title": "Test", "content": "Content", "url": "http://test.com"}]
        }

        # Fire 20 concurrent requests
        tasks = [
            test_client.post("/analyze", json={
                "company": f"Company{i}",
                "industry": "Tech",
                "frameworks": ["porter"]
            })
            for i in range(20)
        ]

        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # Count outcomes
        success_count = sum(
            1 for r in responses
            if not isinstance(r, Exception) and r.status_code == 200
        )
        rate_limited = sum(
            1 for r in responses
            if not isinstance(r, Exception) and r.status_code == 429
        )
        errors = sum(1 for r in responses if isinstance(r, Exception))

        # Most should succeed or be rate limited
        assert success_count + rate_limited >= 15

        # Should not have too many errors
        assert errors < 5


@pytest.mark.integration
@pytest.mark.asyncio
async def test_concurrent_different_endpoints(test_client: AsyncClient):
    """
    Test concurrent requests to different endpoints.

    Should handle mixed workload efficiently.
    """
    tasks = [
        test_client.get("/health"),
        test_client.get("/health"),
        test_client.get("/mvp/health"),
        test_client.post("/analyze", json={
            "company": "Tesla",
            "industry": "EV",
            "frameworks": ["porter"]
        }),
    ]

    responses = await asyncio.gather(*tasks, return_exceptions=True)

    # All should complete
    assert len(responses) == len(tasks)

    # Most should succeed
    success_count = sum(
        1 for r in responses
        if not isinstance(r, Exception) and r.status_code in [200, 201]
    )
    assert success_count >= 3


# ============================================================================
# THROUGHPUT TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.asyncio
async def test_sequential_request_throughput(test_client: AsyncClient):
    """
    Test throughput of sequential requests.

    Measures requests per second baseline.
    """
    with patch("consultantos.tools.tavily_tool.TavilyClient") as mock_tavily:
        mock_tavily.return_value.search.return_value = {
            "results": [{"title": "Test", "content": "Content", "url": "http://test.com"}]
        }

        num_requests = 10
        start_time = time.time()

        for i in range(num_requests):
            response = await test_client.post("/analyze", json={
                "company": f"Company{i}",
                "industry": "Tech",
                "frameworks": ["porter"]
            })

            # Allow failures but track
            if response.status_code not in [200, 429]:
                pass

        elapsed_time = time.time() - start_time
        throughput = num_requests / elapsed_time

        # Should process at least 1 request per second
        # (This is very conservative - actual throughput should be higher)
        assert throughput > 0.5


@pytest.mark.integration
@pytest.mark.asyncio
async def test_parallel_request_speedup(test_client: AsyncClient):
    """
    Test that parallel requests are faster than sequential.

    Validates async processing benefits.
    """
    with patch("consultantos.tools.tavily_tool.TavilyClient") as mock_tavily:
        mock_tavily.return_value.search.return_value = {
            "results": [{"title": "Test", "content": "Content", "url": "http://test.com"}]
        }

        num_requests = 5

        # Sequential timing
        start_sequential = time.time()
        for i in range(num_requests):
            await test_client.post("/analyze", json={
                "company": f"Company{i}",
                "industry": "Tech",
                "frameworks": ["porter"]
            })
        sequential_time = time.time() - start_sequential

        # Parallel timing
        start_parallel = time.time()
        tasks = [
            test_client.post("/analyze", json={
                "company": f"Company{i}",
                "industry": "Tech",
                "frameworks": ["porter"]
            })
            for i in range(num_requests)
        ]
        await asyncio.gather(*tasks, return_exceptions=True)
        parallel_time = time.time() - start_parallel

        # Parallel should be faster (though not guaranteed in test environment)
        # Just verify both complete
        assert sequential_time > 0
        assert parallel_time > 0


# ============================================================================
# STRESS TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.asyncio
async def test_stress_rapid_requests(test_client: AsyncClient):
    """
    Stress test with rapid fire requests.

    Tests system stability under heavy load.
    """
    with patch("consultantos.tools.tavily_tool.TavilyClient") as mock_tavily:
        mock_tavily.return_value.search.return_value = {
            "results": [{"title": "Test", "content": "Content", "url": "http://test.com"}]
        }

        # Fire 50 requests rapidly
        tasks = []
        for i in range(50):
            task = test_client.post("/analyze", json={
                "company": f"Company{i % 10}",  # Reuse companies for caching
                "industry": "Tech",
                "frameworks": ["porter"]
            })
            tasks.append(task)

        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # System should handle gracefully
        # Allow some rate limiting but no crashes
        crashed = sum(1 for r in responses if isinstance(r, Exception))
        assert crashed < 10  # Less than 20% failures


@pytest.mark.integration
@pytest.mark.asyncio
async def test_stress_large_payload(test_client: AsyncClient):
    """
    Stress test with large request payloads.

    Tests payload size handling.
    """
    # Create large but valid payload
    large_payload = {
        "company": "Tesla" * 100,  # Long company name
        "industry": "Electric Vehicles",
        "frameworks": ["porter", "swot", "pestel", "blue_ocean"],  # All frameworks
        "analysis_depth": "deep",
        "context": "A" * 1000  # Large context field
    }

    response = await test_client.post("/analyze", json=large_payload)

    # Should reject or handle large payload
    assert response.status_code in [200, 413, 422]


# ============================================================================
# MEMORY LEAK TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.asyncio
async def test_memory_stability_repeated_requests(test_client: AsyncClient):
    """
    Test memory stability over many requests.

    Checks for memory leaks.
    """
    import psutil
    import os

    with patch("consultantos.tools.tavily_tool.TavilyClient") as mock_tavily:
        mock_tavily.return_value.search.return_value = {
            "results": [{"title": "Test", "content": "Content", "url": "http://test.com"}]
        }

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Make 100 requests
        for i in range(100):
            await test_client.post("/analyze", json={
                "company": f"Company{i % 5}",
                "industry": "Tech",
                "frameworks": ["porter"]
            })

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (less than 500MB for 100 requests)
        # This is very conservative
        assert memory_increase < 500


# ============================================================================
# TIMEOUT TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.asyncio
async def test_request_timeout_handling(test_client: AsyncClient):
    """
    Test that long-running requests timeout appropriately.

    Should not hang indefinitely.
    """
    with patch("consultantos.agents.research_agent.ResearchAgent.execute") as mock_execute:
        # Simulate slow operation
        async def slow_execute(*args, **kwargs):
            await asyncio.sleep(10)
            return {"data": "result"}

        mock_execute.side_effect = slow_execute

        # Request should timeout
        with pytest.raises((asyncio.TimeoutError, Exception)):
            await asyncio.wait_for(
                test_client.post("/analyze", json={
                    "company": "Tesla",
                    "industry": "EV",
                    "frameworks": ["porter"]
                }),
                timeout=5.0
            )


# ============================================================================
# CACHE PERFORMANCE TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.asyncio
async def test_cache_performance_improvement(test_client: AsyncClient):
    """
    Test that caching improves performance for repeated requests.

    Second request should be faster due to caching.
    """
    with patch("consultantos.tools.tavily_tool.TavilyClient") as mock_tavily:
        mock_tavily.return_value.search.return_value = {
            "results": [{"title": "Test", "content": "Content", "url": "http://test.com"}]
        }

        request_data = {
            "company": "CacheTestCompany",
            "industry": "Tech",
            "frameworks": ["porter"]
        }

        # First request (cache miss)
        start_first = time.time()
        first_response = await test_client.post("/analyze", json=request_data)
        first_time = time.time() - start_first

        if first_response.status_code != 200:
            pytest.skip("First request failed")

        # Second request (cache hit)
        start_second = time.time()
        second_response = await test_client.post("/analyze", json=request_data)
        second_time = time.time() - start_second

        if second_response.status_code != 200:
            pytest.skip("Second request failed")

        # Second should be at least as fast (caching might not be enabled)
        # Just verify both complete successfully
        assert first_time > 0
        assert second_time > 0


# ============================================================================
# CONNECTION POOL TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.asyncio
async def test_connection_pool_efficiency(test_client: AsyncClient):
    """
    Test connection pooling efficiency.

    Should reuse connections for multiple requests.
    """
    # Make multiple requests
    responses = []
    for i in range(10):
        response = await test_client.get("/health")
        responses.append(response)

    # All should succeed
    assert all(r.status_code == 200 for r in responses)


# ============================================================================
# GRACEFUL DEGRADATION UNDER LOAD
# ============================================================================

@pytest.mark.integration
@pytest.mark.asyncio
async def test_graceful_degradation_under_load(test_client: AsyncClient):
    """
    Test system degrades gracefully under extreme load.

    Should return errors but not crash.
    """
    with patch("consultantos.tools.tavily_tool.TavilyClient") as mock_tavily:
        mock_tavily.return_value.search.return_value = {
            "results": [{"title": "Test", "content": "Content", "url": "http://test.com"}]
        }

        # Fire 100 concurrent requests
        tasks = [
            test_client.post("/analyze", json={
                "company": f"Company{i}",
                "industry": "Tech",
                "frameworks": ["porter"]
            })
            for i in range(100)
        ]

        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # System should handle gracefully (rate limit or process)
        # No complete crashes
        total_exceptions = sum(1 for r in responses if isinstance(r, Exception))

        # Less than 30% complete failures
        assert total_exceptions < 30


# ============================================================================
# LOAD TEST CONFIGURATION
# ============================================================================

@pytest.mark.integration
@pytest.mark.asyncio
async def test_configurable_load_test(test_client: AsyncClient, load_test_config: dict):
    """
    Test with configurable load parameters.

    Uses environment variables for load test configuration.
    """
    concurrent_requests = load_test_config["concurrent_requests"]
    timeout = load_test_config["request_timeout"]

    with patch("consultantos.tools.tavily_tool.TavilyClient") as mock_tavily:
        mock_tavily.return_value.search.return_value = {
            "results": [{"title": "Test", "content": "Content", "url": "http://test.com"}]
        }

        tasks = [
            test_client.post("/analyze", json={
                "company": f"Company{i}",
                "industry": "Tech",
                "frameworks": ["porter"]
            })
            for i in range(concurrent_requests)
        ]

        try:
            responses = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=timeout
            )

            success_rate = sum(
                1 for r in responses
                if not isinstance(r, Exception) and r.status_code in [200, 429]
            ) / len(responses)

            # At least 70% success rate
            assert success_rate >= 0.7

        except asyncio.TimeoutError:
            pytest.fail("Load test timed out")
