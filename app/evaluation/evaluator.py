from dataclasses import dataclass
from typing import Optional

from app.agents.operations_agent import OperationsAgent
from app.evaluation.dataset import EvaluationCase


@dataclass
class EvaluationResult:
    """
    Captures the actual result produced by the Operations Agent
    for one evaluation case.
    """

    case_id: str
    query: str
    actual_route: str
    actual_tool: Optional[str]
    actual_source: Optional[str]
    actual_grounded: bool
    actual_abstained: bool
    passed: bool


class AgentEvaluator:
    """
    Executes evaluation cases against the Operations Agent.
    """

    def __init__(self, agent: Optional[OperationsAgent] = None):
        self.agent = agent or OperationsAgent()

    def evaluate_case(self, case: EvaluationCase) -> EvaluationResult:
        """
        Execute one evaluation case and compare the actual
        agent behavior with the expected behavior.
        """

        result = self.agent.run(
            query=case.query,
            session_id=f"evaluation-{case.case_id}",
        )

        actual_route = result.get("route", "")
        actual_tool = result.get("tool")
        sources = result.get("sources", [])

        actual_source = None
        if sources:
            actual_source = sources[0].get("source")

        actual_grounded = result.get("grounded", False)
        actual_abstained = result.get("abstained", False)

        passed = self._is_match(
            case=case,
            actual_route=actual_route,
            actual_tool=actual_tool,
            actual_source=actual_source,
            actual_grounded=actual_grounded,
            actual_abstained=actual_abstained,
        )

        return EvaluationResult(
            case_id=case.case_id,
            query=case.query,
            actual_route=actual_route,
            actual_tool=actual_tool,
            actual_source=actual_source,
            actual_grounded=actual_grounded,
            actual_abstained=actual_abstained,
            passed=passed,
        )

    @staticmethod
    def _is_match(
        case: EvaluationCase,
        actual_route: str,
        actual_tool: Optional[str],
        actual_source: Optional[str],
        actual_grounded: bool,
        actual_abstained: bool,
    ) -> bool:
        """
        Compare actual agent behavior against the expectations
        defined in the evaluation dataset.
        """

        if actual_route != case.expected_route:
            return False

        if (
            case.expected_tool is not None
            and actual_tool != case.expected_tool
        ):
            return False

        if (
            case.expected_source is not None
            and actual_source != case.expected_source
        ):
            return False

        if (
            case.expected_grounded is not None
            and actual_grounded != case.expected_grounded
        ):
            return False

        if (
            case.expected_abstained is not None
            and actual_abstained != case.expected_abstained
        ):
            return False

        return True