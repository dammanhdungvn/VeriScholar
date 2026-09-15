"""Base runner specification and protocol for API evaluation harness."""

from abc import ABC, abstractmethod
from typing import Any

from scripts.eval.config import QualityBudget
from scripts.eval.context import EvaluationContext


class BaseAPIRunner(ABC):
    """Abstract base class for all individual API snapshot evaluators."""

    endpoint_name: str
    report_filename: str
    http_method: str
    route_path: str
    budget: QualityBudget = QualityBudget()

    def __init__(
        self,
        endpoint_name: str = "",
        report_filename: str = "",
        http_method: str = "",
        route_path: str = "",
        budget: QualityBudget | None = None,
    ):
        if endpoint_name:
            self.endpoint_name = endpoint_name
        if report_filename:
            self.report_filename = report_filename
        if http_method:
            self.http_method = http_method
        if route_path:
            self.route_path = route_path
        if budget is not None:
            self.budget = budget

    @abstractmethod
    async def evaluate(self, ctx: EvaluationContext, **kwargs: Any) -> dict[str, Any]:
        """Execute evaluation against API endpoint and return detailed metrics dictionary."""
        pass

    @abstractmethod
    def generate_markdown(self, eval_result: dict[str, Any], session_tag: str) -> str:
        """Render markdown report content adhering to the canonical template."""
        pass
