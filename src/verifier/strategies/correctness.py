"""Correctness verification -- focuses on logic errors, algorithm correctness."""

import json
from ..strategy import VerificationStrategy, VerificationResult

PROMPT_TEMPLATE = """You are a code correctness reviewer. Analyze the following code for LOGIC ERRORS only.

Focus on:
- Algorithm correctness (off-by-one, wrong conditions, missing cases)
- Data flow errors (wrong variable used, incorrect return value)
- Control flow errors (wrong loop bounds, missing breaks, fall-through)
- Mathematical errors (wrong formula, integer overflow, precision loss)

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
  "explanation": "detailed explanation",
  "bug_location": "line/function where bug is",
  "bug_type": "off_by_one|wrong_variable|logic_error|missing_case|other",
  "severity": "low|medium|high|critical"
}}"""


class CorrectnessStrategy(VerificationStrategy):
    name = "correctness"
    description = "Logic and algorithm correctness verification"

    def __init__(self, llm_client=None):
        self.llm_client = llm_client

    def verify(self, code: str, spec: str = "", context: str = "") -> VerificationResult:
        spec_section = f"Specification:\n{spec}" if spec else "No specification provided. Analyze based on function name and docstring."
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
