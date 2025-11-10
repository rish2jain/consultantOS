"""
Tests for conversational AI agent with RAG
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from consultantos.agents.conversational_agent import ConversationalAgent
from consultantos.models.conversational import (
    ConversationalResponse,
    Message,
    MessageRole,
    SourceDocument
)
from consultantos.rag.retriever import DocumentResult
from consultantos.routing.query_classifier import AgentIntent


@pytest.fixture
def mock_retriever():
    """Mock RAG retriever"""
    retriever = MagicMock()
    retriever.retrieve = AsyncMock(return_value=[
        DocumentResult(
            content="Tesla's competitive advantages include vertical integration and battery technology.",
            metadata={
                "source": "report_tesla_2024",
                "company": "Tesla",
                "industry": "Electric Vehicles",
                "report_type": "quarterly_analysis"
            },
            distance=0.15,
            doc_id="doc_123"
        )
    ])
    retriever.index_document = AsyncMock(return_value="doc_123")
    retriever.count_documents = AsyncMock(return_value=10)
    return retriever


@pytest.fixture
def mock_router():
    """Mock agent router"""
    router = MagicMock()
    router.classify_query = AsyncMock(return_value=None)  # No routing by default
    router.execute_route = AsyncMock(return_value={
        "success": True,
        "data": {"summary": "Research analysis result"},
        "error": None
    })
    return router


@pytest.fixture
def agent(mock_retriever, mock_router):
    """Create conversational agent with mocked dependencies"""
    agent = ConversationalAgent(timeout=30)
    agent.retriever = mock_retriever
    agent.router = mock_router
    agent._db_service = None  # Disable Firestore for tests
    return agent


class TestConversationalAgent:
    """Test conversational agent functionality"""

    @pytest.mark.asyncio
    async def test_agent_initialization(self):
        """Test agent initializes correctly"""
        agent = ConversationalAgent(timeout=30)
        assert agent.name == "ConversationalAgent"
        assert agent.timeout == 30
        assert agent.retriever is not None
        assert agent.router is not None

    @pytest.mark.asyncio
    async def test_execute_with_rag(self, agent, mock_retriever):
        """Test conversational query with RAG"""
        input_data = {
            "query": "What are Tesla's competitive advantages?",
            "conversation_id": "test_conv_123",
            "use_rag": True
        }

        # Mock response generation
        with patch.object(agent, '_generate_response', new=AsyncMock(return_value="Tesla has strong competitive advantages including vertical integration.")):
            result = await agent.execute(input_data)

        assert result["success"] is True
        assert result["error"] is None
        assert "data" in result

        response_data = result["data"]
        assert "response" in response_data
        assert response_data["conversation_id"] == "test_conv_123"
        assert len(response_data["sources"]) > 0

        # Verify RAG retrieval was called
        mock_retriever.retrieve.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_without_rag(self, agent):
        """Test conversational query without RAG"""
        input_data = {
            "query": "What is competitive intelligence?",
            "conversation_id": "test_conv_456",
            "use_rag": False
        }

        # Mock response generation
        with patch.object(agent, '_generate_response', new=AsyncMock(return_value="Competitive intelligence is strategic information gathering.")):
            result = await agent.execute(input_data)

        assert result["success"] is True
        response_data = result["data"]
        assert response_data["conversation_id"] == "test_conv_456"
        assert len(response_data["sources"]) == 0

    @pytest.mark.asyncio
    async def test_execute_with_routing(self, agent, mock_router):
        """Test query routing to specialized agent"""
        input_data = {
            "query": "What are the latest financial results?",
            "conversation_id": "test_conv_789"
        }

        # Mock router to trigger routing
        mock_router.classify_query.return_value = AgentIntent.FINANCIAL

        result = await agent.execute(input_data)

        assert result["success"] is True
        response_data = result["data"]
        assert response_data["routed_to_agent"] == "financial"

        # Verify routing was called
        mock_router.classify_query.assert_called_once()
        mock_router.execute_route.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_empty_query(self, agent):
        """Test handling of empty query"""
        input_data = {
            "query": "",
            "conversation_id": "test_conv_empty"
        }

        result = await agent.execute(input_data)

        assert result["success"] is False
        assert "Query is required" in result["error"]

    @pytest.mark.asyncio
    async def test_execute_with_company_filter(self, agent, mock_retriever):
        """Test RAG with company filter"""
        input_data = {
            "query": "What are the strengths?",
            "conversation_id": "test_conv_filter",
            "use_rag": True,
            "filter_company": "Tesla"
        }

        with patch.object(agent, '_generate_response', new=AsyncMock(return_value="Tesla's strengths include...")):
            result = await agent.execute(input_data)

        assert result["success"] is True

        # Verify filter was passed to retriever
        call_args = mock_retriever.retrieve.call_args
        assert call_args[1]["filter_metadata"]["company"] == "Tesla"

    @pytest.mark.asyncio
    async def test_conversation_id_generation(self, agent):
        """Test automatic conversation ID generation"""
        input_data = {
            "query": "Test query",
            "use_rag": False
        }

        with patch.object(agent, '_generate_response', new=AsyncMock(return_value="Test response")):
            result = await agent.execute(input_data)

        assert result["success"] is True
        response_data = result["data"]
        assert response_data["conversation_id"].startswith("conv_")

    @pytest.mark.asyncio
    async def test_error_handling(self, agent):
        """Test error handling in agent execution"""
        input_data = {
            "query": "Test query",
            "conversation_id": "test_conv_error"
        }

        # Mock retriever to raise exception
        agent.retriever.retrieve = AsyncMock(side_effect=Exception("RAG failure"))

        with patch.object(agent, '_generate_response', new=AsyncMock(return_value="Fallback response")):
            # Should handle gracefully with fallback to direct query
            result = await agent.execute(input_data)

        assert result["success"] is True  # Graceful degradation

    @pytest.mark.asyncio
    async def test_build_rag_prompt(self, agent):
        """Test RAG prompt construction"""
        query = "What are Tesla's advantages?"
        relevant_docs = [
            DocumentResult(
                content="Tesla has vertical integration.",
                metadata={"source": "report_1", "company": "Tesla", "report_type": "analysis"},
                distance=0.1,
                doc_id="doc_1"
            )
        ]
        history = [
            Message(role=MessageRole.USER, content="Previous question"),
            Message(role=MessageRole.ASSISTANT, content="Previous answer")
        ]

        prompt = agent._build_rag_prompt(query, relevant_docs, history)

        assert "Relevant Context" in prompt
        assert "Tesla has vertical integration" in prompt
        assert "Recent Conversation" in prompt
        assert query in prompt

    @pytest.mark.asyncio
    async def test_format_agent_response(self, agent):
        """Test formatting of routed agent responses"""
        intent = AgentIntent.FINANCIAL
        agent_data = {"summary": "Financial analysis complete"}

        formatted = agent._format_agent_response(intent, agent_data)

        assert "FINANCIAL ANALYSIS" in formatted
        assert "Financial analysis complete" in formatted
