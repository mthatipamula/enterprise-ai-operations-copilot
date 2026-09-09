import re


class PIIGuardrails:
    """
    Basic PII detection and redaction for user-provided content.

    The goal is to prevent common sensitive values from being
    passed directly to the LLM.
    """

    PII_PATTERNS = {
        "email": re.compile(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
        ),
        "phone": re.compile(
            r"\b(?:\+?1[-.\s]?)?"
            r"(?:\(?\d{3}\)?[-.\s]?)"
            r"\d{3}[-.\s]?\d{4}\b"
        ),
        "ssn": re.compile(
            r"\b\d{3}-\d{2}-\d{4}\b"
        ),
        "credit_card": re.compile(
            r"\b(?:\d[ -]*?){13,19}\b"
        ),
    }

    def contains_pii(self, text: str) -> bool:
        """
        Return True when common PII is detected.
        """

        if not text:
            return False

        return any(
            pattern.search(text)
            for pattern in self.PII_PATTERNS.values()
        )

    def redact(self, text: str) -> str:
        """
        Replace detected PII with labeled placeholders.
        """

        if not text:
            return text

        sanitized = text

        sanitized = self.PII_PATTERNS["email"].sub(
            "[REDACTED_EMAIL]",
            sanitized,
        )

        sanitized = self.PII_PATTERNS["phone"].sub(
            "[REDACTED_PHONE]",
            sanitized,
        )

        sanitized = self.PII_PATTERNS["ssn"].sub(
            "[REDACTED_SSN]",
            sanitized,
        )

        sanitized = self.PII_PATTERNS["credit_card"].sub(
            "[REDACTED_CREDIT_CARD]",
            sanitized,
        )

        return sanitized