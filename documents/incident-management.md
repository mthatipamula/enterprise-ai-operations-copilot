# Incident Management Guide

## Severity Levels

### SEV-1

A critical production incident affecting a major customer-facing
capability.

Immediate incident response is required.

### SEV-2

A significant production issue with degraded functionality or
performance.

The owning engineering team should investigate promptly.

### SEV-3

A limited-impact issue that does not significantly affect customers.

The issue can normally be handled through the standard engineering
workflow.

## Incident Response

When an incident is detected:

1. Confirm the affected service.
2. Determine the customer impact.
3. Check recent deployments.
4. Review application and infrastructure metrics.
5. Review logs and traces.
6. Identify dependent services.
7. Communicate status to stakeholders.
8. Document the resolution.

## Production Changes

Avoid making unrelated production changes during an active incident.

Any emergency change should follow the organization's emergency
change-management process.