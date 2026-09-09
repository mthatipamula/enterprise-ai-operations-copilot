from sentence_transformers import CrossEncoder


class Reranker:
    """
    Reranks retrieved document chunks using a cross-encoder model.

    Unlike embedding-based retrieval, the cross-encoder evaluates
    the query and document together to produce a more precise
    relevance score.
    """

    def __init__(
        self,
        model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
    ):
        self.model = CrossEncoder(model_name)

    def rerank(
        self,
        query: str,
        chunks: list[dict],
        top_k: int = 5,
    ) -> list[dict]:
        """
        Rerank candidate chunks against the query.
        """

        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        if not chunks:
            return []

        pairs = [
            (
                query,
                chunk.get("content", ""),
            )
            for chunk in chunks
        ]

        scores = self.model.predict(pairs)

        reranked_results = []

        for chunk, score in zip(chunks, scores):
            reranked_results.append(
                {
                    **chunk,
                    "rerank_score": float(score),
                }
            )

        reranked_results.sort(
            key=lambda result: result["rerank_score"],
            reverse=True,
        )

        return reranked_results[:top_k]