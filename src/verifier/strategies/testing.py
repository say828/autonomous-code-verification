"""Testing verification -- focuses on generating test cases that expose bugs."""

import json
from ..strategy import VerificationStrategy, VerificationResult

PROMPT_TEMPLATE = """You are a test generation expert. Analyze the following code by MENTALLY SIMULATING test cases to find bugs.

Your approach:
1. Generate concrete test inputs (include boundary values, typical values, adversarial inputs)
2. Mentally trace through the code with each input
3. Compare the actual output against the expected output
4. Identify any inputs where the code produces incorrect results

Focus on:
- Concrete test cases with specific input values and expected outputs
- Tracing execution paths step by step
- Finding inputs that trigger incorrect behavior
- Identifying untested code paths (dead code, unreachable branches)
- Regression-prone patterns (code that is fragile under small changes)

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
  "explanation": "describe the failing test case: input, expected output, actual output, and why it fails",
  "bug_location": "line/function where the bug manifests",
  "bug_type": "wrong_output|crash|infinite_loop|untested_path|regression_prone|other",
  "severity": "low|medium|high|critical"
}}"""


class TestingStrategy(VerificationStrategy):
    name = "testing"
    description = "Test case generation and mental simulation verification"

    def __init__(self, llm_client=None):
        self.llm_client = llm_client

    def verify(self, code: str, spec: str = "", context: str = "") -> VerificationResult:
        spec_section = f"Specification:\n{spec}" if spec else "No specification provided. Derive expected behavior from function name, docstring, and code logic."
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
