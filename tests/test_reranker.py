from app.rag.reranker import Reranker


def test_reranker_returns_ranked_results():
    reranker = Reranker()

    chunks = [
        {
            "chunk_id": "chunk-1",
            "source": "payment-api-runbook.md",
            "content": (
                "When the Payment API returns HTTP 503, "
                "check service health and healthy instances."
            ),
        },
        {
            "chunk_id": "chunk-2",
            "source": "incident-management.md",
            "content": (
                "Follow the incident management process "
                "for production incidents."
            ),
        },
        {
            "chunk_id": "chunk-3",
            "source": "customer-notification-sop.md",
            "content": (
                "Notify customers when an incident requires "
                "customer communication."
            ),
        },
    ]

    results = reranker.rerank(
        query="What should I do when the Payment API returns HTTP 503?",
        chunks=chunks,
        top_k=3,
    )

    assert len(results) == 3

    assert all(
        "rerank_score" in result
        for result in results
    )

    scores = [
        result["rerank_score"]
        for result in results
    ]

    assert scores == sorted(
        scores,
        reverse=True,
    )


def test_reranker_returns_most_relevant_chunk_first():
    reranker = Reranker()

    chunks = [
        {
            "chunk_id": "irrelevant",
            "source": "incident-management.md",
            "content": (
                "The incident management process defines "
                "roles and escalation procedures."
            ),
        },
        {
            "chunk_id": "relevant",
            "source": "payment-api-runbook.md",
            "content": (
                "For HTTP 503 from the Payment API, "
                "check service health and healthy instances."
            ),
        },
    ]

    results = reranker.rerank(
        query="What should I do when the Payment API returns HTTP 503?",
        chunks=chunks,
        top_k=2,
    )

    assert results[0]["chunk_id"] == "relevant"


def test_reranker_handles_empty_chunks():
    reranker = Reranker()

    results = reranker.rerank(
        query="payment service",
        chunks=[],
        top_k=5,
    )

    assert results == []