from app.rag.rag_service import RAGService


def test_rag_service():
    service = RAGService(
        collection_name="enterprise_operations",
        relevance_threshold=0.35,
    )

    result = service.answer(
        "What should I do when the payment service returns HTTP 503?",
        top_k=3,
    )

    assert result["answer"]
    assert isinstance(result["answer"], str)
    assert result["sources"]
    assert result["abstained"] is False

    for source in result["sources"]:
        assert source["score"] >= 0.35


def test_rag_service_abstains_for_unknown_question():
    service = RAGService(
        collection_name="enterprise_operations",
        relevance_threshold=0.35,
    )

    result = service.answer(
        "What is the corporate policy for quantum "
        "computing investment?",
        top_k=3,
    )

    assert result["abstained"] is True
    assert result["sources"] == []
    assert (
        result["answer"]
        == RAGService.ABSTENTION_MESSAGE
    )