import re


class SecurityGuardrails:
    """
    Basic security guardrails for the Operations Agent.

    Detects common prompt-injection patterns before a request
    reaches the agent orchestration layer.
    """

    INJECTION_PATTERNS = [
        r"ignore\s+(all\s+)?previous\s+instructions",
        r"ignore\s+(all\s+)?prior\s+instructions",
        r"disregard\s+(all\s+)?previous\s+instructions",
        r"disregard\s+(all\s+)?prior\s+instructions",
        r"forget\s+(all\s+)?previous\s+instructions",
        r"system\s+prompt",
        r"reveal\s+(your|the)\s+(system\s+)?prompt",
        r"show\s+(me\s+)?your\s+(system\s+)?prompt",
        r"bypass\s+(the\s+)?security",
        r"bypass\s+(the\s+)?guardrails",
        r"disable\s+(the\s+)?guardrails",
        r"developer\s+message",
        r"act\s+as\s+if\s+you\s+have\s+no\s+restrictions",
    ]

    MAX_QUERY_LENGTH = 5000

    def validate_input(self, query: str) -> None:
        """
        Validate a user query before agent execution.

        Raises ValueError when the request violates a
        security guardrail.
        """

        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        if len(query) > self.MAX_QUERY_LENGTH:
            raise ValueError(
                "Query exceeds the maximum allowed length."
            )

        if self._contains_prompt_injection(query):
            raise ValueError(
                "Request blocked by security guardrail."
            )

    def _contains_prompt_injection(self, query: str) -> bool:
        normalized_query = query.lower()

        return any(
            re.search(pattern, normalized_query)
            for pattern in self.INJECTION_PATTERNS
        )