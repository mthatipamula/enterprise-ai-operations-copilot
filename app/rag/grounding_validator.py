import re


class GroundingValidator:
    """
    Validates whether an LLM-generated answer is grounded
    in the retrieved knowledge-base context.

    This initial implementation detects unsupported
    factual values such as numbers, limits, and HTTP
    status codes.
    """

    NUMBER_WORDS = {
        "zero",
        "one",
        "two",
        "three",
        "four",
        "five",
        "six",
        "seven",
        "eight",
        "nine",
        "ten",
    }

    def _extract_factual_values(self, text: str) -> set[str]:
        """
        Extract potentially important factual values from text.

        Currently detects:
        - Numbers
        - Common number words
        - HTTP status codes
        """

        values = set()

        text_lower = text.lower()

        # Extract numeric values such as:
        # 3, 10, 503, 2.5
        numbers = re.findall(
            r"\b\d+(?:\.\d+)?\b",
            text_lower,
        )

        values.update(numbers)

        # Extract common number words such as:
        # three, ten
        for number_word in self.NUMBER_WORDS:
            if re.search(
                rf"\b{number_word}\b",
                text_lower,
            ):
                values.add(number_word)

        # Explicitly capture HTTP status codes.
        http_codes = re.findall(
            r"\b(?:HTTP\s*)?[1-5]\d{2}\b",
            text_lower,
            flags=re.IGNORECASE,
        )

        values.update(
            code.replace("http", "").strip()
            for code in http_codes
        )

        return values

    def validate(
        self,
        answer: str,
        retrieved_chunks: list[dict],
    ) -> dict:
        """
        Validate whether the answer is supported by
        the retrieved knowledge-base content.
        """

        if not answer.strip():
            return {
                "grounded": False,
                "reason": "Answer is empty.",
            }

        if not retrieved_chunks:
            return {
                "grounded": False,
                "reason": "No evidence was retrieved.",
            }

        context = " ".join(
            chunk["content"]
            for chunk in retrieved_chunks
        )

        answer_values = self._extract_factual_values(
            answer
        )

        context_values = self._extract_factual_values(
            context
        )

        unsupported_values = (
            answer_values - context_values
        )

        if unsupported_values:
            return {
                "grounded": False,
                "reason": (
                    "Answer contains factual values that "
                    "are not supported by the retrieved evidence."
                ),
                "unsupported_values": sorted(
                    unsupported_values
                ),
            }

        return {
            "grounded": True,
            "reason": (
                "Answer is supported by the retrieved evidence."
            ),
            "unsupported_values": [],
        }