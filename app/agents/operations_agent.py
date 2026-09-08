from app.agents.conversation_memory import ConversationMemory
from app.agents.operations_graph import build_operations_graph


class OperationsAgent:
    """
    Enterprise AI Operations Agent.

    LangGraph is the orchestration layer responsible for:
    - routing knowledge questions to RAG
    - routing operational questions to tools
    - routing general questions to the LLM

    Conversation history is maintained by session_id.
    """

    def __init__(self):
        self.memory = ConversationMemory()
        self.graph = build_operations_graph()

    def run(
        self,
        query: str,
        session_id: str = "default",
    ) -> dict:
        """
        Execute a user request through the LangGraph workflow.
        """

        if not query.strip():
            raise ValueError("Query cannot be empty")

        # Store the user's message.
        self.memory.add_message(
            session_id,
            "user",
            query,
        )

        # Execute the LangGraph workflow.
        result = self.graph.invoke(
            {
                "session_id": session_id,
                "query": query,
            }
        )

        # Store the assistant response.
        answer = result.get("answer", "")

        self.memory.add_message(
            session_id,
            "assistant",
            answer,
        )

        # Return the public agent response.
        response = {
            "query": query,
            "route": result["route"].value,
            "answer": answer,
            "sources": result.get("sources", []),
            "abstained": result.get("abstained", False),
            "grounded": result.get("grounded", False),
        }

        # Include tool information when the tool branch was used.
        if result.get("tool"):
            response["tool"] = result["tool"]

        if result.get("tool_arguments"):
            response["tool_arguments"] = result["tool_arguments"]

        if result.get("tool_result"):
            response["tool_result"] = result["tool_result"]

        return response