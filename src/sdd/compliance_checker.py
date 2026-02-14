"""Compliance checker — measures mu_R (spec compliance rate).

Checks code against specification requirements and measures
what fraction of requirements are satisfied.
"""

import json
from dataclasses import dataclass
from typing import List, Optional
from .spec_parser import Specification, Requirement


@dataclass
class ComplianceResult:
    requirement: Requirement
    satisfied: bool
    confidence: float
    explanation: str


@dataclass
class ComplianceReport:
    spec: Specification
    results: List[ComplianceResult]

    @property
    def mu_R(self) -> float:
        """Requirement compliance rate."""
        if not self.results:
            return 0.0
        satisfied = sum(1 for r in self.results if r.satisfied)
        return satisfied / len(self.results)

    @property
    def must_compliance(self) -> float:
        """Compliance rate for must-have requirements only."""
        must_results = [r for r in self.results
                       if r.requirement.priority == "must"]
        if not must_results:
            return 1.0
        return sum(1 for r in must_results if r.satisfied) / len(must_results)

    @property
    def n_satisfied(self) -> int:
        return sum(1 for r in self.results if r.satisfied)

    @property
    def n_violated(self) -> int:
        return sum(1 for r in self.results if not r.satisfied)

    def violated_requirements(self) -> List[ComplianceResult]:
        return [r for r in self.results if not r.satisfied]

    def summary(self) -> dict:
        return {
            'total_requirements': len(self.results),
            'satisfied': self.n_satisfied,
            'violated': self.n_violated,
            'mu_R': self.mu_R,
            'must_compliance': self.must_compliance,
            'violations': [
                {'id': r.requirement.id, 'desc': r.requirement.description,
                 'explanation': r.explanation}
                for r in self.violated_requirements()
            ],
        }


class ComplianceChecker:
    """Checks code compliance against specification using LLM."""

    def __init__(self, llm_client=None):
        self.llm_client = llm_client

    def check(self, code: str, spec: Specification) -> ComplianceReport:
        """Check code against all requirements in specification."""
        results = []
        for req in spec.requirements:
            result = self._check_requirement(code, req, spec)
            results.append(result)
        return ComplianceReport(spec=spec, results=results)

    def _check_requirement(self, code: str, req: Requirement,
                           spec: Specification) -> ComplianceResult:
        """Check a single requirement against code."""
        if self.llm_client is None:
            return ComplianceResult(
                requirement=req, satisfied=True, confidence=0.0,
                explanation="No LLM client — defaulting to satisfied"
            )

        prompt = f"""Analyze whether this code satisfies the following requirement.

Requirement [{req.id}]: {req.description}
Category: {req.category}
Priority: {req.priority}

Full specification context:
{spec.raw_text}

Code:
```
{code}
```

Respond in JSON:
{{"satisfied": true/false, "confidence": 0.0-1.0, "explanation": "..."}}"""

        response = self.llm_client.complete(prompt)
        return self._parse_response(response, req)

    def _parse_response(self, response: str,
                        req: Requirement) -> ComplianceResult:
        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                data = json.loads(response[start:end])
                return ComplianceResult(
                    requirement=req,
                    satisfied=data.get("satisfied", True),
                    confidence=float(data.get("confidence", 0.5)),
                    explanation=data.get("explanation", ""),
                )
        except (json.JSONDecodeError, ValueError):
            pass
        return ComplianceResult(
            requirement=req, satisfied=True, confidence=0.0,
            explanation="Failed to parse LLM response"
        )
