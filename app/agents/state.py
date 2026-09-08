from typing import Any, TypedDict


class AgentState(TypedDict, total=False):
    """
    Shared state passed between LangGraph nodes.

    Each node can read from and update this state as the
    request moves through the agent workflow.
    """

    # Request/session information
    session_id: str
    query: str

    # Routing decision
    route: str

    # RAG information
    retrieved_chunks: list[dict[str, Any]]
    sources: list[dict[str, Any]]

    # Final response
    answer: str

    # Response validation
    abstained: bool
    grounded: bool
    grounding_reason: str

    # Tool execution information
    tool: str
    tool_arguments: dict[str, Any]
    tool_result: dict[str, Any]