"""
RAG Retriever - combines embedding generation and vector search
"""
import logging
from typing import List, Dict, Any, Optional
from consultantos.rag.embeddings import EmbeddingGenerator
from consultantos.rag.vector_store import VectorStore

logger = logging.getLogger(__name__)


class DocumentResult:
    """Result from RAG retrieval"""

    def __init__(
        self,
        content: str,
        metadata: Dict[str, Any],
        distance: float,
        doc_id: Optional[str] = None
    ):
        self.content = content
        self.metadata = metadata
        self.distance = distance
        self.doc_id = doc_id
        self.source = metadata.get("source", "unknown")
        self.company = metadata.get("company", "")
        self.industry = metadata.get("industry", "")
        self.report_type = metadata.get("report_type", "")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "content": self.content,
            "metadata": self.metadata,
            "distance": self.distance,
            "doc_id": self.doc_id,
            "source": self.source
        }

    def __repr__(self) -> str:
        return f"DocumentResult(source={self.source}, distance={self.distance:.4f})"


class RAGRetriever:
    """
    Retrieval Augmented Generation retriever
    Combines embedding generation and vector search
    """

    def __init__(
        self,
        embedding_model: str = "all-MiniLM-L6-v2",
        collection_name: str = "consultantos_reports",
        persist_directory: Optional[str] = None
    ):
        """
        Initialize RAG retriever

        Args:
            embedding_model: Sentence transformer model name
            collection_name: ChromaDB collection name
            persist_directory: ChromaDB persistence directory
        """
        self.embedding_generator = EmbeddingGenerator(model_name=embedding_model)
        self.vector_store = VectorStore(
            collection_name=collection_name,
            persist_directory=persist_directory
        )

    async def retrieve(
        self,
        query: str,
        top_k: int = 3,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[DocumentResult]:
        """
        Retrieve relevant documents for a query

        Args:
            query: User query text
            top_k: Number of documents to retrieve
            filter_metadata: Optional metadata filter (e.g., {"company": "Tesla"})

        Returns:
            List of DocumentResult objects
        """
        logger.info(f"Retrieving top-{top_k} documents for query: {query[:100]}...")

        # Generate query embedding
        query_embedding = await self.embedding_generator.generate_embedding(query)

        if not query_embedding:
            logger.warning("Failed to generate query embedding")
            return []

        # Search vector store
        results = await self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
            filter_metadata=filter_metadata
        )

        # Convert to DocumentResult objects
        doc_results = [
            DocumentResult(
                content=r["content"],
                metadata=r["metadata"],
                distance=r["distance"],
                doc_id=r.get("id")
            )
            for r in results
        ]

        logger.info(f"Retrieved {len(doc_results)} documents")
        return doc_results

    async def index_document(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        doc_id: Optional[str] = None
    ) -> str:
        """
        Index a single document for future retrieval

        Args:
            content: Document text content
            metadata: Document metadata
            doc_id: Optional document ID

        Returns:
            Document ID
        """
        logger.info(f"Indexing document: {content[:100]}...")

        # Generate embedding
        embedding = await self.embedding_generator.generate_embedding(content)

        if not embedding:
            raise ValueError("Failed to generate embedding for document")

        # Add to vector store
        doc_id = await self.vector_store.add_document(
            content=content,
            embedding=embedding,
            metadata=metadata,
            doc_id=doc_id
        )

        logger.info(f"Indexed document with ID: {doc_id}")
        return doc_id

    async def index_documents_batch(
        self,
        contents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        doc_ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        Index multiple documents in batch

        Args:
            contents: List of document texts
            metadatas: List of metadata dicts
            doc_ids: Optional list of document IDs

        Returns:
            List of document IDs
        """
        logger.info(f"Batch indexing {len(contents)} documents...")

        # Generate embeddings in batch
        embeddings = await self.embedding_generator.generate_embeddings_batch(contents)

        if len(embeddings) != len(contents):
            raise ValueError("Embedding generation failed for some documents")

        # Add to vector store in batch
        doc_ids = await self.vector_store.add_documents_batch(
            contents=contents,
            embeddings=embeddings,
            metadatas=metadatas,
            doc_ids=doc_ids
        )

        logger.info(f"Batch indexed {len(doc_ids)} documents")
        return doc_ids

    async def delete_document(self, doc_id: str) -> bool:
        """
        Delete a document from index

        Args:
            doc_id: Document ID to delete

        Returns:
            True if deleted successfully
        """
        return await self.vector_store.delete_document(doc_id)

    async def count_documents(self) -> int:
        """Get total number of indexed documents"""
        return await self.vector_store.count_documents()

    async def clear_index(self) -> bool:
        """Clear all documents from index"""
        return await self.vector_store.clear_collection()
