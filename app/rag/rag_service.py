from torch import chunk

from app.llm.ollama_client import OllamaClient
from app.rag.grounding_validator import GroundingValidator
from app.rag.prompt_builder import PromptBuilder
from app.rag.relevance_filter import RelevanceFilter
from app.rag.retriever import Retriever
from app.core.document_guardrails import DocumentGuardrails


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
        Relevance Filter
            ↓
        Prompt Builder
            ↓
        LLM
            ↓
        Grounding Validator
            ↓
        Grounded Answer / Abstention
    """

    ABSTENTION_MESSAGE = (
        "I don't have enough relevant information in the "
        "knowledge base to answer this question."
    )

    GROUNDING_FAILURE_MESSAGE = (
        "I generated an answer, but I could not verify that "
        "the answer is fully supported by the knowledge base."
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

        self.grounding_validator = GroundingValidator()

        self.document_guardrails = DocumentGuardrails()

    def answer(
        self,
        query: str,
        top_k: int = 3,
    ) -> dict:
        """
        Retrieve relevant context, generate an answer,
        and validate that the answer is grounded in the
        retrieved evidence.
        """

        if not query.strip():
            raise ValueError("Query cannot be empty")

        safe_chunks = []

        # Step 1: Retrieve candidate documents
        retrieved_chunks = self.retriever.retrieve(
            query=query,
            top_k=top_k,
        )

        for chunk in retrieved_chunks:
            content = chunk.get("content", "")

            if self.document_guardrails.is_safe(content):
                safe_chunks.append(chunk)

        retrieved_chunks = safe_chunks

        # Step 2: Filter weakly relevant documents
        relevant_chunks = self.relevance_filter.filter(
            retrieved_chunks
        )

        # Step 3: Abstain when there is insufficient evidence
        if not relevant_chunks:
            return {
                "answer": self.ABSTENTION_MESSAGE,
                "sources": [],
                "abstained": True,
                "grounded": False,
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

        # Step 6: Validate generated answer
        grounding_result = self.grounding_validator.validate(
            answer=answer,
            retrieved_chunks=relevant_chunks,
        )

        # Step 7: Reject unsupported answer
        if not grounding_result["grounded"]:
            return {
                "answer": self.GROUNDING_FAILURE_MESSAGE,
                "sources": [],
                "abstained": True,
                "grounded": False,
                "grounding_reason": grounding_result["reason"],
            }

        # Step 8: Return validated answer and sources
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
            "grounded": True,
            "grounding_reason": grounding_result["reason"],
        }