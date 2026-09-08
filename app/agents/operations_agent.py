from app.agents.conversation_memory import ConversationMemory
from app.agents.operations_graph import build_operations_graph


class OperationsAgent:
    """
    Enterprise AI Operations Agent.

    LangGraph is the orchestration layer responsible for:
    - routing knowledge questions to RAG
    - routing operational questions to tools
    - routing general questions to the LLM

    Conversation history is persisted in PostgreSQL and
    loaded into the LangGraph state for each request.
    """

    def __init__(self):
        self.memory = ConversationMemory()
        self.graph = build_operations_graph()

    def run(self, query: str, session_id: str = "default") -> dict:
        if not query.strip():
            raise ValueError("Query cannot be empty")

        # Store the current user message.
        self.memory.add_message(
            session_id=session_id,
            role="user",
            content=query,
        )

        # Load the complete conversation history from PostgreSQL.
        messages = self.memory.get_messages(session_id)

        conversation_history = [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in messages
        ]

        result = self.graph.invoke(
            {
                "session_id": session_id,
                "query": query,
                "conversation_history": conversation_history,
            }
        )

        answer = result.get("answer", "")

        # Store the assistant response in PostgreSQL.
        self.memory.add_message(
            session_id=session_id,
            role="assistant",
            content=answer,
        )

        response = {
            "query": query,
            "route": result["route"].value,
            "answer": answer,
            "sources": result.get("sources", []),
            "abstained": result.get("abstained", False),
            "grounded": result.get("grounded", False),
        }

        if result.get("tool"):
            response["tool"] = result["tool"]

        if result.get("tool_arguments"):
            response["tool_arguments"] = result["tool_arguments"]

        if result.get("tool_result"):
            response["tool_result"] = result["tool_result"]

        return response