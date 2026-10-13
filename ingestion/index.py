import os
from typing import List, Dict, Any, Optional
from langchain_core.documents import Document
from langchain_core.embeddings import DeterministicFakeEmbedding
from langchain_postgres.vectorstores import PGVector
from agents.prompts.templates import RAG_SYSTEM_PROMPT

# Global Singleton initialization to avoid concurrent SQLAlchemy thread registration conflicts
_DB_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://langchain:langchain@localhost:6024/langchain")
_EMBEDDINGS = DeterministicFakeEmbedding(size=1536)
_GLOBAL_VECTOR_STORE = PGVector(
    embeddings=_EMBEDDINGS,
    collection_name="zimsignal_knowledge_base",
    connection=_DB_URL,
    use_jsonb=True
)

def get_vector_store() -> PGVector:
    return _GLOBAL_VECTOR_STORE

def query_rag_pipeline(
    query: str, 
    source_tier_filter: Optional[str] = None,
    k: int = 3
) -> Dict[str, Any]:
    """
    Retrieves chunks with strict source tier pre-filtering, prioritizing primary_official sources.
    """
    vector_store = get_vector_store()
    
    filter_dict = {}
    if source_tier_filter:
        filter_dict["source_tier"] = source_tier_filter
    
    if filter_dict:
        docs = vector_store.similarity_search(query, k=k, filter=filter_dict)
    else:
        docs = vector_store.similarity_search(query, k=k, filter={"source_tier": "primary_official"})
        if not docs:
            docs = vector_store.similarity_search(query, k=k)

    if not docs:
        return {
            "answer": "Insufficient evidence available in retrieved documents to answer this question.",
            "formatted_prompt": RAG_SYSTEM_PROMPT.format(context="NO CONTEXT AVAILABLE", query=query),
            "retrieved_chunks": [],
            "source_urls": []
        }

    formatted_context = []
    for doc in docs:
        source_url = doc.metadata.get("source_url", "Unknown Source")
        publisher = doc.metadata.get("publisher", "Unknown Publisher")
        tier = doc.metadata.get("source_tier", "unclassified")
        formatted_context.append(f"--- Document [{tier.upper()}] ({publisher} | {source_url}) ---\n{doc.page_content}")
        
    full_context_str = "\n\n".join(formatted_context)
    
    return {
        "answer": None,
        "formatted_prompt": RAG_SYSTEM_PROMPT.format(context=full_context_str, query=query),
        "retrieved_chunks": docs,
        "source_urls": list(set(d.metadata.get("source_url") for d in docs if d.metadata.get("source_url")))
    }

if __name__ == "__main__":
    res = query_rag_pipeline("What is artificial intelligence?")
    print(f"Retrieved {len(res['retrieved_chunks'])} document chunks.")
