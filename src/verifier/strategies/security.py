"""Security verification -- focuses on vulnerabilities and attack surfaces."""

import json
from ..strategy import VerificationStrategy, VerificationResult

PROMPT_TEMPLATE = """You are a security code reviewer. Analyze the following code for SECURITY VULNERABILITIES only.

Focus on:
- Injection vulnerabilities (SQL injection, command injection, XSS, SSTI)
- Race conditions and TOCTOU (time-of-check-to-time-of-use)
- Buffer/memory issues (buffer overflow, use-after-free, memory leaks)
- Authentication/authorization flaws (missing auth checks, privilege escalation)
- Secret exposure (hardcoded credentials, API keys in source, sensitive data in logs)
- Path traversal and file inclusion
- Insecure deserialization
- Cryptographic weaknesses (weak algorithms, improper key management)

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
  "explanation": "detailed explanation of the vulnerability",
  "bug_location": "line/function where vulnerability is",
  "bug_type": "injection|race_condition|memory|auth|secret_exposure|path_traversal|deserialization|crypto|other",
  "severity": "low|medium|high|critical"
}}"""


class SecurityStrategy(VerificationStrategy):
    name = "security"
    description = "Security vulnerability detection"

    def __init__(self, llm_client=None):
        self.llm_client = llm_client

    def verify(self, code: str, spec: str = "", context: str = "") -> VerificationResult:
        spec_section = f"Specification:\n{spec}" if spec else "No specification provided. Analyze based on common security patterns."
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
