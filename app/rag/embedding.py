from sentence_transformers import SentenceTransformer


class EmbeddingService:
    """
    Generates vector embeddings for document chunks and queries.
    """

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    ):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def embed_text(self, text: str) -> list[float]:
        """
        Generate an embedding vector for a single piece of text.
        """

        if not text.strip():
            raise ValueError("Text cannot be empty")

        embedding = self.model.encode(
            text,
            normalize_embeddings=True,
        )

        return embedding.tolist()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for multiple documents.
        """

        if not texts:
            return []

        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
        )

        return embeddings.tolist()

    @property
    def dimension(self) -> int:
        """
        Return the dimensionality of the embedding vector.
        """

        return self.model.get_embedding_dimension()