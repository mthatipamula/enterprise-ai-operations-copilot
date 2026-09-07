from app.rag.document_loader import load_and_chunk_documents


def test_load_and_chunk_documents():
    chunks = load_and_chunk_documents("documents")

    assert len(chunks) > 0

    for chunk in chunks:
        assert chunk.chunk_id
        assert chunk.source
        assert chunk.content