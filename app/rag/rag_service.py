from torch import chunk

from opentelemetry import trace

from app.llm.ollama_client import OllamaClient
from app.rag.grounding_validator import GroundingValidator
from app.rag.prompt_builder import PromptBuilder
from app.rag.relevance_filter import RelevanceFilter
from app.rag.hybrid_retriever import HybridRetriever
from app.core.document_guardrails import DocumentGuardrails

tracer = trace.get_tracer(__name__)

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

        self.retriever = HybridRetriever(
            collection_name=collection_name,
            dense_top_k=10,
            bm25_top_k=10,
            fusion_top_k=20,
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
        top_k: int = 5,
    ) -> dict:
        """
        Retrieve relevant context, generate an answer,
        and validate that the answer is grounded in the
        retrieved evidence.
        """

        with tracer.start_as_current_span("RAGService.answer") as span:
            span.set_attribute("rag.query_length", len(query))
            span.set_attribute("rag.top_k", top_k)

            if not query.strip():
                span.set_attribute("rag.success", False)
                raise ValueError("Query cannot be empty")

            safe_chunks = []

            # Step 1: Retrieve candidate documents
            retrieved_chunks = self.retriever.retrieve(
                query=query,
                top_k=top_k,
            )

            span.set_attribute(
                "rag.retrieved_documents",
                len(retrieved_chunks),
            )

            span.set_attribute(
                "evaluation.retrieval_count",
                len(retrieved_chunks),
            )


            for chunk in retrieved_chunks:
                content = chunk.get("content", "")

                if self.document_guardrails.is_safe(content):
                    safe_chunks.append(chunk)

            retrieved_chunks = safe_chunks

            span.set_attribute(
                "rag.safe_documents",
                len(retrieved_chunks),
            )

            # Step 2: Filter weakly relevant documents
            relevant_chunks = self.relevance_filter.filter(
                retrieved_chunks
            )

            span.set_attribute(
                "rag.relevant_documents",
                len(relevant_chunks),
            )

            span.set_attribute(
                "evaluation.relevant_count",
                len(relevant_chunks),
            )

            # Step 3: Abstain when there is insufficient evidence
            if not relevant_chunks:
                span.set_attribute("rag.abstained", True)
                span.set_attribute("rag.grounded", False)
                span.set_attribute("evaluation.abstained", True)
                span.set_attribute("evaluation.grounded", False)
                span.set_attribute("rag.success", True)

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
                span.set_attribute("rag.abstained", True)
                span.set_attribute("rag.grounded", False)
                span.set_attribute("evaluation.abstained", True)
                span.set_attribute("evaluation.grounded", False)
                span.set_attribute("rag.success", True)

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

            span.set_attribute("rag.abstained", False)
            span.set_attribute("rag.grounded", True)
            span.set_attribute("evaluation.abstained", False)
            span.set_attribute("evaluation.grounded", True)
            span.set_attribute("rag.success", True)

            return {
                "answer": answer,
                "sources": sources,
                "abstained": False,
                "grounded": True,
                "grounding_reason": grounding_result["reason"],
            }