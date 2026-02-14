"""Specification parser — extracts structured requirements from text.

Parses various spec formats (markdown, docstrings, issue descriptions)
into structured requirement objects for compliance checking.
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Requirement:
    id: str
    description: str
    category: str = "functional"  # functional, performance, security, edge_case
    priority: str = "must"  # must, should, could
    testable: bool = True
    source_line: int = 0


@dataclass
class Specification:
    title: str
    requirements: List[Requirement] = field(default_factory=list)
    raw_text: str = ""

    @property
    def n_requirements(self) -> int:
        return len(self.requirements)

    def must_requirements(self) -> List[Requirement]:
        return [r for r in self.requirements if r.priority == "must"]

    def testable_requirements(self) -> List[Requirement]:
        return [r for r in self.requirements if r.testable]


def parse_markdown_spec(text: str, title: str = "") -> Specification:
    """Parse markdown-formatted specification into structured requirements."""
    requirements = []
    req_id = 0

    # Pattern: lines starting with - or * or numbered
    lines = text.strip().split('\n')
    current_category = "functional"

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Detect category headers
        if stripped.startswith('#'):
            header = stripped.lstrip('#').strip().lower()
            if 'security' in header:
                current_category = "security"
            elif 'performance' in header or 'speed' in header:
                current_category = "performance"
            elif 'edge' in header or 'boundary' in header:
                current_category = "edge_case"
            else:
                current_category = "functional"
            continue

        # Detect requirements (bullet points or numbered items)
        match = re.match(r'^[\-\*]\s+(.+)$', stripped)
        if not match:
            match = re.match(r'^\d+[\.\)]\s+(.+)$', stripped)

        if match:
            req_text = match.group(1)
            req_id += 1

            # Detect priority
            priority = "must"
            if req_text.lower().startswith(("should", "ideally", "optionally")):
                priority = "should"
            elif req_text.lower().startswith(("could", "nice to", "may")):
                priority = "could"

            requirements.append(Requirement(
                id=f"R{req_id:03d}",
                description=req_text,
                category=current_category,
                priority=priority,
                source_line=i + 1,
            ))

    return Specification(
        title=title or "Parsed Specification",
        requirements=requirements,
        raw_text=text,
    )


def parse_docstring_spec(docstring: str, func_name: str = "") -> Specification:
    """Parse function docstring into specification."""
    requirements = []
    req_id = 0

    lines = docstring.strip().split('\n')
    in_args = False
    in_returns = False
    in_raises = False

    for line in lines:
        stripped = line.strip()

        if stripped.lower().startswith(('args:', 'parameters:', 'params:')):
            in_args = True
            in_returns = False
            in_raises = False
            continue
        elif stripped.lower().startswith(('returns:', 'return:')):
            in_args = False
            in_returns = True
            in_raises = False
            req_id += 1
            requirements.append(Requirement(
                id=f"R{req_id:03d}",
                description=f"Returns: {stripped.split(':', 1)[-1].strip()}",
                category="functional",
            ))
            continue
        elif stripped.lower().startswith(('raises:', 'raise:')):
            in_args = False
            in_returns = False
            in_raises = True
            continue

        if in_raises and stripped:
            req_id += 1
            requirements.append(Requirement(
                id=f"R{req_id:03d}",
                description=f"Should raise {stripped}",
                category="edge_case",
            ))

    # First line is usually the summary
    if lines and lines[0].strip():
        req_id += 1
        requirements.insert(0, Requirement(
            id=f"R{req_id:03d}",
            description=lines[0].strip(),
            category="functional",
            priority="must",
        ))

    return Specification(
        title=func_name or "Function Specification",
        requirements=requirements,
        raw_text=docstring,
    )


def parse_issue_spec(issue_text: str) -> Specification:
    """Parse GitHub issue text into specification."""
    return parse_markdown_spec(issue_text, title="Issue Specification")
