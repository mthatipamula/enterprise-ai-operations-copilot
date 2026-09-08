from app.agents.operations_agent import OperationsAgent


def test_agent_routes_rag_question():
    agent = OperationsAgent()

    result = agent.run(
        "What should I do when the payment service returns HTTP 503?"
    )

    assert result["route"] == "rag"
    assert result["answer"]
    assert result["sources"]
    assert result["grounded"] is True
    assert result["abstained"] is False


def test_agent_executes_incident_status_tool():
    agent = OperationsAgent()

    result = agent.run(
        "Is the payment service currently experiencing an incident?"
    )

    assert result["route"] == "tool"
    assert result["tool"] == "incident_status"

    assert result["tool_result"]["service"] == "payment"
    assert result["tool_result"]["status"] == "DEGRADED"
    assert result["tool_result"]["severity"] == "SEV-2"

    assert "degraded" in result["answer"].lower()


def test_agent_executes_operational_service_tool():
    agent = OperationsAgent()

    result = agent.run(
        "Is the customer service currently experiencing an incident?"
    )

    assert result["route"] == "tool"
    assert result["tool"] == "incident_status"

    assert result["tool_result"]["service"] == "customer"
    assert result["tool_result"]["status"] == "OPERATIONAL"

    assert "operational" in result["answer"].lower()


def test_agent_routes_http_503_question_to_rag():
    agent = OperationsAgent()

    result = agent.run(
        "What is HTTP 503?"
    )

    assert result["route"] == "rag"
    assert result["grounded"] is True


def test_agent_rejects_empty_query():
    agent = OperationsAgent()

    try:
        agent.run("")
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert str(exc) == "Query cannot be empty"