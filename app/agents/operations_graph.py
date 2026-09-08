from langgraph.graph import END, START, StateGraph

from app.agents.router import IntentRouter, Route
from app.agents.state import AgentState


router = IntentRouter()


def route_request(state: AgentState) -> AgentState:
    """
    Determine the appropriate route for the incoming request
    using the existing IntentRouter.
    """

    query = state.get("query", "").strip()

    if not query:
        raise ValueError("Query cannot be empty")

    route = router.route(query)

    return {
        **state,
        "route": route,
    }


def rag_node(state: AgentState) -> AgentState:
    """
    Placeholder RAG node.

    The existing RAGService will be connected in a later step.
    """
    return {
        **state,
        "answer": "RAG node reached successfully.",
    }


def tool_node(state: AgentState) -> AgentState:
    """
    Placeholder tool node.

    The existing incident-status tool will be connected
    in a later step.
    """
    return {
        **state,
        "answer": "Tool node reached successfully.",
    }


def direct_llm_node(state: AgentState) -> AgentState:
    """
    Placeholder direct-LLM node.

    The existing LLM implementation will be connected
    in a later step.
    """
    return {
        **state,
        "answer": "Direct LLM node reached successfully.",
    }


def select_route(state: AgentState) -> str:
    """
    Select the next LangGraph node based on the IntentRouter result.
    """

    route = state.get("route")

    if route == Route.RAG:
        return "rag"

    if route == Route.TOOL:
        return "tool"

    if route == Route.DIRECT_LLM:
        return "direct_llm"

    raise ValueError(f"Unsupported route: {route}")


def build_operations_graph():
    """
    Build the LangGraph workflow.

    Current graph:

                    ┌──→ RAG ──────────┐
                    │                  │
        START → Router ─→ TOOL ────────┼──→ END
                    │                  │
                    └──→ DIRECT_LLM ───┘
    """

    graph = StateGraph(AgentState)

    # Nodes
    graph.add_node("route_request", route_request)
    graph.add_node("rag", rag_node)
    graph.add_node("tool", tool_node)
    graph.add_node("direct_llm", direct_llm_node)

    # Start → Router
    graph.add_edge(START, "route_request")

    # Router → conditional branch
    graph.add_conditional_edges(
        "route_request",
        select_route,
        {
            "rag": "rag",
            "tool": "tool",
            "direct_llm": "direct_llm",
        },
    )

    # Branches → END
    graph.add_edge("rag", END)
    graph.add_edge("tool", END)
    graph.add_edge("direct_llm", END)

    return graph.compile()