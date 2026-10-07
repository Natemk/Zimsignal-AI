import os
import pytest
from langchain_core.documents import Document
from pathlib import Path
from dotenv import load_dotenv
from ingestion.firecrawl import (
    SourceDefinition,
    scrape_url_to_document,
    chunk_document,
    index_chunks_to_pgvector,
)
# Points directly to the root .env file regardless of where pytest is invoked
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path, override=True)


@pytest.mark.integration
def test_full_ingestion_and_indexing_pipeline():
    """
    Verifies the complete RAG ingestion pipeline:
    1. Scrapes a live or mock URL into a LangChain Document.
    2. Chunks the document into overlapping segments.
    3. Stores and indexes vector embeddings into PostgreSQL (pgvector).
    """
    if not os.getenv("FIRECRAWL_API_KEY") or not os.getenv("DATABASE_URL"):
        pytest.skip("Skipping integration test: FIRECRAWL_API_KEY or DATABASE_URL not set in environment.")

    source_def = SourceDefinition(
        url="https://example.com",
        publisher="Example Agency",
        source_tier="primary_official"
    )

    # 1. Scrape URL to LangChain Document with metadata
    doc = scrape_url_to_document(source_def)
    assert doc.page_content != ""
    assert doc.metadata["publisher"] == "Example Agency"
    assert doc.metadata["source_tier"] == "primary_official"

    # 2. Chunk document
    chunks = chunk_document(doc, chunk_size=300, chunk_overlap=50)
    assert len(chunks) > 0

    # 3. Index chunks into pgvector database
    inserted_ids = index_chunks_to_pgvector(chunks, collection_name="test_integration_docs")
    assert len(inserted_ids) == len(chunks)