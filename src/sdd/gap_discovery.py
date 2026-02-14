"""Gap discovery — finds missing requirements (addresses T2 mu_R ceiling).

Uses AI to discover requirements not captured in the specification
by analyzing code for untested paths, edge cases, and implicit assumptions.
"""

from dataclasses import dataclass
from typing import List
from .spec_parser import Specification, Requirement


@dataclass
class DiscoveredGap:
    description: str
    category: str
    severity: str  # critical, major, minor
    confidence: float
    evidence: str


class GapDiscovery:
    """Discovers missing requirements through code analysis."""

    def __init__(self, llm_client=None):
        self.llm_client = llm_client

    def discover(self, code: str, spec: Specification,
                 n_iterations: int = 3) -> List[DiscoveredGap]:
        """Iteratively discover requirement gaps.

        Each iteration refines the search based on previous findings.
        Models T2: iterative convergence of requirement completeness.
        """
        all_gaps = []
        known_gaps_text = ""

        for iteration in range(n_iterations):
            new_gaps = self._discover_iteration(
                code, spec, known_gaps_text, iteration
            )
            all_gaps.extend(new_gaps)
            known_gaps_text = "\n".join(
                f"- {g.description}" for g in all_gaps
            )

        return all_gaps

    def _discover_iteration(self, code: str, spec: Specification,
                            known_gaps: str, iteration: int) -> List[DiscoveredGap]:
        """Single iteration of gap discovery."""
        if self.llm_client is None:
            return []

        prompt = f"""Analyze this code and specification to find MISSING requirements.

Specification:
{spec.raw_text}

Code:
```
{code}
```

{"Previously discovered gaps (find NEW ones):" + chr(10) + known_gaps if known_gaps else "This is the first analysis pass."}

Look for:
1. Edge cases not covered by any requirement
2. Error conditions with no specified behavior
3. Implicit assumptions not documented
4. Security considerations not addressed
5. Performance constraints not specified

Iteration {iteration + 1}: {"Look for subtle, non-obvious gaps." if iteration > 0 else "Start with the most critical gaps."}

List each gap as JSON array:
[{{"description": "...", "category": "functional|security|performance|edge_case", "severity": "critical|major|minor", "confidence": 0.0-1.0, "evidence": "..."}}]"""

        response = self.llm_client.complete(prompt)
        return self._parse_gaps(response)

    def _parse_gaps(self, response: str) -> List[DiscoveredGap]:
        import json
        try:
            start = response.find('[')
            end = response.rfind(']') + 1
            if start >= 0 and end > start:
                data = json.loads(response[start:end])
                return [
                    DiscoveredGap(
                        description=g.get("description", ""),
                        category=g.get("category", "functional"),
                        severity=g.get("severity", "minor"),
                        confidence=float(g.get("confidence", 0.5)),
                        evidence=g.get("evidence", ""),
                    )
                    for g in data
                ]
        except (json.JSONDecodeError, ValueError):
            pass
        return []

    def mu_R_improvement(self, original_mu_R: float, n_gaps_found: int,
                         n_total_estimated: int) -> float:
        """Estimate improved mu_R after gap discovery.

        mu_R_new = mu_R_old + (discovered / estimated_total) * (1 - mu_R_old)
        """
        if n_total_estimated <= 0:
            return original_mu_R
        discovery_rate = min(n_gaps_found / n_total_estimated, 1.0)
        return original_mu_R + discovery_rate * (1.0 - original_mu_R)
