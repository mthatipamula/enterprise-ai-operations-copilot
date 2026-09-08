from app.llm.ollama_client import OllamaClient
from app.rag.prompt_builder import PromptBuilder
from app.rag.retriever import Retriever


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
        Relevant Context
            ↓
        Prompt Builder
            ↓
        LLM
            ↓
        Grounded Answer
    """

    def __init__(
        self,
        collection_name: str = "enterprise_operations",
    ):
        self.retriever = Retriever(
            collection_name=collection_name
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
        """

        retrieved_chunks = self.retriever.retrieve(
            query=query,
            top_k=top_k,
        )

        if not retrieved_chunks:
            return {
                "answer": (
                    "The knowledge base does not contain "
                    "enough information to answer this question."
                ),
                "sources": [],
            }

        prompt = self.prompt_builder.build(
            query=query,
            retrieved_chunks=retrieved_chunks,
        )

        answer = self.llm.generate(
            prompt=prompt,
            temperature=0.2,
        )

        sources = [
            {
                "source": chunk["source"],
                "chunk_id": chunk["chunk_id"],
                "score": chunk["score"],
            }
            for chunk in retrieved_chunks
        ]

        return {
            "answer": answer,
            "sources": sources,
        }