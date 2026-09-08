from app.rag.relevance_filter import RelevanceFilter


def test_relevance_filter_keeps_relevant_results():
    relevance_filter = RelevanceFilter(
        threshold=0.35
    )

    results = [
        {
            "score": 0.80,
            "source": "payment-api-runbook.md",
            "content": "HTTP 503 requires health checks.",
        },
        {
            "score": 0.20,
            "source": "incident-management.md",
            "content": "Incident severity information.",
        },
    ]

    filtered = relevance_filter.filter(results)

    assert len(filtered) == 1
    assert filtered[0]["score"] == 0.80


def test_relevance_filter_keeps_score_at_threshold():
    relevance_filter = RelevanceFilter(
        threshold=0.35
    )

    results = [
        {
            "score": 0.35,
            "source": "payment-api-runbook.md",
            "content": "Retry policy.",
        }
    ]

    filtered = relevance_filter.filter(results)

    assert len(filtered) == 1


def test_relevance_filter_abstains_when_nothing_is_relevant():
    relevance_filter = RelevanceFilter(
        threshold=0.35
    )

    results = [
        {
            "score": 0.20,
            "source": "incident-management.md",
            "content": "Incident information.",
        },
        {
            "score": 0.15,
            "source": "customer-notification-sop.md",
            "content": "Customer notification.",
        },
    ]

    filtered = relevance_filter.filter(results)

    assert filtered == []

    assert not relevance_filter.has_relevant_results(
        results
    )