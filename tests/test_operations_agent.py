from app.agents.operations_agent import OperationsAgent
from unittest.mock import patch

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

    mock_result = {
        "service": "payment-api",
        "status": "HEALTHY",
        "version": "2.4.1",
        "uptime": "99.98%",
    }

    with patch(
        "app.agents.operations_graph.mcp_client.call_tool",
        return_value=mock_result,
    ) as mock_call:

        result = agent.run(
            "Is the payment service currently experiencing an incident?"
        )

    assert result["route"] == "tool"
    assert result["tool"] == "incident_status"

    assert result["tool_result"]["service"] == "payment-api"
    assert result["tool_result"]["status"] == "HEALTHY"

    assert "healthy" in result["answer"].lower()

    mock_call.assert_called_once_with(
        "get_service_health",
        {"service_name": "payment-api"},
    )


def test_agent_executes_operational_service_tool():
    agent = OperationsAgent()

    mock_result = {
        "service": "customer-notification-service",
        "status": "DEGRADED",
        "version": "3.1.0",
        "uptime": "99.72%",
    }

    with patch(
        "app.agents.operations_graph.mcp_client.call_tool",
        return_value=mock_result,
    ) as mock_call:

        result = agent.run(
            "Is the customer service currently experiencing an incident?"
        )

    assert result["route"] == "tool"
    assert result["tool"] == "incident_status"

    assert result["tool_result"]["service"] == "customer-notification-service"
    assert result["tool_result"]["status"] == "DEGRADED"

    assert "degraded" in result["answer"].lower()

    mock_call.assert_called_once_with(
        "get_service_health",
        {"service_name": "customer-notification-service"},
    )


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