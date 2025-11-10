"""
Tests for query routing system
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from consultantos.routing.query_classifier import QueryClassifier, AgentIntent
from consultantos.routing.agent_router import AgentRouter


class TestQueryClassifier:
    """Test query intent classification"""

    @pytest.fixture
    def classifier(self):
        """Create query classifier"""
        return QueryClassifier()

    def test_classify_research_query(self, classifier):
        """Test classification of research query"""
        query = "Research and investigate the latest information about Tesla's new products"

        intent = classifier.classify(query)

        assert intent == AgentIntent.RESEARCH

    def test_classify_market_query(self, classifier):
        """Test classification of market analysis query"""
        query = "What are the current market trends in electric vehicles?"

        intent = classifier.classify(query)

        assert intent == AgentIntent.MARKET

    def test_classify_financial_query(self, classifier):
        """Test classification of financial query"""
        query = "What is Tesla's revenue and earnings performance?"

        intent = classifier.classify(query)

        assert intent == AgentIntent.FINANCIAL

    def test_classify_forecasting_query(self, classifier):
        """Test classification of forecasting query"""
        query = "Predict Tesla's revenue for next quarter"

        intent = classifier.classify(query)

        assert intent == AgentIntent.FORECASTING

    def test_classify_social_media_query(self, classifier):
        """Test classification of social media query"""
        query = "What is the sentiment on Twitter about Tesla?"

        intent = classifier.classify(query)

        assert intent == AgentIntent.SOCIAL_MEDIA

    def test_classify_framework_query(self, classifier):
        """Test classification of framework analysis query"""
        query = "Apply Porter's Five Forces to analyze Tesla's competitive position"

        intent = classifier.classify(query)

        assert intent == AgentIntent.FRAMEWORK

    def test_classify_general_query(self, classifier):
        """Test classification of general query (no routing)"""
        query = "Tell me about competitive intelligence"

        intent = classifier.classify(query)

        assert intent == AgentIntent.GENERAL

    def test_classify_empty_query(self, classifier):
        """Test classification of empty query"""
        query = ""

        intent = classifier.classify(query)

        assert intent == AgentIntent.GENERAL

    def test_get_routing_metadata(self, classifier):
        """Test getting routing metadata"""
        query = "What are Tesla's financial results?"

        metadata = classifier.get_routing_metadata(query)

        assert "intent" in metadata
        assert "confidence" in metadata
        assert "matched_keywords" in metadata
        assert "route_to_agent" in metadata
        assert metadata["intent"] == "financial"
        assert len(metadata["matched_keywords"]) > 0

    def test_multiple_keyword_matches(self, classifier):
        """Test query with multiple matching keywords"""
        query = "Research the latest financial performance and revenue trends"

        # Should match both research and financial keywords
        # Classifier should choose highest scoring intent
        intent = classifier.classify(query)

        # Either research or financial is acceptable
        assert intent in [AgentIntent.RESEARCH, AgentIntent.FINANCIAL]


class TestAgentRouter:
    """Test agent routing"""

    @pytest.fixture
    def router(self):
        """Create agent router"""
        return AgentRouter()

    @pytest.mark.asyncio
    async def test_classify_query(self, router):
        """Test query classification for routing"""
        query = "Find the latest news about Tesla"

        intent = await router.classify_query(query)

        assert intent == AgentIntent.RESEARCH

    @pytest.mark.asyncio
    async def test_classify_general_query_returns_none(self, router):
        """Test that general queries return None (no routing)"""
        query = "What is competitive intelligence?"

        intent = await router.classify_query(query)

        assert intent is None

    @pytest.mark.asyncio
    async def test_execute_route_to_research(self, router):
        """Test routing to research agent"""
        with patch('consultantos.agents.research_agent.ResearchAgent') as mock_agent_class:
            mock_agent = MagicMock()
            mock_agent.execute = AsyncMock(return_value={
                "success": True,
                "data": {"summary": "Research results"},
                "error": None
            })
            mock_agent_class.return_value = mock_agent

            result = await router.execute_route(
                intent=AgentIntent.RESEARCH,
                query="Research Tesla",
                input_data={}
            )

            assert result["success"] is True
            assert "summary" in result["data"]
            mock_agent.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_route_to_market(self, router):
        """Test routing to market agent"""
        with patch('consultantos.agents.market_agent.MarketAgent') as mock_agent_class:
            mock_agent = MagicMock()
            mock_agent.execute = AsyncMock(return_value={
                "success": True,
                "data": {"trends": []},
                "error": None
            })
            mock_agent_class.return_value = mock_agent

            result = await router.execute_route(
                intent=AgentIntent.MARKET,
                query="Market trends",
                input_data={}
            )

            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_execute_route_to_financial(self, router):
        """Test routing to financial agent"""
        with patch('consultantos.agents.financial_agent.FinancialAgent') as mock_agent_class:
            mock_agent = MagicMock()
            mock_agent.execute = AsyncMock(return_value={
                "success": True,
                "data": {"financials": {}},
                "error": None
            })
            mock_agent_class.return_value = mock_agent

            result = await router.execute_route(
                intent=AgentIntent.FINANCIAL,
                query="Financial data",
                input_data={}
            )

            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_execute_route_to_unimplemented_agent(self, router):
        """Test routing to unimplemented agent"""
        result = await router.execute_route(
            intent=AgentIntent.SOCIAL_MEDIA,
            query="Social media sentiment",
            input_data={}
        )

        # Should return error for unimplemented agent
        assert result["success"] is False
        assert "coming soon" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_execute_route_error_handling(self, router):
        """Test error handling in routing"""
        with patch('consultantos.agents.research_agent.ResearchAgent') as mock_agent_class:
            mock_agent = MagicMock()
            mock_agent.execute = AsyncMock(side_effect=Exception("Agent failed"))
            mock_agent_class.return_value = mock_agent

            result = await router.execute_route(
                intent=AgentIntent.RESEARCH,
                query="Test query",
                input_data={}
            )

            assert result["success"] is False
            assert "failed" in result["error"].lower()

    def test_get_routing_info(self, router):
        """Test getting routing information"""
        query = "What are the latest financial results?"

        info = router.get_routing_info(query)

        assert "intent" in info
        assert "confidence" in info
        assert "route_to_agent" in info
