"""Type safety verification -- focuses on type mismatches and type-related bugs."""

import json
from ..strategy import VerificationStrategy, VerificationResult

PROMPT_TEMPLATE = """You are a type safety analyst. Analyze the following code for TYPE-RELATED BUGS only.

Focus on:
- Type mismatches (passing wrong type to function, returning wrong type)
- Implicit conversions that lose data (float to int, string to number)
- Null/None handling (calling methods on None, missing null checks)
- Generic type violations (wrong element type in collection, type parameter mismatch)
- Attribute errors (accessing non-existent attributes, wrong object type)
- Index type errors (using wrong type as dict key or list index)
- Callable type errors (calling non-callable, wrong argument count/types)
- Union type pitfalls (unhandled variant, unsafe narrowing)

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
  "explanation": "detailed explanation of the type safety issue",
  "bug_location": "line/function where type error occurs",
  "bug_type": "type_mismatch|implicit_conversion|null_handling|generic_violation|attribute_error|index_error|callable_error|other",
  "severity": "low|medium|high|critical"
}}"""


class TypeSafetyStrategy(VerificationStrategy):
    name = "type_safety"
    description = "Type safety and type mismatch verification"

    def __init__(self, llm_client=None):
        self.llm_client = llm_client

    def verify(self, code: str, spec: str = "", context: str = "") -> VerificationResult:
        spec_section = f"Specification:\n{spec}" if spec else "No specification provided. Analyze based on type hints, docstrings, and usage patterns."
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
