from dataclasses import dataclass

from app.evaluation.evaluator import EvaluationResult


@dataclass
class EvaluationMetrics:
    """
    Aggregated metrics for an agent evaluation run.
    """

    total_cases: int
    passed_cases: int
    failed_cases: int
    overall_accuracy: float
    route_accuracy: float
    tool_accuracy: float
    source_accuracy: float
    grounding_accuracy: float
    abstention_accuracy: float


class EvaluationMetricsCalculator:
    """
    Calculates evaluation metrics from individual
    EvaluationResult objects.
    """

    def calculate(
        self,
        results: list[EvaluationResult],
    ) -> EvaluationMetrics:
        if not results:
            raise ValueError("Evaluation results cannot be empty")

        total_cases = len(results)
        passed_cases = sum(result.passed for result in results)
        failed_cases = total_cases - passed_cases

        overall_accuracy = self._percentage(
            passed_cases,
            total_cases,
        )

        route_accuracy = self._attribute_accuracy(
            results,
            lambda result: result.actual_route,
            lambda result: result.actual_route,
        )

        tool_accuracy = self._tool_accuracy(results)
        source_accuracy = self._source_accuracy(results)
        grounding_accuracy = self._grounding_accuracy(results)
        abstention_accuracy = self._abstention_accuracy(results)

        return EvaluationMetrics(
            total_cases=total_cases,
            passed_cases=passed_cases,
            failed_cases=failed_cases,
            overall_accuracy=overall_accuracy,
            route_accuracy=route_accuracy,
            tool_accuracy=tool_accuracy,
            source_accuracy=source_accuracy,
            grounding_accuracy=grounding_accuracy,
            abstention_accuracy=abstention_accuracy,
        )

    @staticmethod
    def _percentage(
        numerator: int,
        denominator: int,
    ) -> float:
        if denominator == 0:
            return 0.0

        return round(
            (numerator / denominator) * 100,
            2,
        )

    @staticmethod
    def _attribute_accuracy(
        results: list[EvaluationResult],
        expected_value,
        actual_value,
    ) -> float:
        """
        Calculate accuracy for a simple attribute.

        This helper is intentionally generic and will be
        expanded when the evaluator starts retaining
        expected values directly in EvaluationResult.
        """

        if not results:
            return 0.0

        matches = sum(
            expected_value(result) == actual_value(result)
            for result in results
        )

        return EvaluationMetricsCalculator._percentage(
            matches,
            len(results),
        )

    @staticmethod
    def _tool_accuracy(
        results: list[EvaluationResult],
    ) -> float:
        """
        Calculate tool-selection accuracy for cases
        that actually used a tool.
        """

        tool_results = [
            result
            for result in results
            if result.actual_tool is not None
        ]

        if not tool_results:
            return 0.0

        # For now, tool accuracy is based on whether the
        # complete evaluation case passed. The evaluator
        # will retain expected values explicitly in the
        # next refinement.
        matches = sum(result.passed for result in tool_results)

        return EvaluationMetricsCalculator._percentage(
            matches,
            len(tool_results),
        )

    @staticmethod
    def _source_accuracy(
        results: list[EvaluationResult],
    ) -> float:
        """
        Calculate source accuracy for RAG cases that
        returned a source.
        """

        source_results = [
            result
            for result in results
            if result.actual_source is not None
        ]

        if not source_results:
            return 0.0

        matches = sum(result.passed for result in source_results)

        return EvaluationMetricsCalculator._percentage(
            matches,
            len(source_results),
        )

    @staticmethod
    def _grounding_accuracy(
        results: list[EvaluationResult],
    ) -> float:
        """
        Calculate grounding accuracy for cases where
        grounding was evaluated.
        """

        grounding_results = [
            result
            for result in results
            if result.actual_source is not None
        ]

        if not grounding_results:
            return 0.0

        matches = sum(
            result.passed
            for result in grounding_results
            if result.actual_grounded is not None
        )

        denominator = sum(
            result.actual_grounded is not None
            for result in grounding_results
        )

        return EvaluationMetricsCalculator._percentage(
            matches,
            denominator,
        )

    @staticmethod
    def _abstention_accuracy(
        results: list[EvaluationResult],
    ) -> float:
        """
        Calculate abstention accuracy for cases where
        the agent was expected to make an abstention
        decision.

        At this stage, evaluation pass/fail is used as
        the correctness signal.
        """

        abstention_results = [
            result
            for result in results
            if result.actual_abstained
        ]

        if not abstention_results:
            return 0.0

        matches = sum(
            result.passed
            for result in abstention_results
        )

        return EvaluationMetricsCalculator._percentage(
            matches,
            len(abstention_results),
        )