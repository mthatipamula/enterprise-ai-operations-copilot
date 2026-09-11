
from opentelemetry import trace

from app.rag.bm25_retriever import BM25Retriever
from app.rag.rrf import RRFFusion
from app.rag.retriever import Retriever
from app.rag.document_loader import load_and_chunk_documents
from app.rag.reranker import Reranker

tracer = trace.get_tracer(__name__)

class HybridRetriever:
    """
    Combines dense retrieval from Qdrant with lexical retrieval
    from BM25 using Reciprocal Rank Fusion (RRF).
    """

    def __init__(
        self,
        collection_name: str = "enterprise_operations",
        dense_top_k: int = 10,
        bm25_top_k: int = 10,
        fusion_top_k: int = 20,
    ):
        self.dense_top_k = dense_top_k
        self.bm25_top_k = bm25_top_k
        self.fusion_top_k = fusion_top_k

        # Existing dense retriever backed by Qdrant.
        self.dense_retriever = Retriever(
            collection_name=collection_name
        )

        # Load the same document chunks used by the embedding pipeline.
        chunks = load_and_chunk_documents()

        bm25_chunks = [
            {
                "chunk_id": chunk.chunk_id,
                "source": chunk.source,
                "content": chunk.content,
            }
            for chunk in chunks
        ]

        # Lexical retriever.
        # Lexical retriever.
        self.bm25_retriever = BM25Retriever(
            chunks=bm25_chunks,
            top_k=bm25_top_k,
        )

        # Reciprocal Rank Fusion.
        self.rrf = RRFFusion()
        self.reranker = Reranker()

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        department: str | None = None,
        roles: list[str] | None = None,
    ) -> list[dict]:
        """
        Retrieve documents using both dense and BM25 retrieval,
        then combine the results using RRF.
        """

        with tracer.start_as_current_span("HybridRetriever.retrieve") as span:
            span.set_attribute("retrieval.top_k", top_k)
            span.set_attribute("retrieval.dense_top_k", self.dense_top_k)
            span.set_attribute("retrieval.bm25_top_k", self.bm25_top_k)
            span.set_attribute("retrieval.fusion_top_k", self.fusion_top_k)

            if not query or not query.strip():
                span.set_attribute("retrieval.success", False)
                raise ValueError("Query cannot be empty")

            # Dense semantic retrieval from Qdrant
            dense_results = self.dense_retriever.retrieve(
                query=query,
                top_k=self.dense_top_k,
                department=department,
                roles=roles,
            )

            span.set_attribute(
                "retrieval.dense_results",
                len(dense_results),
            )

            # Lexical retrieval using BM25
            bm25_results = self.bm25_retriever.search(
                query=query,
            )

            span.set_attribute(
                "retrieval.bm25_results",
                len(bm25_results),
            )

            # Reciprocal Rank Fusion
            fused_results = self.rrf.fuse(
                result_lists=[
                    dense_results,
                    bm25_results,
                ],
                top_k=self.fusion_top_k,
            )

            span.set_attribute(
                "retrieval.fused_results",
                len(fused_results),
            )

            # Keep only candidates that also have a dense semantic
            # score so the existing relevance gate remains meaningful.
            fused_results = [
                result
                for result in fused_results
                if "score" in result
            ]

            span.set_attribute(
                "retrieval.semantic_candidates",
                len(fused_results),
            )

            # Cross-encoder reranking
            reranked_results = self.reranker.rerank(
                query=query,
                chunks=fused_results,
                top_k=top_k,
            )

            span.set_attribute(
                "retrieval.reranked_results",
                len(reranked_results),
            )

            span.set_attribute("retrieval.success", True)

            return reranked_results