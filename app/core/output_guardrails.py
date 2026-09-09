import re


class OutputGuardrails:
    """
    Basic security validation for AI-generated responses.

    Detects accidental exposure of internal prompts,
    instructions, and obvious secrets before a response
    is returned to the caller.
    """

    BLOCKED_PATTERNS = [
        r"system\s+prompt",
        r"developer\s+message",
        r"system\s+message",
        r"ignore\s+(all\s+)?previous\s+instructions",
    ]

    SECRET_PATTERNS = [
        # Common API key-style patterns
        r"\bsk-[A-Za-z0-9]{20,}\b",

        # Generic bearer token
        r"\bBearer\s+[A-Za-z0-9._-]{20,}\b",

        # AWS access key ID
        r"\bAKIA[0-9A-Z]{16}\b",
    ]

    def is_safe(self, response: str) -> bool:
        """
        Return True when the generated response does not
        contain known sensitive or internal content.
        """

        if not response or not response.strip():
            return True

        normalized_response = response.lower()

        for pattern in self.BLOCKED_PATTERNS:
            if re.search(pattern, normalized_response):
                return False

        for pattern in self.SECRET_PATTERNS:
            if re.search(pattern, response):
                return False

        return True

    def validate(self, response: str) -> None:
        """
        Validate an AI-generated response.

        Raises ValueError when potentially sensitive content
        is detected.
        """

        if not self.is_safe(response):
            raise ValueError(
                "AI response blocked by security guardrail."
            )