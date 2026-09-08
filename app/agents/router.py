from enum import Enum


class Route(str, Enum):
    """
    Supported execution routes for the agent.
    """

    RAG = "rag"
    TOOL = "tool"
    DIRECT_LLM = "direct_llm"


class IntentRouter:
    """
    Determines which capability should handle a user request.

    Agent v1 uses deterministic routing rules.
    """

    def route(self, query: str) -> Route:
        """
        Determine the appropriate route for a user query.
        """

        if not query.strip():
            raise ValueError("Query cannot be empty")

        query_lower = query.lower()

        # Operational questions that require current state
        # should eventually be handled by an API/tool.
        tool_keywords = [
            "currently",
            "right now",
            "is there an incident",
            "incident status",
            "service status",
            "is the service down",
            "is the service degraded",
        ]

        if any(
            keyword in query_lower
            for keyword in tool_keywords
        ):
            return Route.TOOL

        # Questions about company knowledge, procedures,
        # runbooks, policies, and operational guidance
        # should use RAG.
        rag_keywords = [
            "runbook",
            "policy",
            "procedure",
            "how should i",
            "what should i do",
            "what is the process",
            "what is the maximum",
            "what is the minimum",
            "what is the limit",
            "what are the limits",
            "how many",
            "how much",
            "retry policy",
            "retry limit",
            "incident management",
            "customer notification",
            "http 500",
            "http 503",
            "http 599",
        ]

        if any(
            keyword in query_lower
            for keyword in rag_keywords
        ):
            return Route.RAG

        # Default to direct LLM for general questions.
        return Route.DIRECT_LLM