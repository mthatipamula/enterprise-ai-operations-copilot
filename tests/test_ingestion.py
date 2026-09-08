from app.rag.ingestion import KnowledgeBaseIngestion


def test_knowledge_base_ingestion():
    ingestion = KnowledgeBaseIngestion(
        documents_dir="documents",
        collection_name="test_knowledge_base",
    )

    chunk_count = ingestion.ingest()

    assert chunk_count > 0