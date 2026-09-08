from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class EvaluationCase:
    """
    Defines one test case for evaluating the Operations Agent.

    The expected values describe what the agent should do,
    not the exact wording of the generated answer.
    """

    case_id: str
    query: str
    expected_route: str
    expected_tool: Optional[str] = None
    expected_source: Optional[str] = None
    expected_grounded: Optional[bool] = None
    expected_abstained: Optional[bool] = None


EVALUATION_DATASET = [
    EvaluationCase(
        case_id="rag_http_503",
        query="What should I do when the payment service returns HTTP 503?",
        expected_route="rag",
        expected_source="payment-api-runbook.md",
        expected_grounded=True,
        expected_abstained=False,
    ),

    EvaluationCase(
        case_id="tool_payment_status",
        query="What is the current payment service status?",
        expected_route="tool",
        expected_tool="incident_status",
    ),

    EvaluationCase(
        case_id="tool_customer_status",
        query="What is the current customer service status?",
        expected_route="tool",
        expected_tool="incident_status",
    ),

    EvaluationCase(
        case_id="rag_retry_policy",
        query="What is the maximum retry limit for the Payment API?",
        expected_route="rag",
        expected_source="payment-api-runbook.md",
        expected_grounded=True,
        expected_abstained=False,
    ),

    EvaluationCase(
        case_id="rag_out_of_knowledge",
        query="What is the company's policy for international stock trading?",
        expected_route="rag",
        expected_abstained=True,
    ),
]