# Payment API Runbook

## Overview

The Payment API processes payment authorization and capture requests
for enterprise applications.

## HTTP 503 Service Unavailable

HTTP 503 indicates that the Payment API or one of its upstream
dependencies is temporarily unavailable.

### Recommended Actions

1. Check the Payment API health endpoint.
2. Check whether the service has sufficient healthy instances.
3. Review recent deployment activity.
4. Check upstream dependency health.
5. Review application and infrastructure logs.
6. Retry the request only when the operation is safe to retry.

## Retry Policy

The Payment API supports a maximum of three retry attempts for
transient failures.

Retries should use exponential backoff.

Do not retry indefinitely.

## HTTP 500 Internal Server Error

HTTP 500 generally indicates an unexpected server-side failure.

Recommended actions:

1. Check application logs.
2. Check recent deployments.
3. Check database connectivity.
4. Check downstream service failures.
5. Escalate to the owning engineering team if the issue persists.

## HTTP 599

HTTP 599 is not a standard HTTP status code used by the Payment API.

If an HTTP 599 response is observed, do not assume that it has the
same retry behavior as HTTP 503.

Investigate the source of the response before taking corrective action.