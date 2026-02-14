"""Tests for E2E framework."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
import numpy as np
from e2e.convergence import (
    measure_contraction_rate, is_contractive,
    predicted_convergence_steps, fit_exponential_convergence,
)
from e2e.test_runner import TestResult, TestSuiteResult


class TestConvergence:
    def test_contractive_trajectory(self):
        traj = [0.5, 0.75, 0.875, 0.9375]
        assert is_contractive(traj)

    def test_contraction_rate_measurement(self):
        traj = [0.5, 0.75, 0.875, 0.9375]
        c = measure_contraction_rate(traj)
        assert 0 < c < 1
        assert abs(c - 0.5) < 0.01

    def test_predicted_steps(self):
        k = predicted_convergence_steps(0.5, 0.5, tolerance=0.01)
        assert k > 0
        assert k < 20

    def test_exponential_fit(self):
        traj = [0.5, 0.75, 0.875, 0.9375, 0.96875]
        fit = fit_exponential_convergence(traj)
        assert fit['R2'] > 0.9
        assert 0 < fit['c'] < 1


class TestTestRunner:
    def test_suite_result_metrics(self):
        suite = TestSuiteResult(results=[
            TestResult("test1", True),
            TestResult("test2", False, error="assertion error"),
            TestResult("test3", True),
        ])
        assert suite.n_passed == 2
        assert suite.n_failed == 1
        assert suite.pass_rate == pytest.approx(2/3)
        assert not suite.all_passed

    def test_empty_suite(self):
        suite = TestSuiteResult()
        assert suite.pass_rate == 1.0
        assert suite.all_passed
