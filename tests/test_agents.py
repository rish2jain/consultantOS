"""
Tests for agent implementations
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


class TestResearchAgent:
    """Tests for Research Agent"""
    
    @pytest.mark.asyncio
    async def test_research_agent_execution(self):
        """Test research agent execution"""
        agent = ResearchAgent()
        
        # Mock tavily search
        with patch('consultantos.agents.research_agent.tavily_search_tool') as mock_search:
            mock_search.return_value = {
                "results": [
                    {
                        "title": "Tesla Company Overview",
                        "url": "https://example.com/tesla",
                        "content": "Tesla is an electric vehicle company..."
                    }
                ],
                "query": "Tesla",
                "total_results": 1
            }
            
            # Mock structured client
            mock_result = CompanyResearch(
                company_name="Tesla",
                description="Electric vehicle manufacturer",
                products_services=["Model S", "Model 3"],
                target_market="Electric vehicles",
                key_competitors=["Rivian", "Lucid"],
                recent_news=[],
                sources=["https://example.com/tesla"]
            )
            
            # Mock the structured client to return result directly
            mock_chat = Mock()
            mock_chat.completions.create = Mock(return_value=mock_result)
            agent.structured_client = Mock()
            agent.structured_client.chat = mock_chat
            
            result = await agent.execute({"company": "Tesla"})
            
            assert result.company_name == "Tesla"
            assert len(result.products_services) > 0
    
    @pytest.mark.asyncio
    async def test_research_agent_timeout(self):
        """Test research agent timeout handling"""
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
    """Tests for Financial Agent"""
    
    @pytest.mark.asyncio
    async def test_financial_agent_execution(self):
        """Test financial agent execution"""
        agent = FinancialAgent()
        
        # Mock financial tools
        with patch('consultantos.agents.financial_agent.yfinance_tool') as mock_yf, \
             patch('consultantos.agents.financial_agent.sec_edgar_tool') as mock_sec:
            
            mock_yf.return_value = {
                "company_info": {
                    "marketCap": 1000000000,
                    "totalRevenue": 500000000,
                    "profitMargins": 0.15,
                    "trailingPE": 50.0
                },
                "ticker": "TSLA"
            }
            mock_sec.return_value = {"filing_date": "2024-01-01", "ticker": "TSLA"}
            
            # Mock structured client
            mock_result = FinancialSnapshot(
                ticker="TSLA",
                market_cap=1000000000,
                revenue=500000000,
                revenue_growth=0.2,
                profit_margin=0.15,
                pe_ratio=50.0,
                key_metrics={},
                risk_assessment="Low - Strong financials"
            )
            
            # Mock the structured client to return result directly
            mock_chat = Mock()
            mock_chat.completions.create = Mock(return_value=mock_result)
            agent.structured_client = Mock()
            agent.structured_client.chat = mock_chat
            
            result = await agent.execute({"company": "Tesla", "ticker": "TSLA"})
            
            assert result.ticker == "TSLA"
            assert result.market_cap == 1000000000


class TestMarketAgent:
    """Tests for Market Agent"""
    
    @pytest.mark.asyncio
    async def test_market_agent_execution(self):
        """Test market agent execution"""
        agent = MarketAgent()
        
        # Mock trends tool
        with patch('consultantos.agents.market_agent.google_trends_tool') as mock_trends:
            mock_trends.return_value = {
                "search_interest_trend": "Growing",
                "interest_data": {},
                "geographic_distribution": {},
                "related_queries": {},
                "keywords_analyzed": ["Tesla"]
            }
            
            # Mock structured client
            mock_result = MarketTrends(
                search_interest_trend="Growing",
                interest_data={},
                geographic_distribution={},
                related_searches=[],
                competitive_comparison={}
            )
            
            # Mock the structured client to return result directly
            mock_chat = Mock()
            mock_chat.completions.create = Mock(return_value=mock_result)
            agent.structured_client = Mock()
            agent.structured_client.chat = mock_chat
            
            result = await agent.execute({"company": "Tesla", "industry": "Electric Vehicles"})
            
            assert result.search_interest_trend == "Growing"


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

