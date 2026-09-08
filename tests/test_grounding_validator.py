from app.rag.grounding_validator import GroundingValidator


def test_grounded_answer():
    validator = GroundingValidator()

    retrieved_chunks = [
        {
            "source": "payment-api-runbook.md",
            "content": (
                "The Payment API supports a maximum of "
                "three retry attempts for transient failures. "
                "Retries should use exponential backoff."
            ),
        }
    ]

    answer = (
        "The Payment API supports a maximum of three retry "
        "attempts for transient failures."
    )

    result = validator.validate(
        answer=answer,
        retrieved_chunks=retrieved_chunks,
    )

    assert result["grounded"] is True


def test_ungrounded_answer():
    validator = GroundingValidator()

    retrieved_chunks = [
        {
            "source": "payment-api-runbook.md",
            "content": (
                "The Payment API supports a maximum of "
                "three retry attempts for transient failures."
            ),
        }
    ]

    answer = (
        "The Payment API supports a maximum of ten retry "
        "attempts for transient failures."
    )

    result = validator.validate(
        answer=answer,
        retrieved_chunks=retrieved_chunks,
    )

    assert result["grounded"] is False


def test_no_evidence():
    validator = GroundingValidator()

    result = validator.validate(
        answer="The service supports three retries.",
        retrieved_chunks=[],
    )

    assert result["grounded"] is False