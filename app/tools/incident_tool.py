from dataclasses import dataclass


@dataclass
class IncidentStatus:
    service: str
    status: str
    severity: str | None
    summary: str

@dataclass
class ToolInvocation:
    tool_name: str
    arguments: dict


class IncidentStatusTool:
    """
    Tool used by the Operations Agent to retrieve
    the current operational status of a service.

    Agent v2 uses deterministic mock data.
    A real implementation can later call an
    incident-management API.
    """

    ALLOWED_SERVICES = {
        "payment",
        "payment-api",
        "customer",
        "customer-api",
        "booking",
        "booking-api",
    }

    INCIDENTS = {
        "payment": IncidentStatus(
            service="payment",
            status="DEGRADED",
            severity="SEV-2",
            summary=(
                "The Payment API is experiencing elevated "
                "failure rates for authorization requests."
            ),
        ),
        "customer": IncidentStatus(
            service="customer",
            status="OPERATIONAL",
            severity=None,
            summary="No active incident is currently reported.",
        ),
        "booking": IncidentStatus(
            service="booking",
            status="OPERATIONAL",
            severity=None,
            summary="No active incident is currently reported.",
        ),
    }

    def get_status(self, service: str) -> dict:
        """
        Retrieve the current status of a service.
        """

        if not service.strip():
            raise ValueError("Service cannot be empty")

        normalized_service = service.strip().lower()

        if normalized_service not in self.ALLOWED_SERVICES:
            raise ValueError(
                f"Service '{service}' is not authorized "
                "for this tool."
            )

        # Normalize aliases to the canonical service name.
        if normalized_service == "payment-api":
            normalized_service = "payment"

        if normalized_service == "customer-api":
            normalized_service = "customer"

        if normalized_service == "booking-api":
            normalized_service = "booking"

        incident = self.INCIDENTS.get(normalized_service)

        if incident is None:
            return {
                "service": normalized_service,
                "status": "UNKNOWN",
                "severity": None,
                "summary": "No status information is available.",
            }

        return {
            "service": incident.service,
            "status": incident.status,
            "severity": incident.severity,
            "summary": incident.summary,
        }