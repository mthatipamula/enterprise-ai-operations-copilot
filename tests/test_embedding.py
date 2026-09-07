from app.rag.embedding import EmbeddingService


def test_embedding_generation():
    embedding_service = EmbeddingService()

    vector = embedding_service.embed_text(
        "Payment API returns HTTP 503"
    )

    assert vector
    assert len(vector) == embedding_service.dimension


def test_embedding_dimension():
    embedding_service = EmbeddingService()

    assert embedding_service.dimension == 384