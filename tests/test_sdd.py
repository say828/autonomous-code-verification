"""Tests for SDD framework."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from sdd.spec_parser import parse_markdown_spec, parse_docstring_spec, Specification


class TestSpecParser:
    def test_parse_bullet_points(self):
        text = """# Requirements
- Must accept positive integers
- Should handle zero gracefully
- Must return sorted list"""
        spec = parse_markdown_spec(text)
        assert spec.n_requirements == 3

    def test_parse_numbered_list(self):
        text = """1. Input validation
2. Error handling
3. Output formatting"""
        spec = parse_markdown_spec(text)
        assert spec.n_requirements == 3

    def test_parse_priority(self):
        text = """- Must validate input
- Should log errors
- Could cache results"""
        spec = parse_markdown_spec(text)
        priorities = [r.priority for r in spec.requirements]
        assert priorities == ["must", "should", "could"]

    def test_parse_categories(self):
        text = """# Functional
- Process data correctly
# Security
- Validate all inputs
# Edge Cases
- Handle empty input"""
        spec = parse_markdown_spec(text)
        categories = [r.category for r in spec.requirements]
        assert "functional" in categories
        assert "security" in categories
        assert "edge_case" in categories

    def test_must_requirements_filter(self):
        text = """- Must do A
- Should do B
- Must do C"""
        spec = parse_markdown_spec(text)
        must = spec.must_requirements()
        assert len(must) == 2

    def test_docstring_parsing(self):
        doc = """Compute factorial of n.

        Args:
            n: Non-negative integer

        Returns:
            n! as integer

        Raises:
            ValueError: if n < 0
        """
        spec = parse_docstring_spec(doc, "factorial")
        assert spec.n_requirements > 0
