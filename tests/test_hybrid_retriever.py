from app.rag.hybrid_retriever import HybridRetriever


def test_hybrid_retriever_returns_results():
    retriever = HybridRetriever(
        dense_top_k=10,
        bm25_top_k=10,
        fusion_top_k=20,
    )

    results = retriever.retrieve(
        query="What should I do when the payment service returns HTTP 503?",
        top_k=5,
    )

    assert results
    assert len(results) <= 5

    for result in results:
        assert "chunk_id" in result
        assert "source" in result
        assert "content" in result
        assert "rrf_score" in result


def test_hybrid_retriever_returns_unique_chunks():
    retriever = HybridRetriever(
        dense_top_k=10,
        bm25_top_k=10,
        fusion_top_k=20,
    )

    results = retriever.retrieve(
        query="payment service retry policy",
        top_k=5,
    )

    chunk_ids = [
        result["chunk_id"]
        for result in results
    ]

    assert len(chunk_ids) == len(set(chunk_ids))