from app.rag.rrf import RRFFusion


def test_rrf_boosts_documents_found_by_multiple_retrievers():
    dense_results = [
        {
            "chunk_id": "chunk-a",
            "source": "dense.md",
            "content": "Dense result A",
            "score": 0.90,
        },
        {
            "chunk_id": "chunk-b",
            "source": "dense.md",
            "content": "Dense result B",
            "score": 0.80,
        },
        {
            "chunk_id": "chunk-c",
            "source": "dense.md",
            "content": "Dense result C",
            "score": 0.70,
        },
    ]

    bm25_results = [
        {
            "chunk_id": "chunk-b",
            "source": "bm25.md",
            "content": "BM25 result B",
            "score": 8.50,
        },
        {
            "chunk_id": "chunk-d",
            "source": "bm25.md",
            "content": "BM25 result D",
            "score": 7.50,
        },
        {
            "chunk_id": "chunk-a",
            "source": "bm25.md",
            "content": "BM25 result A",
            "score": 6.50,
        },
    ]

    fusion = RRFFusion()

    results = fusion.fuse(
        result_lists=[
            dense_results,
            bm25_results,
        ],
        top_k=4,
    )

    assert len(results) == 4

    chunk_ids = [
        result["chunk_id"]
        for result in results
    ]

    # chunk-b appears in both retrieval systems,
    # so it should receive contributions from both rankings.
    assert chunk_ids[0] == "chunk-b"

    assert "rrf_score" in results[0]
    assert results[0]["rrf_score"] > 0


def test_rrf_removes_duplicate_chunks():
    dense_results = [
        {
            "chunk_id": "chunk-a",
            "source": "test.md",
            "content": "Result A",
            "score": 0.90,
        },
        {
            "chunk_id": "chunk-b",
            "source": "test.md",
            "content": "Result B",
            "score": 0.80,
        },
    ]

    bm25_results = [
        {
            "chunk_id": "chunk-a",
            "source": "test.md",
            "content": "Result A",
            "score": 5.00,
        },
    ]

    fusion = RRFFusion()

    results = fusion.fuse(
        result_lists=[
            dense_results,
            bm25_results,
        ],
        top_k=10,
    )

    chunk_ids = [
        result["chunk_id"]
        for result in results
    ]

    assert len(chunk_ids) == len(set(chunk_ids))
    assert chunk_ids.count("chunk-a") == 1


def test_rrf_respects_top_k():
    results_one = [
        {
            "chunk_id": f"chunk-{index}",
            "source": "test.md",
            "content": f"Result {index}",
            "score": 1.0,
        }
        for index in range(10)
    ]

    fusion = RRFFusion()

    results = fusion.fuse(
        result_lists=[results_one],
        top_k=3,
    )

    assert len(results) == 3