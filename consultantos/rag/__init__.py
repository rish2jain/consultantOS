"""
RAG (Retrieval Augmented Generation) system for ConsultantOS
Provides semantic search over historical reports and analyses
"""
from consultantos.rag.embeddings import EmbeddingGenerator
from consultantos.rag.retriever import RAGRetriever
from consultantos.rag.vector_store import VectorStore

__all__ = ["EmbeddingGenerator", "RAGRetriever", "VectorStore"]
