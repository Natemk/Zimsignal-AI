import hashlib
from typing import List
from langchain_core.documents import Document

def generate_chunk_id(doc_url: str, chunk_index: int, content: str) -> str:
    """
    Generates a deterministic unique ID based on source URL and content hash.
    Ensures exact content deduplication during pgvector inserts.
    """
    hasher = hashlib.sha256()
    hasher.update(f"{doc_url}_{chunk_index}_{content}".encode("utf-8"))
    return hasher.hexdigest()

def prepare_deduplicated_chunks(chunks: List[Document]) -> List[Document]:
    seen_hashes = set()
    deduped_chunks = []
    
    for chunk in chunks:
        c_hash = hashlib.md5(chunk.page_content.encode("utf-8")).hexdigest()
        if c_hash in seen_hashes:
            continue
        seen_hashes.add(c_hash)
        chunk.metadata["content_hash"] = c_hash
        deduped_chunks.append(chunk)
        
    return deduped_chunks