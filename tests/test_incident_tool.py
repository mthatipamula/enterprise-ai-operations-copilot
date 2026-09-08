from app.tools.incident_tool import IncidentStatusTool


def test_payment_service_is_degraded():
    tool = IncidentStatusTool()

    result = tool.get_status("payment")

    assert result["service"] == "payment"
    assert result["status"] == "DEGRADED"
    assert result["severity"] == "SEV-2"
    assert "elevated failure rates" in result["summary"]


def test_customer_service_is_operational():
    tool = IncidentStatusTool()

    result = tool.get_status("customer")

    assert result["service"] == "customer"
    assert result["status"] == "OPERATIONAL"
    assert result["severity"] is None


def test_payment_api_alias_is_supported():
    tool = IncidentStatusTool()

    result = tool.get_status("payment-api")

    assert result["service"] == "payment"
    assert result["status"] == "DEGRADED"


def test_unauthorized_service_is_rejected():
    tool = IncidentStatusTool()

    try:
        tool.get_status("database")
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "not authorized" in str(exc)


def test_empty_service_is_rejected():
    tool = IncidentStatusTool()

    try:
        tool.get_status("")
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert str(exc) == "Service cannot be empty"

def test_tool_invocation_contains_structured_arguments():
    from app.tools.incident_tool import ToolInvocation

    invocation = ToolInvocation(
        tool_name="incident_status",
        arguments={"service": "payment"},
    )

    assert invocation.tool_name == "incident_status"
    assert invocation.arguments["service"] == "payment"