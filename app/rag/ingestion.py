from app.rag.document_loader import load_and_chunk_documents
from app.rag.vector_store import QdrantVectorStore


class KnowledgeBaseIngestion:
    """
    Loads, chunks, embeds, and stores the enterprise
    knowledge base in Qdrant.
    """

    def __init__(
        self,
        documents_dir: str = "documents",
        collection_name: str = "enterprise_operations",
    ):
        self.documents_dir = documents_dir
        self.vector_store = QdrantVectorStore(
            collection_name=collection_name
        )

    def ingest(self) -> int:
        """
        Load all documents, create chunks, and store them
        in Qdrant.

        Returns:
            Number of chunks indexed.
        """

        chunks = load_and_chunk_documents(
            self.documents_dir
        )

        if not chunks:
            return 0

        self.vector_store.add_chunks(chunks)

        return len(chunks)