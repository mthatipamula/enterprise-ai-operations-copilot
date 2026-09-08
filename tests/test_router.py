from app.agents.router import IntentRouter, Route


def test_router_selects_rag_for_runbook_question():
    router = IntentRouter()

    result = router.route(
        "What should I do according to the payment API runbook?"
    )

    assert result == Route.RAG


def test_router_selects_tool_for_current_incident():
    router = IntentRouter()

    result = router.route(
        "Is the payment service currently experiencing an incident?"
    )

    assert result == Route.TOOL


def test_router_selects_direct_llm_for_general_question():
    router = IntentRouter()

    result = router.route(
        "What is HTTP 503?"
    )

    assert result == Route.DIRECT_LLM


def test_router_rejects_empty_query():
    router = IntentRouter()

    try:
        router.route("")
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert str(exc) == "Query cannot be empty"