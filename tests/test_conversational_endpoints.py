"""
Tests for conversational API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
from consultantos.api.main import app
from consultantos.models.conversational import ConversationalResponse


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def mock_agent():
    """Mock conversational agent"""
    with patch('consultantos.api.conversational_endpoints.ConversationalAgent') as mock_class:
        mock_instance = MagicMock()
        mock_instance.execute = AsyncMock(return_value={
            "success": True,
            "data": {
                "response": "Tesla has strong competitive advantages.",
                "conversation_id": "conv_test_123",
                "sources": [],
                "routed_to_agent": None,
                "timestamp": "2025-11-09T12:00:00",
                "metadata": {"rag_enabled": True}
            },
            "error": None
        })
        mock_instance.retriever = MagicMock()
        mock_instance.retriever.index_document = AsyncMock(return_value="doc_123")
        mock_instance.retriever.count_documents = AsyncMock(return_value=10)
        mock_instance.retriever.embedding_generator = MagicMock()
        mock_instance.retriever.embedding_generator.model_name = "all-MiniLM-L6-v2"
        mock_instance.retriever.embedding_generator.get_embedding_dimension = MagicMock(return_value=384)
        mock_instance.retriever.vector_store = MagicMock()
        mock_instance.retriever.vector_store.collection_name = "consultantos_reports"

        mock_class.return_value = mock_instance
        yield mock_instance


class TestConversationalEndpoints:
    """Test conversational API endpoints"""

    def test_chat_endpoint(self, client, mock_agent):
        """Test /conversational/chat endpoint"""
        request_data = {
            "query": "What are Tesla's competitive advantages?",
            "conversation_id": "conv_test_123",
            "use_rag": True
        }

        response = client.post("/conversational/chat", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert data["conversation_id"] == "conv_test_123"
        assert "sources" in data

    def test_chat_endpoint_without_conversation_id(self, client, mock_agent):
        """Test chat endpoint generates conversation ID"""
        request_data = {
            "query": "What is competitive intelligence?"
        }

        response = client.post("/conversational/chat", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert "conversation_id" in data

    def test_chat_endpoint_with_rag_disabled(self, client, mock_agent):
        """Test chat endpoint with RAG disabled"""
        request_data = {
            "query": "Explain competitive intelligence",
            "use_rag": False
        }

        response = client.post("/conversational/chat", json=request_data)

        assert response.status_code == 200

    def test_chat_endpoint_with_filters(self, client, mock_agent):
        """Test chat endpoint with company/industry filters"""
        request_data = {
            "query": "What are the strengths?",
            "filter_company": "Tesla",
            "filter_industry": "Electric Vehicles"
        }

        response = client.post("/conversational/chat", json=request_data)

        assert response.status_code == 200

    def test_chat_endpoint_error_handling(self, client, mock_agent):
        """Test chat endpoint error handling"""
        # Mock agent to return error
        mock_agent.execute = AsyncMock(return_value={
            "success": False,
            "data": None,
            "error": "Agent execution failed"
        })

        request_data = {
            "query": "Test query"
        }

        response = client.post("/conversational/chat", json=request_data)

        assert response.status_code == 500

    def test_get_conversation_history(self, client):
        """Test /conversational/history/{conversation_id} endpoint"""
        with patch('consultantos.api.conversational_endpoints.get_db_service') as mock_db:
            # Mock Firestore response
            mock_db_instance = MagicMock()
            mock_doc = MagicMock()
            mock_doc.exists = True
            mock_doc.to_dict.return_value = {
                "conversation_id": "conv_test_123",
                "messages": [
                    {
                        "role": "user",
                        "content": "Test query",
                        "timestamp": "2025-11-09T12:00:00"
                    }
                ],
                "created_at": "2025-11-09T12:00:00",
                "updated_at": "2025-11-09T12:00:00"
            }
            mock_db_instance.collection.return_value.document.return_value.get.return_value = mock_doc
            mock_db.return_value = mock_db_instance

            response = client.get("/conversational/history/conv_test_123")

            assert response.status_code == 200
            data = response.json()
            assert "conversation" in data
            assert "message_count" in data

    def test_get_conversation_history_not_found(self, client):
        """Test getting non-existent conversation"""
        with patch('consultantos.api.conversational_endpoints.get_db_service') as mock_db:
            mock_db_instance = MagicMock()
            mock_doc = MagicMock()
            mock_doc.exists = False
            mock_db_instance.collection.return_value.document.return_value.get.return_value = mock_doc
            mock_db.return_value = mock_db_instance

            response = client.get("/conversational/history/nonexistent")

            assert response.status_code == 404

    def test_delete_conversation_history(self, client):
        """Test /conversational/history/{conversation_id} DELETE endpoint"""
        with patch('consultantos.api.conversational_endpoints.get_db_service') as mock_db:
            mock_db_instance = MagicMock()
            mock_doc = MagicMock()
            mock_doc.exists = True
            mock_db_instance.collection.return_value.document.return_value.get.return_value = mock_doc
            mock_db.return_value = mock_db_instance

            response = client.delete("/conversational/history/conv_test_123")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

    def test_delete_conversation_history_not_found(self, client):
        """Test deleting non-existent conversation"""
        with patch('consultantos.api.conversational_endpoints.get_db_service') as mock_db:
            mock_db_instance = MagicMock()
            mock_doc = MagicMock()
            mock_doc.exists = False
            mock_db_instance.collection.return_value.document.return_value.get.return_value = mock_doc
            mock_db.return_value = mock_db_instance

            response = client.delete("/conversational/history/nonexistent")

            assert response.status_code == 404

    def test_index_report_endpoint(self, client, mock_agent):
        """Test /conversational/index-report endpoint"""
        request_data = {
            "report_id": "report_tesla_2024",
            "content": "Tesla's competitive advantages include vertical integration.",
            "company": "Tesla",
            "industry": "Electric Vehicles",
            "report_type": "quarterly_analysis"
        }

        response = client.post(
            "/conversational/index-report",
            params=request_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["doc_id"] == "doc_123"

    def test_rag_stats_endpoint(self, client, mock_agent):
        """Test /conversational/rag-stats endpoint"""
        response = client.get("/conversational/rag-stats")

        assert response.status_code == 200
        data = response.json()
        assert "total_documents" in data
        assert "collection_name" in data
        assert "embedding_model" in data
        assert "embedding_dimension" in data
        assert data["total_documents"] == 10
