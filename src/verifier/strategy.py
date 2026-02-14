"""Base verification strategy interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class VerificationResult:
    strategy_name: str
    has_bug: bool
    confidence: float  # 0.0 to 1.0
    explanation: str
    bug_location: str = ""
    bug_type: str = ""
    severity: str = "medium"  # low, medium, high, critical
    raw_response: str = ""


class VerificationStrategy(ABC):
    """Base class for all verification strategies."""

    name: str = "base"
    description: str = "Base verification strategy"

    @abstractmethod
    def verify(self, code: str, spec: str = "", context: str = "") -> VerificationResult:
        """Verify code against specification.

        Args:
            code: Source code to verify
            spec: Specification/requirements (optional)
            context: Additional context (optional)

        Returns:
            VerificationResult with findings
        """
        pass

    def _create_result(self, has_bug: bool, confidence: float,
                       explanation: str, **kwargs) -> VerificationResult:
        return VerificationResult(
            strategy_name=self.name,
            has_bug=has_bug,
            confidence=confidence,
            explanation=explanation,
            **kwargs
        )
