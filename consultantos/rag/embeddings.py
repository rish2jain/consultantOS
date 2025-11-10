"""
Embedding generation for RAG system
Uses sentence-transformers for creating semantic embeddings
"""
import logging
from typing import List, Optional
import asyncio

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Generate embeddings for text using sentence-transformers"""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize embedding generator

        Args:
            model_name: HuggingFace model name for embeddings
                       Default: all-MiniLM-L6-v2 (384 dimensions, fast, good quality)
        """
        self.model_name = model_name
        self._model = None

    def _load_model(self):
        """Lazy load the sentence transformer model"""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"Loading embedding model: {self.model_name}")
                self._model = SentenceTransformer(self.model_name)
                logger.info(f"Embedding model loaded successfully")
            except ImportError:
                logger.error("sentence-transformers not installed. Run: pip install sentence-transformers")
                raise
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                raise

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text

        Args:
            text: Input text to embed

        Returns:
            List of floats representing the embedding vector
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding")
            return []

        self._load_model()

        # Run embedding in thread pool to avoid blocking
        def _encode():
            return self._model.encode(text, convert_to_numpy=True).tolist()

        embedding = await asyncio.to_thread(_encode)
        return embedding

    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (batch processing)

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        if not texts:
            logger.warning("Empty text list provided for batch embedding")
            return []

        self._load_model()

        # Filter out empty texts
        valid_texts = [t for t in texts if t and t.strip()]
        if len(valid_texts) != len(texts):
            logger.warning(f"Filtered out {len(texts) - len(valid_texts)} empty texts")

        if not valid_texts:
            return []

        # Run batch embedding in thread pool
        def _encode_batch():
            embeddings = self._model.encode(valid_texts, convert_to_numpy=True)
            return [emb.tolist() for emb in embeddings]

        embeddings = await asyncio.to_thread(_encode_batch)
        return embeddings

    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings produced by this model

        Returns:
            Embedding dimension (e.g., 384 for all-MiniLM-L6-v2)
        """
        self._load_model()
        return self._model.get_sentence_embedding_dimension()
