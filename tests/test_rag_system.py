"""
Tests for RAG system (embeddings, vector store, retriever)
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from consultantos.rag.embeddings import EmbeddingGenerator
from consultantos.rag.vector_store import VectorStore
from consultantos.rag.retriever import RAGRetriever, DocumentResult


class TestEmbeddingGenerator:
    """Test embedding generation"""

    @pytest.mark.asyncio
    async def test_generate_embedding(self):
        """Test single text embedding generation"""
        generator = EmbeddingGenerator(model_name="all-MiniLM-L6-v2")

        # Mock the sentence transformer
        with patch.object(generator, '_load_model') as mock_load:
            mock_model = MagicMock()
            mock_model.encode.return_value = [0.1, 0.2, 0.3, 0.4]
            generator._model = mock_model

            embedding = await generator.generate_embedding("Test text")

            assert isinstance(embedding, list)
            assert len(embedding) == 4
            assert all(isinstance(x, (int, float)) for x in embedding)

    @pytest.mark.asyncio
    async def test_generate_embeddings_batch(self):
        """Test batch embedding generation"""
        generator = EmbeddingGenerator()

        with patch.object(generator, '_load_model'):
            mock_model = MagicMock()
            mock_model.encode.return_value = [[0.1, 0.2], [0.3, 0.4]]
            generator._model = mock_model

            texts = ["Text 1", "Text 2"]
            embeddings = await generator.generate_embeddings_batch(texts)

            assert len(embeddings) == 2
            assert all(isinstance(emb, list) for emb in embeddings)

    @pytest.mark.asyncio
    async def test_empty_text_handling(self):
        """Test handling of empty text"""
        generator = EmbeddingGenerator()

        embedding = await generator.generate_embedding("")

        assert embedding == []

    @pytest.mark.asyncio
    async def test_get_embedding_dimension(self):
        """Test getting embedding dimension"""
        generator = EmbeddingGenerator()

        with patch.object(generator, '_load_model'):
            mock_model = MagicMock()
            mock_model.get_sentence_embedding_dimension.return_value = 384
            generator._model = mock_model

            dimension = generator.get_embedding_dimension()

            assert dimension == 384


class TestVectorStore:
    """Test ChromaDB vector store"""

    @pytest.fixture
    def vector_store(self):
        """Create vector store with mocked ChromaDB"""
        store = VectorStore(collection_name="test_collection", persist_directory=None)

        # Mock ChromaDB client and collection
        mock_collection = MagicMock()
        mock_collection.add = MagicMock()
        mock_collection.query = MagicMock(return_value={
            "documents": [["Test document"]],
            "metadatas": [[{"source": "test"}]],
            "distances": [[0.1]],
            "ids": [["doc_1"]]
        })
        mock_collection.count = MagicMock(return_value=5)
        mock_collection.delete = MagicMock()

        store._collection = mock_collection
        store._client = MagicMock()

        return store

    @pytest.mark.asyncio
    async def test_add_document(self, vector_store):
        """Test adding single document"""
        doc_id = await vector_store.add_document(
            content="Test content",
            embedding=[0.1, 0.2, 0.3],
            metadata={"source": "test"}
        )

        assert doc_id is not None
        vector_store._collection.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_documents_batch(self, vector_store):
        """Test batch document addition"""
        contents = ["Doc 1", "Doc 2"]
        embeddings = [[0.1, 0.2], [0.3, 0.4]]
        metadatas = [{"source": "test1"}, {"source": "test2"}]

        doc_ids = await vector_store.add_documents_batch(
            contents=contents,
            embeddings=embeddings,
            metadatas=metadatas
        )

        assert len(doc_ids) == 2
        vector_store._collection.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_search(self, vector_store):
        """Test vector similarity search"""
        query_embedding = [0.1, 0.2, 0.3]

        results = await vector_store.search(
            query_embedding=query_embedding,
            top_k=3
        )

        assert len(results) > 0
        assert "content" in results[0]
        assert "metadata" in results[0]
        assert "distance" in results[0]

    @pytest.mark.asyncio
    async def test_search_with_filter(self, vector_store):
        """Test search with metadata filter"""
        query_embedding = [0.1, 0.2, 0.3]
        filter_metadata = {"company": "Tesla"}

        results = await vector_store.search(
            query_embedding=query_embedding,
            top_k=3,
            filter_metadata=filter_metadata
        )

        # Verify filter was passed
        call_args = vector_store._collection.query.call_args
        assert "where" in call_args[1]
        assert call_args[1]["where"] == filter_metadata

    @pytest.mark.asyncio
    async def test_delete_document(self, vector_store):
        """Test document deletion"""
        success = await vector_store.delete_document("doc_123")

        assert success is True
        vector_store._collection.delete.assert_called_once_with(ids=["doc_123"])

    @pytest.mark.asyncio
    async def test_count_documents(self, vector_store):
        """Test document count"""
        count = await vector_store.count_documents()

        assert count == 5


class TestRAGRetriever:
    """Test RAG retriever"""

    @pytest.fixture
    def retriever(self):
        """Create RAG retriever with mocked components"""
        retriever = RAGRetriever(
            embedding_model="all-MiniLM-L6-v2",
            collection_name="test_collection",
            persist_directory=None
        )

        # Mock embedding generator
        mock_embedding_gen = MagicMock()
        mock_embedding_gen.generate_embedding = AsyncMock(return_value=[0.1, 0.2, 0.3])
        mock_embedding_gen.generate_embeddings_batch = AsyncMock(return_value=[[0.1, 0.2], [0.3, 0.4]])
        retriever.embedding_generator = mock_embedding_gen

        # Mock vector store
        mock_vector_store = MagicMock()
        mock_vector_store.search = AsyncMock(return_value=[
            {
                "content": "Test document",
                "metadata": {"source": "test", "company": "Tesla"},
                "distance": 0.1,
                "id": "doc_1"
            }
        ])
        mock_vector_store.add_document = AsyncMock(return_value="doc_123")
        mock_vector_store.add_documents_batch = AsyncMock(return_value=["doc_1", "doc_2"])
        mock_vector_store.count_documents = AsyncMock(return_value=10)
        retriever.vector_store = mock_vector_store

        return retriever

    @pytest.mark.asyncio
    async def test_retrieve(self, retriever):
        """Test document retrieval"""
        query = "What are Tesla's advantages?"

        results = await retriever.retrieve(query, top_k=3)

        assert len(results) > 0
        assert isinstance(results[0], DocumentResult)
        assert results[0].content == "Test document"
        assert results[0].source == "test"

    @pytest.mark.asyncio
    async def test_retrieve_with_filter(self, retriever):
        """Test retrieval with metadata filter"""
        query = "What are the strengths?"
        filter_metadata = {"company": "Tesla"}

        results = await retriever.retrieve(
            query=query,
            top_k=3,
            filter_metadata=filter_metadata
        )

        # Verify filter was passed to vector store
        call_args = retriever.vector_store.search.call_args
        assert call_args[1]["filter_metadata"] == filter_metadata

    @pytest.mark.asyncio
    async def test_index_document(self, retriever):
        """Test single document indexing"""
        content = "Test document content"
        metadata = {"source": "test_report", "company": "Tesla"}

        doc_id = await retriever.index_document(
            content=content,
            metadata=metadata
        )

        assert doc_id == "doc_123"
        retriever.embedding_generator.generate_embedding.assert_called_once_with(content)
        retriever.vector_store.add_document.assert_called_once()

    @pytest.mark.asyncio
    async def test_index_documents_batch(self, retriever):
        """Test batch document indexing"""
        contents = ["Doc 1", "Doc 2"]
        metadatas = [{"source": "test1"}, {"source": "test2"}]

        doc_ids = await retriever.index_documents_batch(
            contents=contents,
            metadatas=metadatas
        )

        assert len(doc_ids) == 2
        retriever.embedding_generator.generate_embeddings_batch.assert_called_once()
        retriever.vector_store.add_documents_batch.assert_called_once()

    @pytest.mark.asyncio
    async def test_count_documents(self, retriever):
        """Test document count"""
        count = await retriever.count_documents()

        assert count == 10
