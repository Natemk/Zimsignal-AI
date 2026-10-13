"""Database seeding script for ZimSignal AI vector store."""

from langchain_core.documents import Document
from ingestion.index import get_vector_store

def seed_knowledge_base():
    print("🌱 Seeding ZimSignal AI knowledge base into PostgreSQL pgvector...")
    vector_store = get_vector_store()

    documents = [
        Document(
            page_content=(
                "Artificial intelligence (AI) is intelligence demonstrated by machines, "
                "distinguishing it from the natural intelligence displayed by humans and animals. "
                "Modern AI systems leverage deep learning, neural networks, and large language models."
            ),
            metadata={
                "source_url": "https://example.com/ai-definition",
                "publisher": "ZimSignal Knowledge Base",
                "source_tier": "secondary_verified"
            }
        ),
        Document(
            page_content=(
                "Cyber-physical systems (CPS) integrate computational intelligence with physical processes, "
                "utilizing edge computing, microcontrollers, and state-space control models."
            ),
            metadata={
                "source_url": "https://example.com/cps-architecture",
                "publisher": "Africa University Research",
                "source_tier": "primary_official"
            }
        )
    ]

    inserted_ids = vector_store.add_documents(documents=documents)
    print(f"✅ Successfully seeded {len(inserted_ids)} document chunk(s) into pgvector!")

if __name__ == "__main__":
    seed_knowledge_base()