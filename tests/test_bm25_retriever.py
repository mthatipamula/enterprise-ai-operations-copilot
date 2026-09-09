from app.rag.bm25_retriever import BM25Retriever
from app.rag.document_loader import load_and_chunk_documents


def test_bm25_retrieves_http_503_content():
    chunks = load_and_chunk_documents()

    retriever = BM25Retriever(
        chunks=[
            {
                "chunk_id": chunk.chunk_id,
                "source": chunk.source,
                "content": chunk.content,
            }
            for chunk in chunks
        ],
        top_k=5,
    )

    results = retriever.search(
        "HTTP 503 payment service"
    )

    assert results
    assert any(
        "503" in result["content"]
        for result in results
    )


def test_bm25_returns_ranked_results():
    chunks = load_and_chunk_documents()

    retriever = BM25Retriever(
        chunks=[
            {
                "chunk_id": chunk.chunk_id,
                "source": chunk.source,
                "content": chunk.content,
            }
            for chunk in chunks
        ],
        top_k=5,
    )

    results = retriever.search(
        "payment service retry"
    )

    assert results

    scores = [
        result["score"]
        for result in results
    ]

    assert scores == sorted(
        scores,
        reverse=True,
    )