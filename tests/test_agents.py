"""
Tests for agent implementations using VCR for API mocking
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from consultantos.agents import (
    ResearchAgent,
    MarketAgent,
    FinancialAgent,
    FrameworkAgent,
    SynthesisAgent
)
from consultantos.models import (
    CompanyResearch,
    MarketTrends,
    FinancialSnapshot,
    FrameworkAnalysis,
    ExecutiveSummary
)
import asyncio
# VCR imports - can be used when cassettes are properly recorded
# from tests.conftest import use_cassette


class TestResearchAgent:
    """Tests for Research Agent with VCR infrastructure ready"""

    @pytest.mark.asyncio
    async def test_research_agent_execution(self, tesla_test_data):
        """
        Test research agent execution.

        VCR Ready: Add @use_cassette("research_agent_tesla_execution") when cassette recorded
        """
        agent = ResearchAgent()

        # Mock Tavily API calls (can be replaced with VCR cassette)
        with patch('consultantos.agents.research_agent.tavily_search_tool') as mock_tavily:
            mock_tavily.return_value = {
                "results": [
                    {"title": "Tesla Overview", "url": "https://www.tesla.com", "content": "Tesla Inc."}
                ],
                "query": "Tesla",
                "total_results": 1
            }

            # Mock Gemini structured client
            mock_result = CompanyResearch(
                company_name="Tesla",
                description="Electric vehicle and clean energy company",
                products_services=["Model S", "Model 3", "Model X", "Model Y"],
                target_market="Electric vehicles",
                key_competitors=["Rivian", "Lucid Motors"],
                recent_news=["Tesla Q4 deliveries"],
                sources=["https://www.tesla.com"]
            )

            mock_chat = Mock()
            mock_chat.completions.create = Mock(return_value=mock_result)
            agent.structured_client = Mock()
            agent.structured_client.chat = mock_chat

            result = await agent.execute(tesla_test_data)

            assert result.company_name == "Tesla"
            assert len(result.products_services) > 0
            assert len(result.key_competitors) > 0

    @pytest.mark.asyncio
    async def test_research_agent_apple(self, apple_test_data):
        """
        Test research agent with Apple data.

        VCR Ready: Add @use_cassette("research_agent_apple_execution") when cassette recorded
        """
        agent = ResearchAgent()

        with patch('consultantos.agents.research_agent.tavily_search_tool') as mock_tavily:
            mock_tavily.return_value = {
                "results": [{"title": "Apple Inc", "url": "https://www.apple.com", "content": "Apple"}],
                "query": "Apple",
                "total_results": 1
            }

            mock_result = CompanyResearch(
                company_name="Apple",
                description="Technology company specializing in consumer electronics",
                products_services=["iPhone", "iPad", "Mac"],
                target_market="Consumer electronics",
                key_competitors=["Samsung", "Google"],
                recent_news=["Apple Vision Pro"],
                sources=["https://www.apple.com"]
            )

            mock_chat = Mock()
            mock_chat.completions.create = Mock(return_value=mock_result)
            agent.structured_client = Mock()
            agent.structured_client.chat = mock_chat

            result = await agent.execute(apple_test_data)

            assert result.company_name == "Apple"
            assert len(result.products_services) > 0

    @pytest.mark.asyncio
    async def test_research_agent_timeout(self):
        """Test research agent timeout handling (no VCR needed)"""
        agent = ResearchAgent(timeout=1)  # Very short timeout

        with patch('consultantos.agents.research_agent.tavily_search_tool') as mock_search:
            mock_search.return_value = {"results": [], "query": "Tesla", "total_results": 0}

            # Mock the structured client to simulate timeout by making _execute_internal take too long
            original_execute_internal = agent._execute_internal

            async def slow_execute_internal(*args, **kwargs):
                await asyncio.sleep(2)  # Sleep longer than timeout (1 second)
                return original_execute_internal(*args, **kwargs)

            agent._execute_internal = slow_execute_internal

            with pytest.raises(asyncio.TimeoutError):  # Should timeout
                await agent.execute({"company": "Tesla"})


class TestFinancialAgent:
    """Tests for Financial Agent with VCR infrastructure ready"""

    @pytest.mark.asyncio
    async def test_financial_agent_execution(self, tesla_test_data):
        """
        Test financial agent execution.

        VCR Ready: Add @use_cassette("financial_agent_tesla_execution") when cassette recorded
        """
        agent = FinancialAgent()

        # Mock financial tools (can be replaced with VCR cassette)
        with patch('consultantos.agents.financial_agent.yfinance_tool') as mock_yf, \
             patch('consultantos.agents.financial_agent.sec_edgar_tool') as mock_sec:

            mock_yf.return_value = {
                "company_info": {"marketCap": 800000000000, "totalRevenue": 96000000000},
                "ticker": "TSLA"
            }
            mock_sec.return_value = {"filing_date": "2024-01-01", "ticker": "TSLA"}

            mock_result = FinancialSnapshot(
                ticker="TSLA",
                market_cap=800000000000,
                revenue=96000000000,
                revenue_growth=0.19,
                profit_margin=0.15,
                pe_ratio=65.0,
                key_metrics={},
                risk_assessment="Medium"
            )

            mock_chat = Mock()
            mock_chat.completions.create = Mock(return_value=mock_result)
            agent.structured_client = Mock()
            agent.structured_client.chat = mock_chat

            result = await agent.execute(tesla_test_data)

            assert result.ticker == "TSLA"
            assert result.market_cap > 0

    @pytest.mark.asyncio
    async def test_financial_agent_apple(self, apple_test_data):
        """
        Test financial agent with Apple data.

        VCR Ready: Add @use_cassette("financial_agent_apple_execution") when cassette recorded
        """
        agent = FinancialAgent()

        with patch('consultantos.agents.financial_agent.yfinance_tool') as mock_yf, \
             patch('consultantos.agents.financial_agent.sec_edgar_tool') as mock_sec:

            mock_yf.return_value = {
                "company_info": {"marketCap": 3000000000000, "totalRevenue": 394000000000},
                "ticker": "AAPL"
            }
            mock_sec.return_value = {"filing_date": "2024-01-01", "ticker": "AAPL"}

            mock_result = FinancialSnapshot(
                ticker="AAPL",
                market_cap=3000000000000,
                revenue=394000000000,
                revenue_growth=0.08,
                profit_margin=0.26,
                pe_ratio=30.0,
                key_metrics={},
                risk_assessment="Low"
            )

            mock_chat = Mock()
            mock_chat.completions.create = Mock(return_value=mock_result)
            agent.structured_client = Mock()
            agent.structured_client.chat = mock_chat

            result = await agent.execute(apple_test_data)

            assert result.ticker == "AAPL"
            assert result.market_cap > 0

    @pytest.mark.asyncio
    async def test_financial_agent_microsoft(self, microsoft_test_data):
        """
        Test financial agent with Microsoft data.

        VCR Ready: Add @use_cassette("financial_agent_microsoft_execution") when cassette recorded
        """
        agent = FinancialAgent()

        with patch('consultantos.agents.financial_agent.yfinance_tool') as mock_yf, \
             patch('consultantos.agents.financial_agent.sec_edgar_tool') as mock_sec:

            mock_yf.return_value = {
                "company_info": {"marketCap": 2800000000000, "totalRevenue": 211000000000},
                "ticker": "MSFT"
            }
            mock_sec.return_value = {"filing_date": "2024-01-01", "ticker": "MSFT"}

            mock_result = FinancialSnapshot(
                ticker="MSFT",
                market_cap=2800000000000,
                revenue=211000000000,
                revenue_growth=0.12,
                profit_margin=0.34,
                pe_ratio=35.0,
                key_metrics={},
                risk_assessment="Low"
            )

            mock_chat = Mock()
            mock_chat.completions.create = Mock(return_value=mock_result)
            agent.structured_client = Mock()
            agent.structured_client.chat = mock_chat

            result = await agent.execute(microsoft_test_data)

            assert result.ticker == "MSFT"
            assert result.market_cap > 0


class TestMarketAgent:
    """Tests for Market Agent with VCR infrastructure ready"""

    @pytest.mark.asyncio
    async def test_market_agent_execution(self, tesla_test_data):
        """
        Test market agent execution.

        VCR Ready: Add @use_cassette("market_agent_tesla_execution") when cassette recorded
        """
        agent = MarketAgent()

        # Mock trends tool (can be replaced with VCR cassette)
        with patch('consultantos.agents.market_agent.google_trends_tool') as mock_trends:
            mock_trends.return_value = {
                "search_interest_trend": "Growing",
                "interest_data": {"2024-01": 85},
                "geographic_distribution": {},
                "related_queries": {},
                "keywords_analyzed": ["Tesla"]
            }

            mock_result = MarketTrends(
                search_interest_trend="Growing",
                interest_data={"2024-01": 85},
                geographic_distribution={},
                related_searches=[],
                competitive_comparison={}
            )

            mock_chat = Mock()
            mock_chat.completions.create = Mock(return_value=mock_result)
            agent.structured_client = Mock()
            agent.structured_client.chat = mock_chat

            result = await agent.execute(tesla_test_data)

            assert result.search_interest_trend == "Growing"

    @pytest.mark.asyncio
    async def test_market_agent_apple(self, apple_test_data):
        """
        Test market agent with Apple data.

        VCR Ready: Add @use_cassette("market_agent_apple_execution") when cassette recorded
        """
        agent = MarketAgent()

        with patch('consultantos.agents.market_agent.google_trends_tool') as mock_trends:
            mock_trends.return_value = {
                "search_interest_trend": "Stable",
                "interest_data": {},
                "geographic_distribution": {},
                "related_queries": {},
                "keywords_analyzed": ["Apple"]
            }

            mock_result = MarketTrends(
                search_interest_trend="Stable",
                interest_data={},
                geographic_distribution={},
                related_searches=[],
                competitive_comparison={}
            )

            mock_chat = Mock()
            mock_chat.completions.create = Mock(return_value=mock_result)
            agent.structured_client = Mock()
            agent.structured_client.chat = mock_chat

            result = await agent.execute(apple_test_data)

            assert result.search_interest_trend in ["Stable", "Growing", "Declining"]

    @pytest.mark.asyncio
    async def test_market_agent_microsoft(self, microsoft_test_data):
        """
        Test market agent with Microsoft data.

        VCR Ready: Add @use_cassette("market_agent_microsoft_execution") when cassette recorded
        """
        agent = MarketAgent()

        with patch('consultantos.agents.market_agent.google_trends_tool') as mock_trends:
            mock_trends.return_value = {
                "search_interest_trend": "Growing",
                "interest_data": {},
                "geographic_distribution": {},
                "related_queries": {},
                "keywords_analyzed": ["Microsoft"]
            }

            mock_result = MarketTrends(
                search_interest_trend="Growing",
                interest_data={},
                geographic_distribution={},
                related_searches=[],
                competitive_comparison={}
            )

            mock_chat = Mock()
            mock_chat.completions.create = Mock(return_value=mock_result)
            agent.structured_client = Mock()
            agent.structured_client.chat = mock_chat

            result = await agent.execute(microsoft_test_data)

            assert result.search_interest_trend in ["Stable", "Growing", "Declining"]


class TestOrchestrator:
    """Tests for Orchestrator"""

    @pytest.mark.asyncio
    async def test_orchestrator_partial_results(self):
        """Test orchestrator handles partial results"""
        from consultantos.orchestrator import AnalysisOrchestrator
        from consultantos.models import AnalysisRequest

        orchestrator = AnalysisOrchestrator()

        # Mock agents to return partial results
        with patch.object(orchestrator.research_agent, 'execute', new_callable=AsyncMock) as mock_research, \
             patch.object(orchestrator.market_agent, 'execute', new_callable=AsyncMock) as mock_market, \
             patch.object(orchestrator.financial_agent, 'execute', new_callable=AsyncMock) as mock_financial:

            # Research succeeds, market fails, financial succeeds
            mock_research.return_value = CompanyResearch(
                company_name="Tesla",
                description="Test",
                products_services=[],
                target_market="",
                key_competitors=[],
                recent_news=[],
                sources=[]
            )
            # Market fails - return None to simulate failure
            mock_market.return_value = None
            mock_financial.return_value = FinancialSnapshot(
                ticker="TSLA",
                market_cap=1000000,
                revenue=500000,
                revenue_growth=None,
                profit_margin=0.1,
                pe_ratio=50.0,
                key_metrics={},
                risk_assessment="Medium"
            )

            # Mock framework and synthesis agents
            with patch.object(orchestrator.framework_agent, 'execute', new_callable=AsyncMock) as mock_framework, \
                 patch.object(orchestrator.synthesis_agent, 'execute', new_callable=AsyncMock) as mock_synthesis:

                mock_framework.return_value = FrameworkAnalysis()
                # Provide at least 3 next_steps for recommendations
                mock_synthesis.return_value = ExecutiveSummary(
                    company_name="Tesla",
                    industry="Electric Vehicles",
                    key_findings=["Test finding 1", "Test finding 2", "Test finding 3"],
                    strategic_recommendation="Test recommendation",
                    confidence_score=0.8,
                    supporting_evidence=[],
                    next_steps=["Step 1", "Step 2", "Step 3", "Step 4"]
                )

                request = AnalysisRequest(
                    company="Tesla",
                    industry="Electric Vehicles",
                    frameworks=["porter"]
                )

                # Should not raise exception even with partial results
                report = await orchestrator.execute(request)

                assert report is not None
                assert report.company_research is not None
                assert report.market_trends is None  # Failed agent
                assert report.financial_snapshot is not None
