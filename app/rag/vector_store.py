from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

from app.rag.document_loader import DocumentChunk
from app.rag.embedding import EmbeddingService
import os

class QdrantVectorStore:
    """
    Stores document embeddings in Qdrant and performs
    semantic similarity search.
    """

    def __init__(
        self,
        collection_name: str = "enterprise_operations",
        host: str | None = None,
        port: int | None = None,
    ):
        self.collection_name = collection_name

        host = host or os.getenv("QDRANT_HOST", "localhost")
        port = port or int(os.getenv("QDRANT_PORT", "6333"))


        self.client = QdrantClient(
            host=host,
            port=port,
        )

        self.embedding_service = EmbeddingService()

        self._create_collection()

    def _create_collection(self) -> None:
        """
        Create the Qdrant collection if it does not already exist.
        """

        collections = self.client.get_collections()

        collection_names = {
            collection.name
            for collection in collections.collections
        }

        if self.collection_name not in collection_names:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.embedding_service.dimension,
                    distance=Distance.COSINE,
                ),
            )

    def add_chunks(
        self,
        chunks: list[DocumentChunk],
    ) -> None:
        """
        Generate embeddings for document chunks and store them
        in Qdrant with source metadata.
        """

        if not chunks:
            return

        texts = [chunk.content for chunk in chunks]

        embeddings = self.embedding_service.embed_documents(texts)

        points = []

        for index, (chunk, embedding) in enumerate(
            zip(chunks, embeddings)
        ):
            points.append(
                PointStruct(
                    id=index,
                    vector=embedding,
                    payload={
                        "chunk_id": chunk.chunk_id,
                        "source": chunk.source,
                        "content": chunk.content,
                    },
                )
            )

        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
        )

    def search(
        self,
        query: str,
        limit: int = 3,
    ) -> list[dict]:
        """
        Perform semantic similarity search against Qdrant.
        """

        query_embedding = self.embedding_service.embed_text(query)

        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_embedding,
            limit=limit,
        ).points

        return [
            {
                "score": result.score,
                "chunk_id": result.payload["chunk_id"],
                "source": result.payload["source"],
                "content": result.payload["content"],
            }
            for result in results
        ]