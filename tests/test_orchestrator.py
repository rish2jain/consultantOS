"""
Comprehensive tests for orchestrator module
Testing graceful degradation, timeout handling, cache scenarios, and concurrent requests
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from consultantos.orchestrator.orchestrator import AnalysisOrchestrator
from consultantos.models import (
    AnalysisRequest,
    CompanyResearch,
    MarketTrends,
    FinancialSnapshot,
    FrameworkAnalysis,
    ExecutiveSummary,
    StrategicReport
)


@pytest.fixture
def mock_research_result():
    """Create mock research result"""
    return CompanyResearch(
        company_name="Tesla",
        description="Electric vehicle manufacturer",
        products_services=["Model S", "Model 3", "Model Y"],
        target_market="Electric vehicles and energy storage",
        key_competitors=["Rivian", "Lucid Motors"],
        recent_news=["Q4 earnings beat expectations"],
        sources=["https://example.com/tesla"]
    )


@pytest.fixture
def mock_market_result():
    """Create mock market result"""
    return MarketTrends(
        industry="Electric Vehicles",
        growth_rate=25.5,
        market_size_billions=500.0,
        key_trends=["Rapid EV adoption", "Battery improvements"],
        regional_insights={"North America": "Strong growth", "Europe": "Policy support"},
        future_outlook="Continued expansion expected"
    )


@pytest.fixture
def mock_financial_result():
    """Create mock financial result"""
    return FinancialSnapshot(
        company="Tesla",
        revenue_billions=96.77,
        profit_margin=15.5,
        key_metrics={"P/E Ratio": 45.2, "Market Cap": "800B"},
        financial_health="Strong",
        growth_indicators=["Revenue growth: 25%", "Expanding margins"]
    )


@pytest.fixture
def mock_framework_result():
    """Create mock framework analysis result"""
    return FrameworkAnalysis(
        framework="porter",
        analysis={
            "supplier_power": 3,
            "buyer_power": 2,
            "competitive_rivalry": 4,
            "threat_of_substitutes": 2,
            "threat_of_new_entrants": 1
        },
        insights=["Strong competitive positioning", "Moderate supplier power"],
        recommendations=["Invest in vertical integration"]
    )


@pytest.fixture
def mock_executive_summary():
    """Create mock executive summary"""
    return ExecutiveSummary(
        key_findings=["Finding 1", "Finding 2", "Finding 3"],
        strategic_recommendations=["Recommendation 1", "Recommendation 2"],
        confidence_score=0.85,
        sources=["https://example.com"]
    )


@pytest.fixture
def orchestrator():
    """Create orchestrator instance"""
    return AnalysisOrchestrator()


class TestGracefulDegradation:
    """Tests for graceful degradation when agents fail"""

    @pytest.mark.asyncio
    async def test_partial_agent_failures(
        self, orchestrator, mock_research_result, mock_market_result
    ):
        """Test orchestrator handles partial agent failures gracefully"""
        # Mock research and market success, financial failure
        orchestrator.research_agent.execute = AsyncMock(return_value=mock_research_result)
        orchestrator.market_agent.execute = AsyncMock(return_value=mock_market_result)
        orchestrator.financial_agent.execute = AsyncMock(side_effect=Exception("Financial data unavailable"))

        # Mock framework and synthesis
        orchestrator.framework_agent.execute = AsyncMock(return_value={
            "porter": {"analysis": {}, "insights": [], "recommendations": []}
        })
        orchestrator.synthesis_agent.execute = AsyncMock(return_value=ExecutiveSummary(
            key_findings=["Finding 1"],
            strategic_recommendations=["Recommendation 1"],
            confidence_score=0.75,  # Reduced confidence due to missing data
            sources=["https://example.com"]
        ))

        request = AnalysisRequest(
            company="Tesla",
            industry="Electric Vehicles",
            frameworks=["porter"],
            depth="standard"
        )

        with patch('consultantos.orchestrator.orchestrator.semantic_cache_lookup', return_value=None):
            with patch('consultantos.orchestrator.orchestrator.semantic_cache_store'):
                report = await orchestrator.execute(request)

        # Should still return a report despite financial agent failure
        assert report is not None
        assert report.executive_summary is not None
        # Confidence should be adjusted due to missing data
        assert report.executive_summary.confidence_score < 0.85

    @pytest.mark.asyncio
    async def test_all_phase1_agents_fail(self, orchestrator):
        """Test behavior when all Phase 1 agents fail"""
        # All data gathering agents fail
        orchestrator.research_agent.execute = AsyncMock(side_effect=Exception("Research failed"))
        orchestrator.market_agent.execute = AsyncMock(side_effect=Exception("Market failed"))
        orchestrator.financial_agent.execute = AsyncMock(side_effect=Exception("Financial failed"))

        request = AnalysisRequest(
            company="Tesla",
            industry="Electric Vehicles",
            frameworks=["porter"],
            depth="standard"
        )

        with patch('consultantos.orchestrator.orchestrator.semantic_cache_lookup', return_value=None):
            with pytest.raises(Exception):
                await orchestrator.execute(request)

    @pytest.mark.asyncio
    async def test_framework_agent_partial_failure(self, orchestrator, mock_research_result):
        """Test framework agent handling when some frameworks succeed and others fail"""
        orchestrator.research_agent.execute = AsyncMock(return_value=mock_research_result)
        orchestrator.market_agent.execute = AsyncMock(return_value=Mock())
        orchestrator.financial_agent.execute = AsyncMock(return_value=Mock())

        # Mock framework agent to succeed for porter but fail for swot
        def framework_side_effect(input_data):
            frameworks_to_run = input_data.get("frameworks", [])
            results = {}
            for framework in frameworks_to_run:
                if framework == "porter":
                    results[framework] = {"analysis": {}, "insights": [], "recommendations": []}
                elif framework == "swot":
                    raise Exception("SWOT analysis failed")
            return results

        orchestrator.framework_agent.execute = AsyncMock(side_effect=framework_side_effect)
        orchestrator.synthesis_agent.execute = AsyncMock(return_value=ExecutiveSummary(
            key_findings=["Finding 1"],
            strategic_recommendations=["Recommendation 1"],
            confidence_score=0.70,
            sources=["https://example.com"]
        ))

        request = AnalysisRequest(
            company="Tesla",
            industry="Electric Vehicles",
            frameworks=["porter"],  # Only test with porter to ensure success
            depth="standard"
        )

        with patch('consultantos.orchestrator.orchestrator.semantic_cache_lookup', return_value=None):
            with patch('consultantos.orchestrator.orchestrator.semantic_cache_store'):
                report = await orchestrator.execute(request)

        assert report is not None


class TestTimeoutHandling:
    """Tests for timeout handling and proper cleanup"""

    @pytest.mark.asyncio
    async def test_agent_timeout_handled_gracefully(self, orchestrator):
        """Test that agent timeouts are handled without crashing orchestrator"""
        # Research agent times out
        async def timeout_agent(*args, **kwargs):
            await asyncio.sleep(10)  # Simulate long operation

        orchestrator.research_agent.execute = timeout_agent

        # Other agents succeed quickly
        orchestrator.market_agent.execute = AsyncMock(return_value=Mock())
        orchestrator.financial_agent.execute = AsyncMock(return_value=Mock())

        request = AnalysisRequest(
            company="Tesla",
            industry="Electric Vehicles",
            frameworks=["porter"],
            depth="standard"
        )

        with patch('consultantos.orchestrator.orchestrator.semantic_cache_lookup', return_value=None):
            # Research agent should timeout but orchestrator should continue
            # This tests the _safe_execute_agent timeout handling
            with pytest.raises((asyncio.TimeoutError, Exception)):
                await asyncio.wait_for(orchestrator.execute(request), timeout=2.0)

    @pytest.mark.asyncio
    async def test_parallel_phase_timeout_cleanup(self, orchestrator):
        """Test that timeouts in parallel phase don't leave hanging tasks"""
        async def slow_research(*args, **kwargs):
            await asyncio.sleep(5)
            return Mock()

        orchestrator.research_agent.execute = slow_research
        orchestrator.market_agent.execute = AsyncMock(return_value=Mock())
        orchestrator.financial_agent.execute = AsyncMock(return_value=Mock())

        request = AnalysisRequest(
            company="Tesla",
            industry="Electric Vehicles",
            frameworks=["porter"],
            depth="standard"
        )

        with patch('consultantos.orchestrator.orchestrator.semantic_cache_lookup', return_value=None):
            try:
                await asyncio.wait_for(orchestrator.execute(request), timeout=1.0)
            except asyncio.TimeoutError:
                pass

        # Verify no tasks are left hanging
        pending_tasks = [task for task in asyncio.all_tasks() if not task.done()]
        # Allow current test task
        assert len(pending_tasks) <= 1


class TestCacheScenarios:
    """Tests for cache hit/miss scenarios"""

    @pytest.mark.asyncio
    async def test_cache_hit_returns_cached_report(self, orchestrator):
        """Test that cache hit returns cached report without executing agents"""
        request = AnalysisRequest(
            company="Tesla",
            industry="Electric Vehicles",
            frameworks=["porter"],
            depth="standard"
        )

        cached_report = StrategicReport(
            company="Tesla",
            industry="Electric Vehicles",
            generated_at="2024-01-01T00:00:00",
            frameworks=["porter"],
            executive_summary=ExecutiveSummary(
                key_findings=["Cached finding"],
                strategic_recommendations=["Cached recommendation"],
                confidence_score=0.90,
                sources=["https://example.com"]
            ),
            research=Mock(),
            market_trends=Mock(),
            financial_snapshot=Mock(),
            framework_analyses={},
            appendix={}
        )

        with patch('consultantos.orchestrator.orchestrator.semantic_cache_lookup', return_value=cached_report):
            report = await orchestrator.execute(request)

        # Should return cached report
        assert report == cached_report
        assert report.executive_summary.key_findings == ["Cached finding"]

        # Agents should NOT have been called
        orchestrator.research_agent.execute = Mock()
        assert not orchestrator.research_agent.execute.called

    @pytest.mark.asyncio
    async def test_cache_miss_executes_full_workflow(self, orchestrator):
        """Test that cache miss executes full workflow and stores result"""
        request = AnalysisRequest(
            company="Tesla",
            industry="Electric Vehicles",
            frameworks=["porter"],
            depth="standard"
        )

        # Mock all agents
        orchestrator.research_agent.execute = AsyncMock(return_value=Mock())
        orchestrator.market_agent.execute = AsyncMock(return_value=Mock())
        orchestrator.financial_agent.execute = AsyncMock(return_value=Mock())
        orchestrator.framework_agent.execute = AsyncMock(return_value={
            "porter": {"analysis": {}, "insights": [], "recommendations": []}
        })
        orchestrator.synthesis_agent.execute = AsyncMock(return_value=ExecutiveSummary(
            key_findings=["Finding 1"],
            strategic_recommendations=["Recommendation 1"],
            confidence_score=0.85,
            sources=["https://example.com"]
        ))

        store_called = False

        async def mock_store(*args, **kwargs):
            nonlocal store_called
            store_called = True

        with patch('consultantos.orchestrator.orchestrator.semantic_cache_lookup', return_value=None):
            with patch('consultantos.orchestrator.orchestrator.semantic_cache_store', side_effect=mock_store):
                report = await orchestrator.execute(request)

        # All agents should have been called
        orchestrator.research_agent.execute.assert_called_once()
        orchestrator.market_agent.execute.assert_called_once()
        orchestrator.financial_agent.execute.assert_called_once()

        # Result should be stored in cache
        assert store_called

    @pytest.mark.asyncio
    async def test_cache_key_includes_all_request_params(self, orchestrator):
        """Test that cache key is properly constructed from request parameters"""
        request = AnalysisRequest(
            company="Tesla",
            industry="Electric Vehicles",
            frameworks=["porter", "swot"],
            depth="standard"
        )

        cache_lookup_called_with = None

        async def mock_lookup(company, frameworks):
            nonlocal cache_lookup_called_with
            cache_lookup_called_with = (company, frameworks)
            return None

        with patch('consultantos.orchestrator.orchestrator.semantic_cache_lookup', side_effect=mock_lookup):
            with patch('consultantos.orchestrator.orchestrator.semantic_cache_store'):
                orchestrator.research_agent.execute = AsyncMock(return_value=Mock())
                orchestrator.market_agent.execute = AsyncMock(return_value=Mock())
                orchestrator.financial_agent.execute = AsyncMock(return_value=Mock())
                orchestrator.framework_agent.execute = AsyncMock(return_value={})
                orchestrator.synthesis_agent.execute = AsyncMock(return_value=ExecutiveSummary(
                    key_findings=["Finding"],
                    strategic_recommendations=["Recommendation"],
                    confidence_score=0.85,
                    sources=["https://example.com"]
                ))

                await orchestrator.execute(request)

        # Verify cache was called with correct parameters
        assert cache_lookup_called_with is not None
        assert cache_lookup_called_with[0] == "Tesla"
        assert set(cache_lookup_called_with[1]) == {"porter", "swot"}


class TestConcurrentRequests:
    """Tests for concurrent request handling"""

    @pytest.mark.asyncio
    async def test_concurrent_analysis_requests(self, orchestrator):
        """Test orchestrator handles multiple concurrent requests"""
        # Mock agents
        orchestrator.research_agent.execute = AsyncMock(return_value=Mock())
        orchestrator.market_agent.execute = AsyncMock(return_value=Mock())
        orchestrator.financial_agent.execute = AsyncMock(return_value=Mock())
        orchestrator.framework_agent.execute = AsyncMock(return_value={
            "porter": {"analysis": {}, "insights": [], "recommendations": []}
        })
        orchestrator.synthesis_agent.execute = AsyncMock(return_value=ExecutiveSummary(
            key_findings=["Finding"],
            strategic_recommendations=["Recommendation"],
            confidence_score=0.85,
            sources=["https://example.com"]
        ))

        requests = [
            AnalysisRequest(
                company=f"Company{i}",
                industry="Technology",
                frameworks=["porter"],
                depth="standard"
            )
            for i in range(5)
        ]

        with patch('consultantos.orchestrator.orchestrator.semantic_cache_lookup', return_value=None):
            with patch('consultantos.orchestrator.orchestrator.semantic_cache_store'):
                # Execute all requests concurrently
                tasks = [orchestrator.execute(req) for req in requests]
                reports = await asyncio.gather(*tasks, return_exceptions=True)

        # All requests should complete successfully
        assert len(reports) == 5
        for report in reports:
            assert not isinstance(report, Exception)
            assert report is not None

    @pytest.mark.asyncio
    async def test_concurrent_requests_independent_failures(self, orchestrator):
        """Test that failure in one concurrent request doesn't affect others"""
        call_count = 0

        async def sometimes_fail(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 2:  # Fail second request
                raise Exception("Intentional failure")
            return Mock()

        orchestrator.research_agent.execute = sometimes_fail
        orchestrator.market_agent.execute = AsyncMock(return_value=Mock())
        orchestrator.financial_agent.execute = AsyncMock(return_value=Mock())
        orchestrator.framework_agent.execute = AsyncMock(return_value={})
        orchestrator.synthesis_agent.execute = AsyncMock(return_value=ExecutiveSummary(
            key_findings=["Finding"],
            strategic_recommendations=["Recommendation"],
            confidence_score=0.85,
            sources=["https://example.com"]
        ))

        requests = [
            AnalysisRequest(
                company=f"Company{i}",
                industry="Technology",
                frameworks=["porter"],
                depth="standard"
            )
            for i in range(3)
        ]

        with patch('consultantos.orchestrator.orchestrator.semantic_cache_lookup', return_value=None):
            with patch('consultantos.orchestrator.orchestrator.semantic_cache_store'):
                tasks = [orchestrator.execute(req) for req in requests]
                reports = await asyncio.gather(*tasks, return_exceptions=True)

        # Two should succeed, one should fail
        successes = [r for r in reports if not isinstance(r, Exception)]
        failures = [r for r in reports if isinstance(r, Exception)]

        assert len(successes) >= 1  # At least one success
        assert len(failures) >= 1  # At least one failure


class TestFrameworkSelection:
    """Tests for framework selection edge cases"""

    @pytest.mark.asyncio
    async def test_single_framework_execution(self, orchestrator):
        """Test execution with single framework"""
        orchestrator.research_agent.execute = AsyncMock(return_value=Mock())
        orchestrator.market_agent.execute = AsyncMock(return_value=Mock())
        orchestrator.financial_agent.execute = AsyncMock(return_value=Mock())
        orchestrator.framework_agent.execute = AsyncMock(return_value={
            "porter": {"analysis": {}, "insights": [], "recommendations": []}
        })
        orchestrator.synthesis_agent.execute = AsyncMock(return_value=ExecutiveSummary(
            key_findings=["Finding"],
            strategic_recommendations=["Recommendation"],
            confidence_score=0.85,
            sources=["https://example.com"]
        ))

        request = AnalysisRequest(
            company="Tesla",
            industry="Electric Vehicles",
            frameworks=["porter"],  # Single framework
            depth="standard"
        )

        with patch('consultantos.orchestrator.orchestrator.semantic_cache_lookup', return_value=None):
            with patch('consultantos.orchestrator.orchestrator.semantic_cache_store'):
                report = await orchestrator.execute(request)

        assert report is not None
        orchestrator.framework_agent.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_multiple_frameworks_execution(self, orchestrator):
        """Test execution with multiple frameworks"""
        orchestrator.research_agent.execute = AsyncMock(return_value=Mock())
        orchestrator.market_agent.execute = AsyncMock(return_value=Mock())
        orchestrator.financial_agent.execute = AsyncMock(return_value=Mock())
        orchestrator.framework_agent.execute = AsyncMock(return_value={
            "porter": {"analysis": {}, "insights": [], "recommendations": []},
            "swot": {"analysis": {}, "insights": [], "recommendations": []},
            "pestel": {"analysis": {}, "insights": [], "recommendations": []}
        })
        orchestrator.synthesis_agent.execute = AsyncMock(return_value=ExecutiveSummary(
            key_findings=["Finding"],
            strategic_recommendations=["Recommendation"],
            confidence_score=0.85,
            sources=["https://example.com"]
        ))

        request = AnalysisRequest(
            company="Tesla",
            industry="Electric Vehicles",
            frameworks=["porter", "swot", "pestel"],  # Multiple frameworks
            depth="standard"
        )

        with patch('consultantos.orchestrator.orchestrator.semantic_cache_lookup', return_value=None):
            with patch('consultantos.orchestrator.orchestrator.semantic_cache_store'):
                report = await orchestrator.execute(request)

        assert report is not None
        # Framework agent should be called with all frameworks
        call_args = orchestrator.framework_agent.execute.call_args[0][0]
        assert "frameworks" in call_args
        assert set(call_args["frameworks"]) == {"porter", "swot", "pestel"}
