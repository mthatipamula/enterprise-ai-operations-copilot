from app.rag.rag_service import RAGService


def test_rag_service():
    service = RAGService(
        collection_name="enterprise_operations"
    )

    result = service.answer(
        "What should I do when the payment service returns HTTP 503?",
        top_k=3,
    )

    assert result["answer"]
    assert isinstance(result["answer"], str)

    assert result["sources"]
    assert len(result["sources"]) <= 3