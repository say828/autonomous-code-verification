"""Test runner — executes tests and captures results."""

import subprocess
import json
import os
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class TestResult:
    name: str
    passed: bool
    output: str = ""
    error: str = ""
    duration: float = 0.0


@dataclass
class TestSuiteResult:
    results: List[TestResult] = field(default_factory=list)
    total_duration: float = 0.0

    @property
    def n_passed(self) -> int:
        return sum(1 for r in self.results if r.passed)

    @property
    def n_failed(self) -> int:
        return sum(1 for r in self.results if not r.passed)

    @property
    def pass_rate(self) -> float:
        if not self.results:
            return 1.0
        return self.n_passed / len(self.results)

    @property
    def all_passed(self) -> bool:
        return all(r.passed for r in self.results)

    def failed_tests(self) -> List[TestResult]:
        return [r for r in self.results if not r.passed]


class TestRunner:
    """Runs tests using pytest and captures structured results."""

    def __init__(self, project_dir: str, python_path: str = "python3"):
        self.project_dir = project_dir
        self.python_path = python_path

    def run(self, test_path: str = "tests/",
            timeout: int = 120) -> TestSuiteResult:
        """Run pytest and return structured results."""
        cmd = [
            self.python_path, "-m", "pytest", test_path,
            "-v", "--tb=short", "--no-header", "-q",
            f"--timeout={timeout}",
        ]

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True,
                cwd=self.project_dir, timeout=timeout + 30,
            )
            return self._parse_pytest_output(result.stdout, result.stderr)
        except subprocess.TimeoutExpired:
            return TestSuiteResult(results=[
                TestResult(name="timeout", passed=False, error="Test suite timed out")
            ])
        except Exception as e:
            return TestSuiteResult(results=[
                TestResult(name="error", passed=False, error=str(e))
            ])

    def run_single(self, test_file: str, test_name: str = "",
                   timeout: int = 60) -> TestResult:
        """Run a single test."""
        target = f"{test_file}::{test_name}" if test_name else test_file
        cmd = [self.python_path, "-m", "pytest", target, "-v", "--tb=short"]

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True,
                cwd=self.project_dir, timeout=timeout,
            )
            passed = result.returncode == 0
            return TestResult(
                name=test_name or test_file,
                passed=passed,
                output=result.stdout,
                error=result.stderr if not passed else "",
            )
        except Exception as e:
            return TestResult(name=test_name or test_file, passed=False, error=str(e))

    def _parse_pytest_output(self, stdout: str, stderr: str) -> TestSuiteResult:
        """Parse pytest verbose output into structured results."""
        results = []
        for line in stdout.split('\n'):
            line = line.strip()
            if ' PASSED' in line:
                name = line.split(' PASSED')[0].strip()
                results.append(TestResult(name=name, passed=True))
            elif ' FAILED' in line:
                name = line.split(' FAILED')[0].strip()
                results.append(TestResult(name=name, passed=False, error=line))
            elif ' ERROR' in line:
                name = line.split(' ERROR')[0].strip()
                results.append(TestResult(name=name, passed=False, error=line))

        return TestSuiteResult(results=results)
