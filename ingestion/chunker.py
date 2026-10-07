
from typing import List, Dict, Any
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

def create_document_chunks(
    documents: List[Document],
    chunk_size: int = 1000,
    chunk_overlap: int = 150,
    extra_metadata: Dict[str, Any] = None
) -> List[Document]:
    """
    Splits documents into smaller chunks and enriches each chunk with structured metadata.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )

    chunked_docs = text_splitter.split_documents(documents)

    # Enrich metadata for every individual chunk
    for idx, chunk in enumerate(chunked_docs):
        # Retain existing document metadata
        chunk.metadata = chunk.metadata or {}
        
        # Add chunk-specific metadata attributes
        chunk.metadata["chunk_id"] = f"{chunk.metadata.get('source_id', 'doc')}_chunk_{idx}"
        chunk.metadata["chunk_index"] = idx
        chunk.metadata["total_chunks"] = len(chunked_docs)
        
        if extra_metadata:
            chunk.metadata.update(extra_metadata)

    return chunked_docs