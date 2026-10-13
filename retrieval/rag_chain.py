"""Backward-compatible imports for document retrieval."""

from ingestion.index import RAG_SYSTEM_PROMPT, get_vector_store, query_rag_pipeline

__all__ = ["RAG_SYSTEM_PROMPT", "get_vector_store", "query_rag_pipeline"]
