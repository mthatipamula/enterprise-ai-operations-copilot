from app.llm.ollama_client import OllamaClient
from app.rag.prompt_builder import PromptBuilder
from app.rag.retriever import Retriever
from app.rag.relevance_filter import RelevanceFilter


class RAGService:
    """
    End-to-end Retrieval-Augmented Generation service.

    Flow:

        User Query
            ↓
        Retriever
            ↓
        Qdrant
            ↓
        Top-K Results
            ↓
        Relevance Filter
            ↓
        Relevant Context
            ↓
        Prompt Builder
            ↓
        LLM
            ↓
        Grounded Answer

    If no retrieved result meets the relevance threshold,
    the service abstains instead of calling the LLM.
    """

    ABSTENTION_MESSAGE = (
        "I don't have enough relevant information in the "
        "knowledge base to answer this question."
    )

    def __init__(
        self,
        collection_name: str = "enterprise_operations",
        relevance_threshold: float = 0.35,
    ):
        self.retriever = Retriever(
            collection_name=collection_name
        )

        self.relevance_filter = RelevanceFilter(
            threshold=relevance_threshold
        )

        self.prompt_builder = PromptBuilder()
        self.llm = OllamaClient()

    def answer(
        self,
        query: str,
        top_k: int = 3,
    ) -> dict:
        """
        Retrieve relevant context and generate
        a grounded answer.

        The LLM is only called when at least one
        retrieved chunk passes the relevance threshold.
        """

        if not query.strip():
            raise ValueError("Query cannot be empty")

        # Step 1: Retrieve candidate documents
        retrieved_chunks = self.retriever.retrieve(
            query=query,
            top_k=top_k,
        )

        # Step 2: Filter weakly relevant documents
        relevant_chunks = self.relevance_filter.filter(
            retrieved_chunks
        )

        # Step 3: Abstain if nothing is relevant enough
        if not relevant_chunks:
            return {
                "answer": self.ABSTENTION_MESSAGE,
                "sources": [],
                "abstained": True,
            }

        # Step 4: Build grounded prompt
        prompt = self.prompt_builder.build(
            query=query,
            retrieved_chunks=relevant_chunks,
        )

        # Step 5: Generate answer
        answer = self.llm.generate(
            prompt=prompt,
            temperature=0.2,
        )

        # Step 6: Return answer and supporting sources
        sources = [
            {
                "source": chunk["source"],
                "chunk_id": chunk["chunk_id"],
                "score": chunk["score"],
            }
            for chunk in relevant_chunks
        ]

        return {
            "answer": answer,
            "sources": sources,
            "abstained": False,
        }