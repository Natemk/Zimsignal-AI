import pytest
from unittest.mock import MagicMock, patch
from langchain_core.documents import Document

from ingestion.firecrawl import (
    SourceDefinition,
    scrape_url_to_document,
    chunk_document,
)


def test_chunk_document_splitting():
    """
    Tests that a large document splits into smaller overlapping chunks
    while retaining original metadata.
    """
    long_content = "Word " * 500  # Creates a long text string
    doc = Document(
        page_content=long_content,
        metadata={"publisher": "Test Publisher", "source_tier": "primary_official"}
    )
    
    chunks = chunk_document(doc, chunk_size=200, chunk_overlap=50)
    
    assert len(chunks) > 1
    assert chunks[0].metadata["publisher"] == "Test Publisher"
    assert chunks[0].metadata["source_tier"] == "primary_official"


@patch("ingestion.firecrawl.get_firecrawl_client")
def test_scrape_url_to_document_mapping(mock_get_client):
    """
    Mocks the Firecrawl SDK output to verify clean mapping into
    a LangChain Document object with proper metadata tracking.
    """
    mock_app = MagicMock()
    mock_app.scrape.return_value = {
        "markdown": "# Sample Title\nSample content body.",
        "metadata": {
            "sourceURL": "https://example.gov.zw/report",
            "title": "Sample Title",
            "statusCode": 200,
        },
    }
    mock_get_client.return_value = mock_app

    source_def = SourceDefinition(
        url="https://example.gov.zw/report",
        publisher="Gov Zimbabwe",
        source_tier="primary_official",
    )

    doc = scrape_url_to_document(source_def)

    assert doc.page_content == "# Sample Title\nSample content body."
    assert doc.metadata["source_url"] == "https://example.gov.zw/report"
    assert doc.metadata["publisher"] == "Gov Zimbabwe"
    assert doc.metadata["source_tier"] == "primary_official"
    assert doc.metadata["http_status"] == 200