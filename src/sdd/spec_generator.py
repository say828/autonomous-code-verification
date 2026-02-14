"""AI specification generator — generates specs from code analysis.

Based on Insight #31: AI-generated specs can outperform human specs
for verification (TPR 1.000 vs 0.900).
"""

from .spec_parser import Specification, Requirement


class SpecGenerator:
    """Generates structured specifications from code using LLM."""

    def __init__(self, llm_client=None):
        self.llm_client = llm_client

    def generate(self, code: str, context: str = "") -> Specification:
        """Generate specification from code analysis."""
        if self.llm_client is None:
            return Specification(title="Generated", raw_text="No LLM client")

        prompt = f"""Analyze this code and generate a complete specification document.

Code:
```
{code}
```

{f"Context: {context}" if context else ""}

Generate a specification that covers:
1. Functional requirements (what the code should do)
2. Input/output contracts (valid inputs, expected outputs)
3. Edge cases (boundary values, error conditions)
4. Type constraints (expected types, null handling)
5. Performance expectations (if applicable)

Format as markdown with bullet points. Each bullet = one requirement.
Use MUST/SHOULD/COULD for priority."""

        response = self.llm_client.complete(prompt)

        from .spec_parser import parse_markdown_spec
        spec = parse_markdown_spec(response, title="AI-Generated Specification")
        return spec

    def generate_from_diff(self, diff: str, context: str = "") -> Specification:
        """Generate specification from a code diff (for review)."""
        if self.llm_client is None:
            return Specification(title="Generated from diff", raw_text="No LLM client")

        prompt = f"""Analyze this code change and generate requirements that the change should satisfy.

Diff:
```
{diff}
```

{f"Context: {context}" if context else ""}

Focus on:
1. What behavior is being changed or added?
2. What invariants should be maintained?
3. What edge cases might be affected?

Format as markdown bullet points."""

        response = self.llm_client.complete(prompt)
        from .spec_parser import parse_markdown_spec
        return parse_markdown_spec(response, title="Diff Specification")
