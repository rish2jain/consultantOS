"""
Vector store for RAG system using ChromaDB
Handles storage and retrieval of document embeddings
"""
import logging
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)


class VectorStore:
    """ChromaDB-based vector store for semantic search"""

    def __init__(
        self,
        collection_name: str = "consultantos_reports",
        persist_directory: Optional[str] = None
    ):
        """
        Initialize vector store

        Args:
            collection_name: Name of ChromaDB collection
            persist_directory: Directory to persist ChromaDB data (None = in-memory)
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self._client = None
        self._collection = None

    def _initialize_client(self):
        """Lazy initialize ChromaDB client"""
        if self._client is None:
            try:
                import chromadb
                from chromadb.config import Settings

                logger.info(f"Initializing ChromaDB client (persist_dir: {self.persist_directory})")

                if self.persist_directory:
                    # Persistent storage
                    self._client = chromadb.Client(Settings(
                        persist_directory=self.persist_directory,
                        anonymized_telemetry=False
                    ))
                else:
                    # In-memory storage (for development/testing)
                    self._client = chromadb.Client(Settings(
                        anonymized_telemetry=False
                    ))

                # Get or create collection
                self._collection = self._client.get_or_create_collection(
                    name=self.collection_name,
                    metadata={"hnsw:space": "cosine"}  # Use cosine similarity
                )

                logger.info(f"ChromaDB collection '{self.collection_name}' ready")

            except ImportError:
                logger.error("chromadb not installed. Run: pip install chromadb")
                raise
            except Exception as e:
                logger.error(f"Failed to initialize ChromaDB: {e}")
                raise

    async def add_document(
        self,
        content: str,
        embedding: List[float],
        metadata: Optional[Dict[str, Any]] = None,
        doc_id: Optional[str] = None
    ) -> str:
        """
        Add a document to the vector store

        Args:
            content: Document text content
            embedding: Pre-computed embedding vector
            metadata: Optional metadata (company, industry, report_type, etc.)
            doc_id: Optional document ID (auto-generated if not provided)

        Returns:
            Document ID
        """
        self._initialize_client()

        # Generate ID if not provided
        if doc_id is None:
            doc_id = str(uuid.uuid4())

        # Add timestamp to metadata
        if metadata is None:
            metadata = {}
        metadata["indexed_at"] = datetime.now().isoformat()

        # Add to collection
        self._collection.add(
            documents=[content],
            embeddings=[embedding],
            metadatas=[metadata],
            ids=[doc_id]
        )

        logger.debug(f"Added document {doc_id} to vector store")
        return doc_id

    async def add_documents_batch(
        self,
        contents: List[str],
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        doc_ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        Add multiple documents to vector store (batch operation)

        Args:
            contents: List of document texts
            embeddings: List of embedding vectors
            metadatas: Optional list of metadata dicts
            doc_ids: Optional list of document IDs

        Returns:
            List of document IDs
        """
        self._initialize_client()

        n_docs = len(contents)

        # Validate inputs
        if len(embeddings) != n_docs:
            raise ValueError(f"Mismatch: {n_docs} contents but {len(embeddings)} embeddings")

        # Generate IDs if not provided
        if doc_ids is None:
            doc_ids = [str(uuid.uuid4()) for _ in range(n_docs)]

        # Add timestamps to metadata
        if metadatas is None:
            metadatas = [{} for _ in range(n_docs)]

        timestamp = datetime.now().isoformat()
        for meta in metadatas:
            meta["indexed_at"] = timestamp

        # Batch add to collection
        self._collection.add(
            documents=contents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=doc_ids
        )

        logger.info(f"Added {n_docs} documents to vector store")
        return doc_ids

    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents using embedding

        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            filter_metadata: Optional metadata filter (e.g., {"company": "Tesla"})

        Returns:
            List of results with content, metadata, and distance
        """
        self._initialize_client()

        # Build query
        query_params = {
            "query_embeddings": [query_embedding],
            "n_results": top_k
        }

        if filter_metadata:
            query_params["where"] = filter_metadata

        # Execute search
        results = self._collection.query(**query_params)

        # Format results
        documents = []
        if results['documents'] and len(results['documents']) > 0:
            for i in range(len(results['documents'][0])):
                documents.append({
                    "content": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                    "distance": results['distances'][0][i] if results['distances'] else 0.0,
                    "id": results['ids'][0][i] if results['ids'] else None
                })

        logger.debug(f"Vector search returned {len(documents)} results")
        return documents

    async def delete_document(self, doc_id: str) -> bool:
        """
        Delete a document from vector store

        Args:
            doc_id: Document ID to delete

        Returns:
            True if deleted successfully
        """
        self._initialize_client()

        try:
            self._collection.delete(ids=[doc_id])
            logger.debug(f"Deleted document {doc_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete document {doc_id}: {e}")
            return False

    async def count_documents(self) -> int:
        """
        Get total number of documents in vector store

        Returns:
            Document count
        """
        self._initialize_client()
        return self._collection.count()

    async def clear_collection(self) -> bool:
        """
        Clear all documents from collection

        Returns:
            True if cleared successfully
        """
        self._initialize_client()

        try:
            # Delete and recreate collection
            self._client.delete_collection(name=self.collection_name)
            self._collection = self._client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Cleared collection '{self.collection_name}'")
            return True
        except Exception as e:
            logger.error(f"Failed to clear collection: {e}")
            return False
