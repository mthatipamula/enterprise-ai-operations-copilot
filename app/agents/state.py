from typing import Any, TypedDict


class AgentState(TypedDict, total=False):
    session_id: str
    query: str
    route: str
    user_context: dict

    # Conversation history loaded from PostgreSQL.
    conversation_history: list[dict[str, str]]

    retrieved_chunks: list[dict[str, Any]]
    sources: list[dict[str, Any]]

    answer: str
    abstained: bool
    grounded: bool
    grounding_reason: str

    tool: str
    tool_arguments: dict[str, Any]
    tool_result: dict[str, Any]