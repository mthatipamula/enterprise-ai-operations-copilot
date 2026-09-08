class PromptBuilder:
    """
    Builds grounded prompts using retrieved enterprise knowledge.
    """

    SYSTEM_INSTRUCTION = """
You are an Enterprise AI Operations Copilot.

Answer the user's question using ONLY the provided
enterprise knowledge context.

Rules:
1. Do not invent information.
2. Do not use outside knowledge.
3. If the context does not contain enough information,
   clearly say that the knowledge base does not contain
   enough information to answer the question.
4. Give practical and concise guidance.
5. When possible, reference the source document.
"""

    def build(
        self,
        query: str,
        retrieved_chunks: list[dict],
    ) -> str:
        if not query.strip():
            raise ValueError("Query cannot be empty")

        if not retrieved_chunks:
            raise ValueError("Retrieved context cannot be empty")

        context_parts = []

        for index, chunk in enumerate(retrieved_chunks, start=1):
            context_parts.append(
                f"""
--- Context {index} ---
Source: {chunk["source"]}
Relevance Score: {chunk["score"]:.4f}

{chunk["content"]}
"""
            )

        context = "\n".join(context_parts)

        return f"""
{self.SYSTEM_INSTRUCTION}

USER QUESTION:
{query}

ENTERPRISE KNOWLEDGE CONTEXT:
{context}

ANSWER:
""".strip()