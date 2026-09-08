from app.rag.ingestion import KnowledgeBaseIngestion


def main():
    ingestion = KnowledgeBaseIngestion(
        documents_dir="documents",
        collection_name="enterprise_operations",
    )

    chunk_count = ingestion.ingest()

    print(
        f"Knowledge base indexed successfully: "
        f"{chunk_count} chunks"
    )


if __name__ == "__main__":
    main()