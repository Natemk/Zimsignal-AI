import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, HttpUrl

# Official Firecrawl SDK import
from firecrawl import Firecrawl

# LangChain primitives for RAG document processing
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


class SourceDefinition(BaseModel):
    """
    Schema representing an allowed data source definition.
    Enforces strict source provenance tracking.
    """
    url: HttpUrl
    publisher: str
    source_tier: str  # e.g., 'primary_official', 'secondary_verified'


def get_firecrawl_client() -> Firecrawl:
    """
    Initializes and returns an authenticated Firecrawl instance.
    
    Why: Keeps API key verification centralized and raises an error early
    if environment variables are missing.
    """
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        raise ValueError("CRITICAL: FIRECRAWL_API_KEY environment variable is missing.")
    return Firecrawl(api_key=api_key)


def scrape_url_to_document(
    source_def: SourceDefinition,
    formats: Optional[List[str]] = None
) -> Document:
    """
    Scrape Implementation: Single-page scrape converted into a LangChain Document.
    
    Args:
        source_def: SourceDefinition container with the target URL & source metadata.
        formats: Requested output formats (defaults to ['markdown']).
        
    Returns:
        A LangChain Document object enriched with provenance metadata.
    """
    if formats is None:
        formats = ["markdown"]
        
    app = get_firecrawl_client()
    
    # Perform clean extraction using Firecrawl SDK
    response = app.scrape(
        url=str(source_def.url),
        formats=formats
    )
    
    # Safely unpack response dictionary/object
    raw_metadata: Dict[str, Any] = getattr(response, "metadata", {}) or response.get("metadata", {})
    markdown_content: str = getattr(response, "markdown", "") or response.get("markdown", "")

    # Normalize into unified LangChain Document structure
    document = Document(
        page_content=markdown_content,
        metadata={
            "source_url": raw_metadata.get("sourceURL", str(source_def.url)),
            "title": raw_metadata.get("title", "Untitled Document"),
            "publisher": source_def.publisher,
            "source_tier": source_def.source_tier,
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "http_status": raw_metadata.get("statusCode", 200),
        }
    )
    return document


def map_domain_urls(target_domain: str) -> List[str]:
    """
    Mapping Implementation: Canonical URL discovery across target domain.
    
    Why: Prevents unguided crawling by discovering high-value URLs first.
    """
    app = get_firecrawl_client()
    map_result = app.map(url=target_domain)
    
    # Extract list of discovered URLs safely
    if isinstance(map_result, dict):
        return map_result.get("links", [])
    return getattr(map_result, "links", [])


def extract_structured_data(
    url: str,
    schema: type[BaseModel],
    prompt: str
) -> Dict[str, Any]:
    """
    Extraction Implementation: Schema-driven structured extraction from public pages.
    
    Why: Extracts typed JSON fields without relying on complex HTML selectors.
    """
    app = get_firecrawl_client()
    
    extract_result = app.scrape(
        url=url,
        formats=[{
            "type": "json",
            "schema": schema.model_json_schema(),
            "prompt": prompt
        }]
    )
    return extract_result


def chunk_document(
    document: Document,
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> List[Document]:
    """
    Splits an ingested document into overlapping token-friendly chunks.
    
    Why: Large documents exceed embedding limits; overlapping boundaries preserve
    sentential context for RAG vector search.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )
    return splitter.split_documents([document])

# TOPIC 9: VECTOR DATABASE & PROVENANCE STORAGE LOGIC (pgvector)

