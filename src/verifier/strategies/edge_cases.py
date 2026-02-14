"""Edge case verification -- focuses on boundary conditions and unusual inputs."""

import json
from ..strategy import VerificationStrategy, VerificationResult

PROMPT_TEMPLATE = """You are an edge case analyst. Analyze the following code for EDGE CASE FAILURES only.

Focus on:
- Boundary values (empty collections, zero, negative numbers, max int, min int)
- Type edge cases (None/null, NaN, infinity, empty string, unicode)
- Concurrency issues (thread safety, deadlocks, starvation)
- Resource exhaustion (infinite loops, unbounded memory, file handle leaks)
- State edge cases (uninitialized state, double initialization, use after close)
- Input combinations that trigger unexpected behavior
- Division by zero, modulo zero, log of zero/negative

{spec_section}

Code to review:
```
{code}
```

{context_section}

Respond in JSON format:
{{
  "has_bug": true/false,
  "confidence": 0.0-1.0,
  "explanation": "detailed explanation of the edge case failure",
  "bug_location": "line/function where edge case fails",
  "bug_type": "boundary|null_handling|concurrency|resource_exhaustion|state|division_by_zero|other",
  "severity": "low|medium|high|critical"
}}"""


class EdgeCaseStrategy(VerificationStrategy):
    name = "edge_cases"
    description = "Edge case and boundary condition verification"

    def __init__(self, llm_client=None):
        self.llm_client = llm_client

    def verify(self, code: str, spec: str = "", context: str = "") -> VerificationResult:
        spec_section = f"Specification:\n{spec}" if spec else "No specification provided. Analyze based on function signatures and common edge cases."
        context_section = f"Additional context:\n{context}" if context else ""

        prompt = PROMPT_TEMPLATE.format(
            code=code, spec_section=spec_section, context_section=context_section
        )

        if self.llm_client is None:
            return self._create_result(False, 0.0, "No LLM client configured")

        response = self.llm_client.complete(prompt)
        return self._parse_response(response)

    def _parse_response(self, response: str) -> VerificationResult:
        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                data = json.loads(response[start:end])
                return self._create_result(
                    has_bug=data.get("has_bug", False),
                    confidence=float(data.get("confidence", 0.5)),
                    explanation=data.get("explanation", ""),
                    bug_location=data.get("bug_location", ""),
                    bug_type=data.get("bug_type", ""),
                    severity=data.get("severity", "medium"),
                    raw_response=response,
                )
        except (json.JSONDecodeError, ValueError):
            pass
        return self._create_result(False, 0.0, "Failed to parse response", raw_response=response)
