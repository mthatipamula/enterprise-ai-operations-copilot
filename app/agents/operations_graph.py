from langgraph.graph import END, START, StateGraph

from app.agents.router import IntentRouter, Route
from app.agents.state import AgentState
from app.rag.rag_service import RAGService
from app.mcp.client import MCPClient
from app.llm.ollama_client import OllamaClient


router = IntentRouter()
rag_service = RAGService()
mcp_client = MCPClient()
llm_client = OllamaClient()


def route_request(state: AgentState) -> AgentState:
    """
    Determine the appropriate route for the incoming request
    using the existing IntentRouter.
    """
    query = state.get("query", "").strip()

    if not query:
        raise ValueError("Query cannot be empty")

    route = router.route(query)

    updated_state = {
        **state,
        "route": route,
    }

    # Extract the service when the request is routed to the tool.
    if route == Route.TOOL:
        service = _extract_service(query)

        updated_state["tool"] = "incident_status"
        updated_state["tool_arguments"] = {
            "service": service
        }

    return updated_state


def _extract_service(query: str) -> str:
    query_lower = query.lower()

    if "payment" in query_lower:
        return "payment"

    if "customer" in query_lower or "notification" in query_lower:
        return "customer"

    if "booking" in query_lower or "reservation" in query_lower:
        return "booking"

    return ""


def rag_node(state: AgentState) -> AgentState:
    query = state.get("query", "").strip()
    if not query:
        raise ValueError("Query cannot be empty")

    conversation_history = state.get(
        "conversation_history",
        [],
    )

    conversation_context = "\n".join(
        f"{message['role'].capitalize()}: {message['content']}"
        for message in conversation_history
    )

    if conversation_context:
        contextual_query = (
            "Conversation history:\n"
            f"{conversation_context}\n\n"
            "Current user question:\n"
            f"{query}"
        )
    else:
        contextual_query = query

        user_context = state.get("user_context", {})

        department = user_context.get("department")
        roles = user_context.get("roles", [])

        result = rag_service.answer(
            contextual_query,
            department=department,
            roles=roles,
        )

    return {
        **state,
        "answer": result.get("answer", ""),
        "sources": result.get("sources", []),
        "abstained": result.get("abstained", False),
        "grounded": result.get("grounded", False),
        "grounding_reason": result.get("grounding_reason", ""),
    }


def tool_node(state: AgentState) -> AgentState:
    tool_arguments = state.get("tool_arguments", {})

    service = tool_arguments.get("service", "").strip()

    mcp_service_name = {
        "payment": "payment-api",
        "customer": "customer-notification-service",
        "booking": "reservation-api",
    }.get(service)

    if not mcp_service_name:
        raise ValueError(f"Unsupported service: {service}")

    tool_result = mcp_client.call_tool(
        "get_service_health",
        {
            "service_name": mcp_service_name,
        },
    )

    return {
        **state,
        "tool": "incident_status",
        "tool_arguments": {
            "service_name": service,
        },
        "tool_result": tool_result,
        "answer": (
            f"Service: {service}\n"
            f"Status: {tool_result}"
        ),
    }


def direct_llm_node(state: AgentState) -> AgentState:
    """
    Generate a response using the existing Ollama/Llama 3 client.
    """
    query = state.get("query", "").strip()

    if not query:
        raise ValueError("Query cannot be empty")

    response = llm_client.generate(
        prompt=query
    )

    return {
        **state,
        "answer": response,
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

                    ┌──→ RAG ──────────┐
                    │                  │
        START → Router ─→ TOOL ────────┼──→ END
                    │                  │
                    └──→ DIRECT_LLM ───┘
    """
    graph = StateGraph(AgentState)

    graph.add_node("route_request", route_request)
    graph.add_node("rag", rag_node)
    graph.add_node("tool", tool_node)
    graph.add_node("direct_llm", direct_llm_node)

    graph.add_edge(START, "route_request")

    graph.add_conditional_edges(
        "route_request",
        select_route,
        {
            "rag": "rag",
            "tool": "tool",
            "direct_llm": "direct_llm",
        },
    )

    graph.add_edge("rag", END)
    graph.add_edge("tool", END)
    graph.add_edge("direct_llm", END)

    return graph.compile()