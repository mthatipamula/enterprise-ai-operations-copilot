from app.rag.vector_store import QdrantVectorStore


class Retriever:
    """
    Retrieves the most relevant knowledge-base chunks
    for a natural-language query.
    """

    def __init__(
        self,
        collection_name: str = "enterprise_operations",
    ):
        self.vector_store = QdrantVectorStore(
            collection_name=collection_name
        )

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
    ) -> list[dict]:
        """
        Retrieve the top-k semantically similar chunks.
        """

        if not query.strip():
            raise ValueError("Query cannot be empty")

        return self.vector_store.search(
            query=query,
            limit=top_k,
        )