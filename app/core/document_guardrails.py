import re


class DocumentGuardrails:
    """
    Basic security guardrails for content retrieved from
    enterprise knowledge documents.

    Detects instruction-like content that could be used
    for indirect prompt injection.
    """

    INJECTION_PATTERNS = [
        r"ignore\s+(all\s+)?previous\s+instructions",
        r"ignore\s+(all\s+)?prior\s+instructions",
        r"disregard\s+(all\s+)?previous\s+instructions",
        r"disregard\s+(all\s+)?prior\s+instructions",
        r"forget\s+(all\s+)?previous\s+instructions",
        r"reveal\s+(your|the)\s+(system\s+)?prompt",
        r"show\s+(me\s+)?your\s+(system\s+)?prompt",
        r"bypass\s+(the\s+)?security",
        r"bypass\s+(the\s+)?guardrails",
        r"disable\s+(the\s+)?guardrails",
        r"developer\s+message",
        r"system\s+message",
        r"act\s+as\s+if\s+you\s+have\s+no\s+restrictions",
    ]

    def is_safe(self, content: str) -> bool:
        """
        Return True when document content does not contain
        known indirect prompt-injection patterns.
        """

        if not content or not content.strip():
            return True

        normalized_content = content.lower()

        return not any(
            re.search(pattern, normalized_content)
            for pattern in self.INJECTION_PATTERNS
        )

    def validate(self, content: str) -> None:
        """
        Validate retrieved document content.

        Raises ValueError when suspicious instruction-like
        content is detected.
        """

        if not self.is_safe(content):
            raise ValueError(
                "Retrieved document content blocked by security guardrail."
            )