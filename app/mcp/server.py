from mcp.server import MCPServer


mcp = MCPServer("Enterprise Operations MCP Server")


@mcp.tool()
def get_service_health(service_name: str) -> dict:
    """Return the current health status of an enterprise service."""

    service_status = {
        "payment-api": {
            "status": "HEALTHY",
            "version": "2.4.1",
            "uptime": "99.98%",
        },
        "customer-notification-service": {
            "status": "DEGRADED",
            "version": "3.1.0",
            "uptime": "99.72%",
        },
        "reservation-api": {
            "status": "HEALTHY",
            "version": "5.8.2",
            "uptime": "99.95%",
        },
    }

    result = service_status.get(service_name.lower())

    if result is None:
        return {
            "service": service_name,
            "status": "UNKNOWN",
            "message": f"No health information found for {service_name}.",
        }

    return {
        "service": service_name,
        **result,
    }


@mcp.tool()
def get_incident_status(incident_id: str) -> dict:
    """Return the current status of an operational incident."""

    incidents = {
        "INC-1001": {
            "status": "OPEN",
            "severity": "SEV2",
            "service": "payment-api",
            "summary": "Elevated HTTP 503 responses",
        },
        "INC-1002": {
            "status": "RESOLVED",
            "severity": "SEV3",
            "service": "customer-notification-service",
            "summary": "Delayed customer notifications",
        },
    }

    result = incidents.get(incident_id.upper())

    if result is None:
        return {
            "incident_id": incident_id,
            "status": "UNKNOWN",
            "message": f"No incident information found for {incident_id}.",
        }

    return {
        "incident_id": incident_id,
        **result,
    }


@mcp.tool()
def get_runbook(service_name: str) -> dict:
    """Return operational runbook guidance for a service."""

    runbooks = {
        "payment-api": {
            "service": "payment-api",
            "primary_action": "Retry failed requests with exponential backoff.",
            "maximum_retries": 3,
            "escalation": "Escalate to the Payments Platform team after the third failed retry.",
        },
        "customer-notification-service": {
            "service": "customer-notification-service",
            "primary_action": "Check downstream messaging provider health.",
            "maximum_retries": 2,
            "escalation": "Escalate to the Customer Communications team.",
        },
    }

    result = runbooks.get(service_name.lower())

    if result is None:
        return {
            "service": service_name,
            "status": "NOT_FOUND",
            "message": f"No runbook found for {service_name}.",
        }

    return result


if __name__ == "__main__":
    mcp.run(transport="streamable-http")