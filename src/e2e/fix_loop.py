"""Self-correction fix loop — T6 convergence implementation.

Implements: test -> analyze failure -> fix -> re-test -> repeat
Converges via Banach contraction mapping.
"""

import json
from dataclasses import dataclass, field
from typing import List, Optional
from .test_runner import TestRunner, TestSuiteResult


@dataclass
class FixAttempt:
    round: int
    test_result: TestSuiteResult
    fix_description: str = ""
    code_before: str = ""
    code_after: str = ""
    fixed_tests: List[str] = field(default_factory=list)
    new_failures: List[str] = field(default_factory=list)


@dataclass
class FixLoopResult:
    attempts: List[FixAttempt] = field(default_factory=list)
    converged: bool = False
    final_pass_rate: float = 0.0
    total_rounds: int = 0

    @property
    def convergence_trajectory(self) -> List[float]:
        return [a.test_result.pass_rate for a in self.attempts]

    @property
    def contraction_rates(self) -> List[float]:
        """Compute contraction rate between consecutive rounds."""
        rates = []
        traj = self.convergence_trajectory
        for i in range(1, len(traj)):
            gap_before = 1.0 - traj[i - 1]
            gap_after = 1.0 - traj[i]
            if gap_before > 0:
                rates.append(gap_after / gap_before)
        return rates


class FixLoop:
    """Automated fix loop with convergence detection."""

    def __init__(self, test_runner: TestRunner, llm_client=None,
                 max_rounds: int = 10, target_pass_rate: float = 1.0):
        self.test_runner = test_runner
        self.llm_client = llm_client
        self.max_rounds = max_rounds
        self.target_pass_rate = target_pass_rate

    def run(self, code: str, test_path: str = "tests/") -> FixLoopResult:
        """Execute the fix loop until convergence or max rounds."""
        result = FixLoopResult()
        current_code = code

        for round_num in range(self.max_rounds):
            # Run tests
            test_result = self.test_runner.run(test_path)

            attempt = FixAttempt(
                round=round_num + 1,
                test_result=test_result,
                code_before=current_code,
            )

            # Check convergence
            if test_result.all_passed or test_result.pass_rate >= self.target_pass_rate:
                attempt.fix_description = "All tests passing — converged"
                result.attempts.append(attempt)
                result.converged = True
                break

            # Analyze failures and propose fix
            if self.llm_client is not None:
                fix = self._propose_fix(current_code, test_result)
                attempt.fix_description = fix.get('description', '')
                attempt.code_after = fix.get('fixed_code', current_code)
                current_code = attempt.code_after

            result.attempts.append(attempt)

        result.total_rounds = len(result.attempts)
        if result.attempts:
            result.final_pass_rate = result.attempts[-1].test_result.pass_rate

        return result

    def _propose_fix(self, code: str, test_result: TestSuiteResult) -> dict:
        """Use LLM to propose a fix for failing tests."""
        failures = test_result.failed_tests()
        failure_text = "\n".join(
            f"- {f.name}: {f.error}" for f in failures[:5]
        )

        prompt = f"""Fix the following test failures.

Code:
```
{code}
```

Failing tests:
{failure_text}

Respond with:
1. Brief description of the fix
2. The corrected code

Format:
{{"description": "...", "fixed_code": "..."}}"""

        response = self.llm_client.complete(prompt)
        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                return json.loads(response[start:end])
        except (json.JSONDecodeError, ValueError):
            pass
        return {'description': 'Failed to parse fix', 'fixed_code': code}
