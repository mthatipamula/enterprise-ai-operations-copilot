from app.rag.document_loader import load_and_chunk_documents
from app.rag.vector_store import QdrantVectorStore


def test_qdrant_vector_store():
    chunks = load_and_chunk_documents("documents")

    vector_store = QdrantVectorStore(
        collection_name="test_enterprise_operations"
    )

    vector_store.add_chunks(chunks)

    results = vector_store.search(
        "What should I do when the payment service returns HTTP 503?",
        limit=3,
    )

    assert results
    assert len(results) <= 3

    for result in results:
        assert result["score"] is not None
        assert result["source"]
        assert result["content"]